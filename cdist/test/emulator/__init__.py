# -*- coding: utf-8 -*-
#
# 2010-2011 Steven Armstrong (steven-cdist at armstrong.cc)
# 2012-2015 Nico Schottelius (nico-cdist at schottelius.org)
# 2014      Daniel Heule     (hda at sfs.biz)
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

import io
import os
import shutil
import random
import logging

import cdist
import cdist.util

from cdist import (core, emulator, test)
from cdist.exec import local

import os.path as op
my_dirs = list(map(op.abspath, map(op.dirname, (test.__file__, __file__))))
conf_dirs = [op.join(d, 'fixtures', 'conf') for d in my_dirs]


class EmulatorTestCase(test.CdistTestCase):

    def setUp(self):
        self.temp_dir = self.mkdtemp()
        handle, self.script = self.mkstemp(dir=self.temp_dir)
        os.close(handle)
        base_path = self.temp_dir
        hostdir = cdist.util.str_hash(self.target_host[0])
        host_base_path = os.path.join(base_path, hostdir)

        self.local = local.Local(
            target_host=self.target_host,
            base_root_path=host_base_path,
            exec_path=test.cdist_exec_path,
            add_conf_dirs=conf_dirs)
        self.local.create_files_dirs()

        self.manifest = core.Manifest(self.target_host, self.local)
        self.env = self.manifest.env_initial_manifest(self.script)
        self.env['__cdist_object_marker'] = self.local.object_marker_name
        if '__cdist_log_level' in self.env:
            del self.env['__cdist_log_level']

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

