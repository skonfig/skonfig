================
skonfig-new-type
================

----------------------------------
create a new skonfig type skeleton
----------------------------------

:Manual section: 1
:Manual group: System administration commands


SYNOPSIS
========

::

   skonfig-new-type TYPE-NAME AUTHOR-NAME AUTHOR-EMAIL [TYPE-BASE-PATH]


DESCRIPTION
===========
skonfig-new-type is a helper script that creates a new skonfig type skeleton.
It is then up to the type author to finish the type.

It creates skeletons for the following files:

* ``man.rst``,
* ``manifest``
* ``gencode-remote``.

Upon creation it prints the path to the newly created type directory.


ARGUMENTS
=========
**TYPE-NAME**
   Name of the new type.

**AUTHOR-NAME**
   Type author's full name.

**AUTHOR-NAME**
   Type author's email.

**TYPE-BASE-PATH**
   Path to the base directory of the type. If not set it defaults
   to ``$PWD/type``.


EXAMPLES
========

.. code-block:: sh

   # Create new type __foo in ~/.skonfig directory.
   $ cd ~/.skonfig
   $ skonfig-new-type '__foo' 'Foo Bar' 'foo.bar@example.org'
   /home/foo/.skonfig/type/__foo


SEE ALSO
========
:strong:`skonfig`\ (1)


AUTHORS
=======
| Dennis Camera <skonfig--@--dtnr.ch>


COPYING
=======
Copyright \(C) 2022 Dennis Camera.
You can redistribute it and/or modify it under the terms of the GNU General
Public License as published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.
