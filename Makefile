# Makefile

# Simplify the pre-commit checks for the code developer.

all :: black flake8 pytest clean_docs examples html

black ::
	black .

clean_docs ::
	make -C docs clean
	rm -rf docs/source/examples/notebooks/geo_*
	rm -rf docs/source/examples/notebooks/tst_*
	rm -rf docs/source/examples/notebooks/var_*

examples ::
	make -C examples

flake8 ::
	flake8

html ::
	make -C docs html

pytest ::
	pytest