#    def test_missing_object_marker_variable(self):
#        del self.env['__cdist_object_marker']
#        self.assertRaises(KeyError, emulator.Emulator, argv, env=self.env)

    def test_nonexistent_type_exec(self):
        argv = ['__does-not-exist']
        self.assertRaises(core.cdist_type.InvalidTypeError, emulator.Emulator,
                          argv, env=self.env)

    def test_nonexistent_type_requirement(self):
        argv = ['__cdist_test_type', 'test_nonexistent_type_requirement']
        self.env['require'] = '__does-not-exist/some-id'
        emu = emulator.Emulator(argv, env=self.env)
        self.assertRaises(core.cdist_type.InvalidTypeError, emu.run)

    def test_illegal_object_id_requirement(self):
        argv = ['__cdist_test_type', 'test_illegal_object_id_requirement']
        self.env['require'] = "__cdist_test_type/bad/id/with/{}/inside".format(
            self.local.object_marker_name)
        emu = emulator.Emulator(argv, env=self.env)
        self.assertRaises(core.IllegalObjectIdError, emu.run)

    def test_missing_object_id_requirement(self):
        argv = ['__cdist_test_type', 'test_missing_object_id_requirement']
        self.env['require'] = '__cdist_test_type'
        emu = emulator.Emulator(argv, env=self.env)
        self.assertRaises(core.cdist_object.MissingObjectIdError, emu.run)

    def test_singleton_object_requirement(self):
        argv = ['__cdist_test_type', 'test_singleton_object_requirement']
        self.env['require'] = '__test_singleton'
        emu = emulator.Emulator(argv, env=self.env)
        emu.run()
        # if we get here all is fine

    def test_requirement_pattern(self):
        argv = ['__cdist_test_type', '/tmp/foobar']
        self.env['require'] = '__file_noop/etc/*'
        emulator.Emulator(argv, env=self.env)
        # if we get here all is fine

    def test_loglevel(self):
        argv = ['__cdist_test_type', 'test_loglevel']
        self.env['require'] = '__file_noop/etc/*'
        emu = emulator.Emulator(argv, env=self.env)
        emu_loglevel = emu.log.getEffectiveLevel()
        self.assertEqual(emu_loglevel, logging.WARNING)
        self.env['__cdist_log_level'] = str(logging.DEBUG)
        emu = emulator.Emulator(argv, env=self.env)
        emu_loglevel = emu.log.getEffectiveLevel()
        self.assertEqual(emu_loglevel, logging.DEBUG)
        del self.env['__cdist_log_level']

    def test_invalid_loglevel_value(self):
        argv = ['__cdist_test_type', 'test_invalid_loglevel_value']
        self.env['require'] = '__file_noop/etc/*'
        emu = emulator.Emulator(argv, env=self.env)
        emu_loglevel = emu.log.getEffectiveLevel()
        self.assertEqual(emu_loglevel, logging.WARNING)
        # lowercase is invalid
        self.env['__cdist_log_level'] = 'debug'
        emu = emulator.Emulator(argv, env=self.env)
        emu_loglevel = emu.log.getEffectiveLevel()
        self.assertEqual(emu_loglevel, logging.WARNING)
        del self.env['__cdist_log_level']

    def test_requirement_via_order_dependency(self):
        self.env['CDIST_ORDER_DEPENDENCY'] = 'on'
        argv = ['__planet', 'earth']
        emu = emulator.Emulator(argv, env=self.env)
        emu.run()
        argv = ['__planet', 'mars']
        emu = emulator.Emulator(argv, env=self.env)
        emu.run()
        # In real world, this is not shared over instances
        del self.env['require']
        argv = ['__file_noop', '/tmp/cdisttest']
        emu = emulator.Emulator(argv, env=self.env)
        emu.run()
        # now load the objects and verify the require parameter of the objects
        cdist_type = core.CdistType(self.local.type_path, '__planet')
        erde_object = core.CdistObject(cdist_type, self.local.object_path,
                                       self.local.object_marker_name, 'erde')
        mars_object = core.CdistObject(cdist_type, self.local.object_path,
                                       self.local.object_marker_name, 'mars')
        cdist_type = core.CdistType(self.local.type_path, '__file_noop')
        file_object = core.CdistObject(cdist_type, self.local.object_path,
                                       self.local.object_marker_name,
                                       '/tmp/cdisttest')
        # now test the recorded requirements
        self.assertTrue(len(erde_object.requirements) == 0)
        self.assertEqual(list(mars_object.requirements), ['__planet/earth'])
        self.assertEqual(list(file_object.requirements), ['__planet/mars'])
        # if we get here all is fine

    def test_order_dependency_context(self):
        test_seq = ('A', True, 'B', 'C', 'D', False, 'E', 'F', True, 'G',
                    'H', False, 'I', )
        expected_requirements = {
            'C': set(('__planet/B', )),
            'D': set(('__planet/C', )),
            'H': set(('__planet/G', )),
        }
        # Ensure env var is not in env
        if 'CDIST_ORDER_DEPENDENCY' in self.env:
            del self.env['CDIST_ORDER_DEPENDENCY']

        for x in test_seq:
            if isinstance(x, str):
                # Clear because of order dep injection
                # In real world, this is not shared over instances
                if 'require' in self.env:
                    del self.env['require']
                argv = ['__planet', x]
                emu = emulator.Emulator(argv, env=self.env)
                emu.run()
            elif isinstance(x, bool):
                if x:
                    self.env['CDIST_ORDER_DEPENDENCY'] = 'on'
                elif 'CDIST_ORDER_DEPENDENCY' in self.env:
                    del self.env['CDIST_ORDER_DEPENDENCY']
        cdist_type = core.CdistType(self.local.type_path, '__planet')
        for x in test_seq:
            if isinstance(x, str):
                obj = core.CdistObject(cdist_type, self.local.object_path,
                                       self.local.object_marker_name, x)
                reqs = set(obj.requirements)
                if x in expected_requirements:
                    self.assertEqual(reqs, expected_requirements[x])
                else:
                    self.assertTrue(len(reqs) == 0)
        # if we get here all is fine


