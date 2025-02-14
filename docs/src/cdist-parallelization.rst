Parallelization
===============

Description
-----------
skonfig can operate in parallel within one host where you specify
the number of jobs. This is enabled with :strong:`-j/--jobs` option where you
can specify the number of parallel jobs. By default,
:strong:`multiprocessing.cpu_count()` (capped to 4) is used. For this mode global explorers,
object preparation and object run are supported.

You can, of course, use those two options together. This means that each host
will be processed by its own process. Within each process cdist will operate
using specified number of parallel jobs.

For more info on this option see :strong:`skonfig`\ (1).


Caveats
-------
When operating in parallel and depending on target SSH server and its
configuration you may encounter connection drops.
This is controlled with sshd :strong:MaxStartups configuration options.
You may also encounter session open refusal. This happens with ssh multiplexing
when you reach maximum number of open sessions permitted per network
connection. In this case ssh will disable multiplexing.
This limit is controlled with sshd :strong:MaxSessions configuration
options. For more details refer to :strong:`sshd_config`\ (5).

For example, if you reach :strong:`MaxSessions` sessions you may get the
following output:

.. code-block:: sh

    $ cdist config -b -j 11 -v 78.47.116.244
    INFO: cdist: version 4.2.2-55-g640b7f9
    INFO: 78.47.116.244: Running global explorers
    INFO: 78.47.116.244: Remote transfer in 11 parallel jobs
    channel 22: open failed: administratively prohibited: open failed
    mux_client_request_session: session request failed: Session open refused by peer
    ControlSocket /tmp/tmpuah6fw_t/d886d4b7e4425a102a54bfaff4d2288b/ssh-control-path already exists, disabling multiplexing
    INFO: 78.47.116.244: Running global explorers in 11 parallel jobs
    channel 22: open failed: administratively prohibited: open failed
    mux_client_request_session: session request failed: Session open refused by peer
    ControlSocket /tmp/tmpuah6fw_t/d886d4b7e4425a102a54bfaff4d2288b/ssh-control-path already exists, disabling multiplexing
    INFO: 78.47.116.244: Running initial manifest /tmp/tmpuah6fw_t/d886d4b7e4425a102a54bfaff4d2288b/data/conf/manifest/init
    INFO: 78.47.116.244: Running manifest and explorers for __file/root/host.file
    INFO: 78.47.116.244: Generating code for __file/root/host.file
    INFO: 78.47.116.244: Finished successful run in 18.655028820037842 seconds
    INFO: cdist: Total processing time for 1 host(s): 19.159148693084717
