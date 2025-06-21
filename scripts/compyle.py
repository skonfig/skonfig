#!/usr/bin/env python3

import os
import zipfile


def find_modules(package):
    try:
        names = sorted(x for x in os.listdir(package) if x[0] != ".")
    except os.error:
        return []
    files = []
    for f in names:
        full_path = os.path.join(package, f)
        path_prefix = os.path.join(f, "")
        if os.path.isdir(full_path):
            files += [(path_prefix + x) for x in find_modules(full_path)]
    files += names
    return [f for f in files if f[-3:] == ".py"]


def add_package_to_zip(package, zipf):
    pkg_name = os.path.basename(package)
    for module in find_modules(package):
        with open(os.path.join(package, module), "rb") as f:
            zipf.writestr(os.path.join(pkg_name, module), f.read())


def compile_package(packages, output_file, compression, main_module=None):
    with open(output_file, "wb") as exe:
        exe.write(b"#!/usr/bin/env python3\n")

        with zipfile.ZipFile(exe, "a", compression=compression) as zipf:
            for package in sorted(packages):
                add_package_to_zip(package, zipf)

            # add __main__ module and make executable
            if main_module:
                with open(main_module, "rb") as f:
                    zipf.writestr("__main__.py", f.read())
        os.fchmod(exe.fileno(), 0o755 if main_module else 0o644)


if __name__ == "__main__":
    zip_compressions = {k: v for (k, v) in (
        ("store", getattr(zipfile, "ZIP_STORED", None)),
        ("deflate", getattr(zipfile, "ZIP_DEFLATED", None)),
        ) if v is not None}

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--compression",
        dest="compression",
        choices=list(zip_compressions.keys()),
        default="store")
    parser.add_argument(
        "--main",
        dest="main_script",
        help="run this script when the binary is executed")
    parser.add_argument(
        "-o",
        dest="output_file",
        required=True)
    parser.add_argument(
        dest="packages",
        nargs="*",
        help="a package path to include")
    args = parser.parse_args()

    compile_package(
        args.packages,
        output_file=args.output_file,
        main_module=args.main_script,
        compression=zip_compressions[args.compression])
