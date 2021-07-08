include Makefile.config
-include Makefile.custom.config

all: install lint check-outdated check

install-venv:
	test -d $(VENV) || python -m venv .venv
	$(PIP) install --upgrade pip flit

install: install-venv
	$(FLIT) install -s

clean:
	rm -fr $(VENV)
	rm -fr *.egg-info

fix:
	$(BLACK) unrest

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

build:
	$(FLIT) build

clean-build:
	rm -rf dist/*

release: check docs clean-build
ifndef RELEASE_VERSION
	$(error RELEASE_VERSION is undefined)
endif
	git pull
	sed -i "s/version = .*/version = '$(RELEASE_VERSION)'/" pyproject.toml
	git commit -am "Bump $(RELEASE_VERSION)"
	git tag $(RELEASE_VERSION)
	$(FLIT) publish
	git push
	git push --tags
