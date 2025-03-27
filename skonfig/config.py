# -*- coding: utf-8 -*-
#
# 2010-2015 Nico Schottelius (nico-cdist at schottelius.org)
# 2013-2017 Steven Armstrong (steven-cdist at armstrong.cc)
# 2016-2017 Darko Poljak (darko.poljak at gmail.com)
# 2020-2021,2023,2025 Dennis Camera (dennis.camera at riiengineering.ch)
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
import sys
import time
import tempfile
import multiprocessing
import shutil

import skonfig
import skonfig.exec.local
import skonfig.exec.remote
import skonfig.logging

from skonfig.exec.util import get_std_fd
from skonfig.mputil import (mp_pool_run, mp_sig_handler)
from skonfig.util import (ipaddr, shquot)
from skonfig.util.remoteutil import inspect_ssh_mux_opts


def graph_check_cycle(graph):
    # Start from each node in the graph and check for cycle starting from it.
    for node in graph:
        # Cycle path.
        path = [node]
        has_cycle = _graph_dfs_cycle(graph, node, path)
        if has_cycle:
            return (has_cycle, path)
    return (False, None)


def _graph_dfs_cycle(graph, node, path):
    for neighbour in graph.get(node, ()):
        # If node is already in path then this is cycle.
        if neighbour in path:
            path.append(neighbour)
            return True
        path.append(neighbour)
        rv = _graph_dfs_cycle(graph, neighbour, path)
        if rv:
            return True
        # Remove last item from list - neighbour whose DFS path we have have
        # just checked.
        del path[-1]
    return False


