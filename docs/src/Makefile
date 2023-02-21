# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS   ?=
SPHINXBUILD  ?= sphinx-build
PAPER        ?=
BUILDDIR     ?= ../dist
# for cache, etc.
_BUILDDIR     = _build

# User-friendly check for sphinx-build
.PHONY: sphinxbuild-check
sphinxbuild-check:
	@command -v $(SPHINXBUILD) || { \
		echo "The '$(SPHINXBUILD)' command was not found. Make sure you have Sphinx installed, then set the SPHINXBUILD environment variable to point to the full path of the '$(SPHINXBUILD)' executable. Alternatively you can add the directory with the executable to your PATH. If you don\'t have Sphinx installed, grab it from http://sphinx-doc.org/)" >&2; \
		exit 2; \
	}

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(_BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .
# the i18n builder cannot share the environment and doctrees with the others
I18NSPHINXOPTS  = $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .

.PHONY: help
help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html       to make standalone HTML files"
	@echo "  dirhtml    to make HTML files named index.html in directories"
	@echo "  singlehtml to make a single large HTML file"
	@echo "  pickle     to make pickle files"
	@echo "  json       to make JSON files"
	@echo "  epub       to make an epub"
	@echo "  epub3      to make an epub3"
	@echo "  latex      to make LaTeX files, you can set PAPER=a4 or PAPER=letter"
	@echo "  latexpdf   to make LaTeX files and run them through pdflatex"
	@echo "  latexpdfja to make LaTeX files and run them through platex/dvipdfmx"
	@echo "  text       to make text files"
	@echo "  man        to make manual pages"
	@echo "  texinfo    to make Texinfo files"
	@echo "  info       to make Texinfo files and run them through makeinfo"
	@echo "  gettext    to make PO message catalogs"
	@echo "  changes    to make an overview of all changed/added/deprecated items"
	@echo "  xml        to make Docutils-native XML files"
	@echo "  pseudoxml  to make pseudoxml-XML files for display purposes"
	@echo "  linkcheck  to check all external links for integrity"
	@echo "  doctest    to run all doctests embedded in the documentation (if enabled)"
	@echo "  coverage   to run coverage check of the documentation (if enabled)"
	@echo "  dummy      to check syntax errors of document sources"

.PHONY: clean
clean:
	rm -rf $(BUILDDIR)/*
	rm -rf $(_BUILDDIR)/*

.PHONY: html
html: sphinxbuild-check
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

.PHONY: dirhtml
dirhtml: sphinxbuild-check
	$(SPHINXBUILD) -b dirhtml $(ALLSPHINXOPTS) $(BUILDDIR)/dirhtml
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/dirhtml."

.PHONY: singlehtml
singlehtml: sphinxbuild-check
	$(SPHINXBUILD) -b singlehtml $(ALLSPHINXOPTS) $(BUILDDIR)/singlehtml
	@echo
	@echo "Build finished. The HTML page is in $(BUILDDIR)/singlehtml."

.PHONY: pickle
pickle: sphinxbuild-check
	$(SPHINXBUILD) -b pickle $(ALLSPHINXOPTS) $(BUILDDIR)/pickle
	@echo
	@echo "Build finished; now you can process the pickle files."

.PHONY: json
json: sphinxbuild-check
	$(SPHINXBUILD) -b json $(ALLSPHINXOPTS) $(BUILDDIR)/json
	@echo
	@echo "Build finished; now you can process the JSON files."

.PHONY: epub
epub: sphinxbuild-check
	$(SPHINXBUILD) -b epub $(ALLSPHINXOPTS) $(BUILDDIR)/epub
	@echo
	@echo "Build finished. The epub file is in $(BUILDDIR)/epub."

.PHONY: epub3
epub3: sphinxbuild-check
	$(SPHINXBUILD) -b epub3 $(ALLSPHINXOPTS) $(BUILDDIR)/epub3
	@echo
	@echo "Build finished. The epub3 file is in $(BUILDDIR)/epub3."

.PHONY: latex
latex: sphinxbuild-check
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) $(BUILDDIR)/latex
	@echo
	@echo "Build finished; the LaTeX files are in $(BUILDDIR)/latex."
	@echo "Run \`make' in that directory to run these through (pdf)latex" \
	      "(use \`make latexpdf' here to do that automatically)."

.PHONY: latexpdf
latexpdf: sphinxbuild-check
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) $(BUILDDIR)/latex
	@echo "Running LaTeX files through pdflatex..."
	$(MAKE) -C $(BUILDDIR)/latex all-pdf
	@echo "pdflatex finished; the PDF files are in $(BUILDDIR)/latex."

.PHONY: latexpdfja
latexpdfja: sphinxbuild-check
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) $(BUILDDIR)/latex
	@echo "Running LaTeX files through platex and dvipdfmx..."
	$(MAKE) -C $(BUILDDIR)/latex all-pdf-ja
	@echo "pdflatex finished; the PDF files are in $(BUILDDIR)/latex."

.PHONY: text
text: sphinxbuild-check
	$(SPHINXBUILD) -b text $(ALLSPHINXOPTS) $(BUILDDIR)/text
	@echo
	@echo "Build finished. The text files are in $(BUILDDIR)/text."

.PHONY: man
man: sphinxbuild-check
	$(SPHINXBUILD) -b cman $(ALLSPHINXOPTS) $(BUILDDIR)/man
	mkdir -p $(BUILDDIR)/man/man7
	@echo
	@echo "Build finished. The manual pages are in $(BUILDDIR)/man."

.PHONY: texinfo
texinfo: sphinxbuild-check
	$(SPHINXBUILD) -b texinfo $(ALLSPHINXOPTS) $(BUILDDIR)/texinfo
	@echo
	@echo "Build finished. The Texinfo files are in $(BUILDDIR)/texinfo."
	@echo "Run \`make' in that directory to run these through makeinfo" \
	      "(use \`make info' here to do that automatically)."

.PHONY: info
info: sphinxbuild-check
	$(SPHINXBUILD) -b texinfo $(ALLSPHINXOPTS) $(BUILDDIR)/texinfo
	@echo "Running Texinfo files through makeinfo..."
	make -C $(BUILDDIR)/texinfo info
	@echo "makeinfo finished; the Info files are in $(BUILDDIR)/texinfo."

.PHONY: gettext
gettext: sphinxbuild-check
	$(SPHINXBUILD) -b gettext $(I18NSPHINXOPTS) $(BUILDDIR)/locale
	@echo
	@echo "Build finished. The message catalogs are in $(BUILDDIR)/locale."

.PHONY: changes
changes: sphinxbuild-check
	$(SPHINXBUILD) -b changes $(ALLSPHINXOPTS) $(BUILDDIR)/changes
	@echo
	@echo "The overview file is in $(BUILDDIR)/changes."

.PHONY: linkcheck
linkcheck: sphinxbuild-check
	$(SPHINXBUILD) -b linkcheck $(ALLSPHINXOPTS) $(BUILDDIR)/linkcheck
	@echo
	@echo "Link check complete; look for any errors in the above output " \
	      "or in $(BUILDDIR)/linkcheck/output.txt."

.PHONY: doctest
doctest: sphinxbuild-check
	$(SPHINXBUILD) -b doctest $(ALLSPHINXOPTS) $(BUILDDIR)/doctest
	@echo "Testing of doctests in the sources finished, look at the " \
	      "results in $(BUILDDIR)/doctest/output.txt."

.PHONY: coverage
coverage: sphinxbuild-check
	$(SPHINXBUILD) -b coverage $(ALLSPHINXOPTS) $(BUILDDIR)/coverage
	@echo "Testing of coverage in the sources finished, look at the " \
	      "results in $(BUILDDIR)/coverage/python.txt."

.PHONY: xml
xml: sphinxbuild-check
	$(SPHINXBUILD) -b xml $(ALLSPHINXOPTS) $(BUILDDIR)/xml
	@echo
	@echo "Build finished. The XML files are in $(BUILDDIR)/xml."

.PHONY: pseudoxml
pseudoxml: sphinxbuild-check
	$(SPHINXBUILD) -b pseudoxml $(ALLSPHINXOPTS) $(BUILDDIR)/pseudoxml
	@echo
	@echo "Build finished. The pseudo-XML files are in $(BUILDDIR)/pseudoxml."

.PHONY: dummy
dummy: sphinxbuild-check
	$(SPHINXBUILD) -b dummy $(ALLSPHINXOPTS) $(BUILDDIR)/dummy
	@echo
	@echo "Build finished. Dummy builder generates no files."