class EmulatorConflictingRequirementsTestCase(test.CdistTestCase):

    def setUp(self):
        self.temp_dir = self.mkdtemp()
        handle, self.script = self.mkstemp(dir=self.temp_dir)
        os.close(handle)
        base_path = self.temp_dir
        hostdir = cdist.util.str_hash(self.target_host[0])
        host_base_path = os.path.join(base_path, hostdir)

        self.local = local.Local(
            target_host=self.target_host,
            base_root_path=host_base_path,
            exec_path=test.cdist_exec_path,
            add_conf_dirs=conf_dirs)
        self.local.create_files_dirs()

        self.manifest = core.Manifest(self.target_host, self.local)
        self.env = self.manifest.env_initial_manifest(self.script)
        self.env['__cdist_object_marker'] = self.local.object_marker_name

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_object_different_requirements_req_none(self):
        argv = ['__directory_noop', 'spam']
        emu = emulator.Emulator(argv, env=self.env)
        emu.run()
        argv = ['__file_noop', 'eggs']
        self.env['require'] = '__directory_noop/spam'
        emu = emulator.Emulator(argv, env=self.env)
        emu.run()
        argv = ['__file_noop', 'eggs']
        if 'require' in self.env:
            del self.env['require']
        emu = emulator.Emulator(argv, env=self.env)
        emu.run()

        cdist_type = core.CdistType(self.local.type_path, '__file_noop')
        cdist_object = core.CdistObject(cdist_type, self.local.object_path,
                                        self.local.object_marker_name, 'eggs')
        reqs = set(('__directory_noop/spam',))
        self.assertEqual(reqs, set(cdist_object.requirements))

    def test_object_different_requirements_none_req(self):
        argv = ['__directory_noop', 'spam']
        emu = emulator.Emulator(argv, env=self.env)
        emu.run()
        argv = ['__file_noop', 'eggs']
        if 'require' in self.env:
            del self.env['require']
        emu = emulator.Emulator(argv, env=self.env)
        emu.run()
        argv = ['__file_noop', 'eggs']
        self.env['require'] = '__directory_noop/spam'
        emu = emulator.Emulator(argv, env=self.env)
        emu.run()

        cdist_type = core.CdistType(self.local.type_path, '__file_noop')
        cdist_object = core.CdistObject(cdist_type, self.local.object_path,
                                        self.local.object_marker_name, 'eggs')
        reqs = set(('__directory_noop/spam',))
        self.assertEqual(reqs, set(cdist_object.requirements))

    def test_object_different_requirements(self):
        argv = ['__directory_noop', 'spam']
        emu = emulator.Emulator(argv, env=self.env)
        emu.run()
        argv = ['__directory_noop', 'spameggs']
        emu = emulator.Emulator(argv, env=self.env)
        emu.run()

        argv = ['__file_noop', 'eggs']
        if 'require' in self.env:
            del self.env['require']
        self.env['require'] = '__directory_noop/spam'
        emu = emulator.Emulator(argv, env=self.env)
        emu.run()

        argv = ['__file_noop', 'eggs']
        self.env['require'] = '__directory_noop/spameggs'
        emu = emulator.Emulator(argv, env=self.env)
        emu.run()

        cdist_type = core.CdistType(self.local.type_path, '__file_noop')
        cdist_object = core.CdistObject(cdist_type, self.local.object_path,
                                        self.local.object_marker_name, 'eggs')
        reqs = set(('__directory_noop/spam', '__directory_noop/spameggs',))
        self.assertEqual(reqs, set(cdist_object.requirements))


class AutoRequireEmulatorTestCase(test.CdistTestCase):

    def setUp(self):
        self.temp_dir = self.mkdtemp()
        base_path = os.path.join(self.temp_dir, "out")
        hostdir = cdist.util.str_hash(self.target_host[0])
        host_base_path = os.path.join(base_path, hostdir)

        self.local = local.Local(
            target_host=self.target_host,
            base_root_path=host_base_path,
            exec_path=test.cdist_exec_path,
            add_conf_dirs=conf_dirs)
        self.local.create_files_dirs()
        self.manifest = core.Manifest(self.target_host, self.local)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_autorequire(self):
        initial_manifest = os.path.join(self.local.manifest_path, "init")
        self.manifest.run_initial_manifest(initial_manifest)
        cdist_type = core.CdistType(self.local.type_path, '__saturn')
        cdist_object = core.CdistObject(cdist_type, self.local.object_path,
                                        self.local.object_marker_name, '')
        self.manifest.run_type_manifest(cdist_object)
        expected = ['__planet/Saturn', '__moon/Prometheus']
        self.assertEqual(sorted(cdist_object.autorequire), sorted(expected))


