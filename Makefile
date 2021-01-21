# Makefile

# Simplify the pre-commit checks for the code developer.

all :: black flake8 pytest examples clean_docs html

black ::
	black .

clean_docs ::
	make -C docs clean

examples ::
	make -C examples

flake8 ::
	flake8

html ::
	make -C docs html

pytest ::
	pytest
