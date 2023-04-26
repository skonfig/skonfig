# -*- coding: utf-8 -*-
#
# 2011-2017 Steven Armstrong (steven-cdist at armstrong.cc)
# 2011-2013 Nico Schottelius (nico-cdist at schottelius.org)
# 2022,2023 Dennis Camera (dennis.camera at riiengineering.ch)
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

import glob
import logging
import os
import subprocess

import cdist

from cdist.exec import util
from cdist.util import (ipaddr, shquot)


def _wrap_addr(addr):
    """If addr is IPv6 then return addr wrapped between '[' and ']',
    otherwise return it unchanged."""
    if ipaddr.is_ipv6(addr):
        return "".join(("[", addr, "]", ))
    else:
        return addr


class DecodeError(cdist.Error):
    def __init__(self, command):
        self.command = command

    def __str__(self):
        return "Cannot decode output of " + " ".join(self.command)


class Remote:
    """Execute commands remotely.

    All interaction with the target should be done through this class.
    Directly accessing the target from Python code is a bug!

    """
    def __init__(self,
                 target_host,
                 remote_exec,
                 remote_copy,
                 base_path="/var/lib/skonfig",
                 quiet_mode=None,
                 archiving_mode=None,
                 configuration={},
                 stdout_base_path=None,
                 stderr_base_path=None,
                 save_output_streams=True):
        self.target_host = target_host
        self._exec = remote_exec
        self._copy = remote_copy

        self.base_path = base_path
        self.quiet_mode = quiet_mode
        self.archiving_mode = archiving_mode
        self.configuration = configuration
        self.save_output_streams = save_output_streams

        self.stdout_base_path = stdout_base_path
        self.stderr_base_path = stderr_base_path

        self.conf_path = os.path.join(self.base_path, "conf")
        self.object_path = os.path.join(self.base_path, "object")

        self.type_path = os.path.join(self.conf_path, "type")
        self.global_explorer_path = os.path.join(self.conf_path, "explorer")

        self._open_logger()

        self._init_env()

    def _open_logger(self):
        self.log = logging.getLogger(self.target_host[0])

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

    def _init_env(self):
        """Setup environment for scripts."""
        # FIXME: better do so in exec functions that require it!
        os.environ['__remote_copy'] = self._copy
        os.environ['__remote_exec'] = self._exec

    def create_files_dirs(self):
        self.rmdir(self.base_path)
        self.mkdir(self.base_path)
        self.run(["chmod", "0700", self.base_path])
        self.mkdir(self.conf_path)

    def remove_files_dirs(self):
        self.rmdir(self.base_path)

    def rmfile(self, path):
        """Remove file on the target."""
        self.log.trace("Remote rm: %s", path)
        self.run(["rm", "-f",  path])

    def rmdir(self, path):
        """Remove directory on the target."""
        self.log.trace("Remote rmdir: %s", path)
        self.run(["rm", "-rf",  path])

    def mkdir(self, path):
        """Create directory on the target."""
        self.log.trace("Remote mkdir: %s", path)
        self.run(["mkdir", "-p", path])

    def extract_archive(self, path, mode):
        """Extract archive path on the target."""
        import cdist.autil as autil

        self.log.trace("Remote extract archive: %s", path)
        command = [
            "tar",
            "-C", os.path.dirname(path),
            "-x",
            "-f", path
        ]
        if mode is not None:
            command += mode.extract_opts
        self.run(command)

    def _transfer_file(self, source, destination):
        command = shquot.split(self._copy) + [
            source,
            "%s:%s" % (_wrap_addr(self.target_host[0]), destination)
        ]
        self._run_command(command)

    def transfer(self, source, destination, jobs=None):
        """Transfer a file or directory to the target."""
        self.log.trace("Remote transfer: %s -> %s", source, destination)
        # self.rmdir(destination)
        if os.path.isdir(source):
            self.mkdir(destination)
            used_archiving = False
            if self.archiving_mode is not None:
                self.log.trace("Remote transfer in archiving mode")
                import cdist.autil as autil

                # create archive
                tarpath, fcnt = autil.tar(source, self.archiving_mode)
                if tarpath is None:
                    self.log.trace("Files count %d is lower than %d limit, "
                                   "skipping archiving",
                                   fcnt, autil.FILES_LIMIT)
                else:
                    self.log.trace("Archiving mode, tarpath: %s, file count: "
                                   "%s", tarpath, fcnt)
                    # get archive name
                    tarname = os.path.basename(tarpath)
                    self.log.trace("Archiving mode tarname: %s", tarname)
                    # archive path at the remote
                    desttarpath = os.path.join(destination, tarname)
                    self.log.trace("Archiving mode desttarpath: %s",
                                   desttarpath)
                    # transfer archive to the target
                    self.log.trace("Archiving mode: transferring")
                    self._transfer_file(tarpath, desttarpath)
                    # extract archive on the target
                    self.log.trace("Archiving mode: extracting")
                    self.extract_archive(desttarpath, self.archiving_mode)
                    # remove remote archive
                    self.log.trace("Archiving mode: removing remote archive")
                    self.rmfile(desttarpath)
                    # remove local archive
                    self.log.trace("Archiving mode: removing local archive")
                    os.remove(tarpath)
                    used_archiving = True
            if not used_archiving:
                self._transfer_dir(source, destination)
        elif jobs:
            raise cdist.Error("Source {} is not a directory".format(source))
        else:
            self._transfer_file(source, destination)

    def _transfer_dir(self, source, destination):
        sources = [os.path.join(source, f) for f in glob.glob1(source, "*")]
        if not sources:
            return
        command = shquot.split(self._copy) + sources
        command.append("%s:%s" % (
            _wrap_addr(self.target_host[0]), destination))

        self._run_command(command)

    def run_script(self, script, env=None, return_output=False, stdout=None,
                   stderr=None):
        """Run the given script with the given environment on the target.
        Return the output as a string.

        """

        command = [
            "exec",
            self.configuration.get('remote_shell', "/bin/sh"),
            "-e",
            script
        ]

        return self.run(command, env=env, return_output=return_output,
                        stdout=stdout, stderr=stderr)

    def run(self, command, env=None, return_output=False,
            stdout=None, stderr=None):
        """Run the given command with the given environment on the target.
        Return the output as a string.

        If command is a list, each item of the list will be quoted if needed.
        If you need some part not to be quoted (e.g. the component is a glob),
        pass command as a str instead.
        """

        # prefix given command with remote_exec
        cmd = shquot.split(self._exec) + [self.target_host[0]]

        if isinstance(command, (list, tuple)):
            command = shquot.join(command)

        # environment variables can't be passed to the target,
        # so prepend command with variable declarations

        # cdist command prepended with variable assignments expects
        # POSIX shell (bourne, bash) at the remote as user default shell.
        # If remote user shell isn't POSIX shell, but for e.g. csh/tcsh
        # then these var assignments are not var assignments for this
        # remote shell, it tries to execute it as a command and fails.
        # So really do this by default:
        # /bin/sh -c 'export <var assignments>; command'
        # so that constructed remote command isn't dependent on remote
        # shell. Do this only if env is not None. env breaks this.
        # Explicitly use /bin/sh, because var assignments assume POSIX
        # shell already.
        # This leaves the posibility to write script that needs to be run
        # remotely in e.g. csh and setting up CDIST_REMOTE_SHELL to e.g.
        # /bin/csh will execute this script in the right way.
        if env:
            remote_env = "export " + (" ".join(
                "%s=%s" % (
                    name, shquot.quote(value) if value else "")
                for (name, value) in env.items())) + "; "
        else:
            remote_env = ""

        cmd.append("exec /bin/sh -c " + shquot.quote(remote_env + command))

        return self._run_command(cmd, return_output=return_output,
                                 stdout=stdout, stderr=stderr)

    def _run_command(self, command, return_output=False,
                     stdout=None, stderr=None):
        """Run the given command locally and return the output as a string"""

        assert isinstance(command, (list, tuple)), (
                "list or tuple argument expected, got: {}".format(command))

        close_stdout = False
        close_stderr = False
        if self.save_output_streams:
            if not return_output and stdout is None:
                stdout = util.get_std_fd(self.stdout_base_path, 'remote')
                close_stdout = True
            if stderr is None:
                stderr = util.get_std_fd(self.stderr_base_path, 'remote')
                close_stderr = True

        # export target_host, target_hostname, target_fqdn
        # for use in __remote_{exec,copy} scripts
        os_environ = os.environ.copy()
        os_environ['__target_host'] = self.target_host[0]
        os_environ['__target_hostname'] = self.target_host[1]
        os_environ['__target_fqdn'] = self.target_host[2]

        self.log.trace("Remote run: %s", command)
        special_devnull = False
        try:
            if self.quiet_mode:
                stderr, close_stderr = util._get_devnull()
                special_devnull = not close_stderr
            if return_output:
                output = subprocess.check_output(command, env=os_environ,
                                                 stderr=stderr).decode()
            else:
                subprocess.check_call(command, env=os_environ, stdout=stdout,
                                      stderr=stderr)
                output = None

            if self.save_output_streams:
                if not special_devnull:
                    util.log_std_fd(self.log, command, stderr, 'Remote stderr')
                util.log_std_fd(self.log, command, stdout, 'Remote stdout')

            return output
        except (OSError, subprocess.CalledProcessError) as error:
            emsg = ""
            if not isinstance(command, (str, bytes)):
                emsg += shquot.join(command)
            else:
                emsg += command
            if error.args:
                emsg += ": " + str(error.args[1])
            raise cdist.Error(emsg)
        except UnicodeDecodeError:
            raise DecodeError(command)
        finally:
            if close_stdout:
                stdout.close()
            if close_stderr:
                if isinstance(stderr, int):
                    os.close(stderr)
                else:
                    stderr.close()