class OverrideTestCase(test.CdistTestCase):

    def setUp(self):
        self.temp_dir = self.mkdtemp()
        handle, self.script = self.mkstemp(dir=self.temp_dir)
        os.close(handle)
        base_path = self.temp_dir
        hostdir = cdist.util.str_hash(self.target_host[0])
        host_base_path = os.path.join(base_path, hostdir)

        self.local = local.Local(
            target_host=self.target_host,
            base_root_path=host_base_path,
            exec_path=test.cdist_exec_path,
            add_conf_dirs=conf_dirs)
        self.local.create_files_dirs()

        self.manifest = core.Manifest(self.target_host, self.local)
        self.env = self.manifest.env_initial_manifest(self.script)
        self.env['__cdist_object_marker'] = self.local.object_marker_name

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_override_negative(self):
        argv = ['__cdist_test_type', 'test_override_negative']
        emu = emulator.Emulator(argv, env=self.env)
        emu.run()
        argv = ['__cdist_test_type', 'test_override_negative',
                '--param1', 'foo']
        emu = emulator.Emulator(argv, env=self.env)
        self.assertRaises(cdist.Error, emu.run)

    def test_override_feature(self):
        argv = ['__cdist_test_type', 'test_override_feature']
        emu = emulator.Emulator(argv, env=self.env)
        emu.run()
        argv = ['__cdist_test_type', 'test_override_feature',
                '--param1', 'foo']
        self.env['CDIST_OVERRIDE'] = 'true'
        emu = emulator.Emulator(argv, env=self.env)
        emu.run()


class ArgumentsTestCase(test.CdistTestCase):

    def setUp(self):
        self.temp_dir = self.mkdtemp()
        base_path = self.temp_dir
        hostdir = cdist.util.str_hash(self.target_host[0])
        host_base_path = os.path.join(base_path, hostdir)
        handle, self.script = self.mkstemp(dir=self.temp_dir)
        os.close(handle)

        self.local = local.Local(
            target_host=self.target_host,
            base_root_path=host_base_path,
            exec_path=test.cdist_exec_path,
            add_conf_dirs=conf_dirs)
        self.local.create_files_dirs()

        self.manifest = core.Manifest(self.target_host, self.local)
        self.env = self.manifest.env_initial_manifest(self.script)
        self.env['__cdist_object_marker'] = self.local.object_marker_name

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_arguments_with_dashes(self):
        argv = ['__arguments_with_dashes', 'some-id', '--with-dash',
                'some value']
        os.environ.update(self.env)
        emu = emulator.Emulator(argv)
        emu.run()

        cdist_type = core.CdistType(self.local.type_path,
                                    '__arguments_with_dashes')
        cdist_object = core.CdistObject(cdist_type, self.local.object_path,
                                        self.local.object_marker_name,
                                        'some-id')
        self.assertTrue('with-dash' in cdist_object.parameters)

    def test_boolean(self):
        type_name = '__arguments_boolean'
        object_id = 'some-id'
        argv = [type_name, object_id, '--boolean1']
        os.environ.update(self.env)
        emu = emulator.Emulator(argv)
        emu.run()

        cdist_type = core.CdistType(self.local.type_path, type_name)
        cdist_object = core.CdistObject(cdist_type, self.local.object_path,
                                        self.local.object_marker_name,
                                        object_id)
        self.assertTrue('boolean1' in cdist_object.parameters)
        self.assertFalse('boolean2' in cdist_object.parameters)
        # empty file -> True
        self.assertTrue(cdist_object.parameters['boolean1'] == '')

    def test_required_arguments(self):
        """check whether assigning required parameter works"""

        type_name = '__arguments_required'
        object_id = 'some-id'
        value = 'some value'
        argv = [type_name, object_id, '--required1', value,
                '--required2', value]
        os.environ.update(self.env)
        emu = emulator.Emulator(argv)
        emu.run()

        cdist_type = core.CdistType(self.local.type_path, type_name)
        cdist_object = core.CdistObject(cdist_type, self.local.object_path,
                                        self.local.object_marker_name,
                                        object_id)
        self.assertTrue('required1' in cdist_object.parameters)
        self.assertTrue('required2' in cdist_object.parameters)
        self.assertEqual(cdist_object.parameters['required1'], value)
        self.assertEqual(cdist_object.parameters['required2'], value)

    def test_required_multiple_arguments(self):
        """check whether assigning required multiple parameter works"""

        type_name = '__arguments_required_multiple'
        object_id = 'some-id'
        value1 = 'value1'
        value2 = 'value2'
        argv = [type_name, object_id, '--required1', value1,
                '--required1', value2]
        os.environ.update(self.env)
        emu = emulator.Emulator(argv)
        emu.run()

        cdist_type = core.CdistType(self.local.type_path, type_name)
        cdist_object = core.CdistObject(cdist_type, self.local.object_path,
                                        self.local.object_marker_name,
                                        object_id)
        self.assertTrue('required1' in cdist_object.parameters)
        self.assertTrue(value1 in cdist_object.parameters['required1'])
        self.assertTrue(value2 in cdist_object.parameters['required1'])

