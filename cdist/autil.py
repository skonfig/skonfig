# -*- coding: utf-8 -*-
#
# 2017 Darko Poljak (darko.poljak at gmail.com)
# 2023 Dennis Camera (dennis.camera at riiengineering.ch)
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

import glob
import os
import tarfile
import tempfile


class ArchivingMode:
    @classmethod
    def is_supported(cls):
        if cls.tarmode:
            return cls.tarmode in tarfile.TarFile.OPEN_METH
        else:
            # plain tar is always supported
            return True

    @classmethod
    def name(cls):
        return cls.__name__.lower()

    @classmethod
    def doc(cls):
        return cls.__doc__


class TAR(ArchivingMode):
    "tar archive"
    tarmode = ""
    file_ext = ".tar"
    extract_opts = []


class TGZ(ArchivingMode):
    "gzip tar archive"
    tarmode = "gz"
    file_ext = ".tar.gz"
    extract_opts = ["-z"]


class TBZ2(ArchivingMode):
    "bzip2 tar archive"
    tarmode = "bz2"
    file_ext = ".tar.bz2"
    extract_opts = ["-j"]


class TXZ(ArchivingMode):
    "lzma tar archive"
    tarmode = "xz"
    file_ext = ".tar.xz"
    extract_opts = ["-J"]


archiving_modes = [TAR, TGZ, TBZ2, TXZ]

# for CLI or config
archiving_values = dict(
    none="no archiving",
    **{m.name(): m.doc() for m in archiving_modes})


def mode_from_str(s):
    s_lc = s.lower()

    if s_lc == "none":
        # special case to disable the archiving feature
        return None

    for mode in archiving_modes:
        if (mode.name() == s_lc):
            break
    else:
        raise ValueError("invalid archiving mode: %s" % s)

    # check if the method is supported by this python version
    if not mode.is_supported():
        raise RuntimeError(
            "the archiving mode '%s' is not supported by this version of "
            "Python" % (mode.name()))

    return mode


# Archiving will be enabled if directory contains more than FILES_LIMIT files.
FILES_LIMIT = 1


def tar(source, mode=TGZ):
    files = glob.glob1(source, '*')
    fcnt = len(files)
    if fcnt <= FILES_LIMIT:
        return None, fcnt

    tarmode = "w:%s" % mode.tarmode
    _, tarpath = tempfile.mkstemp(suffix=mode.file_ext)
    with tarfile.open(tarpath, tarmode, dereference=True) as tar:
        if os.path.isdir(source):
            for f in files:
                tar.add(os.path.join(source, f), arcname=f)
        else:
            tar.add(source)
    return tarpath, fcnt
