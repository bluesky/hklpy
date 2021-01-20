# Makefile

# Simplify the pre-commit checks for the code developer.

all :: black flake8 pytest examples clean_docs html

clean_docs:
	make -C docs clean

html:
	make -C docs html

examples:
	make -C examples

pytest:
	pytest

flake8:
	flake8

black:
	black -l 115 .
