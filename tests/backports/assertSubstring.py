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
# backport of unittest/case.py's assert(Not)StartsWith(),
# assert(Not)EndsWith().
#

from unittest.util import safe_repr

def _tail_type_check(self, s, tails, msg):
    if not isinstance(tails, tuple):
        tails = (tails,)
    for tail in tails:
        if isinstance(tail, str):
            if not isinstance(s, str):
                self.fail(self._formatMessage(msg,
                        'Expected str, not %s' % (type(s).__name__)))
        elif isinstance(tail, (bytes, bytearray)):
            if not isinstance(s, (bytes, bytearray)):
                self.fail(self._formatMessage(msg,
                        'Expected bytes, not %s' % (type(s).__name__)))

def assertStartsWith(self, s, prefix, msg=None):
    try:
        if s.startswith(prefix):
            return
    except (AttributeError, TypeError):
        self._tail_type_check(s, prefix, msg)
        raise
    a = safe_repr(s, short=True)
    b = safe_repr(prefix)
    if isinstance(prefix, tuple):
        standardMsg = "%s doesn't start with any of %s" % (a, b)
    else:
        standardMsg = "%s doesn't start with %s" % (a, b)
    self.fail(self._formatMessage(msg, standardMsg))

def assertNotStartsWith(self, s, prefix, msg=None):
    try:
        if not s.startswith(prefix):
            return
    except (AttributeError, TypeError):
        self._tail_type_check(s, prefix, msg)
        raise
    if isinstance(prefix, tuple):
        for x in prefix:
            if s.startswith(x):
                prefix = x
                break
    a = safe_repr(s, short=True)
    b = safe_repr(prefix)
    self.fail(self._formatMessage(msg, "%s starts with %s" % (a, b)))

def assertEndsWith(self, s, suffix, msg=None):
    try:
        if s.endswith(suffix):
            return
    except (AttributeError, TypeError):
        self._tail_type_check(s, suffix, msg)
        raise
    a = safe_repr(s, short=True)
    b = safe_repr(suffix)
    if isinstance(suffix, tuple):
        standardMsg = "%s doesn't end with any of %s" % (a, b)
    else:
        standardMsg = "%s doesn't end with %s" % (a, b)
    self.fail(self._formatMessage(msg, standardMsg))

def assertNotEndsWith(self, s, suffix, msg=None):
    try:
        if not s.endswith(suffix):
            return
    except (AttributeError, TypeError):
        self._tail_type_check(s, suffix, msg)
        raise
    if isinstance(suffix, tuple):
        for x in suffix:
            if s.endswith(x):
                suffix = x
                break
    a = safe_repr(s, short=True)
    b = safe_repr(suffix)
    self.fail(self._formatMessage(msg, "%s ends with %s" % (a, b)))
