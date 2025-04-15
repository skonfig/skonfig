# -*- coding: utf-8 -*-
#
# 2010-2011 Steven Armstrong (steven-cdist at armstrong.cc)
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

import getpass
import io
import logging
import os
import random
import shlex
import shutil
import string
import sys

import skonfig
import skonfig.settings
import skonfig.util

import tests as test

from skonfig.exec import local
from skonfig import core
from skonfig.core import manifest

my_dir = os.path.abspath(os.path.dirname(__file__))
fixtures = os.path.join(my_dir, 'fixtures')
conf_dir = os.path.join(fixtures, 'conf')


class ManifestTestCase(test.SkonfigTestCase):

    def setUp(self):
        self.temp_dir = self.mkdtemp()

        out_path = self.temp_dir
        hostdir = skonfig.util.str_hash(self.target_host[0])
        base_root_path = os.path.join(out_path, hostdir)

        self.settings = skonfig.settings.SettingsContainer()
        self.settings.conf_dir = [conf_dir]

        self.local = local.Local(
            self.target_host,
            base_root_path,
            self.settings,
            exec_path=test.skonfig_exec_path)

        self.local.create_files_dirs()

        self.manifest = manifest.Manifest(self.target_host, self.local)
        self.log = logging.getLogger(self.target_host[0])

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @test.patch.dict("os.environ")
    def test_initial_manifest_environment(self):
        initial_manifest = os.path.join(self.local.manifest_path,
                                        "dump_environment")
        (handle, output_file) = self.mkstemp(dir=self.temp_dir)
        os.close(handle)
        os.environ['__cdist_test_out'] = output_file
        old_loglevel = logging.root.getEffectiveLevel()
        self.log.setLevel(logging.OFF)
        manifest = skonfig.core.manifest.Manifest(self.target_host, self.local)
        manifest.run_initial_manifest(initial_manifest)

        with open(output_file, "r") as f:
            output_is = dict(
                line.split(': ', 2)
                for line in filter(None, f.read().splitlines(False)))

        self.assertTrue(output_is['PATH'].startswith(self.local.bin_path))
        self.assertEqual(output_is['__target_host'],
                         self.local.target_host[0])
        self.assertEqual(output_is['__target_hostname'],
                         self.local.target_host[1])
        self.assertEqual(output_is['__target_fqdn'],
                         self.local.target_host[2])
        self.assertEqual(output_is['__global'], self.local.base_path)
        self.assertEqual(output_is['__cdist_type_base_path'],
                         self.local.type_path)
        self.assertEqual(output_is['__manifest'], self.local.manifest_path)
        self.assertEqual(output_is['__files'], self.local.files_path)
        self.assertEqual(output_is['__target_host_tags'], '')
        self.assertEqual(output_is['__cdist_log_level'], str(logging.OFF))
        self.assertEqual(output_is['__cdist_log_level_name'], 'OFF')

        self.log.setLevel(old_loglevel)

    @test.patch.dict("os.environ")
    def test_initial_manifest_locale(self):
        initial_manifest = os.path.join(self.local.manifest_path, "locale")

        (output_fd, output_file) = self.mkstemp(dir=self.temp_dir)
        os.environ["__cdist_test_out"] = output_file
        manifest = skonfig.core.manifest.Manifest(self.target_host, self.local)
        manifest.run_initial_manifest(initial_manifest)

        with os.fdopen(output_fd) as f:
            lines = filter(None, f.read().splitlines(False))

        for line in lines:
            (k, v) = line.split("=", 2)

            if "LANG" == k or k.startswith("LC_"):
                self.assertEqual(
                    "C", shlex.split(v)[0],
                    "Environment variable %s is expected to be %s" % (k, "C"))

    @test.patch.dict("os.environ")
    def test_type_manifest_environment(self):
        cdist_type = core.CdistType(self.local.type_path, '__dump_environment')
        cdist_object = core.CdistObject(cdist_type, self.local.object_path,
                                        self.local.object_marker_name,
                                        'whatever')
        cdist_object.create()
        (handle, output_file) = self.mkstemp(dir=self.temp_dir)
        os.close(handle)
        os.environ['__cdist_test_out'] = output_file
        old_loglevel = self.log.getEffectiveLevel()
        self.log.setLevel(logging.OFF)
        manifest = skonfig.core.manifest.Manifest(self.target_host, self.local)
        manifest.run_type_manifest(cdist_object)

        with open(output_file, "r") as f:
            output_is = dict(
                line.split(': ', 2)
                for line in filter(None, f.read().splitlines(False)))

        self.assertTrue(output_is['PATH'].startswith(self.local.bin_path))
        self.assertEqual(output_is['__target_host'],
                         self.local.target_host[0])
        self.assertEqual(output_is['__target_hostname'],
                         self.local.target_host[1])
        self.assertEqual(output_is['__target_fqdn'],
                         self.local.target_host[2])
        self.assertEqual(output_is['__global'], self.local.base_path)
        self.assertEqual(output_is['__cdist_type_base_path'],
                         self.local.type_path)
        self.assertEqual(output_is['__type'], cdist_type.absolute_path)
        self.assertEqual(output_is['__object'], cdist_object.absolute_path)
        self.assertEqual(output_is['__object_id'], cdist_object.object_id)
        self.assertEqual(output_is['__object_name'], cdist_object.name)
        self.assertEqual(output_is['__files'], self.local.files_path)
        self.assertEqual(output_is['__target_host_tags'], '')
        self.assertEqual(output_is['__cdist_log_level'], str(logging.OFF))
        self.assertEqual(output_is['__cdist_log_level_name'], 'OFF')
        self.log.setLevel(old_loglevel)

    @test.patch.dict("os.environ")
    def test_type_manifest_locale(self):
        cdist_type = core.CdistType(self.local.type_path, "__locale")
        cdist_object = core.CdistObject(cdist_type, self.local.object_path,
                                        self.local.object_marker_name,
                                        "whatever")
        cdist_object.create()

        (output_fd, output_file) = self.mkstemp(dir=self.temp_dir)
        os.environ["__cdist_test_out"] = output_file
        manifest = skonfig.core.manifest.Manifest(self.target_host, self.local)
        manifest.run_type_manifest(cdist_object)

        with os.fdopen(output_fd) as f:
            lines = filter(None, f.read().splitlines(False))

        for line in lines:
            (k, v) = line.split("=", 2)

            if "LANG" == k or k.startswith("LC_"):
                self.assertEqual(
                    "C", shlex.split(v)[0],
                    "Environment variable %s is expected to be %s" % (k, "C"))

    def test_loglevel_env_setup(self):
        current_level = self.log.getEffectiveLevel()
        self.log.setLevel(logging.DEBUG)
        manifest = skonfig.core.manifest.Manifest(self.target_host, self.local)
        self.assertTrue("__cdist_log_level" in manifest.env)
        self.assertTrue("__cdist_log_level_name" in manifest.env)
        self.assertEqual(manifest.env["__cdist_log_level"],
                         str(logging.DEBUG))
        self.assertEqual(manifest.env["__cdist_log_level_name"], 'DEBUG')
        self.log.setLevel(current_level)


if __name__ == '__main__':
    import unittest
    unittest.main()
