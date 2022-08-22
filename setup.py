import os
import collections
import re
import subprocess
import glob

# Set locale
try:
    import locale
    locale.setlocale(locale.LC_ALL, "C")
except:
    pass

from distutils import log

try:
    from packaging.version import Version
except ImportError:
    # fallback to distutils.version
    from distutils.version import LooseVersion as Version

# Import setuptools / distutils
try:
    import setuptools
    from setuptools import setup
    using_setuptools = True

    if Version(setuptools.__version__) < Version("38.6.0"):
        # setuptools 38.6.0 is required for connections to PyPI.
        # cf. also _pypi_can_connect()
        log.warn("You are running an old version of setuptools: %s. "
                    "Consider upgrading." % setuptools.__version__)
except ImportError:
    from distutils.core import setup
    using_setuptools = False

    log.warn("You are running %s using distutils. "
                "Please consider installing setuptools." % __file__)

from distutils.errors import DistutilsError

import distutils.command.build
import distutils.command.build_py
import distutils.command.clean
import distutils.command.sdist


class ManPages:
    rst_glob = glob.glob(os.path.join(
        os.path.dirname(__file__), "docs", "man", "man?", "*.rst"))

    @classmethod
    def _render_manpage(cls, rst_path, dest_path):
        from docutils.core import publish_file
        from docutils.writers import manpage

        publish_file(
            source_path=rst_path,
            destination_path=dest_path,
            writer=manpage.Writer(),
            settings_overrides={
                "language_code": "en",
                "report_level": 1,  # info
                "halt_level": 1,  # info
                "smart_quotes": True,
                "syntax_highlight": "none",
                "traceback": True
            })

    @classmethod
    def build(cls, distribution, dry_run=False):
        try:
            import docutils  # noqa
        except ImportError:
            log.warn(
                "docutils is not available, no man pages will be generated")
            return

        man_pages = collections.defaultdict(list)

        # convert man pages
        for path in cls.rst_glob:
            pagename = os.path.splitext(os.path.basename(path))[0]
            section_dir = os.path.basename(os.path.dirname(path))
            section = int(section_dir.replace("man", ""))

            destpath = os.path.join(
                os.path.dirname(path), "%s.%u" % (pagename, section))

            log.info("generating man page %s" % destpath)
            if not dry_run:
                cls._render_manpage(path, destpath)

            man_pages[section_dir].append(destpath)

        # add man pages to data_files so that they are installed
        for (section, pages) in man_pages.items():
            distribution.data_files.append(
                (os.path.join(("share", "man", section)), pages))

    @classmethod
    def clean(cls, distribution, dry_run=False):
        for path in cls.rst_glob:
            pattern = os.path.join(
                os.path.dirname(path),
                os.path.splitext(os.path.basename(path))[0] + ".?")
            for manpage in glob.glob(pattern):
                log.info("removing %s" % manpage)
                if not dry_run:
                    os.remove(manpage)


def hardcode_version(file):
    log.info("injecting version number into %s", file)
    with open(file, "w") as f:
        f.write('VERSION = "%s"\n' % (__import__("skonfig").__version__))


class skonfig_build(distutils.command.build.build):
    def run(self):
        distutils.command.build.build.run(self)

        # Build man pages
        log.info("generating man pages")
        ManPages.build(self.distribution, dry_run=self.dry_run)


class skonfig_build_py(distutils.command.build_py.build_py):
    def build_module(self, module, module_file, package):
        (dest_name, copied) = super().build_module(
            module, module_file, package)

        if dest_name == os.path.join(self.build_lib, "skonfig", "version.py") \
                and not self.dry_run:
            # Hard code generated version number into source distribution
            if os.path.exists(dest_name):
                os.remove(dest_name)
            hardcode_version(dest_name)

        return (dest_name, copied)


class skonfig_sdist(distutils.command.sdist.sdist):
    def make_release_tree(self, base_dir, files):
        distutils.command.sdist.sdist.make_release_tree(self, base_dir, files)

        # Hard code generated version number into source distribution
        version_file = os.path.join(base_dir, "skonfig", "version.py")
        if os.path.exists(version_file):
            os.remove(version_file)
        hardcode_version(version_file)


class skonfig_clean(distutils.command.clean.clean):
    def run(self):
        ManPages.clean(self.distribution, dry_run=self.dry_run)
        distutils.command.clean.clean.run(self)


def _pypi_can_connect():
    # PyPI requires an SSL client with SNI and TLSv1.2 support.
    # https://github.com/pypi/warehouse/issues/3411
    # https://github.com/pypa/pypi-support/issues/978

    # for setup_require (which uses easy_install in the back),
    # setuptools >= 36.8.0 is also required, older versions produce:
    # distutils.errors.DistutilsError: Could not find suitable distribution for Requirement.parse('docutils')

    import ssl

    try:
        # Python >= 3.7
        supports_tlsv1_2 = hasattr(ssl.TLSVersion, "TLSv1_2")
    except AttributeError:
        # Python < 3.10
        supports_tlsv1_2 = hasattr(ssl, "PROTOCOL_TLSv1_2")

    return \
        ssl.HAS_SNI \
        and supports_tlsv1_2 \
        and Version(setuptools.__version__) >= Version("36.8.0")


if using_setuptools:
    # setuptools specific setup() keywords
    kwargs = dict(
        python_requires=">=3.2",
        )

    if _pypi_can_connect():
        kwargs["setup_requires"] = ["docutils"]
else:
    # distutils specific setup() keywords
    kwargs = dict()


setup(
    name="skonfig",
    packages=["skonfig", "cdist", "cdist.core", "cdist.exec", "cdist.scan", "cdist.util"],
    scripts=glob.glob(os.path.join(os.path.dirname(__file__), "bin", "*")),
    version=__import__("skonfig").__version__,
    description="system configuration framework",
    author="skonfig nerds",
    url="https://skonfig.li",
    data_files=[
        ("share/doc/skonfig", [
            "README.md",
            "docs/src/config.skeleton",
            "docs/changelog"
        ]),
    ],
    cmdclass={
        "build": skonfig_build,
        "build_py": skonfig_build_py,
        "sdist": skonfig_sdist,
        "clean": skonfig_clean,
    },
    classifiers=[
        "Development Status :: 6 - Mature",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",  # noqa
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: BSD",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: System :: Boot",
        "Topic :: System :: Installation/Setup",
        "Topic :: System :: Operating System",
        "Topic :: System :: Software Distribution",
        "Topic :: Utilities"
    ],
    **kwargs
)
