import os
import shutil
import sys

import skonfig

import cdist
import cdist.argparse
import cdist.banner
import cdist.config
import cdist.configuration
import cdist.emulator
import cdist.install
import cdist.integration
import cdist.shell


def get_arguments(skonfig_arguments):
    cdist_argv = ["config"]
    if skonfig_arguments.manifest:
        cdist_argv.append("-i")
        cdist_argv.append(skonfig_arguments.manifest)
    if skonfig_arguments.dry_run:
        cdist_argv.append("-n")
    # skonfig default verbosity level is INFO, which in cdist is one -v,
    # but for skonfig we use -v = VERBOSE, -vv = DEBUG and -vvv = TRACE.
    cdist_argv += ["-v"] * (skonfig_arguments.verbose + 1)
    cdist_argv.append(skonfig_arguments.host)
    cdist_parser = cdist.argparse.get_parsers()
    cdist_arguments = cdist_parser["main"].parse_args(cdist_argv)
    for argument, value in vars(cdist_arguments).items():
        skonfig.logger.debug("arguments: cdist: %s: %s", argument, value)
    return cdist_arguments


def get_configuration(cdist_arguments):
    cdist_configuration_init = cdist.configuration.Configuration(
        cdist_arguments, config_files=(), singleton=False
    )
    skonfig_configuration = skonfig.get_configuration()
    if cdist_arguments.verbose:
        skonfig_configuration["verbosity"] = cdist_arguments.verbose
    for option in skonfig_configuration:
        cdist_configuration_init.config["GLOBAL"][option] = \
            skonfig_configuration[option]
    cdist_configuration_args = cdist_configuration_init.get_args()
    cdist.argparse.handle_loglevel(cdist_configuration_args)
    cdist.argparse.handle_log_colors(cdist_configuration_args)
    cdist_configuration = vars(cdist_configuration_args)
    for option in cdist_configuration:
        skonfig.logger.debug(
            "configuration: cdist: %s: %s", option, cdist_configuration[option]
        )
    return cdist_configuration


def run_config(skonfig_arguments):
    cdist_arguments = get_arguments(skonfig_arguments)
    cdist_configuration = get_configuration(cdist_arguments)
    target_host = cdist_arguments.host[0]
    cdist_config = cdist.config.Config
    cdist_config.construct_remote_exec_copy_patterns(cdist_arguments)
    base_root_path = cdist_config.create_base_root_path(None)
    host_base_path, hostdir = cdist_config.create_host_base_dirs(
        target_host, base_root_path
    )
    cdist_config._check_and_prepare_args(cdist_arguments)
    cdist_config.onehost(
        target_host,
        None,
        host_base_path,
        hostdir,
        cdist_arguments,
        parallel=False,
        configuration=cdist_configuration,
        remove_remote_files_dirs=(skonfig_arguments.verbose < 2),
    )
    shutil.rmtree(base_root_path)


def run_emulator():
    cdist.emulator.Emulator(sys.argv).run()
