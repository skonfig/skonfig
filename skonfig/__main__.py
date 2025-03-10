import os
import sys

import skonfig


def run_main():
    import cdist
    import skonfig.arguments
    import skonfig.cdist

    (parser, arguments) = skonfig.arguments.get()

    if arguments.version:
        print("skonfig", skonfig.__version__)
        return

    if arguments.dump:
        import skonfig.dump
        skonfig.dump.run(arguments.host)
        return

    if not arguments.host:
        from argparse import (ArgumentError, _)
        e = ArgumentError(
            None, _("the following arguments are required: %s") % ("host"))
        parser.error(str(e))
        sys.exit(1)

    try:
        return skonfig.cdist.run(arguments)
    except cdist.Error as e:
        pass


def run_emulator():
    import cdist
    import skonfig.cdist
    skonfig.cdist.emulator()


def run():
    try:
        if os.path.basename(sys.argv[0]).startswith("__"):
            run_emulator()
        else:
            run_main()
    except KeyboardInterrupt:
        sys.exit(2)


if __name__ == "__main__":
    # change argv[0] because __main__.py would trigger the emulator
    sys.argv[0] = "skonfig"
    run()
