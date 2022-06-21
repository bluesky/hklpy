# Makefile

# Simplify the pre-commit checks for the code developer.

all :: black flake8 pytest html

black ::
	black .

flake8 ::
	flake8

html ::
	make -C docs html

pytest ::
	pytest
