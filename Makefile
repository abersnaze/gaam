init:
	pip3 install -r requirements.txt

test:
	python3 -m unittest

SOURCEDIR := usank
SOURCES := $(shell find $(SOURCEDIR) -name '*.py')

build: $(SOURCES)
	python3 setup.py build