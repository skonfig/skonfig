=======
skonfig
=======

:Manual section: 1
:Manual group: System administration commands

SYNOPSIS
========

::

    usage: skonfig [-h] [-V] [-d] [-i path] [-n] [-v] [host]

    positional arguments:
      host        host to configure

    options:
      -h, --help  show this help message and exit
      -V          print version
      -d          print dumped hosts, -d <host> = print dump
      -i path     initial manifest or '-' to read from stdin
      -j jobs     maximum number of jobs (defaults to host CPU count)
      -n          dry-run, do not execute generated code
      -v          -v = VERBOSE, -vv = DEBUG, -vvv = TRACE


COPYING
=======
Copyright \(C) 2022 skonfig
You can redistribute it and/or modify it under the terms of the GNU General
Public License as published by the Free Software Foundation, either version 3
of the License, or (at your option) any later version.
