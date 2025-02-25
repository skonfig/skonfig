import os
import sys

from skonfig.version import VERSION as __version__


def run():
    import cdist
    import skonfig.cdist
    if os.path.basename(sys.argv[0]).startswith("__"):
        try:
            return skonfig.cdist.emulator()
        except cdist.Error:
            pass
    import skonfig.arguments
    (parser, arguments) = skonfig.arguments.get()
    if arguments.version:
        print("skonfig", __version__)
        return True
    if arguments.dump:
        import skonfig.dump
        return skonfig.dump.run(arguments.host)
    if not arguments.host:
        from argparse import ArgumentError, _
        e = ArgumentError(
            None, _("the following arguments are required: %s") % ("host"))
        parser.error(str(e))
        return False
    try:
        return skonfig.cdist.run(arguments)
    except cdist.Error:
        pass
