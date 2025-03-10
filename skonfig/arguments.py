import argparse
import logging


_logger = logging.getLogger(__name__)


def verbosity_to_logging_level(verbosity):
    levels_pre_py34 = getattr(logging, "_levelNames", {})
    levels_available = getattr(logging, "_levelToName", levels_pre_py34)
    levels_used = list(reversed(sorted([
        level
        for (level, level_name) in levels_available.items()
        if isinstance(level, int)
        and level <= logging.getLevelName("INFO")
        and level_name != "NOTSET"])))
    return levels_used[min(verbosity, len(levels_used)-1)]


def get():
    parser = argparse.ArgumentParser()
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
        "-i",
        dest="manifest",
        metavar="path",
        help="initial manifest or '-' to read from stdin",
    )
    parser.add_argument(
        "-j",
        dest="jobs",
        metavar="jobs",
        type=int,
        help="maximum number of jobs (defaults to host CPU count, maximum: 4)"
    )
    parser.add_argument(
        "-n",
        dest="dry_run",
        action="store_true",
        help="dry-run, do not execute generated code",
    )
    parser.add_argument(
        "-v",
        dest="verbosity",
        action="count",
        default=0,
        help="-v = VERBOSE, -vv = DEBUG, -vvv = TRACE",
    )
    parser.add_argument("host", nargs='?', help="host to configure")
    arguments = parser.parse_args()
    for argument, value in vars(arguments).items():
        _logger.debug("%s: %s", argument, value)
    return (parser, arguments)
