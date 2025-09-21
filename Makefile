#
# 2022,2025 Dennis Camera (dennis.camera at riiengineering.ch)
#
# This file is part of skonfig.
#
# skonfig is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# skonfig is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with skonfig. If not, see <http://www.gnu.org/licenses/>.
#

.POSIX:

help: .FORCE
	@echo "Please use \`make <target>' where <target> is one of"
	@echo ""
	@echo "Building:"
	@echo "  build           build the skonfig source code"
	@echo "  install         install in the system site-packages directory"
	@echo "  install-user    install in the user site-packages directory"
	@echo "  skonfig.pyz     generate a single file executable of skonfig for distribution"
	@echo "  clean           clean"
	@echo ""
	@echo "Documentation:"
	@echo "  docs            build html user documentation"
	@echo "  docs-clean      clean user documentation"
	@echo ""
	@echo "  man             build only man pages"
	@echo ""
	@echo "Testing:"
	@echo "  lint            run all of the following linters:"
	@echo "  pep8            check that the Python source code adheres to PEP 8"
	@echo "  shellcheck      check the shell scripts for errors"
	@echo ""
	@echo "  test            run all of the following test targets:"
	@echo "  unittest(*)     run unit tests"
	@echo "  unittest-remote(*) "
	@echo ""
	@echo "(*) if the environment variable SANDBOX is set, the tests will be"
	@echo "    executed in a sandbox (use SANDBOX=help for a list of options)."
	@echo ""


PYTHON = python3


###############################################################################
# directories
#

dist:
	mkdir -p $@


###############################################################################
# docs
#

DOCS_SRC_DIR=docs/src

docs: man html

html: .FORCE
	$(MAKE) -C $(DOCS_SRC_DIR) html

docs-clean: .FORCE
	$(MAKE) -C $(DOCS_SRC_DIR) clean

man: .FORCE
	$(PYTHON) setup.py build_manpages



###############################################################################
# tests and checkers
#

lint: pep8 shellcheck
test: unittest unittest-remote

pycodestyle pep8: .FORCE
	pycodestyle bin/ skonfig/


SHELLCHECKCMD = shellcheck -s sh -f gcc -x
shellcheck: .FORCE
	find ./bin -type f \
		-exec awk 'FNR==1{exit !/^#!\/bin\/sh/}' {} \; \
		-exec ${SHELLCHECKCMD} {} +


# unit tests

UNITTEST_PYTHONPATH = $$(pwd -P)
UNITTEST_CMD = $(PYTHON) -m tests$(TEST_SUITE:%=.%.__init__)
UNITTEST_REMOTE_CMD = $(UNITTEST_CMD).exec.remote

unittest: _unittest$(SANDBOX:%=-sandbox_%)
unittest-remote: _unittest-remote$(SANDBOX:%=-sandbox_%)

# unittest commands no sandbox
_unittest: .FORCE
	PYTHONPATH=$(UNITTEST_PYTHONPATH) $(UNITTEST_CMD)

_unittest-remote: .FORCE
	PYTHONPATH=$(UNITTEST_PYTHONPATH) $(UNITTEST_REMOTE_CMD)

# help output
_unittest-sandbox_help \
_unittest-remote-sandbox_help: .FORCE
	@echo "SANDBOX accepts the following values:"
	@echo ""
	@echo "  bubblewrap    uses bubblewrap (bwrap command) on Linux"
	@echo "  openbsd       uses pledge(2)/unveil(2) on OpenBSD (and SerenityOS?)"
	@echo "  seatbelt      uses the seatbelt sandboxing framework on Mac OS X 10.5+"
	@echo ""


# unittest commands using bubblewrap sandbox

UNITTEST_BWRAP_CMD = bwrap\
	--unshare-net\
	--unshare-pid\
	--unshare-ipc\
	--cap-drop ALL\
	--ro-bind / /\
	--dev /dev\
	--proc /proc\
	--tmpfs /tmp\
	--dir /tmp/tmp.skonfig.unittest\
	--dir /tmp/tmp.skonfig.unittest/tmp\
	--dir /tmp/tmp.skonfig.unittest/cache\
	--setenv TMPDIR /tmp/tmp.skonfig.unittest/tmp\
	--setenv XDG_CACHE_HOME /tmp/tmp.skonfig.unittest/cache\
	--setenv PYTHONPATH "$(UNITTEST_PYTHONPATH)"\
	--chdir "$$(pwd -P)"

