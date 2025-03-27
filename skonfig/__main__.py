# -*- coding: utf-8 -*-
#
# 2022,2024 Ander Punnar (ander at kvlt.ee)
# 2025 Dennis Camera (dennis.camera at riiengineering.ch)
#
# This file is part of skonfig.
#
# skonfig is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# skonfig is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with skonfig. If not, see <http://www.gnu.org/licenses/>.
#

import atexit
import os
import shutil
import sys
import tempfile

import skonfig


def _initialise_global_settings():
    import skonfig.settings
    settings = skonfig.settings.SettingsContainer()

    # read values from config file(s)
    settings.update_from_config_files()

    # read values from environment variables
    settings.update_from_env()

    # resolve sets
    search_dirs = skonfig.settings.get_config_search_dirs()
    for search_dir in search_dirs:
        sets_dir = os.path.join(search_dir, "set")
        if os.path.isdir(sets_dir):
            settings.conf_dir += [
                os.path.join(sets_dir, set_dir)
                for set_dir in os.listdir(sets_dir)
                if os.path.isdir(os.path.join(sets_dir, set_dir))]

    # because last one wins
    settings.conf_dir += search_dirs

    return settings


def run_main():
    import skonfig.arguments
    (parser, arguments) = skonfig.arguments.get()

    if arguments.version:
        print("skonfig", skonfig.__version__)
        return

    if arguments.dump:
        import skonfig.dump
        skonfig.dump.run(arguments.host)
        return

    if not arguments.host:
        from argparse import (ArgumentError, _)
        e = ArgumentError(
            None, _("the following arguments are required: %s") % ("host"))
        parser.error(str(e))
        sys.exit(1)

    try:
        settings = _initialise_global_settings()

        # configure logging
        if arguments.verbosity:
            loglevel = skonfig.arguments.verbosity_to_logging_level(
                arguments.verbosity)
        else:
            loglevel = settings.verbosity

        logging.basicConfig(level=loglevel)

        if settings.colored_output:
            skonfig.logging.CdistFormatter.USE_COLORS = True

        target_host = arguments.host

        jobs = arguments.jobs or settings.jobs

        if arguments.manifest:
            # first, we use the initial manifest provided in argv (-i)
            init_manifest = arguments.manifest

            if init_manifest == "-":
                # read manifest from stdin, only possible using argv option
                try:
                    (handle, init_manifest_temp_path) = tempfile.mkstemp(
                        prefix="skonfig.stdin.")
                    atexit.register(lambda: os.remove(init_manifest_temp_path))
                    with os.fdopen(handle, "w") as fd:
                        fd.write(sys.stdin.read())
                    init_manifest = init_manifest_temp_path
                except (IOError, OSError) as e:
                    raise skonfig.Error(
                        "Creating tempfile for stdin data failed: %s" % (e))
        elif settings.init_manifest is not None:
            # then, we respect the setting chosen in the config file
            init_manifest = settings.init_manifest
        else:
            # default: use the default as skonfig.exec.local detects it.
            init_manifest = None

        import skonfig.config

        skonfig.config.Config.onehost(
            target_host,
            host_base_path,
            override_init_manifest=init_manifest,
            settings=settings,
            dry_run=arguments.dry_run,
            jobs=jobs,
            remove_remote_files_dirs=(arguments.verbosity < 2))
    except skonfig.Error as e:
        pass


def run_emulator():
    import skonfig.emulator
    emulator = skonfig.emulator.Emulator(sys.argv)
    emulator.run()


def run():
    try:
        if os.path.basename(sys.argv[0]).startswith("__"):
            run_emulator()
        else:
            run_main()
    except KeyboardInterrupt:
        sys.exit(2)


if __name__ == "__main__":
    # change argv[0] because __main__.py would trigger the emulator
    sys.argv[0] = "skonfig"
    run()
