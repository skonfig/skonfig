import logging
import os
import sys


_logger = logging.getLogger(__name__)

CONFIGURATION_HOME_PATH = os.path.join(os.getenv("HOME"), ".skonfig")
CONFIGURATION_FILE_PATH = os.path.join(CONFIGURATION_HOME_PATH, "config")

DEFAULT_INITIAL_MANIFEST = """
#!/bin/sh -e

hostname="$( cat "$__global/explorer/hostname" )"

if [ -f "$__manifest/$__target_host" ]
then
    . "$__manifest/$__target_host"
elif
    [ -f "$__manifest/$hostname" ]
then
    . "$__manifest/$hostname"
fi
"""


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
    for option in configuration:
        _logger.debug("%s: %s", option, configuration[option])
    return configuration


def bootstrap():
    if os.path.isdir(CONFIGURATION_HOME_PATH):
        return True
    _logger.info("first run detected")
    for path in [
        CONFIGURATION_HOME_PATH,
        os.path.join(CONFIGURATION_HOME_PATH, "dump"),
        os.path.join(CONFIGURATION_HOME_PATH, "explorer"),
        os.path.join(CONFIGURATION_HOME_PATH, "files"),
        os.path.join(CONFIGURATION_HOME_PATH, "manifest"),
        os.path.join(CONFIGURATION_HOME_PATH, "set"),
        os.path.join(CONFIGURATION_HOME_PATH, "type")
    ]:
        if not os.path.isdir(path):
            os.mkdir(path, mode=0o700)
            _logger.info("created directory `%s'", path)
    initial_manifest_path = os.path.join(CONFIGURATION_HOME_PATH, "manifest", "init")
    if not os.path.isfile(initial_manifest_path):
        with open(initial_manifest_path, "w") as handle:
            handle.write(DEFAULT_INITIAL_MANIFEST)
        os.chmod(initial_manifest_path, 0o700)
        _logger.info("created initial manifest `%s'", initial_manifest_path)
    return True
