#
# 2013 Nico Schottelius (nico-cdist at schottelius.org)
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
	@echo "man             build only man user documentation"
	@echo "html            build only html user documentation"
	@echo "docs            build both man and html user documentation"
	@echo "install         install in the system site-packages directory"
	@echo "install-user    install in the user site-packages directory"
	@echo "docs-clean      clean documentation"
	@echo "clean           clean"

cdist/version.py:
	bin/cdist-build-helper version


################################################################################
# Docs
#

DOCS_SRC_DIR=./docs/src

man: cdist/version.py .FORCE
	$(MAKE) -C $(DOCS_SRC_DIR) man

html: cdist/version.py .FORCE
	$(SPHINXM)$(MAKE) -C $(DOCS_SRC_DIR) html

docs: man html

docs-clean: .FORCE
	$(SPHINXH)$(MAKE) -C $(DOCS_SRC_DIR) clean


################################################################################
# Misc
#
clean: docs-clean .FORCE
	find * -name __pycache__  | xargs rm -rf

	# distutils
	rm -rf ./build ./.eggs

################################################################################
# install
#

install: .FORCE
	python3 setup.py install

install-user: .FORCE
	python3 setup.py install --user


.FORCE:
