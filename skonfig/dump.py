# -*- coding: utf-8 -*-
#
# 2022 Ander Punnar (ander at kvlt.ee)
# 2022,2025 Dennis Camera (dennis.camera at riiengineering.ch)
#
# This file is part of skonfig.
#
# skonfig is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# skonfig is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with skonfig. If not, see <http://www.gnu.org/licenses/>.
#

import os


def run(host):
    dumps = _get_dumps()
    if not host:
        _print_dumped_hosts(dumps)
    elif host in dumps:
        _print_dump(dumps[host])


def _get_dumps():
    dumps = {}
    from skonfig.settings import get_cache_dir
    dumps_directory = get_cache_dir()
    if not os.path.isdir(dumps_directory):
        return dumps
    for dump_basename in os.listdir(dumps_directory):
        dump_directory = os.path.join(dumps_directory, dump_basename)
        if not os.path.isdir(dump_directory):
            continue
        target_host_file = os.path.join(dump_directory, "target_host")
        if not os.path.isfile(target_host_file):
            continue
        target_host = _read_file(target_host_file)
        if target_host != dump_basename:
            continue
        dumps[target_host] = dump_directory
    return dumps


def _read_file(file_path):
    if not os.path.isfile(file_path):
        return None
    with open(file_path) as handle:
        return handle.read().rstrip()
    return None


def _print_dumped_hosts(dumps):
    for host in sorted(dumps):
        print(host)


def _print_dump(dump_directory):
    for dump_file in _get_dump_files(dump_directory):
        line_prefix = dump_file[(len(dump_directory) + 1):]
        dump_file_content = _read_file(os.path.join(dump_directory, dump_file))
        if not dump_file_content:
            continue
        for line in dump_file_content.split("\n"):
            print("{}: {}".format(line_prefix, line))


def _get_dump_files(dump_directory):
    dump_files = []
    for dump_entry_basename in [
        "typeorder",
        "explorer",
        "object",
        "stdout",
        "stderr",
        "messages",
    ]:
        dump_entry = os.path.join(dump_directory, dump_entry_basename)
        if os.path.isfile(dump_entry):
            dump_files.append(dump_entry)
        elif os.path.isdir(dump_entry):
            for root, _, files in os.walk(dump_entry):
                for file in sorted(files):
                    dump_files.append(os.path.join(root, file))
    return dump_files
