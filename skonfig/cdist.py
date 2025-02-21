import atexit
import logging
import os
import shutil
import sys
import tempfile

import cdist.log
import skonfig.settings

_logger = cdist.log.getLogger(__name__)


def _initialise_global_settings():
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


def run(skonfig_arguments):
    settings = _initialise_global_settings()

    # configure logging
    if skonfig_arguments.verbosity:
        loglevel = skonfig.arguments.verbosity_to_logging_level(
            skonfig_arguments.verbosity)
    else:
        loglevel = settings.verbosity

    logging.basicConfig(level=loglevel)

    if settings.colored_output:
        cdist.log.CdistFormatter.USE_COLORS = True

    target_host = skonfig_arguments.host

    jobs = skonfig_arguments.jobs or settings.jobs

    if skonfig_arguments.manifest:
        # first, we use the initial manifest provided in argv (-i)
        init_manifest = skonfig_arguments.manifest

        if init_manifest == '-':
            # read initial manifest from stdin, only possible using argv option
            try:
                (handle, initial_manifest_temp_path) = tempfile.mkstemp(
                    prefix='skonfig.stdin.')
                atexit.register(lambda: os.remove(initial_manifest_temp_path))
                with os.fdopen(handle, 'w') as fd:
                    fd.write(sys.stdin.read())
                init_manifest = initial_manifest_temp_path
            except (IOError, OSError) as e:
                raise cdist.Error(
                    "Creating tempfile for stdin data failed: %s" % (e))
    elif settings.init_manifest is not None:
        # then, we respect the setting chosen in the config file
        init_manifest = settings.init_manifest
    else:
        # default: use the default as cdist.exec.local detects it.
        init_manifest = None

    from cdist.config import Config as cdist_config

    host_base_path = cdist_config.create_temp_host_base_dir(
        settings.out_path)
    _logger.debug("Created temporary working directory for host \"%s\": %s",
                  target_host, host_base_path)

    cdist_config.onehost(
        target_host,
        host_base_path,
        override_init_manifest=init_manifest,
        settings=settings,
        dry_run=skonfig_arguments.dry_run,
        jobs=jobs,
        remove_remote_files_dirs=(skonfig_arguments.verbosity < 2))

    _logger.debug("Cleaning up %s", host_base_path)
    shutil.rmtree(host_base_path)

    return True


def emulator():
    import cdist.emulator
    cdist.emulator.Emulator(sys.argv).run()
    return True
