# -*- coding: utf-8 -*-
#
# 2013 Nico Schottelius (nico-cdist at schottelius.org)
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
import shutil
import tempfile


class Message:
    """Support messaging between types"""
    def __init__(self, prefix, messages, temp_dir=None):
        self.prefix = prefix
        self.global_messages = messages

        (in_fd, self.messages_in) = tempfile.mkstemp(
            dir=temp_dir, suffix='.message_in')
        (out_fd, self.messages_out) = tempfile.mkstemp(
            dir=temp_dir, suffix='.message_out')

        os.close(in_fd)
        os.close(out_fd)

        self._copy_messages()

    @property
    def env(self):
        return {
            "__messages_in": self.messages_in,
            "__messages_out": self.messages_out,
            }

    def _copy_messages(self):
        """Copy global contents into our copy"""
        shutil.copyfile(self.global_messages, self.messages_in)

    def _cleanup(self):
        """remove temporary files"""
        if os.path.exists(self.messages_in):
            os.remove(self.messages_in)
        if os.path.exists(self.messages_out):
            os.remove(self.messages_out)

    def _merge_messages(self):
        """merge newly written lines into global file"""
        with open(self.messages_out) as messages_out, \
             open(self.global_messages, 'a') as global_messages:
            for line in messages_out:
                global_messages.write("%s:%s" % (self.prefix, line))

    def merge_messages(self):
        self._merge_messages()
        self._cleanup()
