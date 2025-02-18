import argparse
import collections
import functools
import multiprocessing

import cdist
import cdist.log


# Parser others can reuse
parser = None


def check_lower_bounded_int(value, lower_bound, name):
    try:
        val = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
                "{} is invalid int value".format(value))
    if val < lower_bound:
        raise argparse.ArgumentTypeError(
                "{} is invalid {} value".format(val, name))
    return val


def get_parsers():
    global parser

    # Construct parser others can reuse
    if parser:
        return parser
    else:
        parser = {}
    # Options _all_ parsers have in common
    parser['loglevel'] = argparse.ArgumentParser(add_help=False)
    parser['loglevel'].add_argument(
            '-v', '--verbose',
            help=('Increase the verbosity level. Every instance of -v '
                  'increments the verbosity level by one. Its default value '
                  'is 0 which includes ERROR and WARNING levels. '
                  'The levels, in order from the lowest to the highest, are: '
                  'ERROR (-1), WARNING (0), INFO (1), VERBOSE (2), DEBUG (3) '
                  'TRACE (4 or higher). If used along with -l then -l '
                  'overwrites last set value and -v increases last set '
                  'value.'),
            action='count', default=None)

    import cdist.configuration
    parser['colored_output'] = argparse.ArgumentParser(add_help=False)
    parser['colored_output'].add_argument(
            '--colors', metavar='WHEN',
            help="Colorize cdist's output based on log level; "
                 "WHEN is 'always', 'never', or 'auto'.",
            action='store', dest='colored_output', required=False,
            choices=cdist.configuration.ColoredOutputOption.CHOICES)

    # Main subcommand parser
    parser['main'] = argparse.ArgumentParser(
            description='%(prog)s ' + cdist.__version__)
    parser['sub'] = parser['main'].add_subparsers(
            title="Commands", dest="command")

    # Config
    parser['config_main'] = argparse.ArgumentParser(add_help=False)
    parser['config_main'].add_argument(
            '-C', '--cache-path-pattern',
            help=('Specify custom cache path pattern. If '
                  'it is not set then default hostdir is used.'),
            dest='cache_path_pattern',
            default=None)
    parser['config_main'].add_argument(
            '-c', '--conf-dir',
            help=('Add configuration directory (can be repeated, '
                  'last one wins).'), action='append')
    parser['config_main'].add_argument(
           '-i', '--initial-manifest',
           help='Path to a manifest or \'-\' to read from stdin.',
           dest='manifest', required=False)
    parser['config_main'].add_argument(
           '-j', '--jobs', nargs='?',
           type=functools.partial(check_lower_bounded_int, lower_bound=1,
                                  name="positive int"),
           help=('Operate in parallel in specified maximum number of jobs. '
                 'Global explorers, object prepare and object run are '
                 'supported. Without argument CPU count is used by default. '),
           action='store', dest='jobs',
           const=min(4, multiprocessing.cpu_count()))
    parser['config_main'].add_argument(
           '-n', '--dry-run',
           help='Do not execute code.', action='store_true')
    parser['config_main'].add_argument(
           '-o', '--out-dir',
           help='Directory to save cdist output in.', dest="out_path")
    parser['config_main'].add_argument(
           '-R', '--use-archiving', nargs='?',
           choices=cdist.autil.archiving_values.keys(),
           help=('Operate by using archiving with compression where '
                 'appropriate. Supported values are: '
                 + ", ".join(
                     "%s - %s" % (name, doc)
                     for (name, doc) in cdist.autil.archiving_values.items())),
           action='store', dest='use_archiving',
           const='tgz')

    # remote-copy and remote-exec defaults are environment variables
    # if set; if not then None - these will be futher handled after
    # parsing to determine implementation default
    parser['config_main'].add_argument(
           '-r', '--remote-out-dir',
           help='Directory to save cdist output in on the target host.',
           dest="remote_out_path")
    parser['config_main'].add_argument(
           '--remote-exec',
           help=('Command to use for remote execution '
                 '(should behave like SSH).'),
           action='store', dest='remote_exec',
           default=None)

    # Config
    import cdist.config

    parser['config_args'] = argparse.ArgumentParser(add_help=False)
    parser['config_args'].add_argument(
            'host', nargs=1, help='Host to operate on.')
    parser['config'] = parser['sub'].add_parser(
            'config', parents=[parser['loglevel'],
                               parser['colored_output'],
                               parser['config_main'],
                               parser['config_args']])
    parser['config'].set_defaults(cls=cdist.config.Config)

    return parser


def handle_loglevel(args):
    cdist.log.getLogger().setLevel(cdist.log._verbosity_level[args.verbose])


def handle_log_colors(args):
    if cdist.configuration.ColoredOutputOption.translate(args.colored_output):
        cdist.log.CdistFormatter.USE_COLORS = True


def parse_and_configure(argv, singleton=True):
    parser = get_parsers()
    parser_args = parser['main'].parse_args(argv)
    try:
        cfg = cdist.configuration.Configuration(parser_args,
                                                singleton=singleton)
        args = cfg.get_args()
    except ValueError as e:
        raise cdist.Error(str(e))
    # Loglevels are handled globally in here
    handle_loglevel(args)
    handle_log_colors(args)

    log = cdist.log.getLogger("cdist")

    log.verbose("version %s", cdist.__version__)
    log.trace('command line args: %s', cfg.command_line_args)
    log.trace('configuration: %s', cfg.get_config())
    log.trace('configured args: %s', args)

    return parser, cfg
