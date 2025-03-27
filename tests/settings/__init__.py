# -*- coding: utf-8 -*-
#
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
#

import logging
import os

import cdist.autil

import tests as test

import skonfig.settings

my_dir = os.path.abspath(os.path.dirname(__file__))
fixtures = os.path.join(my_dir, "fixtures")
interpolation_config_file = os.path.join(fixtures, "interpolation-test.cfg")


class AnySettingTestCase(test.CdistTestCase):
    any_setting_nullable = skonfig.settings.any_setting(nullable=True)
    any_setting = skonfig.settings.any_setting(default="")

    def test_any_setting_nullable(self):
        test_cases = (
            (None, None, None),
            # initialisation from None
            (None, 42, 42),
            (None, "foo", "foo"),
            (None, [], []),
            (None, True, True),
            # accepts strings
            ("", "foo", "foo"),
            ("foo", "bar", "bar"),
            ("foo", "", ""),
            ('spam', 'eggs', 'eggs'),
            # accepts numbers
            (0, 42, 42),
            (42, 0, 0),
            (0, 1.414, 1.414),
            (0, -2, -2),
            # accepts bools
            (True, True, True),
            (False, False, False),
            (True, False, False),
            (False, True, True),
            # accepts lists
            ([], [], []),
            ([], ['spam', 'eggs'], ['spam', 'eggs']),
            (['spam', 'eggs'], [], []),
            (['spam', 'eggs'], ['ham', 'spamspam'], ['ham', 'spamspam']),
            (['spam', 'eggs'], 'spam:eggs', 'spam:eggs'),
            ('spam:eggs', ['spam', 'eggs'], ['spam', 'eggs']),
            (['spam', 'eggs'], ['ham', 'spamspam'], ['ham', 'spamspam']),
        )
        for (currval, newval, expected) in test_cases:
            self.any_setting_nullable = currval
            self.assertEqual(self.any_setting_nullable, currval)
            self.any_setting_nullable = newval
            self.assertEqual(self.any_setting_nullable, expected)

    def test_nonnullable_assign_null(self):
        self.any_setting = 42
        with self.assertRaises(ValueError):
            self.any_setting = None
        self.assertEqual(self.any_setting, 42)


class StringSettingTestCase(test.CdistTestCase):
    string_setting_nullable = skonfig.settings.string_setting(nullable=True)
    string_setting = skonfig.settings.string_setting(default="")

    def test_nonnullable_assign_null(self):
        self.string_setting = "foo"
        with self.assertRaises(ValueError):
            self.string_setting = None

    def test_assign_str(self):
        self.string_setting = "hello world"
        self.assertEqual(self.string_setting, "hello world")

        self.string_setting = ""
        self.assertEqual(self.string_setting, "")

    def test_assign_other_types(self):
        values = [0, 42, -42, 1.414, True, list(), tuple(), dict()]

        init_value = "init"
        self.string_setting = init_value

        for value in values:
            with self.assertRaises(ValueError):
                self.string_setting = value

            self.assertEqual(self.string_setting, init_value)


class ChoiceSettingTestCase(test.CdistTestCase):
    choice_setting_nullable = skonfig.settings.choice_setting(nullable=True)

    def setUp(self):
        self.__class__.choice_setting_nullable._choices = (0, 42, "foo")

    def test_nullable_assign_null(self):
        self.choice_setting_nullable = None
        self.assertIsNone(self.choice_setting_nullable)

    def test_assign_valid_choice(self):
        for c in self.__class__.choice_setting_nullable._choices:
            self.choice_setting_nullable = c
            self.assertEqual(self.choice_setting_nullable, c)

    def test_assign_invalid_choice(self):
        import math

        self.choice_setting_nullable = 0
        for c in [2, "bar", math.e]:
            with self.assertRaises(ValueError):
                self.choice_setting_nullable = c
            self.assertEqual(self.choice_setting_nullable, 0)


