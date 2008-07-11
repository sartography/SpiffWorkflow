DEPENDENCIES=spiff-signal spiff-workflow
PACKAGE_NAME=spiff-workflow
PREFIX=/usr/local/

fetch-svn:
	mkdir -p $(PACKAGE_NAME)-svn
	cd $(PACKAGE_NAME)-svn; \
	for DEP in $(DEPENDENCIES); do \
		svn checkout http://$$DEP.googlecode.com/svn/trunk/ $$DEP; \
	done

svn-install: fetch-svn
	for DEP in $(DEPENDENCIES); do \
		cd $(PACKAGE_NAME)-svn/$$DEP; \
		python setup.py install --prefix $(PREFIX); \
		cd -; \
	done

install:
	python setup.py install --prefix $(PREFIX)