#    def test_required_missing(self):
#        type_name = '__arguments_required'
#        object_id = 'some-id'
#        value = 'some value'
#        argv = [type_name, object_id, '--required1', value]
#        os.environ.update(self.env)
#        emu = emulator.Emulator(argv)
#
#        self.assertRaises(SystemExit, emu.run)

    def test_optional(self):
        type_name = '__arguments_optional'
        object_id = 'some-id'
        value = 'some value'
        argv = [type_name, object_id, '--optional1', value]
        os.environ.update(self.env)
        emu = emulator.Emulator(argv)
        emu.run()

        cdist_type = core.CdistType(self.local.type_path, type_name)
        cdist_object = core.CdistObject(cdist_type, self.local.object_path,
                                        self.local.object_marker_name,
                                        object_id)
        self.assertTrue('optional1' in cdist_object.parameters)
        self.assertFalse('optional2' in cdist_object.parameters)
        self.assertEqual(cdist_object.parameters['optional1'], value)

    def test_optional_multiple(self):
        type_name = '__arguments_optional_multiple'
        object_id = 'some-id'
        value1 = 'value1'
        value2 = 'value2'
        argv = [type_name, object_id, '--optional1', value1, '--optional1',
                value2]
        os.environ.update(self.env)
        emu = emulator.Emulator(argv)
        emu.run()

        cdist_type = core.CdistType(self.local.type_path, type_name)
        cdist_object = core.CdistObject(cdist_type, self.local.object_path,
                                        self.local.object_marker_name,
                                        object_id)
        self.assertTrue('optional1' in cdist_object.parameters)
        self.assertTrue(value1 in cdist_object.parameters['optional1'])
        self.assertTrue(value2 in cdist_object.parameters['optional1'])

    def test_argument_defaults(self):
        type_name = '__argument_defaults'
        object_id = 'some-id'
        value = 'value1'
        argv = [type_name, object_id]
        os.environ.update(self.env)
        emu = emulator.Emulator(argv)
        emu.run()

        cdist_type = core.CdistType(self.local.type_path, type_name)
        cdist_object = core.CdistObject(cdist_type, self.local.object_path,
                                        self.local.object_marker_name,
                                        object_id)
        self.assertTrue('optional1' in cdist_object.parameters)
        self.assertFalse('optional2' in cdist_object.parameters)
        self.assertEqual(cdist_object.parameters['optional1'], value)

    def test_object_params_in_context(self):
        type_name = '__arguments_all'
        object_id = 'some-id'
        argv = [type_name, object_id, '--opt', 'opt', '--req', 'req',
                '--bool', '--optmul', 'val1', '--optmul', 'val2',
                '--reqmul', 'val3', '--reqmul', 'val4',
                '--optmul1', 'val5', '--reqmul1', 'val6']
        os.environ.update(self.env)
        emu = emulator.Emulator(argv)
        emu.run()

        obj_params = emu._object_params_in_context()
        obj_params_expected = {
            'bool': '',
            'opt': 'opt',
            'optmul1': ['val5', ],
            'optmul': ['val1', 'val2', ],
            'req': 'req',
            'reqmul1': ['val6', ],
            'reqmul': ['val3', 'val4', ],
        }
        self.assertEqual(obj_params, obj_params_expected)