_unittest-sandbox_bwrap \
_unittest-sandbox_bubblewrap: .FORCE
	$(UNITTEST_BWRAP_CMD) $(UNITTEST_CMD)

_unittest-remote-sandbox_bwrap \
_unittest-remote-sandbox_bubblewrap: .FORCE
	$(UNITTEST_BWRAP_CMD) $(UNITTEST_REMOTE_CMD)


# unittest commands using OpenBSD sandbox

UNITTEST_OPENBSD_CMD = tests/openbsd-sandbox

tests/openbsd-sandbox: tests/openbsd-sandbox.c
	$(CC) -o $@ tests/openbsd-sandbox.c

_unittest-sandbox_openbsd: .FORCE $(UNITTEST_OPENBSD_CMD) /tmp/tmp.skonfig.unittest/tmp /tmp/tmp.skonfig.unittest/cache
	TMPDIR=/tmp/tmp.skonfig.unittest/tmp\
	XDG_CACHE_HOME=/tmp/tmp.skonfig.unittest/cache\
	PYTHONPATH="$(UNITTEST_PYTHONPATH)"\
	$(UNITTEST_OPENBSD_CMD) $(UNITTEST_CMD)
	rm -R -f /tmp/tmp.skonfig.unittest/

_unittest-remote-sandbox_openbsd: .FORCE $(UNITTEST_OPENBSD_CMD) /tmp/tmp.skonfig.unittest/tmp /tmp/tmp.skonfig.unittest/cache
	TMPDIR=/tmp/tmp.skonfig.unittest/tmp\
	XDG_CACHE_HOME=/tmp/tmp.skonfig.unittest/cache\
	PYTHONPATH="$(UNITTEST_PYTHONPATH)"\
	$(UNITTEST_OPENBSD_CMD) $(UNITTEST_REMOTE_CMD)
	rm -R -f /tmp/tmp.skonfig.unittest/


# unittest commands using Mac OS X seatbelt

/tmp/tmp.skonfig.unittest \
/tmp/tmp.skonfig.unittest/tmp \
/tmp/tmp.skonfig.unittest/cache:
	test -d $@ || mkdir $@

/tmp/tmp.skonfig.unittest/tmp /tmp/tmp.skonfig.unittest/cache: /tmp/tmp.skonfig.unittest

_unittest-sandbox_seatbelt: .FORCE /tmp/tmp.skonfig.unittest/tmp /tmp/tmp.skonfig.unittest/cache
	TMPDIR=/tmp/tmp.skonfig.unittest/tmp \
	XDG_CACHE_HOME=/tmp/tmp.skonfig.unittest/cache \
	PYTHONPATH="$(UNITTEST_PYTHONPATH)" \
	sandbox-exec -f tests/unittest.sb $(UNITTEST_CMD)
	rm -R -f /tmp/tmp.skonfig.unittest/

_unittest-remote-sandbox_seatbelt: .FORCE /tmp/tmp.skonfig.unittest/tmp /tmp/tmp.skonfig.unittest/cache
	TMPDIR=/tmp/tmp.skonfig.unittest/tmp \
	XDG_CACHE_HOME=/tmp/tmp.skonfig.unittest/cache \
	PYTHONPATH="$(UNITTEST_PYTHONPATH)" \
	sandbox-exec -f tests/unittest.sb $(UNITTEST_REMOTE_CMD)
	rm -R -f /tmp/tmp.skonfig.unittest/


###############################################################################
# clean
#

clean: docs-clean .FORCE
	$(PYTHON) setup.py clean --all
	find . -name __pycache__ | xargs rm -rf

# distutils
	rm -rf ./build ./.eggs ./dist

# Temporary files
	rm -f ./*.tmp ./.*.tmp


###############################################################################
# build and install
#

build: .FORCE
	$(PYTHON) setup.py build

install: build .FORCE
	$(PYTHON) setup.py install

install-user: build .FORCE
	$(PYTHON) setup.py install --user


###############################################################################
# release commands
#

MAKE_PYZ_CMD = $(PYTHON) scripts/compyle.py --compression deflate --main scripts/pyzmain.py skonfig -o
SKONFIG_VERSION_CMD = $$(python3 -c 'print(__import__("skonfig.version").version.__guess_git_version())')

skonfig.pyz: .FORCE
	$(MAKE_PYZ_CMD) $@

release-pyz: dist/. .FORCE
	$(MAKE_PYZ_CMD) "dist/skonfig-$(SKONFIG_VERSION_CMD).pyz"


.FORCE:
