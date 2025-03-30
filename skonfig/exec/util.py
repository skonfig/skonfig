# -*- coding: utf-8 -*-
#
# 2016-2017 Darko Poljak (darko.poljak at gmail.com)
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

import itertools
import os
import subprocess

import skonfig

from collections import OrderedDict

from skonfig.util import shquot


def get_std_fd(base_path, name):
    path = os.path.join(base_path, name)
    return open(path, 'ba+')


# subprocess.DEVNULL is added in 3.3.
if hasattr(subprocess, 'DEVNULL'):
    def log_std_fd(log, command, stdfd, prefix):
        if stdfd is not None and stdfd != subprocess.DEVNULL:
            stdfd.seek(0, 0)
            log.trace("Command: %s; %s: %s",
                      shquot.join(command),
                      prefix, stdfd.read().decode())
else:
    def log_std_fd(log, command, stdfd, prefix):
        if stdfd is not None and not isinstance(stdfd, int):
            stdfd.seek(0, 0)
            log.trace("Command: %s; %s: %s",
                      shquot.join(command),
                      prefix, stdfd.read().decode())


def resolve_conf_dirs(*args):
    return list(OrderedDict.fromkeys(itertools.chain.from_iterable(args)))
