Messaging
=========

Description
-----------
cdist has a simple but powerful way of allowing communication between
the initial manifest and types as well as types and types.

Whenever execution is passed from cdist to one of the
scripts described below, cdist generate 2 new temporary files
and exports the environment variables **__messages_in** and
**__messages_out** to point to them.

Before handing over the control, the content of the global message
file is copied into the file referenced by **$__messages_in**.

After cdist gained control back, the content of the file referenced
by **$__messages_out** is appended to the global message file.

This way overwriting any of the two files by accident does not
interfere with other types.

The order of execution is not defined unless you create dependencies
between the different objects (see `manifest <cdist-manifest.html>`_) and thus you
can only react reliably on messages by objects that you depend on.


Availability
------------
Messaging is possible between all **local** scripts:

- initial manifest
- type/manifest
- type/gencode-local
- type/gencode-remote


Examples
--------
When you want to emit a message use:

.. code-block:: sh

    echo "something" >> "$__messages_out"

When you want to react on a message use:

.. code-block:: sh

    if grep -q "^__your_type/object/id:something" "$__messages_in"; then
        echo "I do something else"
    fi

Some real life examples:

.. code-block:: sh

    # Reacting on changes from block for keepalive
    if grep -q "^__block/keepalive-vrrp" "$__messages_in"; then
        echo /etc/init.d/keepalived restart
    fi

    # Reacting on changes of configuration files
    if grep -q "^__file/etc/one" $__messages_in; then
        echo 'for init in /etc/init.d/opennebula*; do $init restart; done'
    fi

Restart sshd on changes

.. code-block:: sh

    os="$(cat "$__global/explorer/os")"

    case "$os" in
        centos|redhat|suse)
            restart="/etc/init.d/sshd restart"
        ;;
        debian|ubuntu)
            restart="/etc/init.d/ssh restart"
        ;;
        *)
            cat << eof >&2
    Unsupported os $os.
    If you would like to have this type running on $os,
    you can either develop the changes and send a pull
    request or ask for a quote at www.ungleich.ch
    eof
            exit 1
        ;;
    esac

    if grep -q "^__key_value/PermitRootLogin" "$__messages_in"; then
        echo $restart
    fi
