# -*- coding: utf-8 -*-
#
# 2010-2015 Nico Schottelius (nico-cdist at schottelius.org)
# 2012-2017 Steven Armstrong (steven-cdist at armstrong.cc)
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

from skonfig import __version__


class Error(Exception):
    """Base exception class for this project"""
    pass


class UnresolvableRequirementsError(Error):
    """Resolving requirements failed"""
    pass


class CdistEntityError(Error):
    """Something went wrong while executing cdist entity"""
    def __init__(self, entity_name, entity_params, stdout_paths,
                 stderr_paths, subject=''):
        self.entity_name = entity_name
        self.entity_params = entity_params
        self.stderr_paths = stderr_paths
        self.stdout_paths = stdout_paths
        if isinstance(subject, Error):
            self.original_error = subject
        else:
            self.original_error = None
        self.message = str(subject)

    def _stdpath(self, stdpaths, header_name):
        result = {}
        for name, path in stdpaths:
            if name not in result:
                result[name] = []
            try:
                if os.path.exists(path) and os.path.getsize(path) > 0:
                    output = []
                    label_begin = name + ":" + header_name
                    output.append(label_begin)
                    output.append('\n')
                    output.append('-' * len(label_begin))
                    output.append('\n')
                    with open(path, 'r') as fd:
                        output.append(fd.read())
                    output.append('\n')
                    result[name].append(''.join(output))
            except UnicodeError as ue:
                result[name].append(('Cannot output {}:{} due to: {}.\n'
                                     'You can try to read the error file "{}"'
                                     ' yourself.').format(
                                         name, header_name, ue, path))
        return result

    def _stderr(self):
        return self._stdpath(self.stderr_paths, 'stderr')

    def _stdout(self):
        return self._stdpath(self.stdout_paths, 'stdout')

    def _update_dict_list(self, target, source):
        for x in source:
            if x not in target:
                target[x] = []
            target[x].extend(source[x])

    @property
    def std_streams(self):
        std_dict = {}
        self._update_dict_list(std_dict, self._stdout())
        self._update_dict_list(std_dict, self._stderr())
        return std_dict

    def __str__(self):
        output = []
        output.append(self.message)
        output.append('\n\n')
        header = "Error processing " + self.entity_name
        under_header = '=' * len(header)
        output.append(header)
        output.append('\n')
        output.append(under_header)
        output.append('\n')
        for param_name, param_value in self.entity_params:
            output.append(param_name + ': ' + str(param_value))
            output.append('\n')
        output.append('\n')
        for x in self.std_streams:
            output.append(''.join(self.std_streams[x]))
        return ''.join(output)


class CdistObjectError(CdistEntityError):
    """Something went wrong while working on a specific object"""
    def __init__(self, cdist_object, subject=''):
        params = [
            ('name', cdist_object.name),
            ('path', cdist_object.absolute_path),
            ('source', " ".join(cdist_object.source)),
            ('type', os.path.realpath(
                cdist_object.cdist_type.absolute_path)),
            ]
        stderr_paths = []
        for stderr_name in os.listdir(cdist_object.stderr_path):
            stderr_path = os.path.join(cdist_object.stderr_path,
                                       stderr_name)
            stderr_paths.append((stderr_name, stderr_path))
        stdout_paths = []
        for stdout_name in os.listdir(cdist_object.stdout_path):
            stdout_path = os.path.join(cdist_object.stdout_path,
                                       stdout_name)
            stdout_paths.append((stdout_name, stdout_path))
        super().__init__("object '{}'".format(cdist_object.name),
                         params, stdout_paths, stderr_paths, subject)


class CdistObjectExplorerError(CdistEntityError):
    """Something went wrong while working on a specific object explorer"""
    def __init__(self, cdist_object, explorer_name, explorer_path,
                 stderr_path, subject=''):
        params = [
            ('object name', cdist_object.name),
            ('object path', cdist_object.absolute_path),
            ('object source', " ".join(cdist_object.source)),
            ('object type', os.path.realpath(
                cdist_object.cdist_type.absolute_path)),
            ('explorer name', explorer_name),
            ('explorer path', explorer_path),
            ]
        stdout_paths = []
        stderr_paths = [
            ('remote', stderr_path),
            ]
        super().__init__("explorer '{}' of object '{}'".format(
            explorer_name, cdist_object.name), params, stdout_paths,
            stderr_paths, subject)


class InitialManifestError(CdistEntityError):
    """Something went wrong while executing initial manifest"""
    def __init__(self, initial_manifest, stdout_path, stderr_path, subject=''):
        params = [
            ('path', initial_manifest),
            ]
        stdout_paths = [
            ('init', stdout_path),
            ]
        stderr_paths = [
            ('init', stderr_path),
            ]
        super().__init__('initial manifest', params, stdout_paths,
                         stderr_paths, subject)


class GlobalExplorerError(CdistEntityError):
    """Something went wrong while executing global explorer"""
    def __init__(self, name, path, stderr_path, subject=''):
        params = [
            ('name', name),
            ('path', path),
            ]
        stderr_paths = [
            ('remote', stderr_path),
            ]
        super().__init__("global explorer '{}'".format(name),
                         params, [], stderr_paths, subject)
