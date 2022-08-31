import argparse
import logging
import sys


_logger = logging.getLogger(__name__)


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
    if arguments.verbose > 3:
        arguments.verbose = 3
    logging.basicConfig(level=[20, 15, 10, 5][arguments.verbose])
    for argument, value in vars(arguments).items():
        _logger.debug("%s: %s", argument, value)
    return parser, arguments
