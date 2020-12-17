# create reStructured text from jupyter notebooks
#
# Create the rst files and related resources
# in the documentation directory.

TARGET_DIR = ../docs/source/examples/notebooks
NOTEBOOKS := $(wildcard *.ipynb)
RSTS := $(subst .ipynb,.rst, ${NOTEBOOKS})
RESOURCES := $(wildcard resources/*)

# default rule: just rebuild everything
# TODO: could be smarter and rebuild conditionally
all :: ${RSTS} resources

# copy all the local resources cited in the notebooks
resources :: #./resources/*
	mkdir -p ${TARGET_DIR}/resources/
	cp ${RESOURCES} ${TARGET_DIR}/resources/

# rule to build a rst file from a notebook
%.rst: %.ipynb
	jupyter nbconvert --output-dir ${TARGET_DIR} --to rst $<
