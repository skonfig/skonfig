import argparse
import logging


_logger = logging.getLogger(__name__)


def _set_logging_level(argument_level):
    levels_pre_py34 = getattr(logging, "_levelNames", {})
    levels_available = getattr(logging, "_levelToName", levels_pre_py34)
    levels_used = []
    for level, level_name in levels_available.items():
        if not isinstance(level, int):
            continue
        if level > logging.getLevelName("INFO"):
            continue
        if level_name == "NOTSET":
            continue
        levels_used.append(level)
    levels = list(reversed(sorted(levels_used)))
    level = levels[min(argument_level, len(levels)-1)]
    logging.basicConfig(level=level)


def get():
    parser = argparse.ArgumentParser(
        usage="skonfig [-hVdjnv] [host] [</path/to/manifest]"
    )
    parser.add_argument(
        "-V",
        dest="version",
        action="store_true",
        help="print version"
    )
    parser.add_argument(
        "-d",
        dest="dump",
        action="store_true",
        help="print dumped hosts, -d <host> = print dump",
    )
    parser.add_argument(
        "-j",
        dest="jobs",
        metavar="jobs",
        help="maximum number of jobs (defaults to host CPU count)"
    )
    parser.add_argument(
        "-n",
        dest="dry_run",
        action="store_true",
        help="dry-run, do not execute generated code",
    )
    parser.add_argument(
        "-v",
        dest="verbose",
        action="count",
        default=0,
        help="-v = VERBOSE, -vv = DEBUG, -vvv = TRACE",
    )
    parser.add_argument("host", nargs="?", help="host to configure")
    arguments = parser.parse_args()
    _set_logging_level(arguments.verbose)
    for argument, value in vars(arguments).items():
        _logger.debug("%s: %s", argument, value)
    return parser, arguments
