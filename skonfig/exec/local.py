# -*- coding: utf-8 -*-
#
# 2011-2017 Steven Armstrong (steven-cdist at armstrong.cc)
# 2011-2015 Nico Schottelius (nico-cdist at schottelius.org)
# 2016-2017 Darko Poljak (darko.poljak at gmail.com)
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

import datetime
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

import skonfig
import skonfig.core
import skonfig.logging
import skonfig.message

import skonfig.exec.util as util

from skonfig.util import shquot

CONF_SUBDIRS_LINKED = ["explorer", "files", "manifest", "type"]


class Local:
    """Execute commands locally.

    All interaction with the local side should be done through this class.
    Directly accessing the local side from python code is a bug.

    """
    def __init__(self,
                 target_host,
                 base_root_path,
                 settings,
                 initial_manifest=None,
                 exec_path=sys.argv[0]):
        self.target_host = target_host
        self.hostdir = os.path.basename(base_root_path.rstrip("/"))
        self.base_path = os.path.join(base_root_path, "data")

        self.exec_path = exec_path
        self.custom_initial_manifest = initial_manifest
        self.settings = settings

        self._init_log()
        self._init_permissions()
        self.mkdir(self.base_path)
        self._init_cache_dir(None)
        self._init_paths()
        self._init_object_marker()
        self._init_conf_dirs()

    def _init_log(self):
        self.log = skonfig.logging.getLogger(self.target_host[0])

    # logger is not pickable, so remove it when we pickle
    def __getstate__(self):
        state = self.__dict__.copy()
        if 'log' in state:
            del state['log']
        return state

    # recreate logger when we unpickle
    def __setstate__(self, state):
        self.__dict__.update(state)
        self._init_log()

    def _init_permissions(self):
        # Setup file permissions using umask
        os.umask(0o077)

    def _init_paths(self):
        # Depending on out_path
        self.bin_path = os.path.join(self.base_path, "bin")
        self.conf_path = os.path.join(self.base_path, "conf")
        self.global_explorer_out_path = os.path.join(self.base_path,
                                                     "explorer")
        self.object_path = os.path.join(self.base_path, "object")
        self.messages_path = os.path.join(self.base_path, "messages")
        self.stdout_base_path = os.path.join(self.base_path, "stdout")
        self.stderr_base_path = os.path.join(self.base_path, "stderr")

        # Depending on conf_path
        self.files_path = os.path.join(self.conf_path, "files")
        self.global_explorer_path = os.path.join(self.conf_path, "explorer")
        self.manifest_path = os.path.join(self.conf_path, "manifest")
        self.initial_manifest = (self.custom_initial_manifest or
                                 os.path.join(self.manifest_path, "init"))

        self.type_path = os.path.join(self.conf_path, "type")

    def _init_object_marker(self):
        self.object_marker_file = os.path.join(self.base_path, "object_marker")

        # Does not need to be secure - just randomly different from .skonfig
        self.object_marker_name = tempfile.mktemp(prefix=".skonfig-", dir='')

    def _init_conf_dirs(self, *args):
        self.conf_dirs = util.resolve_conf_dirs(self.settings.conf_dir, *args)

    def _init_directories(self):
        self.mkdir(self.conf_path)
        self.mkdir(self.global_explorer_out_path)
        self.mkdir(self.object_path)
        self.mkdir(self.bin_path)
        self.mkdir(self.cache_path)
        self.mkdir(self.stdout_base_path)
        self.mkdir(self.stderr_base_path)

    def create_files_dirs(self):
        self._init_directories()
        self._create_conf_path_and_link_conf_dirs()
        self._create_messages()
        self._link_types_for_emulator()
        self._setup_object_marker_file()

    def _setup_object_marker_file(self):
        with open(self.object_marker_file, 'w') as fd:
            fd.write("{}\n".format(self.object_marker_name))

        self.log.trace("Object marker %s saved in %s",
                       self.object_marker_name, self.object_marker_file)

    def _init_cache_dir(self, cache_dir):
        from skonfig.settings import get_cache_dir
        self.cache_path = get_cache_dir()

    def rmdir(self, path):
        """Remove directory on the local side."""
        self.log.trace("Local rmdir: %s", path)
        shutil.rmtree(path)

    def mkdir(self, path):
        """Create directory on the local side."""
        self.log.trace("Local mkdir: %s", path)
        os.makedirs(path, exist_ok=True)

    def run(self, command, env=None, return_output=False, message_prefix=None,
            stdout=None, stderr=None, save_output=True):
        """Run the given command with the given environment.
        Return the output as a string.
        """
        assert isinstance(command, (list, tuple)), (
                "list or tuple argument expected, got: {}".format(command))

        close_stdout_afterwards = False
        close_stderr_afterwards = False
        if save_output:
            if not return_output and stdout is None:
                stdout = util.get_std_fd(self.stdout_base_path, 'local')
                close_stdout_afterwards = True
            if stderr is None:
                stderr = util.get_std_fd(self.stderr_base_path, 'local')
                close_stderr_afterwards = True

        env = env if env is not None else os.environ.copy()
        # Export __target_host, __target_hostname, __target_fqdn
        # for use in __remote_{copy,exec} scripts
        env['__target_host'] = self.target_host[0]
        env['__target_hostname'] = self.target_host[1]
        env['__target_fqdn'] = self.target_host[2]

        # Export for emulator
        env['__cdist_object_marker'] = self.object_marker_name

        if message_prefix:
            message = skonfig.message.Message(
                message_prefix, self.messages_path)
            env.update(message.env)

        self.log.trace("Local run: %s", shquot.join(command))
        try:
            if return_output:
                result = subprocess.check_output(
                    command, env=env, stderr=stderr).decode()
            else:
                subprocess.check_call(
                    command, env=env, stdout=stdout, stderr=stderr)
                result = None

            util.log_std_fd(self.log, command, stderr, 'Local stderr')
            util.log_std_fd(self.log, command, stdout, 'Local stdout')

            return result
        except subprocess.CalledProcessError as e:
            raise skonfig.Error("%s: %d" % (" ".join(e.cmd), e.returncode))
        except OSError as e:
            raise skonfig.Error("%s: %d" % (" ".join(command), e.errno))
        finally:
            if message_prefix:
                message.merge_messages()
            if close_stdout_afterwards:
                if isinstance(stdout, int):
                    os.close(stdout)
                else:
                    stdout.close()
            if close_stderr_afterwards:
                if isinstance(stderr, int):
                    os.close(stderr)
                else:
                    stderr.close()

    def run_script(self, script, env=None, return_output=False,
                   message_prefix=None, stdout=None, stderr=None):
        """Run the given script with the given environment.
        Return the output as a string.

        """
        if os.access(script, os.X_OK):
            self.log.debug('%s is executable, running it', script)
            command = [os.path.realpath(script)]
        else:
            command = [self.settings.local_shell, "-e"]
            self.log.debug('%s is NOT executable, running it with %s',
                           script, " ".join(command))
            command.append(script)

        return self.run(command, env=env, return_output=return_output,
                        message_prefix=message_prefix, stdout=stdout,
                        stderr=stderr)

    def _cache_subpath_repl(self, matchobj):
        if matchobj.group(2) == '%P':
            repl = str(os.getpid())
        elif matchobj.group(2) == '%h':
            repl = self.hostdir
        elif matchobj.group(2) == '%N':
            repl = self.target_host[0]

        return matchobj.group(1) + repl

    def _cache_subpath(self, start_time=time.time(), path_format=None):
        if path_format:
            repl_func = self._cache_subpath_repl
            cache_subpath = re.sub(r'([^%]|^)(%h|%P|%N)', repl_func,
                                   path_format)
            dt = datetime.datetime.fromtimestamp(start_time)
            cache_subpath = dt.strftime(cache_subpath)
        else:
            cache_subpath = self.hostdir

        i = 0
        while i < len(cache_subpath) and cache_subpath[i] == os.sep:
            i += 1
        cache_subpath = cache_subpath[i:]
        if not cache_subpath:
            cache_subpath = self.hostdir
        return cache_subpath

    def save_cache(self, start_time=time.time()):
        self.log.trace("cache subpath pattern: %s",
                       self.settings.cache_path_pattern)
        cache_subpath = self._cache_subpath(start_time,
                                            self.settings.cache_path_pattern)
        self.log.debug("cache subpath: %s", cache_subpath)
        destination = os.path.join(self.cache_path, cache_subpath)
        self.log.trace("Saving cache %s to %s", self.base_path, destination)

        if not os.path.exists(destination):
            shutil.move(self.base_path, destination)
        else:
            for direntry in os.listdir(self.base_path):
                srcentry = os.path.join(self.base_path, direntry)
                destentry = os.path.join(destination, direntry)
                try:
                    if os.path.isdir(destentry):
                        shutil.rmtree(destentry)
                    elif os.path.exists(destentry):
                        os.remove(destentry)
                except (PermissionError, OSError) as e:
                    raise skonfig.Error(
                            "Cannot delete old cache entry {}: {}".format(
                                destentry, e))
                shutil.move(srcentry, destentry)

        # add target_host since cache dir can be hash-ed target_host
        host_cache_path = os.path.join(destination, "target_host")
        with open(host_cache_path, 'w') as hostf:
            print(self.target_host[0], file=hostf)

    def _create_messages(self):
        """Create empty messages"""
        with open(self.messages_path, "w"):
            pass

    def _create_conf_path_and_link_conf_dirs(self):
        # Create destination directories
        for sub_dir in CONF_SUBDIRS_LINKED:
            self.mkdir(os.path.join(self.conf_path, sub_dir))

        # Iterate over all directories and link the to the output dir
        for conf_dir in self.conf_dirs:
            self.log.debug("Checking conf_dir %s ...", conf_dir)
            for sub_dir in CONF_SUBDIRS_LINKED:
                current_dir = os.path.join(conf_dir, sub_dir)

                # Allow conf dirs to contain only partial content
                if not os.path.exists(current_dir):
                    continue

                for entry in os.listdir(current_dir):
                    src = os.path.abspath(os.path.join(
                        conf_dir, sub_dir, entry))
                    dst = os.path.join(self.conf_path, sub_dir, entry)

                    # Already exists? remove and link
                    if os.path.exists(dst):
                        os.unlink(dst)

                    self.log.trace("Linking %s to %s ...", src, dst)
                    try:
                        os.symlink(src, dst)
                    except OSError as e:
                        raise skonfig.Error(
                            "Linking {} {} to {} failed: {}".format(
                                sub_dir, src, dst, e.__str__()))

    def _link_types_for_emulator(self):
        """Link emulator to types"""
        src = os.path.abspath(self.exec_path)
        for cdist_type in skonfig.core.CdistType.list_types(self.type_path):
            dst = os.path.join(self.bin_path, cdist_type.name)
            self.log.trace("Linking emulator: %s to %s", src, dst)

            try:
                os.symlink(src, dst)
            except OSError as e:
                raise skonfig.Error(
                        "Linking emulator from {} to {} failed: {}".format(
                            src, dst, e.__str__()))
