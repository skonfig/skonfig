# -*- coding: utf-8 -*-
#
# 2011-2017 Steven Armstrong (steven-cdist at armstrong.cc)
# 2012-2015 Nico Schottelius (nico-cdist at schottelius.org)
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
import logging
import os
import re
import shlex
import shutil

import skonfig
import skonfig.settings
import skonfig.util

import tests as test

from skonfig import core
from skonfig.core import code
from skonfig.exec import (local, remote)

my_dir = os.path.abspath(os.path.dirname(__file__))
fixtures = os.path.join(my_dir, 'fixtures')
conf_dir = os.path.join(fixtures, 'conf')


class CodeTestCase(test.SkonfigTestCase):

    def setUp(self):
        self.local_dir = self.mkdtemp()
        self.hostdir = skonfig.util.str_hash(self.target_host[0])
        self.host_base_path = os.path.join(self.local_dir, self.hostdir)

        self.settings = skonfig.settings.SettingsContainer()
        self.settings.conf_dir = [conf_dir]
        self.settings.remote_exec = self.remote_exec

        self.local = local.Local(
            self.target_host,
            self.host_base_path,
            self.settings,
            exec_path=test.skonfig_exec_path)

        self.local.create_files_dirs()

        self.remote_dir = self.mkdtemp()
        self.remote = remote.Remote(
            self.target_host,
            remote_exec=self.settings.remote_exec,
            base_path=self.remote_dir,
            settings=self.settings,
            stdout_base_path=self.local.stdout_base_path,
            stderr_base_path=self.local.stderr_base_path)
        self.remote.create_files_dirs()

        self.code = code.Code(self.target_host, self.local, self.remote)

        self.cdist_type_env = core.CdistType(
            self.local.type_path, "__dump_environment")
        self.cdist_object_env = core.CdistObject(
                self.cdist_type_env, self.local.object_path, "whatever",
                self.local.object_marker_name)
        self.cdist_object_env.create()

        self.cdist_type_locale = core.CdistType(
            self.local.type_path, "__dump_locale")
        self.cdist_object_locale = core.CdistObject(
                self.cdist_type_locale, self.local.object_path, "whatever",
                self.local.object_marker_name)
        self.cdist_object_locale.create()

    def tearDown(self):
        shutil.rmtree(self.local_dir)
        shutil.rmtree(self.remote_dir)

    def test_run_gencode_local_environment(self):
        output_string = self.code.run_gencode_local(self.cdist_object_env)

        regex = re.compile(r"^echo (['\"]?)(.*?): *(.*)\1")
        output_is = dict(
            regex.match(line).groups()[1:]
            for line in filter(None, output_string.splitlines(False)))

        output_expected = {
            "__target_host": self.local.target_host[0],
            "__target_hostname": self.local.target_host[1],
            "__target_fqdn": self.local.target_host[2],
            "__global": self.local.base_path,
            "__type": self.cdist_type_env.absolute_path,
            "__object": self.cdist_object_env.absolute_path,
            "__object_id": self.cdist_object_env.object_id,
            "__object_name": self.cdist_object_env.name,
            "__files": self.local.files_path,
            "__target_host_tags": "",
            "__cdist_log_level": str(logging.WARNING),
            "__cdist_log_level_name": "WARNING",
            }

        self.assertEqual(output_expected, output_is)

    def test_run_gencode_local_locale(self):
        output_string = self.code.run_gencode_local(self.cdist_object_locale)

        for line in output_string.splitlines(False):
            if not line.startswith("#"):
                continue

            (k, v) = re.sub(r"^# *", "", line).split("=", 2)

            if "LANG" == k or k.startswith("LC_"):
                self.assertEqual(
                    "C", shlex.split(v)[0],
                    "Environment variable %s is expected to be %s" % (k, "C"))

    def test_run_gencode_remote_environment(self):
        output_string = self.code.run_gencode_remote(self.cdist_object_env)

        regex = re.compile(r"^echo (['\"]?)(.*?): *(.*)\1")
        output_is = dict(
            regex.match(line).groups()[1:]
            for line in filter(None, output_string.splitlines(False)))

        output_expected = {
            "__target_host": self.local.target_host[0],
            "__target_hostname": self.local.target_host[1],
            "__target_fqdn": self.local.target_host[2],
            "__global": self.local.base_path,
            "__type": self.cdist_type_env.absolute_path,
            "__object": self.cdist_object_env.absolute_path,
            "__object_id": self.cdist_object_env.object_id,
            "__object_name": self.cdist_object_env.name,
            "__files": self.local.files_path,
            "__target_host_tags": "",
            "__cdist_log_level": str(logging.WARNING),
            "__cdist_log_level_name": "WARNING",
            }

        self.assertEqual(output_expected, output_is)

    def test_run_gencode_remote_locale(self):
        output_string = self.code.run_gencode_remote(self.cdist_object_locale)

        for line in output_string.splitlines(False):
            if not line.startswith("#"):
                continue

            (k, v) = re.sub(r"^# *", "", line).split("=", 2)

            if "LANG" == k or k.startswith("LC_"):
                self.assertEqual(
                    "C", shlex.split(v)[0],
                    "Environment variable %s is expected to be %s" % (k, "C"))

    def test_transfer_code_remote(self):
        self.cdist_object_env.code_remote = self.code.run_gencode_remote(
                self.cdist_object_env)
        self.code.transfer_code_remote(self.cdist_object_env)
        destination = os.path.join(self.remote.object_path,
                                   self.cdist_object_env.code_remote_path)
        self.assertTrue(os.path.isfile(destination))

    def test_run_code_local_environment(self):
        self.cdist_object_env.code_local = self.code.run_gencode_local(
                self.cdist_object_env)
        self.code.run_code_local(self.cdist_object_env)

        code_local_stdout = os.path.join(
            self.cdist_object_env.stdout_path, "code-local")

        with open(code_local_stdout, "rt") as f:
            output_is = dict(
                line.split(": ", 2)
                for line in filter(None, f.read().splitlines(False)))

        output_expected = {
            "__target_host": self.local.target_host[0],
            "__target_hostname": self.local.target_host[1],
            "__target_fqdn": self.local.target_host[2],
            "__global": self.local.base_path,
            "__type": self.cdist_type_env.absolute_path,
            "__object": self.cdist_object_env.absolute_path,
            "__object_id": self.cdist_object_env.object_id,
            "__object_name": self.cdist_object_env.name,
            "__files": self.local.files_path,
            "__target_host_tags": "",
            "__cdist_log_level": str(logging.WARNING),
            "__cdist_log_level_name": "WARNING",
            }

        self.maxDiff = None
        self.assertEqual(output_expected, output_is)

    def test_run_code_local_locale(self):
        self.cdist_object_locale.code_local = self.code.run_gencode_local(
            self.cdist_object_locale)
        self.code.run_code_local(self.cdist_object_locale)

        code_local_stdout = os.path.join(
            self.cdist_object_locale.stdout_path, "code-local")

        with open(code_local_stdout, "rt") as f:
            for line in f.read().splitlines(False):
                (k, v) = line.split("=", 2)

                if "LANG" == k or k.startswith("LC_"):
                    self.assertEqual(
                        "C", shlex.split(v)[0],
                        "Environment variable %s is expected to be %s" % (k, "C"))

    def test_run_code_remote_environment(self):
        self.cdist_object_env.code_remote = self.code.run_gencode_remote(
                self.cdist_object_env)
        self.code.transfer_code_remote(self.cdist_object_env)
        self.code.run_code_remote(self.cdist_object_env)

        code_remote_stdout = os.path.join(
            self.cdist_object_env.stdout_path, "code-remote")

        with open(code_remote_stdout, "rt") as f:
            output_is = dict(
                line.split(": ", 2)
                for line in filter(None, f.read().splitlines(False)))

        output_expected = {
            "__target_host": self.local.target_host[0],
            "__target_hostname": self.local.target_host[1],
            "__target_fqdn": self.local.target_host[2],
            "__global": self.local.base_path,
            "__type": self.cdist_type_env.absolute_path,
            "__object": self.cdist_object_env.absolute_path,
            "__object_id": self.cdist_object_env.object_id,
            "__object_name": self.cdist_object_env.name,
            "__files": self.local.files_path,
            "__target_host_tags": "",
            "__cdist_log_level": str(logging.WARNING),
            "__cdist_log_level_name": "WARNING",
            }

        self.maxDiff = None
        self.assertEqual(output_expected, output_is)

    def test_run_code_remote_locale(self):
        self.cdist_object_locale.code_remote = self.code.run_gencode_remote(
            self.cdist_object_locale)
        self.code.transfer_code_remote(self.cdist_object_locale)
        self.code.run_code_remote(self.cdist_object_locale)

        code_remote_stdout = os.path.join(
            self.cdist_object_locale.stdout_path, "code-remote")

        with open(code_remote_stdout, "rt") as f:
            for line in f.read().splitlines(False):
                (k, v) = line.split("=", 2)

                if "LANG" == k or k.startswith("LC_"):
                    self.assertEqual(
                        "C", shlex.split(v)[0],
                        "Environment variable %s is expected to be %s" % (k, "C"))


if __name__ == '__main__':
    import unittest
    unittest.main()
