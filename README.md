# Rhea

This scaffolded project is based on the [The Chromosome Project Python template](https://github.com/chromosomeAI-org/core-python-template),
which is setup according to agreed-on best practices: Poetry, Black formatting, flake8,
isort, mypy, and pytest.

## Installation

```bash
git clone git@github.com:chromosomeAI-org/core-rhea.git
cd rhea
poetry install
krakenw run fmt lint test
```

## Development

Ensure that every functionality inside `rc_core_rhea` is covered by a test inside `tests`.

Before committing any code changes, run the following, which leverages Poetry to run Black, isort, mypy, flake8, and
pytest:

```bash
poetry run isort
poetry run black
poetry run flake8
poetry run pytest
```

Only then commit your code changes.

### Development with VS Code or PyCharm

Please ensure that the (selected) Python environment has all requirements including `pytest` installed, or otherwise
tests will not be discovered, and formatting and linting may produce incorrect behavior.

## Deploying as a Python package

Create a
[new tag](git@github.com:chromosomeAI-org/core-rhea/-/tags/new).