class JobsSettingTestCase(test.CdistTestCase):
    jobs_setting = skonfig.settings.jobs_setting(default=1)

    @staticmethod
    def auto_value():
        import multiprocessing
        try:
            return min(4, multiprocessing.cpu_count())
        except NotImplementedError:
            return 1

    def test_assign_pos_int(self):
        for c in [1, 2, 4, 6, 7, 16, 123, 128, 1024]:
            self.jobs_setting = c
            self.assertEqual(self.jobs_setting, c)

    def test_assign_zero(self):
        self.jobs_setting = 1
        with self.assertRaises(ValueError):
            self.jobs_setting = 0
        self.assertEqual(self.jobs_setting, 1)

    def test_assign_auto(self):
        self.jobs_setting = 1
        self.jobs_setting = -1

        self.assertEqual(self.jobs_setting, self.auto_value())

    def test_assign_neg_int(self):
        self.jobs_setting = 1
        for c in [-2, -4, -16, -128, -1024]:
            with self.assertRaises(ValueError):
                self.jobs_setting = c
            self.assertEqual(self.jobs_setting, 1)


class SearchPathSettingTestCase(test.CdistTestCase):
    path_setting = skonfig.settings.search_path_setting()

    def test_default(self):
        self.assertEqual(self.path_setting, [])

    def test_nonnullable_assign_none(self):
        self.path_setting = []
        with self.assertRaises(ValueError):
            self.path_setting = None
        self.assertEqual(self.path_setting, [])

    def test_assign_string(self):
        self.path_setting = "/bin"
        self.assertEqual(self.path_setting, ["/bin"])

        self.path_setting = "/bin:/usr/bin:/sbin:/usr/sbin:/usr/local/bin"
        self.assertEqual(self.path_setting, [
            "/bin", "/usr/bin", "/sbin", "/usr/sbin", "/usr/local/bin"])

    def test_assign_empty_list(self):
        self.jobs_setting = []
        self.assertEqual(self.jobs_setting, [])

    def test_assign_list(self):
        lst = [
            "/bin", "/usr/bin", "/sbin", "/usr/sbin", "/usr/local/bin"
            ]
        self.path_setting = lst
        self.assertEqual(self.path_setting, lst)

    def test_assign_other_types(self):
        values = [0, 42, -42, 1.414, True]

        init_value = "/bin"
        self.path_setting = init_value

        for value in values:
            with self.assertRaises(ValueError):
                self.path_setting = value

            self.assertEqual(self.path_setting, [init_value])

    def test_can_use_list_manipulation_operators(self):
        self.path_setting = ["/bin"]
        self.assertEqual(self.path_setting, ["/bin"])

        self.path_setting.insert(0, "/sbin")
        self.assertEqual(self.path_setting, ["/sbin", "/bin"])

        self.path_setting += ["/usr/sbin", "/usr/bin"]
        self.assertEqual(self.path_setting, [
            "/sbin", "/bin",
            "/usr/sbin", "/usr/bin"])

        self.path_setting.extend(["/usr/local/sbin", "/usr/local/bin"])
        self.assertEqual(self.path_setting, [
            "/sbin", "/bin",
            "/usr/sbin", "/usr/bin",
            "/usr/local/sbin", "/usr/local/bin"])

        self.path_setting.append("/opt/bin")
        self.assertEqual(self.path_setting, [
            "/sbin", "/bin",
            "/usr/sbin", "/usr/bin",
            "/usr/local/sbin", "/usr/local/bin",
            "/opt/bin"])


class FileSettingTestCase(test.CdistTestCase):
    existing_file = os.path.join(fixtures, "somefile.txt")
    file_setting = skonfig.settings.file_setting(default=existing_file)

    def test_nonnullable_assign_none(self):
        self.file_setting = self.existing_file
        with self.assertRaises(ValueError):
            self.file_setting = None
        self.assertEqual(self.file_setting, self.existing_file)

    def test_assign_nonexisting_file(self):
        with self.assertRaises(ValueError):
            self.file_setting = os.path.join(fixtures, ".nonexist")

    def test_assign_other_types(self):
        values = ["C:\\abc", 0, 42, -42, 1.414, True, list(), tuple(), dict()]

        init_value = self.existing_file
        self.file_setting = init_value

        for value in values:
            with self.assertRaises(ValueError):
                self.file_setting = value
            self.assertEqual(self.file_setting, init_value)


