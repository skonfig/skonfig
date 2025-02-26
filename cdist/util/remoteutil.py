# -*- coding: utf-8 -*-
#
# 2016 Darko Poljak (darko.poljak at gmail.com)
# 2025 Dennis Camera (dennis.camera at riiengineering.ch)
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

from cdist.util import shquot


def inspect_ssh_mux_opts():
    """Inspect whether or not ssh supports multiplexing options.

    Return string containing multiplexing options if supported.
    If ControlPath is supported then placeholder for that path is
    specified and can be used for final string formatting.
    For example, this function can return string:
    "-o ControlMaster=auto -o ControlPersist=125 -o ControlPath={}".
    Then it can be formatted:
    mux_opts_string.format('/tmp/tmpxxxxxx/ssh-control-path').
    """
    import subprocess

    mux_opts = {
        "ControlPath": "{}",
        "ControlMaster": "auto",
        "ControlPersist": "2h",
    }

    mux_opts_str = \
        " ".join("-o %s=%s" % (k, v) for (k, v) in mux_opts.items())
    try:
        # check if SSH connections with mux options work
        subprocess.check_output(
            (["ssh"] + shquot.split(mux_opts_str)),
            stderr=subprocess.STDOUT,
            shell=False)
    except subprocess.CalledProcessError as e:
        subproc_output = e.output.decode().lower()
        if "bad configuration option" in subproc_output:
            return ""

    return mux_opts_str
