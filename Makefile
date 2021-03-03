include Makefile.config
-include Makefile.custom.config

all: install lint check-outdated check

install:
	test -d $(VENV) || virtualenv $(VENV)
	$(PIP) install --upgrade --no-cache pip setuptools -e .[test,docs,flask,tornado,yaml]

clean:
	rm -fr $(VENV)
	rm -fr *.egg-info

fix:
	blac,

lint:
	$(PYTEST) --flake8 -m flake8 $(PROJECT_NAME)
	$(PYTEST) --isort -m isort $(PROJECT_NAME)

check-outdated:
	$(PIP) list --outdated --format=columns

check: lint
	$(PYTEST) $(PROJECT_NAME) $(PYTEST_ARGS) -p no:warnings --cov-report=html --cov unrest

.PHONY: docs
docs:
	cd docs && PATH=$(PATH):$(VENV)/bin/ $(VENV)/bin/pydocmd gh-deploy

docs-debug:
	cd docs && PATH=$(PATH):$(VENV)/bin/ $(VENV)/bin/pydocmd serve

run:
	FLASK_DEBUG=1 FLASK_APP=unrest/tests/flask/demo.py $(VENV)/bin/flask run -h localhost -p 9996

release: check docs
	rm -fr dist
	git pull
	$(eval VERSION := $(shell PROJECT_NAME=$(PROJECT_NAME) $(VENV)/bin/devcore bump $(LEVEL)))
	git commit -am "Bump $(VERSION)"
	git tag $(VERSION)
	$(PYTHON) setup.py sdist bdist_wheel --universal
	twine upload dist/*
	git push
	git push --tags