class ExecutableSettingTestCase(test.CdistTestCase):
    existing_file = os.path.join(fixtures, "somefile.txt")
    existing_bin = os.path.join(fixtures, "somescript")
    exec_setting = skonfig.settings.executable_setting(default=existing_bin)

    def test_assign_executable_script(self):
        self.exec_setting = self.existing_bin
        self.assertEqual(self.exec_setting, self.existing_bin)

    def test_nonnullable_assign_none(self):
        self.exec_setting = self.existing_bin
        with self.assertRaises(ValueError):
            self.exec_setting = None
        self.assertEqual(self.exec_setting, self.existing_bin)

    def test_assign_nonexisting_file(self):
        self.exec_setting = self.existing_bin
        with self.assertRaises(ValueError):
            self.exec_setting = "/kdfjsaofi/sdfklj/djf/sdklfj/lkj23423/foo.tgz"
        self.assertEqual(self.exec_setting, self.existing_bin)

    def test_assign_nonexec_file(self):
        self.exec_setting = self.existing_bin
        with self.assertRaises(ValueError):
            self.exec_setting = os.path.join(fixtures, "somefile.txt")
        self.assertEqual(self.exec_setting, self.existing_bin)

    def test_assign_other_types(self):
        values = [0, 42, -42, 1.414, True, list(), tuple(), dict()]

        init_value = self.existing_bin
        self.exec_setting = init_value

        for value in values:
            with self.assertRaises(ValueError):
                self.exec_setting = value
            self.assertEqual(self.exec_setting, init_value)


class ArchivingSettingTestCase(test.CdistTestCase):
    archiving_setting = skonfig.settings.archiving_setting(default="tar")

    def test_nonnullable_assign_none(self):
        self.archiving_setting = "tar"
        with self.assertRaises(ValueError):
            self.archiving_setting = None
        self.assertEqual(self.archiving_setting,
                         cdist.autil.mode_from_str("tar"))

    def test_assigning_valid_modes(self):
        for m in cdist.autil.archiving_modes:
            if not m.is_supported():
                continue
            self.archiving_setting = m.name()
            self.assertEqual(self.archiving_setting, m)

    def test_raises_if_mode_not_supported(self):
        orig = cdist.autil.TAR
        self.archiving_setting = orig
        self.assertEqual(self.archiving_setting, orig)

        import tarfile
        patched_open_meths = tarfile.TarFile.OPEN_METH.copy()
        if "xz" in patched_open_meths:
            del patched_open_meths['xz']
        with test.patch.dict(
                tarfile.TarFile.OPEN_METH, patched_open_meths, clear=True):
            with self.assertRaises(RuntimeError):
                self.archiving_setting = "txz"
            self.assertEqual(self.archiving_setting, orig)

    def test_assigning_invalid_modes(self):
        self.archiving_setting = "tar"
        init_value = self.archiving_setting
        for s in ("foo", "bar", 42):
            with self.assertRaises(ValueError):
                self.archiving_setting = s
            self.assertEqual(self.archiving_setting, init_value)


class ColouredOutputSettingTestCase(test.CdistTestCase):
    coloured_output_setting = skonfig.settings.coloured_output_setting(
        default="auto")

    def test_nonnullable_assign_none(self):
        self.coloured_output_setting = "always"
        with self.assertRaises(ValueError):
            self.coloured_output_setting = None
        self.assertEqual(self.coloured_output_setting, True)

    def test_valid_choices(self):
        mapping = {
            "always": True,
            "never": False,
            }

        for (s, b) in mapping.items():
            self.coloured_output_setting = s
            self.assertEqual(self.coloured_output_setting, b)

    @test.patch('sys.stdout.isatty')
    @test.patch.dict("os.environ")
    def test_auto_respects_no_color(self, stdout_isatty):
        stdout_isatty.return_value = True

        self.coloured_output_setting = "always"
        self.assertEqual(self.coloured_output_setting, True)
        os.environ["NO_COLOR"] = ""
        self.coloured_output_setting = "auto"
        self.assertEqual(self.coloured_output_setting, False)

    @test.patch('sys.stdout.isatty')
    @test.patch.dict("os.environ")
    def test_auto_checks_isatty(self, stdout_isatty):
        self.coloured_output_setting = "always"
        self.assertEqual(self.coloured_output_setting, True)

        if "NO_COLOR" in os.environ:
            del os.environ["NO_COLOR"]

        # enabled if isatty
        stdout_isatty.return_value = True
        self.coloured_output_setting = "auto"
        self.assertEqual(self.coloured_output_setting, True)

        # disabled ifnot isatty
        stdout_isatty.return_value = False
        self.coloured_output_setting = "auto"
        self.assertEqual(self.coloured_output_setting, False)

    @test.patch("sys.stdout.isatty")
    @test.patch.dict("os.environ")
    def test_auto_checks_for_dumb_terminals(self, stdout_isatty):
        stdout_isatty.return_value = True
        if "NO_COLOR" in os.environ:
            del os.environ["NO_COLOR"]
        if "TERM" in os.environ:
            del os.environ["TERM"]

        # colours should be enabled
        self.coloured_output_setting = "auto"
        self.assertEqual(self.coloured_output_setting, True)

        # with TERM=dumb, colours should be disabled
        os.environ["TERM"] = "dumb"
        self.coloured_output_setting = "auto"
        self.assertEqual(self.coloured_output_setting, False)

    def test_invalid_choices(self):
        self.coloured_output_setting = "always"

        for s in ["foo", "linux", 42]:
            with self.assertRaises(ValueError):
                self.coloured_output_setting = s
            self.assertEqual(self.coloured_output_setting, True)


