# -*- coding: utf-8 -*-
#
# 2012 Nico Schottelius (nico-cdist at schottelius.org)
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

import hashlib
import os


def str_hash(s):
    """Return hash of string s"""
    if isinstance(s, str):
        return hashlib.md5(s.encode('utf-8')).hexdigest()
    else:
        raise Error("Param should be string")


def ilistdir(path, recursive=False):
    """Return a directory listing of path as an interator.

    Hidden files and save files are ignored.
    """
    for f in os.listdir(path):
        if "." == f[0] or "~" == f[-1]:
            continue

        if recursive:
            full_path = os.path.join(path, f)
            if os.path.isdir(full_path):
                subprefix = os.path.join(f, "")
                for x in ilistdir(full_path, recursive=True):
                    yield (subprefix + x)
                continue

        yield f


def listdir(path, recursive=False):
    """Return a directory listing of path as a list."""
    return list(ilistdir(path, recursive=recursive))
