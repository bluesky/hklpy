# create reStructured text from jupyter notebooks

TARGET_DIR = ../docs/source/examples
NOTEBOOKS := $(wildcard *.ipynb)
RSTS := $(subst .ipynb,.rst, ${NOTEBOOKS})

all :: ${RSTS}

%.rst: %.ipynb
	jupyter nbconvert --output-dir ${TARGET_DIR} --to rst $<
