include Makefile.config
-include Makefile.custom.config

all: install check

install:
	test -d $(VENV) || virtualenv $(VENV)
	$(PIP) install --upgrade --no-cache pip setuptools -e .[test]

clean:
	rm -fr $(VENV)
	rm -fr *.egg-info

lint:
	$(PYTEST) --flake8 -m flake8 $(PROJECT_NAME)
	$(PYTEST) --isort -m isort $(PROJECT_NAME)

check-outdated:
	$(PIP) list --outdated --format=columns

check: check-outdated
	$(PYTEST) $(PROJECT_NAME) $(PYTEST_ARGS)
