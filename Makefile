NAME=SpiffWorkflow
VERSION=`python setup.py --version`
PREFIX=/usr/local/
BIN_DIR=$(PREFIX)/bin
SITE_DIR=$(PREFIX)`python -c "import sys; from distutils.sysconfig import get_python_lib; print get_python_lib()[len(sys.prefix):]"`
DISTDIR=/pub/code/releases/spiff_workflow

###################################################################
# Standard targets.
###################################################################
.PHONY : clean
clean:
	find . -name "*.pyc" -o -name "*.pyo" | xargs -n1 rm -f
	find . -name "*.egg-info" | xargs -n1 rm -r
	rm -Rf build
	cd doc; make clean

.PHONY : dist-clean
dist-clean: clean
	rm -Rf dist

.PHONY : doc
doc:
	cd doc; make

install:
	mkdir -p $(SITE_DIR)
	./version.sh
	export PYTHONPATH=$(SITE_DIR):$(PYTHONPATH); \
	python setup.py install --prefix $(PREFIX) \
		                    --install-scripts $(BIN_DIR) \
		                    --install-lib $(SITE_DIR)
	./version.sh --reset

uninstall:
	# Sorry, Python's distutils support no such action yet.

.PHONY : tests
tests:
	cd tests/$(NAME); \
		[ -e run_suite.* ] && ./run_suite.* || [ ! -e run_suite.* ]

###################################################################
# Package builders.
###################################################################
targz:
	./version.sh
	python setup.py sdist --formats gztar
	./version.sh --reset

tarbz:
	./version.sh
	python setup.py sdist --formats bztar
	./version.sh --reset

deb:
	./version.sh
	debuild -S -sa
	cd ..; sudo pbuilder build $(NAME)_$(VERSION)-0ubuntu1.dsc; cd -
	./version.sh --reset

dist: targz tarbz

###################################################################
# Publishers.
###################################################################
dist-publish: dist
	mkdir -p $(DISTDIR)/
	mv dist/* $(DISTDIR)

.PHONY : doc-publish
doc-publish:
	cd doc; make publish
