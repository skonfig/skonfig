# -*- coding: utf-8 -*-
#
# 2011-2012 Nico Schottelius (nico-cdist at schottelius.org)
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

import logging
import os
import sys
import tempfile
import unittest

try:
    from unittest.mock import patch
except ImportError:
    from .backports.mock import patch

cdist_base_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../"))

cdist_exec_path = os.path.join(cdist_base_path, "bin/skonfig")

global_fixtures_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "fixtures"))


class CdistTestCase(unittest.TestCase):
    remote_exec = os.path.join(global_fixtures_dir, "remote", "exec")

    # host, hostname, fqdn
    target_host = ('cdisttesthost', 'cdisttesthost', 'cdisttesthost')

    def mkdtemp(self, **kwargs):
        return tempfile.mkdtemp(prefix='tmp.cdist.test.', **kwargs)

    def mkstemp(self, **kwargs):
        return tempfile.mkstemp(prefix='tmp.cdist.test.', **kwargs)


if sys.version_info[:2] < (3, 4):
    from .backports.assertLogs import _AssertLogsContext
    CdistTestCase.assertLogs = lambda self, logger=None, level=None: \
        _AssertLogsContext(self, logger, level, no_logs=False)
