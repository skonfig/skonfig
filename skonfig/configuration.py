import logging
import os
import sys


_logger = logging.getLogger(__name__)

CONFIGURATION_DIRECTORY = "{}/.skonfig".format(os.getenv("HOME"))
CONFIGURATION_FILE_PATH = CONFIGURATION_DIRECTORY + "/config"


def _set_defaults(configuration):
    configuration["cache_path_pattern"] = "%N"
    defaults = {
        "archiving": "tar",
        "colored_output": "never",
        "parallel": 0
    }
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
    configuration["conf_dir"].insert(0, CONFIGURATION_DIRECTORY)
    # find sets and insert them into PATH
    sets_dir = os.path.join(CONFIGURATION_DIRECTORY, "set")
    if os.path.isdir(sets_dir):
        configuration["conf_dir"] += [
            os.path.join(sets_dir, s) for s in os.listdir(sets_dir)
        ]
    configuration["conf_dir"].reverse()


def get():
    if os.path.isfile(CONFIGURATION_FILE_PATH):
        import configparser
        parser = configparser.RawConfigParser()
        parser.read(CONFIGURATION_FILE_PATH)
        configuration = dict(parser.items("skonfig"))
    else:
        configuration = {}
    _set_defaults(configuration)
    _set_conf_dirs(configuration)
    for option in configuration:
        _logger.debug("%s: %s", option, configuration[option])
    return configuration
