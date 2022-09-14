import logging
import os


_logger = logging.getLogger(__name__)

CONFIGURATION_HOME_PATH = os.path.join(os.getenv("HOME"), ".skonfig")
CONFIGURATION_FILE_PATH = os.path.join(CONFIGURATION_HOME_PATH, "config")


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
        configuration["conf_dir"] = [
            conf_dir
            for conf_dir in configuration["conf_dir"].split(os.pathsep)
            if os.path.isdir(conf_dir)
        ]
    else:
        configuration["conf_dir"] = []
    if os.path.isdir(CONFIGURATION_HOME_PATH):
        configuration["conf_dir"].insert(0, CONFIGURATION_HOME_PATH)
    # find sets and insert them into PATH
    sets_dir = os.path.join(CONFIGURATION_HOME_PATH, "set")
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
    if not configuration["conf_dir"]:
        # since we expect everything is in ~/.skonfig,
        # then no conf_dirs implies no conf home
        _logger.error(
            "no configuration found, %s does not exist",
            CONFIGURATION_HOME_PATH
        )
        return False
    for option in configuration:
        _logger.debug("%s: %s", option, configuration[option])
    return configuration
