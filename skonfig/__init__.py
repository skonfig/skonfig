import os
import sys

from skonfig.version import VERSION as __version__


THIS_IS_SKONFIG = False


def run():
    import cdist
    import skonfig.cdist
    if os.path.basename(sys.argv[0])[:2] == "__":
        try:
            return skonfig.cdist.emulator()
        except cdist.Error:
            pass
    import skonfig.arguments
    parser, arguments = skonfig.arguments.get()
    if arguments.version:
        print("skonfig", __version__)
        return True
    if not arguments.host and not arguments.dump:
        parser.print_help()
        return True
    if arguments.dump:
        import skonfig.dump
        return skonfig.dump.run(arguments.host)
    try:
        return skonfig.cdist.run(arguments)
    except cdist.Error:
        pass
