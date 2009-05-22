NAME=SpiffWorkflow
VERSION=`python setup.py --version`
PACKAGE=$(NAME)-$(VERSION)-1
PREFIX=/usr/local/
DISTDIR=/pub/code/releases/spiff_workflow

###################################################################
# Project-specific targets.
###################################################################
DEPENDS=spiff-signal spiff-workflow

svn-environment:
	mkdir -p $(NAME)
	cd $(NAME); for PKG in $(DEPENDS); do \
		svn checkout http://$$PKG.googlecode.com/svn/trunk/ $$PKG; \
	done

git-environment:
	mkdir -p $(NAME)
	cd spiff; for PKG in $(DEPENDS); do \
		git svn init http://$$PKG.googlecode.com/svn/trunk/ $$PKG; \
		cd $$PKG; \
		git svn fetch; \
		cd -; \
	done

###################################################################
# Standard targets.
###################################################################
clean:
	find . -name "*.pyc" -o -name "*.pyo" | xargs -n1 rm -f
	rm -Rf build

dist-clean: clean
	rm -Rf dist $(PACKAGE)*

doc:
	cd doc; make

install:
	python setup.py install --prefix $(PREFIX)

uninstall:
	# Sorry, Python's distutils support no such action yet.

tests:
	cd tests/$(NAME); \
		[ -e run_suite.* ] && ./run_suite.* || [ ! -e run_suite.* ]

###################################################################
# Package builders.
###################################################################
targz:
	python setup.py sdist --formats gztar

tarbz:
	python setup.py sdist --formats bztar

deb:
	debuild -S -sa
	cd ..; sudo pbuilder build $(NAME)_$(VERSION)-0ubuntu1.dsc; cd -

dist: targz tarbz

###################################################################
# Publishers.
###################################################################
dist-publish: dist
	mkdir -p $(DISTDIR)/
	mv dist/* $(DISTDIR)

doc-publish:
	cd doc; make publish