class StdinTestCase(test.CdistTestCase):

    def setUp(self):
        self.orig_environ = os.environ
        os.environ = os.environ.copy()

        self.temp_dir = self.mkdtemp()
        base_path = os.path.join(self.temp_dir, "out")
        hostdir = cdist.util.str_hash(self.target_host[0])
        host_base_path = os.path.join(base_path, hostdir)

        self.local = local.Local(
            target_host=self.target_host,
            base_root_path=host_base_path,
            exec_path=test.cdist_exec_path,
            add_conf_dirs=conf_dirs)

        self.local.create_files_dirs()

    def tearDown(self):
        os.environ = self.orig_environ
        shutil.rmtree(self.temp_dir)

    def test_file_from_stdin(self):
        """
        Test whether reading from stdin works
        """

        ######################################################################
        # Create string with random content
        random_string = str(random.sample(range(1000), 800))
        random_buffer = io.BytesIO(bytes(random_string, 'utf-8'))

        ######################################################################
        # Prepare required args and environment for emulator
        type_name = '__file_noop'
        object_id = "cdist-test-id"
        argv = [type_name, object_id]

        env = os.environ.copy()
        env['__cdist_manifest'] = "/cdist-test/path/that/does/not/exist"
        env['__cdist_object_marker'] = self.local.object_marker_name
        env['__cdist_type_base_path'] = self.local.type_path
        env['__global'] = self.local.base_path

        ######################################################################
        # Create path where stdin should reside at
        cdist_type = core.CdistType(self.local.type_path, type_name)
        cdist_object = core.CdistObject(cdist_type, self.local.object_path,
                                        self.local.object_marker_name,
                                        object_id)
        stdin_out_path = os.path.join(cdist_object.absolute_path, 'stdin')

        ######################################################################
        # Run emulator
        emu = emulator.Emulator(argv, stdin=random_buffer, env=env)
        emu.run()

        ######################################################################
        # Read where emulator should have placed stdin
        with open(stdin_out_path, 'r') as fd:
            stdin_saved_by_emulator = fd.read()

        self.assertEqual(random_string, stdin_saved_by_emulator)


class EmulatorAlreadyExistingRequirementsWarnTestCase(test.CdistTestCase):

    def setUp(self):
        self.temp_dir = self.mkdtemp()
        handle, self.script = self.mkstemp(dir=self.temp_dir)
        os.close(handle)
        base_path = self.temp_dir
        hostdir = cdist.util.str_hash(self.target_host[0])
        host_base_path = os.path.join(base_path, hostdir)

        self.local = local.Local(
            target_host=self.target_host,
            base_root_path=host_base_path,
            exec_path=test.cdist_exec_path,
            add_conf_dirs=conf_dirs)
        self.local.create_files_dirs()

        self.manifest = core.Manifest(self.target_host, self.local)
        self.env = self.manifest.env_initial_manifest(self.script)
        self.env['__cdist_object_marker'] = self.local.object_marker_name

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_object_existing_requirements_req_none(self):
        """Test to show dependency resolver warning message."""
        argv = ['__directory_noop', 'spam']
        emu = emulator.Emulator(argv, env=self.env)
        emu.run()
        argv = ['__file_noop', 'eggs']
        self.env['require'] = '__directory_noop/spam'
        emu = emulator.Emulator(argv, env=self.env)
        emu.run()
        argv = ['__file_noop', 'eggs']
        if 'require' in self.env:
            del self.env['require']
        emu = emulator.Emulator(argv, env=self.env)

    def test_object_existing_requirements_none_req(self):
        """Test to show dependency resolver warning message."""
        argv = ['__directory_noop', 'spam']
        emu = emulator.Emulator(argv, env=self.env)
        emu.run()
        argv = ['__file_noop', 'eggs']
        if 'require' in self.env:
            del self.env['require']
        emu = emulator.Emulator(argv, env=self.env)
        emu.run()
        argv = ['__file_noop', 'eggs']
        self.env['require'] = '__directory_noop/spam'
        emu = emulator.Emulator(argv, env=self.env)

    def test_parse_require(self):
        require = " \t \n  \t\t\n\t\na\tb\nc d \te\t\nf\ng\t "
        expected = ['', 'a', 'b', 'c', 'd', 'e', 'f', 'g', '', ]

        argv = ['__directory_noop', 'spam']
        emu = emulator.Emulator(argv, env=self.env)
        requirements = emu._parse_require(require)

        self.assertEqual(expected, requirements)


if __name__ == '__main__':
    import unittest
    unittest.main()
