import os
import sys
import collections
import re
import subprocess
import glob
import shutil


try:
    import setuptools
    from setuptools import setup
    using_setuptools = True
except ImportError:
    from distutils.core import setup
    using_setuptools = False

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
    rc = subprocess.call([build_helper, 'version'], shell=False)
    if rc != 0:
        raise DistutilsError("Failed to generate {}".format(version_file))
else:
    # Otherwise, version.py should be present.
    if not os.path.exists(version_file):
        raise DistutilsError("Missing version file {}".format(version_file))


import cdist  # noqa


def data_finder(data_dir):
    entries = []
    for name in os.listdir(data_dir):
        # Skip .gitignore files
        if name == ".gitignore":
            continue

        # Skip vim swp files
        if re.search(r'^\..*\.swp$', name):
            continue

        # Skip Emacs backups files
        if re.search(r'(^\.?#|~$)', name):
            continue

        entry = os.path.join(data_dir, name)
        entries += data_finder(entry) if os.path.isdir(entry) else [entry]

    return entries


class ManPages:
    rst_glob = glob.glob("man/man?/*.rst")

    @classmethod
    def _find_egg_scripts_dir(cls, package):
        # find the scripts directory of an egg
        try:
            import pkg_resources
            from itertools import chain

            dist = next((
                d for d in chain.from_iterable(
                    pkg_resources.find_distributions(p)
                    for p in sys.path
                    if p.endswith(".egg"))
                if d.project_name == package))
            scripts_dir = os.path.join(dist.location, "EGG-INFO", "scripts")
            if os.path.isdir(scripts_dir):
                return scripts_dir
        except StopIteration:
            pass

    @classmethod
    def _find_rst2man(cls):
        rst2man_name_candidates = (
            # Debian
            "rst2man",
            # pip
            "rst2man.py",
            # e.g. MacPorts
            "rst2man-%s.py" % (".".join(map(str, sys.version_info[:2]))),
            )

        rst2man = None

        # use setuptools downloaded egg if available
        egg_scripts = cls._find_egg_scripts_dir("docutils")
        if egg_scripts:
            for scr in (os.path.join(egg_scripts, c)
                        for c in rst2man_name_candidates):
                # NOTE: prefer running scripts with given interpreter instead
                #       of relying on sheband, because the shebang can be wrong
                #       in egg.
                if os.access(scr, os.R_OK) and sys.executable:
                    rst2man = [sys.executable, scr]
                    break
                elif os.access(scr, os.X_OK):
                    rst2man = [scr]
                    break

        # otherwise, search system rst2man executable
        if not rst2man:
            try:
                rst2man = [next(filter(None, map(shutil.which, rst2man_name_candidates)))]
            except StopIteration:
                pass

        if not rst2man:
            raise RuntimeError("rst2man not found")

        return rst2man

    @classmethod
    def build(cls, distribution):
        rst2man = cls._find_rst2man()

        man_pages = collections.defaultdict(list)

        # convert man pages
        for path in cls.rst_glob:
            base = os.path.basename(path)
            section_dir = os.path.basename(os.path.dirname(path))
            section = int(section_dir.replace("man", ""))
            pagename = os.path.splitext(base)[0]
            destpath = os.path.join(
                os.path.dirname(path), "%s.%u" % (pagename, section))

            print("generating man page %s" % destpath)
            pargs = rst2man + ["--strict", path]
            with open(destpath, "wb") as f:
                p = subprocess.Popen(
                    pargs, executable=pargs[0],
                    stdin=subprocess.DEVNULL, stdout=f, stderr=None,
                    env={
                        "LC_ALL": "C",
                        "PYTHONPATH": os.pathsep.join(sys.path)
                    },
                    shell=False, close_fds=True)
                p.wait()
                if p.returncode:
                    raise RuntimeError(
                        "%s returned %d" % (" ".join(pargs), p.returncode))

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
            for mp in glob.glob(pattern):
                print("removing %s" % mp)
                os.remove(mp)


class cdist_build(distutils.command.build.build):
    def run(self):
        distutils.command.build.build.run(self)
        ManPages.build(self.distribution)


class cdist_clean(distutils.command.clean.clean):
    def run(self):
        ManPages.clean(self.distribution)
        distutils.command.clean.clean.run(self)


cur = os.getcwd()
os.chdir("cdist")
package_data = data_finder("conf")
os.chdir(cur)

if using_setuptools:
    # setuptools specific setup() keywords
    kwargs = dict(
        python_requires=">=3.2",
        )

    from distutils.version import LooseVersion as Version
    if Version(setuptools.__version__) >= Version("36.8.0"):
        # https://github.com/pypa/pypi-support/issues/978
        # on setuptools < 36.8.0 produces:
        # distutils.errors.DistutilsError: Could not find suitable distribution for Requirement.parse('docutils')
        kwargs["setup_requires"] = ["docutils", "Pygments"]
else:
    # distutils specific setup() keywords
    kwargs = dict()


setup(
    name="cdist",
    packages=["cdist", "cdist.core", "cdist.exec", "cdist.scan", "cdist.util"],
    package_data={'cdist': package_data},
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
