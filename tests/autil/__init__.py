# -*- coding: utf-8 -*-
#
# 2017 Darko Poljak (darko.poljak at gmail.com)
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
import os.path as op
import tarfile

import skonfig.autil

import tests as test

my_dir = op.abspath(op.dirname(__file__))
fixtures = op.join(my_dir, 'fixtures')
explorers_path = op.join(fixtures, 'explorer')


class AUtilTestCase(test.SkonfigTestCase):
    def test_tar(self):
        source = explorers_path
        for mode in skonfig.autil.archiving_modes:
            try:
                (tarpath, fcnt) = skonfig.autil.tar(source, mode)
                self.assertIsNotNone(tarpath)
                fcnt = 0
                with tarfile.open(tarpath, "r:" + mode.tarmode) as tar:
                    for tarinfo in tar:
                        fcnt += 1
                os.remove(tarpath)
                self.assertGreater(fcnt, 0)
            except tarfile.CompressionError:
                pass


if __name__ == "__main__":
    import unittest

    unittest.main()
