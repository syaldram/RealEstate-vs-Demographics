.PHONY: build serve clean install

PY ?= python

install:
	$(PY) -m pip install -r app/requirements.txt

build: clean
	cd app && $(PY) freeze.py

serve:
	$(PY) -m http.server 8000 -d build

clean:
	rm -rf build
