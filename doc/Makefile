all: html

clean:
	rm -Rf html

.PHONY : html
html:
	cd ..; ./version.sh
	sphinx-build . html
	cd ..; ./version.sh --reset

publish: html
	mkdir -p .gh-pages
	cd gh-pages; git clone git@github.com:knipknap/SpiffWorkflow.git .; \
	git checkout gh-pages; \
	rm -R *
	cp -r html/* gh-pages
	cd gh-pages; git add .; git commit -m "generated `date`"; \
	git push origin gh-pages
	rm -R .gh-pages
	make clean
