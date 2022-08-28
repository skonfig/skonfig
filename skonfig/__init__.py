import argparse
import configparser
import logging
import os
import sys

from skonfig.version import VERSION as __version__

THIS_IS_SKONFIG = False

SKONFIG_CONFIGURATION_DIRECTORY = "{}/.skonfig".format(os.getenv("HOME"))
SKONFIG_CONFIGURATION_FILE_PATH = SKONFIG_CONFIGURATION_DIRECTORY + "/config"

logger = logging.getLogger("skonfig")


def run():
    import skonfig.cdist

    if os.path.basename(sys.argv[0])[:2] == "__":
        return skonfig.cdist.run_emulator()
    arguments = get_arguments()
    if arguments.verbose > 1:
        logger.setLevel(logging.DEBUG)
    if arguments.dump:
        import skonfig.dump
        return skonfig.dump.run(arguments.host)
    for argument, value in vars(arguments).items():
        skonfig.logger.debug("arguments: %s: %s", argument, value)
    return skonfig.cdist.run_config(arguments)


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-V",
        dest="version",
        action="store_true",
        help="print version"
    )
    parser.add_argument(
        "-d",
        dest="dump",
        action="store_true",
        help="print dumped hosts, -d <host> = print dump",
    )
    parser.add_argument(
        "-i",
        dest="manifest",
        metavar="path",
        help="initial manifest or '-' to read from stdin",
    )
    parser.add_argument(
        "-n",
        dest="dry_run",
        action="store_true",
        help="dry-run, do not execute generated code",
    )
    parser.add_argument(
        "-v",
        dest="verbose",
        action="count",
        default=0,
        help="-v = VERBOSE, -vv = DEBUG, -vvv = TRACE",
    )
    parser.add_argument("host", nargs="?", help="host to configure")
    arguments = parser.parse_args()
    if arguments.version:
        print("skonfig", __version__)
        sys.exit(0)
    if not arguments.host and not arguments.dump:
        parser.print_help()
        sys.exit(0)
    return arguments


def get_configuration():
    if os.path.isfile(SKONFIG_CONFIGURATION_FILE_PATH):
        parser = configparser.RawConfigParser()
        parser.read(SKONFIG_CONFIGURATION_FILE_PATH)
        configuration = dict(parser.items("skonfig"))
    else:
        configuration = {}
    _set_configuration_defaults(configuration)
    for option in configuration:
        logger.debug("configuration: %s: %s", option, configuration[option])
    return configuration


def _set_configuration_defaults(configuration):
    _set_conf_dirs(configuration)
    configuration["beta"] = True
    configuration["cache_path_pattern"] = "%N"
    defaults = {"archiving": "tar", "colored_output": "never", "parallel": 0}
    for option in defaults:
        if option not in configuration:
            configuration[option] = defaults[option]


def _set_conf_dirs(configuration):
    # loading order:
    #   ~/.skonfig/set/
    #   ~/.skonfig/config:conf_dirs = ...
    #   ~/.skonfig/
    if "conf_dir" in configuration:
        configuration["conf_dir"] = configuration["conf_dir"].split(os.pathsep)
    else:
        configuration["conf_dir"] = []
    configuration["conf_dir"].insert(0, SKONFIG_CONFIGURATION_DIRECTORY)
    # find sets and insert them into PATH
    sets_dir = os.path.join(SKONFIG_CONFIGURATION_DIRECTORY, "set")
    if os.path.isdir(sets_dir):
        configuration["conf_dir"] += [
            os.path.join(sets_dir, s) for s in os.listdir(sets_dir)
        ]
    configuration["conf_dir"].reverse()
