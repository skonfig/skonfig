# -*- coding: utf-8 -*-
#
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

import os

import cdist.autil

_logger = cdist.log.getLogger(__name__)


def get_cache_dir():
    return os.path.join(
        os.getenv(
            "XDG_CACHE_HOME",
            os.path.join(os.path.expanduser("~"), ".cache")),
        "skonfig")


def get_config_search_dirs():
    if "SKONFIG_PATH" in os.environ:
        # parse SKONFIG_PATH environment variable for config file locations
        search_dirs = os.environ["SKONFIG_PATH"].split(os.pathsep)
    else:
        # use default locations
        search_dirs = ["~/.skonfig", "/etc/skonfig"]

    # filter out non-existing directories
    search_dirs = [
        search_dir
        for search_dir in map(os.path.expanduser, search_dirs)
        if os.path.isdir(search_dir)]

    # In cdist "last wins", but from user perspective we want "first wins"
    # (just like with $PATH). This is also useful in next function,
    # _set_from_files, where we overwrite previous value(s).
    return list(reversed(search_dirs))


class any_setting(property):
    private_name = None

    def __init__(self, *, default=None, doc=None, nullable=False):
        super().__init__(
            lambda container: self._get(container),
            lambda container, value: self._set(container, value),
            None,
            doc)

        if default is None and not nullable:
            raise ValueError(
                "if the setting is not nullable a default is required.")

        self.is_nullable = nullable
        self.default = self.transform_store(default)

    def __set_name__(self, owner, name):
        self.private_name = "_%s" % (name)

    def transform_load(self, value):
        return value

    def transform_store(self, value):
        if value is None and not self.is_nullable:
            raise ValueError("this property is not nullable")

        return value

    def _get(self, container):
        if not self.private_name:
            return None
        return self.transform_load(
            getattr(container, self.private_name, self.default))

    def _set(self, container, value):
        if not self.private_name:
            raise ValueError(
                "cannot assign to this setting, has no private_name.")

        value = self.transform_store(value)
        setattr(container, self.private_name, value)


class string_setting(any_setting):
    def transform_store(self, value):
        value = super().transform_store(value)

        if value is None:
            return value

        if not isinstance(value, str):
            raise ValueError("value must be a str")

        return value


class choice_setting(any_setting):
    _choices = ()

    def transform_store(self, value):
        value = super().transform_store(value)

        if value is None:
            return value

        if value not in self._choices:
            raise ValueError(
                "invalid value. value must be one of: %s" % (
                    ", ".join("\"%s\"" % (s) for s in self._choices)))

        return value


class file_setting(string_setting):
    def transform_store(self, value):
        value = super().transform_store(value)

        if value is None:
            return value

        if not os.path.isfile(value):
            raise ValueError("No such file: %s" % (value))

        return value


class executable_setting(file_setting):
    def transform_store(self, value):
        value = super().transform_store(value)

        if value is None:
            return value

        if not os.access(value, os.X_OK):
            raise ValueError("File is not executable: %s" % (value))

        return value


class archiving_setting(any_setting):
    def transform_store(self, value):
        value = super().transform_store(value)

        if value is None:
            return value

        if isinstance(value, str):
            value = cdist.autil.mode_from_str(value)
        elif isinstance(value, cdist.autil.ArchivingMode):
            pass
        else:
            raise ValueError("invalid archiving mode: %r" % (value))

        return value


class coloured_output_setting(choice_setting):
    _choices = ("auto", "always", "never")

    def transform_load(self, value):
        value = super().transform_load(value)

        if value is None:
            return None

        if isinstance(value, bool):
            return val
        elif value == "always":
            return True
        elif value == "never":
            return False
        elif value == "auto":
            import sys
            return "NO_COLOR" not in os.environ and sys.stdout.isatty()


class loglevel_setting(any_setting):
    def transform_store(self, value):
        value = super().transform_store(value)

        if value is None:
            return None

        if isinstance(value, int) and not isinstance(value, bool):
            return value
        elif isinstance(value, str):
            import logging
            # < Python 3.4
            levels_pre34 = getattr(logging, "_levelNames", {})
            # >= Python 3.4
            levels_available = getattr(logging, "_levelToName", levels_pre34)

            for (level, level_name) in levels_available.items():
                if value == level_name:
                    return level

            raise ValueError("invalid logging level: %s" % (value))
        else:
            raise ValueError("invalid value: %s" % (value))


class jobs_setting(any_setting):
    def transform_store(self, value):
        value = super().transform_store(value)

        if not isinstance(value, int):
            raise ValueError("value must be an int")
        elif value == -1:
            # special case
            import multiprocessing
            value = min(4, multiprocessing.cpu_count())
        elif value < 1:
            raise ValueError("value must be at least 1")

        return value


class search_path_setting(any_setting):
    def __init__(self, *, default=[], doc=None, nullable=False):
        super().__init__(default=default, doc=doc, nullable=nullable)

    def transform_store(self, value):
        super().transform_store(value)

        if isinstance(value, str):
            # process as path string
            lst = value.split(os.pathsep)
        elif isinstance(value, (list, tuple)):
            # process as path list
            lst = value
        else:
            raise ValueError("invalid value for search path option")

        return lst


