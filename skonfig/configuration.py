import logging
import multiprocessing
import os

from cdist.configuration import _VERBOSITY_VALUES


_logger = logging.getLogger(__name__)

_config_options = {
    "archiving": {
        "options": ["none", "tar", "tgz", "tbz2", "txz"],
        "default": "tar",
        },
    "cache_path_pattern": {
        "default": "%h",
        },
    "colored_output": {
        "options": ["always", "never", "auto"],
        "default": "never",
        },
    "conf_dir": {
        },
    "init_manifest": {
        },
    "jobs": {
        "type": "int",
        "default": min(4, multiprocessing.cpu_count()),
        "special_cases": {
            -1: min(4, multiprocessing.cpu_count()),
            }
        },
    "local_shell": {
        "default": "/bin/sh",
        },
    "out_path": {
        },
    "parallel": {
        "type": "int",
        "default": 0,
        },
    "remote_exec": {
        },
    "remote_out_path": {
        },
    "remote_shell": {
        "default": "/bin/sh",
        },
    "verbosity": {
        "options": _VERBOSITY_VALUES,
        "default": "INFO",
        },
    }


def _set_defaults(configuration):
    configuration["cache_path_pattern"] = "%N"
    defaults = {
        k: v["default"]
        for (k, v) in _config_options.items()
        if "default" in v}
    for option in defaults:
        if option not in configuration:
            configuration[option] = defaults[option]


def _get_search_dirs():
    pathsep_search_dirs = os.getenv("SKONFIG_PATH", "~/.skonfig:/etc/skonfig")
    search_dirs = []
    for search_dir in pathsep_search_dirs.split(":"):
        search_dir = os.path.expanduser(search_dir)
        if os.path.isdir(search_dir):
            search_dirs.append(search_dir)
    # In cdist "last wins", but from user perspective we want "first wins"
    # (just like with $PATH). This is also useful in next function,
    # _set_from_files, where we overwrite previous value(s).
    search_dirs.reverse()
    return search_dirs


def _set_from_files(configuration):
    import configparser
    for search_dir in _get_search_dirs():
        configuration_file = os.path.join(search_dir, "config")
        if not os.path.isfile(configuration_file):
            continue
        _logger.debug("reading configuration from %s", configuration_file)
        parser = configparser.RawConfigParser()
        parser.read(configuration_file)

        for k in parser["skonfig"]:
            if k not in _config_options:
                _logger.error(
                    "Invalid configuration option \"%s\" found in file %s. "
                    "Ignoring.",
                    k, configuration_file)
                continue

            spec = _config_options[k]

            if "type" in spec:
                config_value = \
                    getattr(parser, ("get" + spec["type"]))("skonfig", k)
            else:
                config_value = parser.get("skonfig", k)

            if "options" in spec and config_value not in spec["options"]:
                _logger.error(
                    "Invalid value for configuration option \"%s\": \"%s\". "
                    "Ignoring.",
                    k, config_value)
                continue

            if config_value in spec.get("special_cases", {}):
                config_value = spec["special_cases"][config_value]

            configuration[k] = config_value


def _set_cdist_conf_dir(configuration):
    # cdist needs "conf_dir" option to function,
    # but we don't use it, because we have sets.
    cdist_conf_dir = []
    search_dirs = _get_search_dirs()
    for search_dir in search_dirs:
        sets_dir = os.path.join(search_dir, "set")
        if os.path.isdir(sets_dir):
            for set_dir in os.listdir(sets_dir):
                cdist_conf_dir.append(os.path.join(sets_dir, set_dir))
        cdist_conf_dir.append(search_dir)
    configuration["conf_dir"] = cdist_conf_dir


def get():
    configuration = {}
    _set_defaults(configuration)
    _set_from_files(configuration)
    _set_cdist_conf_dir(configuration)
    if not configuration["conf_dir"]:
        _logger.error("no configuration")
        return False
    for option in configuration:
        _logger.debug("%s: %s", option, configuration[option])
    return configuration


def get_cache_dir():
    return os.path.join(
        os.getenv(
            "XDG_CACHE_HOME",
            os.path.join(
                os.path.expanduser("~"),
                ".cache"
            )
        ),
        "skonfig"
    )
