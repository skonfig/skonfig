# -*- coding: utf-8 -*-
#
# 2023 Dennis Camera (dennis.camera at riiengineering.ch)
#
# This file is part of cdist.
#
# cdist is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# cdist is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with cdist. If not, see <http://www.gnu.org/licenses/>.
#

import re
import shlex

_needs_shell_quoting = re.compile(r"[^\w@%+=:,./-]", re.ASCII).search


def join(cmd_args):
    return " ".join(map(quote, cmd_args))


def quote(s):
    """Return a shell-escaped version of the string *s*."""
    if not s:
        return "''"
    if _needs_shell_quoting(s) is not None:
        s = "'" + (s.replace("'", r"'\''")) + "'"

    return s


def split(s):
    return shlex.split(s)
