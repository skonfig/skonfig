import logging


_logger = logging.getLogger(__name__)


def get(skonfig_arguments):
    cdist_argv = ["config"]
    if skonfig_arguments.manifest:
        cdist_argv.append("-i")
        cdist_argv.append(skonfig_arguments.manifest)
    if skonfig_arguments.dry_run:
        cdist_argv.append("-n")
    # skonfig default verbosity level is INFO, which in cdist is one -v,
    # but for skonfig we use -v = VERBOSE, -vv = DEBUG and -vvv = TRACE.
    cdist_argv += ["-v"] * (skonfig_arguments.verbose + 1)
    cdist_argv.append(skonfig_arguments.host)
    import cdist.argparse
    cdist_parser = cdist.argparse.get_parsers()
    cdist_arguments = cdist_parser["main"].parse_args(cdist_argv)
    for argument, value in vars(cdist_arguments).items():
        _logger.debug("%s: %s", argument, value)
    return cdist_arguments
