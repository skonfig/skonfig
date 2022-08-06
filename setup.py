import os
import collections
import re
import subprocess
import glob

# Logging output
import logging
logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("setup.py")

# Set locale
try:
    import locale
    locale.setlocale(locale.LC_ALL, "C")
except:
    pass

from distutils.version import LooseVersion as Version

# Import setuptools / distutils
try:
    import setuptools
    from setuptools import setup
    using_setuptools = True

    if Version(setuptools.__version__) < Version("38.6.0"):
        # setuptools 38.6.0 is required for connections to PyPI.
        # cf. also _pypi_can_connect()
        LOG.warning("You are running an old version of setuptools: %s. "
                    "Consider upgrading." % setuptools.__version__)
except ImportError:
    from distutils.core import setup
    using_setuptools = False

    LOG.warning("You are running %s using distutils. "
                "Please consider installing setuptools." % __file__)

from distutils.errors import DistutilsError

import distutils.command.build
import distutils.command.clean


# We have it only if it is a git cloned repo.
build_helper = os.path.join('bin', 'cdist-build-helper')
# Version file path.
version_file = os.path.join('cdist', 'version.py')
# If we have build-helper we could be a git repo.
if os.path.exists(build_helper):
    # Try to generate version.py.
    if subprocess.call([build_helper, 'version'], shell=False) != 0:
        raise DistutilsError("Failed to generate {}".format(version_file))
else:
    # Otherwise, version.py should be present.
    if not os.path.exists(version_file):
        raise DistutilsError("Missing version file {}".format(version_file))


import cdist  # noqa


class ManPages:
    rst_glob = glob.glob("man/man?/*.rst")

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
    def build(cls, distribution):
        try:
            import docutils  # noqa
        except ImportError:
            LOG.warning(
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

            print("generating man page %s" % destpath)
            cls._render_manpage(path, destpath)

            man_pages[section_dir].append(destpath)

        # add man pages to data_files so that they are installed
        for (section, pages) in man_pages.items():
            distribution.data_files.append(
                ("share/man/" + section, pages))

    @classmethod
    def clean(cls, distribution):
        for path in cls.rst_glob:
            pattern = os.path.join(
                os.path.dirname(path),
                os.path.splitext(os.path.basename(path))[0] + ".?")
            for manpage in glob.glob(pattern):
                print("removing %s" % manpage)
                os.remove(manpage)


class cdist_build(distutils.command.build.build):
    def run(self):
        distutils.command.build.build.run(self)
        ManPages.build(self.distribution)


class cdist_clean(distutils.command.clean.clean):
    def run(self):
        ManPages.clean(self.distribution)
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
    name="cdist",
    packages=["cdist", "cdist.core", "cdist.exec", "cdist.scan", "cdist.util"],
    scripts=["bin/cdist", "bin/cdist-dump", "bin/skonfig-new-type", "bin/cdist-type-helper"],
    version=cdist.version.VERSION,
    description="A Usable Configuration Management System",
    author="cdist contributors",
    url="https://cdi.st",
    data_files=[
    ],
    cmdclass={
        "build": cdist_build,
        "clean": cdist_clean,
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
    long_description='''
        cdist is a usable configuration management system.
        It adheres to the KISS principle and is being used in small up to
        enterprise grade environments.
        cdist is an alternative to other configuration management systems like
        cfengine, bcfg2, chef and puppet.
    ''',
    **kwargs
)
