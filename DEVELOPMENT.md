# Development
HackerBot is built using Python 3.11 but tested on python3.10 - python3.12
We use [Poetry](https://python-poetry.org/) to manage dependencies. To install poetry run:
```bash
pip install poetry==1.8.3
```
### Dependencies - Install
To install hackerbot dependencies run:
```bash
poetry install
```
### Dependencies - Update
To update dependencies run:
```bash
poetry update
```
### Dependencies - Add new dependency
To add a new dependency run:
```bash
poetry add <package-name>
```
## Tests
To install test dependencies run:
```bash
poetry install --with test
```
To run tests:
```bash
poetry run pytest
```
## Building & Publishing
To build the package run:
```bash
poetry install --with build
poetry build
```

To publish the package to PyPi make sure you have the correct credentials in your `.pypirc` file and run:
```bash
twine upload dist/*
```
For help on how to create a `.pypirc` file see [here](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#create-an-account)