class LoglevelSettingTestCase(test.CdistTestCase):
    log_setting = skonfig.settings.loglevel_setting(default="INFO")

    def test_default(self):
        self.assertEqual(self.log_setting, logging.INFO)

    def test_nonnullable_assign_none(self):
        self.log_setting = "INFO"
        with self.assertRaises(ValueError):
            self.log_setting = None
        self.assertEqual(self.log_setting, logging.INFO)

    def test_assign_string(self):
        self.log_setting = "DEBUG"
        self.assertEqual(self.log_setting, logging.DEBUG)

    def test_assign_logging_int(self):
        lvl = logging.DEBUG
        self.log_setting = lvl
        self.assertEqual(self.log_setting, lvl)

    def test_assign_other_types(self):
        values = [list(), tuple(), dict(), True]

        self.log_setting = "INFO"

        for value in values:
            with self.assertRaises(ValueError):
                self.log_setting = value

            self.assertEqual(self.log_setting, logging.INFO)


class SettingsTestCase(test.CdistTestCase):
    all_settings = [
        "archiving_mode", "cache_path_pattern", "colored_output",
        "conf_dir", "init_manifest", "jobs", "local_shell", "out_path",
        "remote_exec", "remote_out_path", "remote_shell", "verbosity"]

    def assert_defaults(self, settings):
        self.assertEqual(settings.archiving_mode,
                         cdist.autil.mode_from_str("tar"))
        self.assertEqual(settings.cache_path_pattern, "%N")
        self.assertEqual(settings.colored_output, False)
        self.assertEqual(settings.conf_dir, [])
        self.assertEqual(settings.init_manifest, None)
        self.assertEqual(settings.jobs, JobsSettingTestCase.auto_value())
        self.assertEqual(settings.local_shell, "/bin/sh")
        self.assertEqual(settings.out_path, None)
        self.assertEqual(settings.remote_exec, None)
        self.assertEqual(settings.remote_out_path, "/var/lib/skonfig")
        self.assertEqual(settings.remote_shell, "/bin/sh")
        self.assertEqual(settings.verbosity, logging.INFO)

    def test_defaults(self):
        s = skonfig.settings.SettingsContainer()
        self.assert_defaults(s)

    def test_settings_can_have_multiple_instances(self):
        s1 = skonfig.settings.SettingsContainer()
        s2 = skonfig.settings.SettingsContainer()

        self.assertEqual(s1, s2)

        s1.cache_path_pattern = "%h"
        s2.cache_path_pattern = "%N"

        self.assertNotEqual(s1.cache_path_pattern, s2.cache_path_pattern)

    def test_update_from_env(self):
        s_default = skonfig.settings.SettingsContainer()

        s = skonfig.settings.SettingsContainer()
        self.assert_defaults(s)

        env = {
            "SKONFIG_PATH": fixtures,
            "SKONFIG_LOCAL_SHELL": os.path.join(fixtures, "somescript"),
            "SKONFIG_REMOTE_SHELL": "/nonexist",
            "SKONFIG_REMOTE_EXEC": ":",
            "SKONFIG_COLORED_OUTPUT": "always",
            }

        s.update_from_env(env)

        expect_changed = {
            "conf_dir": True,
            "colored_output": True,
            "local_shell": True,
            "remote_shell": True,
            "remote_exec": True,
            }

        for setting in self.all_settings:
            if expect_changed.get(setting, False):
                self.assertNotEqual(
                    getattr(s, setting), getattr(s_default, setting), setting)
            else:
                self.assertEqual(
                    getattr(s, setting), getattr(s_default, setting), setting)

    def test_invalid_update_from_env(self):
        s = skonfig.settings.SettingsContainer()
        self.assert_defaults(s)

        env = {
            "SKONFIG_REMOTE_SHELL": "/bin/bash",
            "SKONFIG_LOCAL_SHELL": "/sdlkfj/sklfjasl",
            }

        # assertLogs requires Python >= 3.4
        with self.assertLogs(logger="skonfig.settings") as logs:
            s.update_from_env(env)

        # update_from_env should produce this error message:
        # ERROR: skonfig.settings: Environment variable "SKONFIG_LOCAL_SHELL" \
        # has invalid value "/sdlkfj/sklfjasl": No such file: /sdlkfj/sklfjasl
        self.assertEqual(logs.output, [
            'ERROR:skonfig.settings:Environment variable "SKONFIG_LOCAL_SHELL"'
            ' has invalid value "/sdlkfj/sklfjasl": '
            'No such file: /sdlkfj/sklfjasl'
            ])

        # invalid setting should not be updated
        self.assertNotEqual(s.local_shell, env["SKONFIG_LOCAL_SHELL"])
        # but the valid setting should be updated
        self.assertEqual(s.remote_shell, env["SKONFIG_REMOTE_SHELL"])

    def test_update_from_configfile(self):
        config_empty = os.path.join(fixtures, "config-empty.ini")
        config_valid = os.path.join(fixtures, "config-valid.ini")

        s_default = skonfig.settings.SettingsContainer()
        self.assert_defaults(s_default)

        s = skonfig.settings.SettingsContainer()
        self.assert_defaults(s)

        s.update_from_config_files([config_empty])

        self.assertEqual(s_default, s)

        s.update_from_config_files([config_valid])

        self.assertNotEqual(s_default, s)
        self.assertEqual(s.remote_shell, "/usr/local/bin/ksh")

    def test_update_from_configfile_with_interpolation(self):
        import configparser

        try:
            s = skonfig.settings.SettingsContainer()
            s.cache_path_pattern = "x"
            s.update_from_config_files([interpolation_config_file])

            self.assertIsNotNone(s.cache_path_pattern)
            self.assertEqual(s.cache_path_pattern, '%N')
        except configparser.InterpolationSyntaxError as e:
            self.fail("Exception should not have been raised: %r" % (e))

    def test_invalid_update_from_configfile(self):
        config_file = os.path.join(fixtures, "config-invalid.ini")

        s = skonfig.settings.SettingsContainer()
        self.assert_defaults(s)

        # assertLogs requires Python >= 3.4
        with self.assertLogs(logger="skonfig.settings") as logs:
            s.update_from_config_files([config_file])

        # valid settings are applied
        self.assertEqual(s.jobs, 3)

        # and errors are logged for the others
        self.assertEqual(sorted(logs.output), sorted(map(
            lambda s: s % {"file": config_file}, [
                # archiving: invalid value with post-processing
                'ERROR:skonfig.settings:Configuration option "archiving" has '
                'invalid value "some" in file "%(file)s": '
                'invalid archiving mode: some',
                # foo: invalid setting
                'ERROR:skonfig.settings:Invalid configuration option "foo" '
                'found in file "%(file)s". Ignoring.',
                # local_shell: invalid value
                'ERROR:skonfig.settings:Configuration option "local_shell" has'
                ' invalid value "/opt/ksdfjdf/lsdjfal" in file "%(file)s": '
                'No such file: /opt/ksdfjdf/lsdjfal',
                # verbosity: invalid value
                'ERROR:skonfig.settings:Configuration option "verbosity" has '
                'invalid value "OHYES" in file "%(file)s": '
                'invalid logging level: OHYES',
                ])))


if __name__ == "__main__":
    import unittest

    unittest.main()
