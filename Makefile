NAME=SpiffWorkflow
RUN ?=
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
	$(RUN) python -m unittest discover -vs tests/SpiffWorkflow -p \*Test.py -t .

.PHONY : tests-par
tests-par:
	@if ! $(RUN) unittest-parallel --help >/dev/null 2>&1; then \
		echo "unittest-parallel not found. Please install it with:"; \
		echo "  pip install -e .[dev]"; \
		echo "  or"; \
		echo "  uv sync --extra dev"; \
		exit 1; \
	fi
	$(RUN) unittest-parallel -qbs tests/SpiffWorkflow -p \*Test.py -t .

.PHONY : tests-cov
tests-cov:
	cd tests/$(NAME) && $(RUN) coverage run --source=$(NAME) -m unittest discover -v . "*Test.py"

.PHONY : tests-ind
tests-ind:
	cd tests/$(NAME) && PYTHONPATH=../.. find . -name "*Test.py" -printf '%p' -exec $(RUN) python -m unittest {} \;

.PHONY : tests-timing
tests-timing:
	@make tests-ind 2>&1 | ./scripts/test_times.py


wheel: clean
	$(RUN) python -m build --sdist --wheel --outdir dist/
