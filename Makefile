NAME=SpiffWorkflow
VERSION=`python setup.py --version`
PREFIX=/usr/local/
BIN_DIR=$(PREFIX)/bin
SITE_DIR=$(PREFIX)`python -c "import sys; from distutils.sysconfig import get_python_lib; print(get_python_lib()[len(sys.prefix):])"`

###################################################################
# Standard targets.
###################################################################
.PHONY : clean
clean:
	find . -name "*.pyc" -o -name "*.pyo" | xargs -rn1 rm -f
	find . -name "*.egg-info" | xargs -rn1 rm -r
	rm -Rf build
	cd doc; make clean

.PHONY : dist-clean
dist-clean: clean
	rm -Rf dist

.PHONY : doc
doc:
	cd doc; make html

.PHONY : tests
tests:
	python -m unittest discover -vs tests/SpiffWorkflow -p \*Test.py -t .

.PHONY : tests-par
tests-par:
	@if ! command -v unittest-parallel >/dev/null 2>&1; then \
		echo "unittest-parallel not found. Please install it with:"; \
		echo "  pip install unittest-parallel"; \
		exit 1; \
	fi
	unittest-parallel --module-fixtures -qbs tests/SpiffWorkflow -p \*Test.py -t .

.PHONY : tests-cov
tests-cov:
	cd tests/$(NAME)
	coverage run --source=$(NAME) -m unittest discover -v . "*Test.py"

.PHONY : tests-ind
tests-ind:
	cd tests/$(NAME)
	@PYTHONPATH=../.. find . -name "*Test.py" -printf '%p' -exec python -m unittest {} \;

.PHONY : tests-timing
tests-timing:
	@make tests-ind 2>&1 | ./scripts/test_times.py


wheel: clean
	python -m build --sdist --wheel --outdir dist/
