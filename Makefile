.DEFAULT_GOAL := all
sources = asana2calendar tests

.PHONY: install
install:
	python -m pip install -U pip
	pip install '.[dev,test]'

.PHONY: format
format:
	isort $(sources) --profile black
	black $(sources)

.PHONY: lint
lint:
	isort $(sources) --profile black --check-only --df
	black $(sources) --check --diff
	pylint $(sources)

.PHONY: pyright
pyright:
	pyright $(sources)

.PHONY: test
test:
	pytest -s --cov-config=pyproject.toml $(addprefix --cov=,$(sources))

.PHONY: all
all: lint pylint

.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]'`
	rm -f `find . -type f -name '*~'`
	rm -f `find . -type f -name '.*~'`
	rm -rf .cache
	rm -rf .pytest_cache
	rm -rf .pylint_cache
	rm -rf *.egg-info
	rm -f .coverage
	rm -f .coverage.*
	rm -rf dist
	rm -rf coverage.xml
