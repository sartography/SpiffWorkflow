all: html

clean:
	rm -Rf html

html:
	cd ..; ./version.sh
	sphinx-build . html
	cd ..; ./version.sh --reset

publish: html
	# TODO
	make clean
