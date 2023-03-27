sources = asana2calendar tests

all: lint pylint

install:
	python -m pip install -U pip
	pip install '.[dev,test]'

format:
	isort $(sources) --profile black
	black $(sources)

lint:
	isort $(sources) --profile black --check-only --df
	black $(sources) --check --diff
	pylint $(sources)

pyright:
	pyright $(sources)

test:
	pytest -s --cov-config=pyproject.toml $(addprefix --cov=,$(sources))

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
