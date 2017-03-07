all: html

clean:
	rm -Rf html

.PHONY : html
html:
	cd ..; ./version.sh
	sphinx-build . html
	cd ..; ./version.sh --reset
