# create reStructured text from jupyter notebooks

TARGET_DIR = ../docs/source/examples/notebooks
NOTEBOOKS := $(wildcard *.ipynb)
RSTS := $(subst .ipynb,.rst, ${NOTEBOOKS})

all :: ${RSTS}
	cp *.png *.jpg *.gif ${TARGET_DIR}

%.rst: %.ipynb
	jupyter nbconvert --output-dir ${TARGET_DIR} --to rst $<
