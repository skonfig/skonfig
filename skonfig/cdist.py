import logging
import shutil
import sys

import cdist.log

_logger = cdist.log.getLogger(__name__)


def _arguments(skonfig_arguments):
    cdist_argv = ["config"]
    if skonfig_arguments.manifest:
        cdist_argv.append("-i")
        cdist_argv.append(skonfig_arguments.manifest)
    # how cdist parses -j flag:
    # no -j = single job
    # only -j = use cpu count
    # -j n = n jobs
    cdist_argv.append("-j")
    if skonfig_arguments.jobs:
        cdist_argv.append(skonfig_arguments.jobs)
    if skonfig_arguments.dry_run:
        cdist_argv.append("-n")
    # skonfig default verbosity level is INFO, which in cdist is one -v,
    # but for skonfig we use -v = VERBOSE, -vv = DEBUG and -vvv = TRACE.
    cdist_argv += ["-v"] * (skonfig_arguments.verbose + 1)
    cdist_argv.append(skonfig_arguments.host)

    import cdist.argparse
    cdist_parser = cdist.argparse.get_parsers()
    cdist_arguments = cdist_parser["main"].parse_args(cdist_argv)
    # for argument, value in vars(cdist_arguments).items():
    #     _logger.debug("cdist argv: %s: %s", argument, value)
    return cdist_arguments


def _configuration(cdist_arguments):
    import cdist.configuration
    cdist_configuration_init = cdist.configuration.Configuration(
        cdist_arguments,
        config_files=(),
        singleton=False)
    import skonfig.configuration
    skonfig_configuration = skonfig.configuration.get()
    if not skonfig_configuration:
        return False
    if cdist_arguments.verbose:
        skonfig_configuration["verbosity"] = cdist_arguments.verbose
    cdist_configuration_init.config["skonfig"].update(skonfig_configuration)
    cdist_configuration_args = cdist_configuration_init.get_args()
    import cdist.argparse
    cdist.argparse.handle_loglevel(cdist_configuration_args)
    cdist.argparse.handle_log_colors(cdist_configuration_args)
    cdist_configuration = vars(cdist_configuration_args)
    # for option in cdist_configuration:
    #     _logger.debug("%s: %s", option, cdist_configuration[option])
    return cdist_configuration


def run(skonfig_arguments):
    cdist_arguments = _arguments(skonfig_arguments)
    if not cdist_arguments:
        return False

    cdist_configuration = _configuration(cdist_arguments)
    if not cdist_configuration:
        return False

    target_host = cdist_arguments.host[0]

    from cdist.config import Config as cdist_config

    cdist_config._check_and_prepare_args(cdist_arguments)
    cdist_config.construct_remote_exec_patterns(cdist_arguments)
    host_base_path = cdist_config.create_temp_host_base_dir(
        cdist_arguments.out_path)
    _logger.debug("Created temporary working directory for host \"%s\": %s",
                  target_host, host_base_path)

    cdist_config.onehost(
        target_host,
        host_base_path,
        cdist_arguments,
        cdist_configuration,
        (skonfig_arguments.verbose < 2))

    _logger.debug("Cleaning up %s", host_base_path)
    shutil.rmtree(host_base_path)

    return True


def emulator():
    import cdist.emulator
    cdist.emulator.Emulator(sys.argv).run()
    return True