class Config:
    """Cdist main class to hold arbitrary data"""

    # list of paths (files and/or directories) that will be removed on finish
    _paths_for_removal = []

    @classmethod
    def _register_path_for_removal(cls, path):
        cls._paths_for_removal.append(path)

    @classmethod
    def _remove_paths(cls):
        while cls._paths_for_removal:
            path = cls._paths_for_removal.pop()
            if os.path.isfile(path):
                os.remove(path)
            else:
                shutil.rmtree(path)

    def __init__(self, local, remote, dry_run=False, jobs=None,
                 cleanup_cmds=None, remove_remote_files_dirs=False):

        self.local = local
        self.remote = remote
        self._open_logger()
        self.dry_run = dry_run
        self.jobs = jobs
        self.cleanup_cmds = cleanup_cmds if cleanup_cmds else []
        self.remove_remote_files_dirs = remove_remote_files_dirs

        self.explorer = skonfig.core.Explorer(
            self.local.target_host, self.local, self.remote, jobs=self.jobs,
            dry_run=self.dry_run)
        self.manifest = skonfig.core.Manifest(
            self.local.target_host, self.local, dry_run=self.dry_run)
        self.code = skonfig.core.Code(
            self.local.target_host, self.local, self.remote,
            dry_run=self.dry_run)

    def _init_files_dirs(self):
        """Prepare files and directories for the run"""
        self.local.create_files_dirs()
        self.remote.create_files_dirs()

    def _remove_remote_files_dirs(self):
        """Remove remote files and directories for the run"""
        self.remote.remove_files_dirs()

    def _remove_files_dirs(self):
        """Remove files and directories for the run"""
        if self.remove_remote_files_dirs:
            self._remove_remote_files_dirs()
        self.manifest.cleanup()

    @staticmethod
    def construct_remote_exec_patterns(settings):
        # default remote cmd patterns
        remote_exec_pattern = None
        remote_cmds_cleanup_pattern = None

        if settings.remote_exec is not None:
            # if remote_exec is not None then then user specified a custom
            # remote_exec command. In this case, we don’t add mux options.
            return (None, None)

        mux_opts = inspect_ssh_mux_opts()
        if mux_opts:
            default_remote_exec = "ssh -o User=root"
            remote_exec_pattern = "%s %s" % (default_remote_exec, mux_opts)
            remote_cmds_cleanup_pattern = "%s -O exit -S {}" % (
                default_remote_exec)

        return (remote_exec_pattern, remote_cmds_cleanup_pattern)

    @classmethod
    def _resolve_ssh_control_path(cls):
        base_path = tempfile.mkdtemp()
        cls._register_path_for_removal(base_path)
        control_path = os.path.join(base_path, "s")
        return control_path

    @classmethod
    def _resolve_remote_cmds(cls, settings):
        (remote_exec_pattern, remote_cmds_cleanup_pattern) = \
            cls.construct_remote_exec_patterns(settings)

        if remote_exec_pattern or remote_cmds_cleanup_pattern:
            control_path = cls._resolve_ssh_control_path()

        # If we constructed patterns for remote commands then there is a {}
        # placeholder for SSH’s ControlPath option, format the pattern and we
        # have unique ControlPath for each host.
        #
        # If not then use remote_exec as the user specified.
        if remote_exec_pattern:
            remote_exec = remote_exec_pattern.format(control_path)
        else:
            remote_exec = settings.remote_exec

        if remote_cmds_cleanup_pattern:
            remote_cmds_cleanup = remote_cmds_cleanup_pattern.format(
                control_path)
        else:
            remote_cmds_cleanup = ""

        return (remote_exec, remote_cmds_cleanup)

    @staticmethod
    def resolve_target_addresses(host):
        try:
            return ipaddr.resolve_target_addresses(host)
        except:  # noqa
            e = sys.exc_info()[1]
            raise skonfig.Error(
                "Error resolving target addresses for host '%s': %s" % (
                    host, e))

    @classmethod
    def onehost(cls, host, host_base_path, override_init_manifest, settings,
                dry_run=False, jobs=1,
                remove_remote_files_dirs=False):
        """Configure ONE system."""
        log = skonfig.logging.getLogger(host)

        try:
            (remote_exec, cleanup_cmd) = cls._resolve_remote_cmds(settings)
            log.debug("remote_exec for host \"%s\": %s", host, remote_exec)

            target_host = cls.resolve_target_addresses(host)
            log.debug("target_host for host \"%s\": %s", host, target_host)

            local = skonfig.exec.local.Local(
                target_host=target_host,
                base_root_path=host_base_path,
                settings=settings,
                initial_manifest=override_init_manifest)

            # Make __global state dir available to custom remote scripts.
            os.environ['__global'] = local.base_path

            remote = skonfig.exec.remote.Remote(
                target_host=target_host,
                remote_exec=remote_exec,
                base_path=settings.remote_out_path,
                settings=settings,
                stdout_base_path=local.stdout_base_path,
                stderr_base_path=local.stderr_base_path)

            cleanup_cmds = []
            if cleanup_cmd:
                cleanup_cmds.append(cleanup_cmd)
            c = cls(local, remote, dry_run=dry_run, jobs=jobs,
                    cleanup_cmds=cleanup_cmds,
                    remove_remote_files_dirs=remove_remote_files_dirs)
            c.run()
            cls._remove_paths()

        except skonfig.Error as e:
            log.error(e)
            raise

    @staticmethod
    def create_temp_host_base_dir(tmpdir=None):
        return tempfile.mkdtemp(prefix="skonfig.", dir=tmpdir)

    def run(self):
        """Do what is most often done: deploy & cleanup"""
        start_time = time.time()

        self.log.info("Starting %s run",
                      'dry' if self.dry_run else 'configuration')

        self._init_files_dirs()

        self.explorer.run_global_explorers(self.local.global_explorer_out_path)
        try:
            self.manifest.run_initial_manifest(self.local.initial_manifest)
        except skonfig.Error as e:
            which = "init"
            stdout_path = os.path.join(self.local.stdout_base_path, which)
            stderr_path = os.path.join(self.local.stderr_base_path, which)
            raise skonfig.InitialManifestError(
                self.local.initial_manifest, stdout_path, stderr_path, e)
        self.iterate_until_finished()
        self._remove_files_dirs()
        self.cleanup()

        self.local.save_cache(start_time)
        self.log.info("Finished %s run in %.2f seconds",
                      'dry' if self.dry_run else 'successful',
                      time.time() - start_time)

    def cleanup(self):
        self.log.debug("Running cleanup commands")
        local = self.local

        for cleanup_cmd in self.cleanup_cmds:
            cmd = shquot.split(cleanup_cmd) + [self.local.target_host[0]]
            try:
                with get_std_fd(local.stdout_base_path, "cleanup") as stdout, \
                     get_std_fd(local.stderr_base_path, "cleanup") as stderr:
                    local.run(
                        cmd, return_output=False, stdout=stdout, stderr=stderr)
            except skonfig.Error as e:
                # Log warning but continue.
                self.log.warning("Cleanup command failed: %s", e)

    def object_list(self):
        """Short name for object list retrieval"""
        for cdist_object in skonfig.core.CdistObject.list_objects(
                self.local.object_path, self.local.type_path,
                self.local.object_marker_name):
            if cdist_object.cdist_type.is_install:
                self.log.debug("Running in config mode, ignoring install "
                               "object: %s", cdist_object)
            else:
                yield cdist_object

    def iterate_once(self):
        """
            Iterate over the objects once - helper method for
            iterate_until_finished
        """
        if self.jobs:
            return self._iterate_once_parallel()
        else:
            return self._iterate_once_sequential()

    def _iterate_once_sequential(self):
        self.log.debug("Iteration in sequential mode")
        objects_changed = False

        for cdist_object in self.object_list():
            if cdist_object.has_requirements_unfinished(
                    cdist_object.requirements):
                """We cannot do anything for this poor object"""
                continue

            if cdist_object.state == skonfig.core.CdistObject.STATE_UNDEF:
                """Prepare the virgin object"""

                self.object_prepare(cdist_object)
                objects_changed = True

            if cdist_object.has_requirements_unfinished(
                    cdist_object.autorequire):
                """The previous step created objects we depend on -
                    wait for them
                """
                continue

            if cdist_object.state == skonfig.core.CdistObject.STATE_PREPARED:
                self.object_run(cdist_object)
                objects_changed = True

        return objects_changed

    def _iterate_once_parallel(self):
        self.log.debug("Iteration in parallel mode in %d jobs", self.jobs)
        objects_changed = False

        cargo = []
        for cdist_object in self.object_list():
            if cdist_object.has_requirements_unfinished(
                    cdist_object.requirements):
                """We cannot do anything for this poor object"""
                continue

            if cdist_object.state == skonfig.core.CdistObject.STATE_UNDEF:
                """Prepare the virgin object"""

                # self.object_prepare(cdist_object)
                # objects_changed = True
                cargo.append(cdist_object)

        n = len(cargo)
        if n == 1:
            self.log.debug("Only one object, preparing sequentially")
            self.object_prepare(cargo[0])
            objects_changed = True
        elif cargo:
            if callable(getattr(multiprocessing, "get_start_method", None)):
                # Python >= 3.4
                self.log.trace(
                    "Multiprocessing start method is %s",
                    multiprocessing.get_start_method())

            self.log.trace("Multiprocessing cargo: %s", cargo)

            cargo_types = set()
            for c in cargo:
                cargo_types.add(c.cdist_type)
            self.log.trace("Multiprocessing cargo_types: %s", cargo_types)
            nt = len(cargo_types)
            if nt == 1:
                self.log.debug(("Only one type, transferring explorers "
                                "sequentially"))
                self.explorer.transfer_type_explorers(cargo_types.pop())
            else:
                self.log.trace("Starting multiprocessing Pool for %d "
                               "parallel types explorers transferring", nt)
                args = [(ct,) for ct in cargo_types]
                mp_pool_run(self.explorer.transfer_type_explorers, args,
                            jobs=self.jobs)
                self.log.trace(("Multiprocessing for parallel transferring "
                                "types' explorers finished"))

            self.log.trace("Starting multiprocessing Pool for %d parallel "
                           "objects preparation", n)
            args = [(c, False) for c in cargo]
            mp_pool_run(self.object_prepare, args, jobs=self.jobs)
            self.log.trace(("Multiprocessing for parallel object "
                            "preparation finished"))
            objects_changed = True

        del cargo[:]
        for cdist_object in self.object_list():
            if cdist_object.has_requirements_unfinished(
                    cdist_object.requirements):
                """We cannot do anything for this poor object"""
                continue

            if cdist_object.state == skonfig.core.CdistObject.STATE_PREPARED:
                if cdist_object.has_requirements_unfinished(
                        cdist_object.autorequire):
                    """The previous step created objects we depend on -
                    wait for them
                    """
                    continue

                # self.object_run(cdist_object)
                # objects_changed = True

                # put objects in chuncks of distinct types
                # so that there is no more than one object
                # of the same type in one chunk because there is a
                # possibility of object's process locking which
                # prevents parallel execution at remote
                # and do this only for nonparallel marked types
                for chunk in cargo:
                    for obj in chunk:
                        if (obj.cdist_type == cdist_object.cdist_type and
                           cdist_object.cdist_type.is_nonparallel):
                            break
                    else:
                        chunk.append(cdist_object)
                        break
                else:
                    chunk = [cdist_object]
                    cargo.append(chunk)

        for chunk in cargo:
            self.log.trace("Running chunk: %s", chunk)
            n = len(chunk)
            if n == 1:
                self.log.debug("Only one object, running sequentially")
                self.object_run(chunk[0])
                objects_changed = True
            elif chunk:
                if callable(getattr(
                        multiprocessing, "get_start_method", None)):
                    # Python >= 3.4
                    self.log.trace(
                        "Multiprocessing start method is %s",
                        multiprocessing.get_start_method())
                self.log.trace("Starting multiprocessing Pool for %d "
                               "parallel object run", n)
                args = [(c,) for c in chunk]
                mp_pool_run(self.object_run, args, jobs=self.jobs)
                self.log.trace(("Multiprocessing for parallel object "
                                "run finished"))
                objects_changed = True

        return objects_changed

    def _open_logger(self):
        self.log = skonfig.logging.getLogger(self.local.target_host[0])

    # logger is not pickable, so remove it when we pickle
    def __getstate__(self):
        state = self.__dict__.copy()
        if 'log' in state:
            del state['log']
        return state

    # recreate logger when we unpickle
    def __setstate__(self, state):
        self.__dict__.update(state)
        self._open_logger()

    def _validate_dependencies(self):
        """Build dependency graph for unfinished objects and
        check for cycles.
        """
        graph = {}

        def _add_requirements(cdist_object, requirements):
            obj_name = cdist_object.name
            if obj_name not in graph:
                graph[obj_name] = []

            for requirement in cdist_object.requirements_unfinished(
                    requirements):
                graph[obj_name].append(requirement.name)

        for cdist_object in self.object_list():
            if cdist_object.state == cdist_object.STATE_DONE:
                continue

            _add_requirements(cdist_object, cdist_object.requirements)
            _add_requirements(cdist_object, cdist_object.autorequire)
        return graph_check_cycle(graph)

    def iterate_until_finished(self):
        """
            Go through all objects and solve them
            one after another
        """

        objects_changed = True

        while objects_changed:
            # Check for cycles as early as possible.
            (has_cycle, path) = self._validate_dependencies()
            if has_cycle:
                raise skonfig.UnresolvableRequirementsError(
                    "Cycle detected in object dependencies:\n{}!".format(
                        " -> ".join(path)))
            objects_changed = self.iterate_once()

        # Check whether all objects have been finished
        unfinished_objects = []
        for cdist_object in self.object_list():
            if not cdist_object.state == cdist_object.STATE_DONE:
                unfinished_objects.append(cdist_object)

        if unfinished_objects:
            info_string = []

            for cdist_object in unfinished_objects:
                requirement_names = []
                autorequire_names = []

                for requirement in cdist_object.requirements_unfinished(
                        cdist_object.requirements):
                    requirement_names.append(requirement.name)

                for requirement in cdist_object.requirements_unfinished(
                        cdist_object.autorequire):
                    autorequire_names.append(requirement.name)

                requirements = "\n        ".join(requirement_names)
                autorequire = "\n        ".join(autorequire_names)
                info_string.append(("%s requires:\n"
                                    "        %s\n"
                                    "%s ""autorequires:\n"
                                    "        %s" % (
                                        cdist_object.name,
                                        requirements, cdist_object.name,
                                        autorequire)))

            raise skonfig.UnresolvableRequirementsError(
                    ("The requirements of the following objects could not be "
                     "resolved:\n{}").format("\n".join(info_string)))

    def _handle_deprecation(self, cdist_object):
        cdist_type = cdist_object.cdist_type
        deprecated = cdist_type.deprecated
        if deprecated is not None:
            if deprecated:
                self.log.warning("Type %s is deprecated: %s", cdist_type.name,
                                 deprecated)
            else:
                self.log.warning("Type %s is deprecated.", cdist_type.name)
        for param in cdist_object.parameters:
            if param in cdist_type.deprecated_parameters:
                msg = cdist_type.deprecated_parameters[param]
                if msg:
                    format = "%s parameter of type %s is deprecated: %s"
                    args = [param, cdist_type.name, msg]
                else:
                    format = "%s parameter of type %s is deprecated."
                    args = [param, cdist_type.name]
                self.log.warning(format, *args)

    def object_prepare(self, cdist_object, transfer_type_explorers=True):
        """Prepare object: Run type explorer + manifest"""
        self._handle_deprecation(cdist_object)
        self.log.verbose("Preparing object %s", cdist_object.name)
        self.log.verbose("Running manifest and explorers for %s",
                         cdist_object.name)
        self.explorer.run_type_explorers(cdist_object, transfer_type_explorers)
        try:
            self.manifest.run_type_manifest(cdist_object)
            self.log.trace("[ORDER_DEP] Removing order dep files for %s",
                           cdist_object)
            cdist_object.cleanup()
            cdist_object.state = skonfig.core.CdistObject.STATE_PREPARED
        except skonfig.Error as e:
            raise skonfig.ObjectError(cdist_object, e)

    def object_run(self, cdist_object):
        """Run gencode and code for an object"""
        if cdist_object.state == skonfig.core.CdistObject.STATE_DONE:
            raise skonfig.ObjectError(
                "Attempting to run an already finished object: %s" % (
                    cdist_object))

        try:
            self.log.verbose("Running object %s", cdist_object.name)

            # Generate code
            self.log.debug("Generating code for %s", cdist_object.name)
            cdist_object.code_local = self.code.run_gencode_local(cdist_object)
            cdist_object.code_remote = self.code.run_gencode_remote(
                cdist_object)
            cdist_object.changed = \
                (cdist_object.code_local or cdist_object.code_remote)

            # Execute
            if cdist_object.code_local or cdist_object.code_remote:
                self.log.info("Processing %s", cdist_object.name)

            if not self.dry_run:
                if cdist_object.code_local:
                    self.log.trace("Executing local code for %s",
                                   cdist_object.name)
                    self.code.run_code_local(cdist_object)

                if cdist_object.code_remote:
                    self.log.trace("Executing remote code for %s",
                                   cdist_object.name)
                    self.code.transfer_code_remote(cdist_object)
                    self.code.run_code_remote(cdist_object)

            # Mark this object as done
            self.log.trace("Finishing run of %s", cdist_object.name)
            cdist_object.state = skonfig.core.CdistObject.STATE_DONE
        except skonfig.Error as e:
            raise skonfig.ObjectError(cdist_object, e)
