#
# 2022 Dennis Camera (skonfig at dtnr.ch)
#
# This file is part of cdist.
#
# cdist is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# cdist is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with cdist. If not, see <http://www.gnu.org/licenses/>.
#
#

.POSIX:

help: .FORCE
	@echo "Please use \`make <target>' where <target> is one of"
	@echo ""
	@echo "Install:"
	@echo "  install         install in the system site-packages directory"
	@echo "  install-user    install in the user site-packages directory"
	@echo "  clean           clean"
	@echo ""
	@echo "Documentation:"
	@echo "  docs            build both man and html user documentation"
	@echo "  man             build only man user documentation"
	@echo "  html            build only html user documentation"
	@echo "  docs-clean      clean documentation"
	@echo ""
	@echo "Testing:"
	@echo "  lint            run all of the following linters:"
	@echo "  pep8            check that the Python source code adheres to PEP 8"
	@echo "  shellcheck      check the shell scripts for errors"
	@echo "  test            run all of the following test targets:"
	@echo "  unittest        run unit tests"
	@echo "  unittest-remote "
	@echo ""


###############################################################################
# docs
#

DOCS_SRC_DIR=docs/src

docs: man html

html: .FORCE
	$(MAKE) -C $(DOCS_SRC_DIR) html

man: .FORCE
	$(MAKE) -C $(DOCS_SRC_DIR) man

docs-clean: .FORCE
	$(MAKE) -C $(DOCS_SRC_DIR) clean


###############################################################################
# tests and checkers
#

lint: pep8 shellcheck
test: unittest unittest-remote

pycodestyle pep8: .FORCE
	pycodestyle bin/ skonfig/ cdist/


SHELLCHECKCMD = shellcheck -s sh -f gcc -x
shellcheck: .FORCE
	find ./bin -type f \
		-exec awk 'FNR==1{exit !/^#!\/bin\/sh/}' {} \; \
		-exec ${SHELLCHECKCMD} {} +

unittest: .FORCE
	PYTHONPATH=$$(pwd -P) python3 -m cdist.test

unittest-remote: .FORCE
	PYTHONPATH=$$(pwd -P) python3 -m cdist.test.exec.remote


###############################################################################
# clean
#

clean: docs-clean .FORCE
	python3 setup.py clean --all
	find . -name __pycache__ | xargs rm -rf

# distutils
	rm -rf ./build ./.eggs ./dist

# Temporary files
	rm -f ./*.tmp ./.*.tmp


###############################################################################
# install
#

install: .FORCE
	python3 setup.py install

install-user: .FORCE
	python3 setup.py install --user


.FORCE:
