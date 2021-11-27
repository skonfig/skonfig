# -*- coding: utf-8 -*-
#
# 2019-2020 Steven Armstrong
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

import asyncio
import contextlib
import logging
import pickle
import os
import threading


async def handle_log_client(reader, writer):
    while True:
        chunk = await reader.read(4)
        if len(chunk) < 4:
            return

        data_size = struct.unpack('>L', chunk)[0]
        data = await reader.read(data_size)

        obj = pickle.loads(data)
        record = logging.makeLogRecord(obj)
        logger = logging.getLogger(record.name)
        logger.handle(record)


def run_log_server(server_address):
    # Get a new loop inside the current thread to run the log server.
    loop = asyncio.new_event_loop()
    loop.create_task(asyncio.start_unix_server(handle_log_client,
                                               server_address))
    loop.run_forever()


def setupLogServer(socket_dir, log=logging.getLogger(__name__)):
    """Run a asyncio based unix socket log server in a background thread.
    """
    log_server_socket = os.path.join(socket_dir, 'log-server')
    log.debug('Starting logging server on: %s', log_server_socket)
    os.environ['__cdist_log_server_socket_export'] = log_server_socket
    with contextlib.suppress(FileNotFoundError):
        os.remove(log_server_socket)
    t = threading.Thread(target=run_log_server, args=(log_server_socket,))
    # Deamonizing the thread means we don't have to care about stoping it.
    # It will die together with the main process.
    t.daemon = True
    t.start()