class SettingsContainer:
    archiving_mode = archiving_setting(
        nullable=True,
        default="tar",
        doc="""\
        Use specified archiving method to transfer multiple files to the
        target.
        Valid values include: none, tar, tgz, tbz2 and txz.
        """)
    cache_path_pattern = string_setting(
        nullable=False,
        default="%N",
        doc="""\
        Specify cache path pattern.
        Valid formatter options include:
        ... TODO
        """)
    colored_output = coloured_output_setting(
        nullable=False,
        default="never",
        doc="""\
        Colorize skonfig's output. If enabled, skonfig will use different
        colours for different log levels.
        Recognized values are: "always", "never", and "auto".

        If the value is "auto", colors are enabled if stdout is a TTY unless
        the NO_COLOR (https://no-color.org/) environment variable is defined.
        """)
    conf_dir = search_path_setting(
        nullable=True,
        doc="""\
        List of configuration directories separated with the character
        conventionally used by the operating system to separate search path
        components (as in PATH), such as ':' for POSIX or ';' for Windows.  If
        also specified at command line then values from command line are
        appended to this value.  Notice that this works in a "last one wins"
        fashion, so if a type is redefined in multiple conf_dirs, the last one
        in which it is defined will be used.  Consider using a unique prefix
        for your own roles if this can be an issue.
        """)
    init_manifest = file_setting(
        nullable=True,
        doc="""\
        Specify the initial manifest.
        """)
    jobs = jobs_setting(
        nullable=False,
        default=-1,
        doc="""\
        Specify number of jobs for parallel processing.
        If -1 then the number of CPUs in this system (maximum: 4) is used.
        If 0 or 1 then parallel processing is disabled.
        If set to a positive number then the specified maximum number of
        processes will be used.
        """)
    local_shell = executable_setting(
        nullable=False,
        default="/bin/sh",
        doc="""\
        Shell command used for local execution.
        """)
    out_path = string_setting(
        nullable=True,
        doc="""\
        Working directory for skonfig on this machine.
        """)
    remote_exec = string_setting(
        nullable=True,
        doc="""\
        Command to use for remote execution (should behave like SSH).

        By default ssh(1) is used.
        """)
    remote_out_path = string_setting(
        nullable=False,
        default="/var/lib/skonfig",
        doc="""\
        Working directory for skonfig on the remote host.
        """)
    remote_shell = string_setting(
        nullable=False,
        default="/bin/sh",
        doc="""\
        Shell command to use on the remote host for execution of scripts.
        """)
    verbosity = loglevel_setting(
        nullable=False,
        default="INFO",
        doc="""\
        Set verbosity level.
        Valid values are: ERROR, WARNING, INFO, VERBOSE, DEBUG, TRACE and OFF.
        """)

    def __repr__(self):
        return "\n".join(
            "%s = %s" % (k, v)
            for (k, v) in self.__dict__.items())

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    __config_file_settings_map = {
        # config file option = {setting=name of setting, getf=get func to use}
        "archiving": {"setting": "archiving_mode", "getf": "get"},
        "cache_path_pattern": {"setting": "cache_path_pattern", "getf": "get"},
        "colored_output": {"setting": "colored_output", "getf": "get"},
        "conf_dir": {"setting": "conf_dir", "getf": "get"},
        "init_manifest": {"setting": "init_manifest", "getf": "get"},
        "jobs": {"setting": "jobs", "getf": "getint"},
        "local_shell": {"setting": "local_shell", "getf": "get"},
        "out_path": {"setting": "out_path", "getf": "get"},
        "remote_exec": {"setting": "remote_exec", "getf": "get"},
        "remote_out_path": {"setting": "remote_out_path", "getf": "get"},
        "remote_shell": {"setting": "remote_shell", "getf": "get"},
        "verbosity": {"setting": "verbosity", "getf": "get"},
        }

    def update_from_config_files(self, config_files=None):
        # searches and updates a settings object from a given config files
        # list, or, if none is given, uses default locations

        import configparser

        _map = self.__config_file_settings_map

        if config_files is None:
            # default config files
            config_files = [
                os.path.join(sdir, "config")
                for sdir in get_config_search_dirs()
                if os.path.isfile(os.path.join(sdir, "config"))]

        for config_file in config_files:
            _logger.debug("reading configuration from: %s", config_file)
            parser = configparser.RawConfigParser()
            parser.read(config_file)

            if not parser.has_section("skonfig"):
                _logger.warning(
                    "Config file %s has no skonfig section. Ignoring.",
                    config_file)
                continue

            for k in parser.options("skonfig"):
                if k not in _map:
                    _logger.error(
                        "Invalid configuration option \"%s\" found in file "
                        "\"%s\". Ignoring.", k, config_file)
                    continue

                v = getattr(parser, _map[k]["getf"])("skonfig", k)

                try:
                    _logger.trace("Setting %s = %r from config file %s",
                                  k, v, config_file)
                    setattr(self, _map[k]["setting"], v)
                except ValueError as e:
                    _logger.error(
                        "Configuration option \"%s\" has invalid value \"%s\" "
                        "in file \"%s\": %s",
                        k, v, config_file, e)

    __env_settings_map = {
        'SKONFIG_PATH': 'conf_dir',
        'SKONFIG_LOCAL_SHELL': 'local_shell',
        'SKONFIG_REMOTE_SHELL': 'remote_shell',
        'SKONFIG_REMOTE_EXEC': 'remote_exec',
        'SKONFIG_COLORED_OUTPUT': 'colored_output',
        '__cdist_log_level': 'verbosity',
        }

    def update_from_env(self, environ=os.environ):
        for (env, setting) in self.__env_settings_map.items():
            if env not in environ:
                continue

            try:
                _logger.trace("Setting %s = %r from environment",
                              setting, environ[env])
                setattr(self, setting, environ[env])
            except ValueError as e:
                _logger.error(
                    "Environment variable \"%s\" has invalid value \"%s\": %s",
                    env, environ[env], e)
