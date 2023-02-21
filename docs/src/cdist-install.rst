How to install cdist
====================

Requirements
-------------

Source Host
~~~~~~~~~~~

This is the machine from which you will configure target hosts.

 * ``/bin/sh``: A POSIX like shell (for instance bash, dash, zsh)
 * Python >= 3.2
 * SSH client
 * sphinx with the rtd theme (for building html docs and/or the man pages)

Target Hosts
~~~~~~~~~~~~

 * ``/bin/sh``: A POSIX like shell (for instance bash, dash, zsh)
 * SSH server

Install cdist
-------------

From git
~~~~~~~~

Cloning cdist from git gives you the advantage of having
a version control in place for development of your own stuff
immediately.

To install cdist, execute the following commands:

.. code-block:: sh

   git clone https://github.com/skonfig/skonfig.git
   cd skonfig
   export PATH=$PATH:$(pwd -P)/bin

Then install skonfig using:

.. code-block:: sh

   make install

or:

.. code-block:: sh

   make install-user

to install it into user *site-packages* directory.

Or directly with pip:

.. code-block:: sh

   pip install .


Available versions in git
^^^^^^^^^^^^^^^^^^^^^^^^^

 * The active development takes place in the **main** branch
 * The released versions can be found in the tags

Other branches may be available for features or bugfixes, but they
may vanish at any point. To select a specific branch use

.. code-block:: sh

   # generic code
   git checkout -b <localbranchname> origin/<branchname>

So for instance if you want to use and stay with version 4.1, you can use

.. code-block:: sh

    git checkout -b 4.1 origin/4.1

Building and using documentation (man and html)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to build and use the documentation, run:

.. code-block:: sh

   make docs

Documentation comes in two formats, man pages and full HTML
documentation. Documentation is built into distribution's
docs/dist directory. man pages are in docs/dist/man and
HTML documentation in docs/dist/html.

If you want to use man pages, run:

.. code-block:: sh

   export MANPATH=$MANPATH:$(pwd -P)/docs/dist/man

Or you can move man pages from docs/dist/man directory to some
other directory and add it to MANPATH.

Full HTML documentation can be accessed at docs/dist/html/index.html.

You can also build only man pages or only html documentation, for
only man pages run:

.. code-block:: sh

   make man

for only html documentation run:

.. code-block:: sh

   make html
