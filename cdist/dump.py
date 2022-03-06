import os

import cdist


class Dump:
    @classmethod
    def commandline(cls, args):
        cls(args)

    def _read_file(self, file_path):
        if not os.path.isfile(file_path):
            return None
        with open(file_path) as handle:
            return handle.read().rstrip()
        return None

    def _get_dump_files(self, host_cache_dir):
        dump_files = []
        for cache_entry in [
            "typeorder",
            "explorer",
            "object",
            "stdout",
            "stderr",
            "messages",
        ]:
            cache_entry_path = os.path.join(host_cache_dir, cache_entry)
            if os.path.isfile(cache_entry_path):
                dump_files.append(cache_entry_path)
            elif os.path.isdir(cache_entry_path):
                for root, _, files in os.walk(cache_entry_path):
                    for file in files:
                        dump_files.append(os.path.join(root, file))
        return dump_files

    def _get_dump(self, host_cache_dir):
        dump = {}
        dump_files = self._get_dump_files(host_cache_dir)
        for dump_file in dump_files:
            dump[dump_file] = self._read_file(dump_file)
        return dump

    def _print_dump(self, host, cache_suffix, host_cache_dir):
        dump = self._get_dump(host_cache_dir)
        for dump_file, dump_file_content in dump.items():
            dump_file_suffix = dump_file[len(host_cache_dir)+1:]
            for line in dump_file_content.split("\n"):
                if host == cache_suffix:
                    print("{}: {}: {}".format(
                        host, dump_file_suffix, line))
                else:
                    print("{}: {}/{}: {}".format(
                        host, cache_suffix, dump_file_suffix, line))

    def _get_hosts(self, cache_dir):
        hosts = {}
        for root, _, files in os.walk(cache_dir):
            if "target_host" not in files:
                continue
            host = self._read_file(os.path.join(root, "target_host"))
            if host not in hosts.keys():
                hosts[host] = []
            hosts[host].append(root)
        return sorted(hosts.items())

    def __init__(self, args):
        cache_dir = "{}/cache/".format(cdist.home_dir())
        hosts = self._get_hosts(cache_dir)
        for host, host_cache_dirs in hosts:
            for host_cache_dir in host_cache_dirs:
                cache_suffix = host_cache_dir[len(cache_dir):]
                if args.host:
                    if host not in args.host:
                        continue
                    self._print_dump(host, cache_suffix, host_cache_dir)
                else:
                    if host == cache_suffix:
                        print(host)
                    else:
                        print("{}: {}".format(host, cache_suffix))
