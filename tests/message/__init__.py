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
import tempfile

import tests as test

import skonfig.message


class MessageTestCase(test.SkonfigTestCase):

    def setUp(self):
        self.prefix = "cdist-test"
        self.content = "A very short story"

        self.tempdir = tempfile.mkdtemp()
        (fd, self.tempfile) = tempfile.mkstemp(dir=self.tempdir)
        os.close(fd)

        self.message = skonfig.message.Message(
            prefix=self.prefix, messages=self.tempfile, temp_dir=self.tempdir)

    def tearDown(self):
        os.remove(self.tempfile)
        self.message._cleanup()

    def test_env(self):
        """Ensure environment contains __messages_{in,out}."""
        self.assertIn("__messages_in", self.message.env)
        self.assertIn("__messages_out", self.message.env)

    def test_messages_files_location(self):
        expected_path = (self.tempdir + os.path.sep)
        self.assertStartsWith(self.message.messages_in, expected_path)
        self.assertStartsWith(self.message.messages_out, expected_path)

    def test_copy_content(self):
        """Ensure content copying is working."""

        with open(self.tempfile, "w") as f:
            f.write(self.content)

        self.message._copy_messages()

        with open(self.tempfile, "r") as f:
            testcontent = f.read()

        self.assertEqual(self.content, testcontent)

    def test_message_merge_prefix(self):
        """Ensure messages are merged and are prefixed."""

        expectedcontent = "{}:{}".format(self.prefix, self.content)

        out = self.message.env["__messages_out"]

        with open(out, "w") as fd:
            fd.write(self.content)

        self.message._merge_messages()

        with open(self.tempfile, "r") as f:
            testcontent = f.read()

        self.assertEqual(expectedcontent, testcontent)


if __name__ == '__main__':
    import unittest

    unittest.main()
