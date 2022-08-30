import logging


_logger = logging.getLogger(__name__)


def get(cdist_arguments):
    import cdist.configuration
    cdist_configuration_init = cdist.configuration.Configuration(
        cdist_arguments,
        config_files=(),
        singleton=False
    )
    import skonfig.configuration
    skonfig_configuration = skonfig.configuration.get()
    if cdist_arguments.verbose:
        skonfig_configuration["verbosity"] = cdist_arguments.verbose
    for option in skonfig_configuration:
        cdist_configuration_init.config["GLOBAL"][option] = \
            skonfig_configuration[option]
    cdist_configuration_args = cdist_configuration_init.get_args()
    import cdist.argparse
    cdist.argparse.handle_loglevel(cdist_configuration_args)
    cdist.argparse.handle_log_colors(cdist_configuration_args)
    cdist_configuration = vars(cdist_configuration_args)
    for option in cdist_configuration:
        _logger.debug("%s: %s", option, cdist_configuration[option])
    return cdist_configuration
