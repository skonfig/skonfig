import logging
import os


_logger = logging.getLogger(__name__)


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


def _get_search_dirs():
    pathsep_search_dirs = os.getenv("SKONFIG_PATH", "~/.skonfig:/etc/skonfig")
    search_dirs = []
    for search_dir in pathsep_search_dirs.split(":"):
        search_dir = os.path.expanduser(search_dir)
        if not os.path.isdir(search_dir):
            continue
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
        configuration.update(dict(parser.items("skonfig")))


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
