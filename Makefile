.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	- rm -fr build/
	- rm -fr dist/
	- rm -fr .eggs/
	- find . -name '*.egg-info' -exec rm -fr {} +
	- find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	- find . -name '*.pyc' -exec rm -f {} +
	- find . -name '*.pyo' -exec rm -f {} +
	- find . -name '*~' -exec rm -f {} +
	- find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -f .coverage*
	rm -fr htmlcov/
	rm -rf .pytest_cache

test: ## run tests quickly with the default Python
	poetry run python -m pytest tests --cov=src/git_inquisitor --cov-report=term-missing

test-debug: ## run tests quickly with the default Python
	poetry run python -m pytest tests --pdb

version:
	poetry run python bump_version.py

release: clean version ## package and upload a release
	poetry publish --build

dist: clean version ## builds source and wheel package
	poetry build

bootstrap: ## install development dependencies
	poetry install

lint: ## lint all python files with flake8 and black
	poetry run flake8 ./src --count --select=E9,F63,F7,F82 --max-complexity=10 --max-line-length=127 --show-source --statistics