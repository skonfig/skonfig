# -*- coding: utf-8 -*-
#
# 2016-2017 Darko Poljak (darko.poljak at gmail.com)
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

import concurrent.futures as cf
import itertools
import logging
import multiprocessing
import os
import signal

import cdist.log

log = logging.getLogger("cdist-mputil")


def mp_sig_handler(signum, frame):
    log.trace("signal %s, SIGKILL whole process group", signum)
    os.killpg(os.getpgrp(), signal.SIGKILL)


def _mp_run_method(self, fname, *args, **kwargs):
    return getattr(self, fname)(*args, **kwargs)


def mp_pool_run(func, args=None, kwds=None, jobs=multiprocessing.cpu_count()):
    """Run func using concurrent.futures.ProcessPoolExecutor with jobs jobs
       and supplied iterables of args and kwds with one entry for each
       parallel func instance.
       Return list of results.
    """
    if args and kwds:
        fargs = zip(args, kwds)
    elif args:
        fargs = zip(args, itertools.repeat({}))
    elif kwds:
        fargs = zip(itertools.repeat(()), kwds)
    else:
        return [func(), ]

    if hasattr(func, "__self__"):
        # Special case that wraps bound methods for pickling on Python < 3.3
        fself = func.__self__
        fname = func.__func__.__name__

        func = _mp_run_method
        fargs = (((fself, fname) + a, k) for (a, k) in fargs)

    with cf.ProcessPoolExecutor(jobs) as executor:
        try:
            return [
                f.result()
                for f in cf.as_completed(
                    [executor.submit(func, *a, **k)
                     for a, k in fargs])
                ]
        except KeyboardInterrupt:
            mp_sig_handler(signal.SIGINT, None)
            raise
