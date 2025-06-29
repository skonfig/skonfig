# -*- coding: utf-8 -*-
#
# 2010-2011 Steven Armstrong (steven-cdist at armstrong.cc)
# 2011-2013 Nico Schottelius (nico-cdist at schottelius.org)
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

import glob
import logging
import os
import shlex
import shutil

import skonfig
import skonfig.settings
import skonfig.util

import tests as test

from skonfig import core
from skonfig.core import explorer
from skonfig.exec import (local, remote)

ilistdir = skonfig.util.ilistdir

my_dir = os.path.abspath(os.path.dirname(__file__))
fixtures = os.path.join(my_dir, 'fixtures')
conf_dir = os.path.join(fixtures, "conf")


class ExplorerClassTestCase(test.SkonfigTestCase):

    def setUp(self):
        self.temp_dir = self.mkdtemp()
        self.local_path = os.path.join(self.temp_dir, "local")
        hostdir = skonfig.util.str_hash(self.target_host[0])
        base_root_path = os.path.join(self.local_path, hostdir)
        self.remote_base_path = os.path.join(self.temp_dir, "remote")
        os.makedirs(self.remote_base_path)

        self.settings = skonfig.settings.SettingsContainer()
        self.settings.conf_dir = [conf_dir]

        self.local = local.Local(
            self.target_host,
            base_root_path,
            self.settings,
            exec_path=test.skonfig_exec_path)

        self.local.create_files_dirs()

        self.remote = remote.Remote(
            self.target_host,
            self.remote_exec,
            self.remote_base_path,
            self.settings,
            stdout_base_path=self.local.stdout_base_path,
            stderr_base_path=self.local.stderr_base_path)
        self.remote.create_files_dirs()

        self.explorer = explorer.Explorer(
            self.target_host,
            self.local,
            self.remote)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_list_global_explorer_names(self):
        """Ensure that all explorers are listed"""
        names = self.explorer.list_global_explorer_names()
        self.assertIn("foobar", names)
        self.assertIn("global", names)

    def test_transfer_global_explorers(self):
        """Ensure transferring explorers to remote works"""
        self.explorer.transfer_global_explorers()
        source = self.local.global_explorer_path
        destination = self.remote.global_explorer_path
        self.assertEqual(
            sorted(ilistdir(source, recursive=False)),
            sorted(ilistdir(destination, recursive=False)))

        self.assertFalse(
            os.path.exists(os.path.join(destination, ".hidden")))

    def test_run_global_explorer(self):
        """Check that running ONE global explorer works"""
        self.explorer.transfer_global_explorers()
        output = self.explorer.run_global_explorer('global')
        self.assertEqual(output, 'global\n')

    def test_global_explorer_output(self):
        """Ensure output is created for every global explorer"""
        out_path = self.mkdtemp()

        self.explorer.run_global_explorers(out_path)
        names = sorted(self.explorer.list_global_explorer_names())
        output = sorted(os.listdir(out_path))

        self.assertEqual(names, output)
        shutil.rmtree(out_path)

    def test_list_type_explorer_names(self):
        cdist_type = core.CdistType(self.local.type_path, '__test_type')
        expected = cdist_type.explorers
        self.assertEqual(self.explorer.list_type_explorer_names(cdist_type),
                         expected)

    def test_transfer_type_explorers(self):
        """Test if transferring type explorers works"""
        cdist_type = core.CdistType(self.local.type_path, '__test_type')
        self.explorer.transfer_type_explorers(cdist_type)
        source = os.path.join(self.local.type_path, cdist_type.explorer_path)
        destination = os.path.join(self.remote.type_path,
                                   cdist_type.explorer_path)
        self.assertEqual(
            sorted(ilistdir(source, recursive=False)),
            sorted(ilistdir(destination, recursive=False)))

    def test_transfer_type_explorers_only_once(self):
        cdist_type = core.CdistType(self.local.type_path, '__test_type')
        # first transfer
        self.explorer.transfer_type_explorers(cdist_type)
        source = os.path.join(self.local.type_path, cdist_type.explorer_path)
        destination = os.path.join(self.remote.type_path,
                                   cdist_type.explorer_path)
        self.assertEqual(
            sorted(ilistdir(source, recursive=False)),
            sorted(ilistdir(destination, recursive=False)))
        # nuke destination folder content, but recreate directory
        shutil.rmtree(destination)
        os.makedirs(destination)
        # second transfer, should not happen
        self.explorer.transfer_type_explorers(cdist_type)
        self.assertFalse(os.listdir(destination))

    def test_transfer_object_parameters(self):
        cdist_type = core.CdistType(self.local.type_path, '__test_type')
        cdist_object = core.CdistObject(cdist_type, self.local.object_path,
                                        self.local.object_marker_name,
                                        'whatever')
        cdist_object.create()
        cdist_object.parameters = {
                'first': 'first value',
                'second': 'second value'
        }
        self.explorer.transfer_object_parameters(cdist_object)
        source = os.path.join(self.local.object_path,
                              cdist_object.parameter_path)
        destination = os.path.join(self.remote.object_path,
                                   cdist_object.parameter_path)
        self.assertEqual(
            sorted(ilistdir(source, recursive=False)),
            sorted(ilistdir(destination, recursive=False)))

    def test_run_type_explorer(self):
        cdist_type = core.CdistType(self.local.type_path, '__test_type')
        cdist_object = core.CdistObject(cdist_type, self.local.object_path,
                                        self.local.object_marker_name,
                                        'whatever')
        self.explorer.transfer_type_explorers(cdist_type)
        output = self.explorer.run_type_explorer('world', cdist_object)
        self.assertEqual(output, 'hello\n')

    def test_run_type_explorers(self):
        cdist_type = core.CdistType(self.local.type_path, '__test_type')
        cdist_object = core.CdistObject(cdist_type, self.local.object_path,
                                        self.local.object_marker_name,
                                        'whatever')
        cdist_object.create()
        self.explorer.run_type_explorers(cdist_object)
        self.assertEqual(cdist_object.explorers, {'world': 'hello'})

    def test_jobs_parameter(self):
        self.assertIsNone(self.explorer.jobs)
        expl = explorer.Explorer(
            self.target_host,
            self.local,
            self.remote,
            jobs=8)
        self.assertEqual(expl.jobs, 8)

    def test_transfer_global_explorers_parallel(self):
        expl = explorer.Explorer(
            self.target_host,
            self.local,
            self.remote,
            jobs=4)
        self.assertIsNotNone(expl.jobs)

        expl.transfer_global_explorers()
        source = self.local.global_explorer_path
        destination = self.remote.global_explorer_path
        self.assertEqual(
            sorted(ilistdir(source, recursive=False)),
            sorted(ilistdir(destination, recursive=False)))

    def test_run_parallel_jobs(self):
        expl = explorer.Explorer(
            self.target_host,
            self.local,
            self.remote,
            jobs=4)
        self.assertIsNotNone(expl.jobs)
        out_path = self.mkdtemp()

        expl.run_global_explorers(out_path)
        names = sorted(expl.list_global_explorer_names())
        # hidden files should not be copied, so os.listdir() is fine
        output = sorted(os.listdir(out_path))

        self.assertEqual(names, output)
        shutil.rmtree(out_path)

    def test_explorer_environment(self):
        cdist_type = core.CdistType(self.local.type_path, '__dump_env')
        cdist_object = core.CdistObject(cdist_type, self.local.object_path,
                                        self.local.object_marker_name,
                                        'whatever')
        self.explorer.transfer_type_explorers(cdist_type)
        output = self.explorer.run_type_explorer('dump', cdist_object)

        output_is = dict(
            line.split(': ', 2)
            for line in filter(None, output.split("\n")))

        output_expected = {
            "__target_host": self.local.target_host[0],
            "__target_hostname": self.local.target_host[1],
            "__target_fqdn": self.local.target_host[2],
            "__explorer": self.remote.global_explorer_path,
            "__target_host_tags": "",
            "__cdist_log_level": str(logging.WARNING),
            "__cdist_log_level_name": "WARNING",
            }

        self.assertEqual(output_expected, output_is)

    def test_explorer_locale(self):
        cdist_type = core.CdistType(self.local.type_path, "__dump_locale")
        cdist_object = core.CdistObject(cdist_type, self.local.object_path,
                                        self.local.object_marker_name,
                                        "whatever")
        self.explorer.transfer_type_explorers(cdist_type)
        output = self.explorer.run_type_explorer("dump", cdist_object)

        for line in output.splitlines(False):
            (k, v) = line.split("=", 2)

            if "LANG" == k or k.startswith("LC_"):
                self.assertEqual(
                    "C", shlex.split(v)[0],
                    "Environment variable %s is expected to be %s" % (k, "C"))


if __name__ == '__main__':
    import unittest

    unittest.main()
