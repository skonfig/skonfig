# -*- coding: utf-8 -*-
#
# backported from Python stdlib by
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
# backport of unittest/case.py's assertLogs().
#

import logging


class _CapturingHandler(logging.Handler):
    def __init__(self, level):
        super().__init__(level)
        import collections
        self.watcher = collections.namedtuple(
            "_LoggingWatcher", ["records", "output"])([], [])

    def emit(self, record):
        self.watcher.records.append(record)
        self.watcher.output.append(self.format(record))


class _AssertLogsContext:
    LOGGING_FORMAT = "%(levelname)s:%(name)s:%(message)s"

    def __init__(self, test_case, logger_name, level, no_logs):
        self.test_case = test_case
        self.logger_name = logger_name
        self.level = logging.INFO
        for (lvl_, lvl_name) in getattr(logging, "_levelNames", {}).items():
            if level == lvl_name:
                self.level = lvl_
        self.msg = None
        self.no_logs = no_logs

    def _raiseFailure(self, standardMsg):
        raise self.test_case.failureException(
            self.test_case._formatMessage(self.msg, standardMsg))

    def __enter__(self):
        if isinstance(self.logger_name, logging.Logger):
            logger = self.logger = self.logger_name
        else:
            logger = self.logger = logging.getLogger(self.logger_name)
        formatter = logging.Formatter(self.LOGGING_FORMAT)
        handler = _CapturingHandler(self.level)
        handler.setFormatter(formatter)
        self.watcher = handler.watcher
        self.old_handlers = logger.handlers[:]
        self.old_level = logger.level
        self.old_propagate = logger.propagate
        logger.handlers = [handler]
        logger.setLevel(self.level)
        logger.propagate = False
        if self.no_logs:
            return
        return handler.watcher

    def __exit__(self, exc_type, exc_value, tb):
        self.logger.handlers = self.old_handlers
        self.logger.propagate = self.old_propagate
        self.logger.setLevel(self.old_level)
        if exc_type is not None:
            return False
        if self.no_logs:
            if len(self.watcher.records) > 0:
                self._raiseFailure(
                    "Unexpected logs found: {!r}".format(
                        self.watcher.output))
        else:
            if len(self.watcher.records) == 0:
                self._raiseFailure(
                    "no logs of level {} or higher triggered on {}".format(
                        logging.getLevelName(self.level), self.logger.name))
