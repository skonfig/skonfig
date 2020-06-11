# -*- coding: utf-8 -*-
#
# 2016-2017 Darko Poljak (darko.poljak at gmail.com)
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
#

import fileinput


def hostfile_process_line(line, strip_func=str.strip):
    """Return entry from read line or None if no entry present."""
    if not line:
        return None
    # remove comment if present
    comment_index = line.find('#')
    if comment_index >= 0:
        foo = line[:comment_index]
    else:
        foo = line
    # remove leading and trailing whitespaces
    foo = strip_func(foo)
    # skip empty lines
    if foo:
        return foo
    else:
        return None


class HostSource:
    """
    Host source object.
    Source can be a sequence or filename (stdin if \'-\').
    In case of filename each line represents one host.
    """
    def __init__(self, source):
        self.source = source

    def _process_file_line(self, line):
        return hostfile_process_line(line)

    def _hosts_from_sequence(self):
        for host in self.source:
            yield host

    def _hosts_from_file(self):
        for line in fileinput.input(files=(self.source)):
            host = self._process_file_line(line)
            if host:
                yield host

    def hosts(self):
        if not self.source:
            return

        if isinstance(self.source, str):
            for x in self._hosts_from_file():
                yield x
        else:
            for x in self._hosts_from_sequence():
                yield x

    def __call__(self):
        for x in self.hosts():
            yield x
