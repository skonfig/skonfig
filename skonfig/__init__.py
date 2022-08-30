import os
import sys

from skonfig.version import VERSION as __version__


THIS_IS_SKONFIG = False


def run():
    import skonfig.cdist
    if os.path.basename(sys.argv[0])[:2] == "__":
        return skonfig.cdist.emulator()
    import skonfig.arguments
    parser, arguments = skonfig.arguments.get()
    if arguments.version:
        from skonfig import __version__
        print("skonfig", __version__)
        return True
    if not arguments.host and not arguments.dump:
        parser.print_help()
        return True
    if arguments.dump:
        import skonfig.dump
        return skonfig.dump.run(arguments.host)
    return skonfig.cdist.run(arguments)
