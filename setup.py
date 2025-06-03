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

import logging
log = logging.getLogger("setup.py")

class Version:
    """this class is a stripped down version of distutils.version.LooseVersion
    before it was removed from CPython.
    """

    component_re = re.compile(r'(\d+ | [a-z]+ | \.)', re.VERBOSE)

    def __eq__(self, other):
        return self._cmp(other) == 0

    def __lt__(self, other):
        return self._cmp(other) < 0

    def __le__(self, other):
        return self._cmp(other) <= 0

    def __gt__(self, other):
        return self._cmp(other) > 0

    def __ge__(self, other):
        return self._cmp(other) >= 0

    def __init__(self, vstring):
        self.parse(vstring)

    def parse(self, vstring):
        components = [x for x in self.component_re.split(vstring)
                              if x and x != '.']
        for i, obj in enumerate(components):
            try:
                components[i] = int(obj)
            except ValueError:
                pass

        self.version = components

    def _cmp(self, other):
        if isinstance(other, str):
            other = Version(other)

        if self.version == other.version:
            return 0
        if self.version < other.version:
            return -1
        if self.version > other.version:
            return 1


# Import setuptools / distutils
try:
    import setuptools
    from setuptools import setup
    using_setuptools = True

    if Version(setuptools.__version__) < Version("38.6.0"):
        # setuptools 38.6.0 is required for connections to PyPI.
        # cf. also _pypi_can_connect()
        log.warn("You are running an old version of setuptools: %s. "
                    "Consider upgrading." % (setuptools.__version__))
except ImportError:
    from distutils.core import setup
    using_setuptools = False

    log.warn("You are running %s using distutils. "
             "Please consider installing setuptools." % (__file__))


import distutils.command.build
import distutils.command.build_py
import distutils.command.clean
import distutils.command.sdist


class ManPages:
    man_dir = os.path.join(os.path.dirname(__file__), "docs", "man")
    rst_glob = glob.glob(os.path.join(man_dir, "man*", "*.rst"))

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

        log.info("generating man pages")

        man_pages = collections.defaultdict(list)

        # convert man pages
        for path in cls.rst_glob:
            pagename = os.path.splitext(os.path.basename(path))[0]
            section_dir = os.path.basename(os.path.dirname(path))
            section = section_dir.replace("man", "", 1)

            destpath = os.path.join(
                os.path.dirname(path), "%s.%s" % (pagename, section))

            log.info("generating man page %s" % (destpath))
            if not dry_run:
                cls._render_manpage(path, destpath)

            man_pages[section_dir].append(destpath)

        # add man pages to data_files so that they are installed
        cls.update_data_files(distribution.data_files)

    @classmethod
    def find(cls, group_by_section=False):
        for section_path in glob.glob(os.path.join(cls.man_dir, "man*/")):
            section_name = os.path.basename(section_path.rstrip("/"))

            manglob = os.path.join(
                section_path, "*." + section_name.replace("man", "", 1))

            if group_by_section:
                yield (section_name, list(glob.glob(manglob)))
            else:
                for manpage in glob.glob(manglob):
                    yield manpage

    @classmethod
    def update_data_files(cls, data_files):
        for section_name, manpages in cls.find(group_by_section=True):
            inst_dir = os.path.join("share/man", section_name)

            for d, files in data_files:
                if d == inst_dir:
                    break
            else:
                files = []
                data_files.append((inst_dir, files))

            for manpage in manpages:
                if manpage not in files:
                    files.append(manpage)

    @classmethod
    def clean(cls, distribution, dry_run=False):
        for manpage in cls.find(group_by_section=False):
            log.info("removing %s" % (manpage))
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


class skonfig_build_manpages(distutils.command.build.build):
    def run(self):
        ManPages.build(self.distribution, dry_run=self.dry_run)


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


data_files = [
        ("share/doc/skonfig", [
            os.path.join(os.path.dirname(__file__), s) for s in [
                "README.md",
                "docs/src/config.skeleton",
                "docs/changelog"
            ]
        ]),
    ]

# include examples recursively
for dirname, _, files in os.walk(
        os.path.join(os.path.dirname(__file__), "docs", "examples")):
    data_files.append(
        (os.path.join(
            "share/doc/skonfig/examples",
            dirname.split("/examples", 1)[1].lstrip("/")).rstrip("/"),
         [os.path.join(dirname, f) for f in files]))

# include man pages
ManPages.update_data_files(data_files)


setup(
    name="skonfig",
    license="GPL-3.0-or-later",
    packages=["skonfig"],
    scripts=glob.glob(os.path.join(os.path.dirname(__file__), "bin", "*")),
    version=__import__("skonfig").__version__,
    description="system configuration framework",
    author="skonfig nerds",
    url="https://skonfig.li",
    data_files=data_files,
    cmdclass={
        "build": skonfig_build,
        "build_py": skonfig_build_py,
        "sdist": skonfig_sdist,
        "clean": skonfig_clean,

        # custom commands
        "build_manpages": skonfig_build_manpages,
    },
    classifiers=[
        "Development Status :: 6 - Mature",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
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
