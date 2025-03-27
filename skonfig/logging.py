# -*- coding: utf-8 -*-
#
# 2010-2013 Nico Schottelius (nico-cdist at schottelius.org)
# 2019-2020 Steven Armstrong
# 2021-2023 Dennis Camera (dennis.camera at riiengineering.ch)
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

import collections
import logging as _logging

from logging import *

root = _logging.root

# Define additional cdist logging levels.
OFF = CRITICAL + 10  # disable logging
addLevelName(OFF, 'OFF')
_logging.OFF = OFF

VERBOSE = INFO - 5
addLevelName(VERBOSE, 'VERBOSE')
_logging.VERBOSE = VERBOSE


def _verbose(self, msg, *args, **kwargs):
    self.log(VERBOSE, msg, *args, **kwargs)


Logger.verbose = _verbose


TRACE = DEBUG - 5
addLevelName(TRACE, 'TRACE')


def _trace(self, msg, *args, **kwargs):
    self.log(TRACE, msg, *args, **kwargs)


Logger.trace = _trace


_verbosity_level_off = -2

# All verbosity levels above 4 are TRACE.
_verbosity_level = collections.defaultdict(lambda: TRACE, {
    None: WARNING,
    _verbosity_level_off: OFF,
    -1: ERROR,
    0: WARNING,
    1: INFO,
    2: VERBOSE,
    3: DEBUG,
    4: TRACE,
    })

# Generate verbosity level constants:
# VERBOSE_OFF, VERBOSE_ERROR, VERBOSE_WARNING, VERBOSE_INFO, VERBOSE_VERBOSE,
# VERBOSE_DEBUG, VERBOSE_TRACE.
globals().update({
    ("VERBOSE_" + getLevelName(l)): i
    for i, l in _verbosity_level.items()
    if i is not None
    })


class CdistFormatter(Formatter):
    USE_COLORS = False
    RESET = '\033[0m'
    COLOR_MAP = {
        'ERROR': '\033[0;31m',
        'WARNING': '\033[0;33m',
        'INFO': '\033[0;94m',
        'VERBOSE': '\033[0;34m',
        'DEBUG': '\033[0;90m',
        'TRACE': '\033[0;37m',
    }

    def __init__(self, fmt):
        super().__init__(fmt=fmt)

    def format(self, record):
        msg = super().format(record)
        if self.USE_COLORS:
            color = self.COLOR_MAP.get(record.levelname)
            if color:
                msg = color + msg + self.RESET
        return msg


class DefaultLog(Logger):
    FORMAT = '%(levelname)s: %(name)s: %(message)s'

    class StdoutFilter(Filter):
        def filter(self, rec):
            return rec.levelno != ERROR

    class StderrFilter(Filter):
        def filter(self, rec):
            return rec.levelno == ERROR

    def __init__(self, name):
        import sys

        super().__init__(name)
        self.propagate = False

        formatter = CdistFormatter(self.FORMAT)

        stdout_handler = StreamHandler(sys.stdout)
        stdout_handler.addFilter(self.StdoutFilter())
        stdout_handler.setLevel(TRACE)
        stdout_handler.setFormatter(formatter)

        stderr_handler = StreamHandler(sys.stderr)
        stderr_handler.addFilter(self.StderrFilter())
        stderr_handler.setLevel(ERROR)
        stderr_handler.setFormatter(formatter)

        self.addHandler(stdout_handler)
        self.addHandler(stderr_handler)

    def verbose(self, msg, *args, **kwargs):
        self.log(VERBOSE, msg, *args, **kwargs)

    def trace(self, msg, *args, **kwargs):
        self.log(TRACE, msg, *args, **kwargs)


def log_level_env_var_val(log):
    return str(log.getEffectiveLevel())


def log_level_name_env_var_val(log):
    return getLevelName(log.getEffectiveLevel())


def setupDefaultLogging():
    del getLogger().handlers[:]
    setLoggerClass(DefaultLog)


setupDefaultLogging()
