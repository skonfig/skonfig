How to upgrade cdist
====================

Update the git installation
---------------------------

To upgrade cdist in the current branch use

.. code-block:: sh

    git pull

    # Also update the manpages
    make man
    export MANPATH=$MANPATH:$(pwd -P)/doc/man

If you stay on a version branch (i.e. 1.0, 1.1., ...), nothing should break.
The master branch on the other hand is the development branch and may not be
working, break your setup or eat the tree in your garden.

Safely upgrading to new versions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To upgrade to **any** further cdist version, you can take the
following procedure to do a safe upgrade:

.. code-block:: sh

    # Create new branch to try out the update
    git checkout -b upgrade_cdist

    # Get latest cdist version in git database
    git fetch -v

    # see what will happen on merge - replace
    # master with the branch you plan to merge
    git diff upgrade_cdist..origin/master

    # Merge the new version
    git merge origin/master

Now you can ensure all custom types work with the new version.
Assume that you need to go back to an older version during
the migration/update, you can do so as follows:

.. code-block:: sh

    # commit changes
    git commit -m ...

    # go back to original branch
    git checkout master

After that, you can go back and continue the upgrade:

.. code-block:: sh

    # git checkout upgrade_cdist


Update the python package
-------------------------

To upgrade to the latest version do

.. code-block:: sh

    pip install --upgrade cdist
