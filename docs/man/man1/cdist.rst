=====
cdist
=====

--------------------------
legacy frontend to skonfig
--------------------------

:Manual section: 1
:Manual group: System administration commands

SYNOPSIS
========

::

    cdist [-h] [-V] config ...

    cdist config [-h] [-l LOGLEVEL] [-q] [-v] [--colors WHEN]
                 [-g CONFIG_FILE] [-4] [-6] [-C CACHE_PATH_PATTERN]
                 [-c CONF_DIR] [-i MANIFEST] [-j [JOBS]] [-n] [-o OUT_PATH]
                 [-P] [-R [{tar,tgz,tbz2,txz}]] [-r REMOTE_OUT_PATH]
                 [--remote-copy REMOTE_COPY] [--remote-exec REMOTE_EXEC]
                 [-S] [-f HOSTFILE] [-p [HOST_MAX]] [-s]
                 [host [host ...]]


DESCRIPTION
===========
cdist is the legacy frontend to the skonfig system configuration framework.
It supports different subcommands as explained below.

It is written in Python so it requires :strong:`python3`\ (1) to be installed.


GENERAL
=======
All commands accept the following options:

``-h``, ``--help``
   Show the help screen.

``--colors WHEN``
   Colorize cdist's output. If enabled, skonfig will use different colors for
   different log levels.
   WHEN recognizes the values ``always``, ``never``, and ``auto`` (the default).

   If the value is ``auto``, colored output is enabled if stdout is a TTY
   unless the ``NO_COLOR`` (https://no-color.org/) environment variable is defined.

``-v``, ``--verbose``
   Increase the verbosity level. Every instance of -v
   increments the verbosity level by one. Its default
   value is 0 which includes ERROR and WARNING levels.
   The levels, in order from the lowest to the highest,
   are: ERROR (-1), WARNING (0), INFO (1), VERBOSE (2),
   DEBUG (3), TRACE (4 or higher). If used along with -l
   then -l overwrites last set value and -v increases
   last set value.

``-V``, ``--version``
   Show version and exit.

``-4``, ``--force-ipv4``
   Force to use IPv4 addresses only. No influence for
   custom remote commands.

``-6``, ``--force-ipv6``
   Force to use IPv6 addresses only. No influence for
   custom remote commands.

``-C CACHE_PATH_PATTERN``, ``--cache-path-pattern CACHE_PATH_PATTERN``
   Specify custom cache path pattern. If it is not set then
   default hostdir is used. For more info on format see
   :strong:`CACHE PATH PATTERN FORMAT` below.

``-c CONF_DIR``, ``--conf-dir CONF_DIR``
   Add a configuration directory. Can be specified multiple times.
   If configuration directories contain conflicting types, explorers or
   manifests, then the last one found is used.

``-f HOSTFILE``, ``--file HOSTFILE``
   Read specified file for a list of additional hosts to operate on
   or if '-' is given, read stdin (one host per line). For the file
   format see :strong:`HOSTFILE FORMAT` below.

``-g CONFIG_FILE``, ``--config-file CONFIG_FILE``
   Use specified custom configuration file.

``-i MANIFEST``, ``--initial-manifest MANIFEST``
   Path to a manifest or - to read from stdin.

``-j [JOBS]``, ``--jobs [JOBS]``
   Operate in parallel in specified maximum number of
   jobs. Global explorers, object prepare and object run
   are supported. Without argument CPU count is used by
   default.

``--log-server``
   Start a log server for sub processes to use. This is
   mainly useful when running cdist nested from a code-
   local script.

``-n``, ``--dry-run``
   Do not execute code.

``-o OUT_PATH``, ``--out-dir OUT_PATH``
   Directory to save cdist output in.

``-P``, ``--timestamp``
   Timestamp log messages with the current local date and time
   in the format: YYYYMMDDHHMMSS.us.

``-p [HOST_MAX]``, ``--parallel [HOST_MAX]``
   Operate on multiple hosts in parallel for specified
   maximum hosts at a time. Without argument CPU count is
   used by default.

``-R [{tar,tgz,tbz2,txz}]``, ``--use-archiving [{tar,tgz,tbz2,txz}]``
   Operate by using archiving with compression where
   appropriate. Supported values are: tar - tar archive,
   tgz - gzip tar archive (the default), tbz2 - bzip2 tar
   archive and txz - lzma tar archive.

``-r REMOTE_OUT_PATH``, ``--remote-out-dir REMOTE_OUT_PATH``
   Directory to save cdist output in on the target host.

``-S``, ``--disable-saving-output-streams``
   Disable saving output streams.

``-s``, ``--sequential``
   Operate on multiple hosts sequentially (default).

``--remote-copy REMOTE_COPY``
   Command to use for remote copy (should behave like scp).

``--remote-exec REMOTE_EXEC``
   Command to use for remote execution (should behave like ssh).

HOSTFILE FORMAT
---------------
The HOSTFILE contains one host per line.
A comment is started with '#' and continues to the end of the line.
Any leading and trailing whitespace on a line is ignored.
Empty lines are ignored/skipped.


The Hostfile lines are processed as follows. First, all comments are
removed. Then all leading and trailing whitespace characters are stripped.
If such a line results in empty line it is ignored/skipped. Otherwise,
host string is used.

CACHE PATH PATTERN FORMAT
-------------------------
Cache path pattern specifies path for a cache directory subdirectory.
In the path, ``%N`` will be substituted by the target host, ``%h`` will
be substituted by the calculated host directory, ``%P`` will be substituted
by the current process id. All format codes that
Python's ``datetime.strftime()`` function supports, except
``%h``, are supported. These date/time directives format cdist config/install
start time.

If empty pattern is specified then default calculated host directory is used.

Calculated host directory is a hash of a host cdist operates on.

Resulting path is used to specify cache path subdirectory under which
current host cache data are saved.


CONFIGURATION
=============
cdist obtains configuration data from the following sources in the following
order (from higher to lower precedence):

   #. command-line options
   #. configuration file specified at command-line
   #. configuration file specified in CDIST_CONFIG_FILE environment variable
   #. environment variables
   #. user's configuration file (first one found of ~/.skonfig/config, $XDG_CONFIG_HOME/skonfig/config, in specified order)
   #. system-wide configuration file (/etc/skonfig/config).

CONFIGURATION FILE FORMAT
-------------------------
cdist configuration file is in the INI file format. Currently it supports
only ``[GLOBAL]`` section.
The possible keywords and their meanings are as follows:

:strong:`archiving`
   Use specified archiving. Valid values include:
   'none', 'tar', 'tgz', 'tbz2' and 'txz'.

:strong:`cache_path_pattern`
   Specify cache path pattern.

:strong:`colored_output`
   Colorize cdist's output. cf. the :code:`--colors` option.

:strong:`conf_dir`
   List of configuration directories separated with the character conventionally
   used by the operating system to separate search path components (as in PATH),
   such as ':' for POSIX or ';' for Windows.
   If also specified at command line then values from command line are
   appended to this value.

:strong:`init_manifest`
   Specify default initial manifest.

:strong:`jobs`
   Specify number of jobs for parallel processing. If -1 then the default,
   number of CPU's in the system is used. If 0 then parallel processing in
   jobs is disabled. If set to positive number then specified maximum
   number of processes will be used.

:strong:`local_shell`
   Shell command used for local execution.

:strong:`out_path`
   Directory to save cdist output in.

:strong:`parallel`
   Process hosts in parallel. If -1 then the default, number of CPU's in
   the system is used. If 0 then parallel processing of hosts is disabled.
   If set to positive number then specified maximum number of processes
   will be used.

:strong:`remote_copy`
   Command to use for remote copy (should behave like scp).

:strong:`remote_exec`
   Command to use for remote execution (should behave like ssh).

:strong:`remote_out_path`
   Directory to save cdist output in on the target host.

:strong:`remote_shell`
   Shell command at remote host used for remote execution.

:strong:`save_output_streams`
   Enable/disable saving output streams (enabled by default).
   It recognizes boolean values from 'yes'/'no', 'on'/'off', 'true'/'false'
   and '1'/'0'.

:strong:`timestamp`
   Timestamp log messages with the current local date and time
   in the format: YYYYMMDDHHMMSS.us.

:strong:`verbosity`
   Set verbosity level. Valid values are:
   'ERROR', 'WARNING', 'INFO', 'VERBOSE', 'DEBUG', 'TRACE' and 'OFF'.


FILES
=====
``~/.skonfig``
   Your personal skonfig config directory. If exists it will be
   automatically used.
``/etc/skonfig/config``
   Global skonfig configuration file, if exists.
``~/.skonfig/config`` or ``$XDG_CONFIG_HOME/skonfig/config``
   Local skonfig configuration file, if exists.

NOTES
=====
cdist detects if host is specified by IPv6 address. If so then remote_copy
command is executed with host address enclosed in square brackets
(see :strong:`scp`\ (1)).

EXAMPLES
========

.. code-block:: sh

   # Configure hosts www.example.com
   $ cdist config www.example.com


ENVIRONMENT
===========
``TMPDIR``, ``TEMP``, ``TMP``
   Setup the base directory for the temporary directory.
   See http://docs.python.org/py3k/library/tempfile.html for
   more information. This is rather useful, if the standard
   directory used does not allow executables.

``CDIST_PATH``
   Colon delimited list of config directories.

``CDIST_LOCAL_SHELL``
   Selects shell for local script execution, defaults to /bin/sh.

``CDIST_REMOTE_SHELL``
   Selects shell for remote script execution, defaults to /bin/sh.

``CDIST_OVERRIDE``
   Allow overwriting type parameters.

``CDIST_ORDER_DEPENDENCY``
   Create dependencies based on the execution order.
   Note that in version 6.2.0 semantic of this processing mode is
   finally fixed and well defined.

``CDIST_REMOTE_EXEC``
   Use this command for remote execution (should behave like ssh).

``CDIST_REMOTE_COPY``
   Use this command for remote copy (should behave like scp).

``CDIST_CACHE_PATH_PATTERN``
   Custom cache path pattern.

``CDIST_COLORED_OUTPUT``
   Colorize cdist's output. cf. the :code:`--colors` option.

``CDIST_CONFIG_FILE``
   Custom configuration file.


EXIT STATUS
===========
The following exit values shall be returned:

0   Successful completion.

1   One or more host configurations failed.


AUTHORS
=======
Originally written by Nico Schottelius <nico-cdist--@--schottelius.org>
and Steven Armstrong <steven-cdist--@--armstrong.cc>.


CAVEATS
=======
When operating in parallel, either by operating in parallel for each host
(-p/--parallel) or by parallel jobs within a host (-j/--jobs), and depending
on target SSH server and its configuration you may encounter connection drops.
This is controlled with sshd :strong:`MaxStartups` configuration options.
You may also encounter session open refusal. This happens with ssh multiplexing
when you reach maximum number of open sessions permitted per network
connection. In this case ssh will disable multiplexing.
This limit is controlled with sshd :strong:`MaxSessions` configuration
options. For more details refer to :strong:`sshd_config`\ (5).

When requirements for the same object are defined in different manifests (see
example below), for example, in init manifest and in some other type manifest
and those requirements differ then dependency resolver cannot detect
dependencies correctly. This happens because cdist cannot prepare all objects first
and run all objects afterwards. Some object can depend on the result of type
explorer(s) and explorers are executed during object run. cdist will detect
such case and display a warning message. An example of such a case:

.. code-block:: sh

   init manifest:
      __a a
      require="__e/e" __b b
      require="__f/f" __c c
      __e e
      __f f
      require="__c/c" __d d
      __g g
      __h h

   type __g manifest:
      require="__c/c __d/d" __a a

   Warning message:
      WARNING: cdisttesthost: Object __a/a already exists with requirements:
      /usr/home/darko/ungleich/cdist/cdist/test/config/fixtures/manifest/init-deps-resolver /tmp/tmp.cdist.test.ozagkg54/local/759547ff4356de6e3d9e08522b0d0807/data/conf/type/__g/manifest: set()
      /tmp/tmp.cdist.test.ozagkg54/local/759547ff4356de6e3d9e08522b0d0807/data/conf/type/__g/manifest: {'__c/c', '__d/d'}
      Dependency resolver could not handle dependencies as expected.


COPYING
=======
Copyright \(C) 2011-2020 Nico Schottelius.
You can redistribute it and/or modify it under the terms of the GNU General
Public License as published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.
