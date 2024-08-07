# HackerBot
An AI-CyberSecurity Bot. HackerBot is being trained to help investigate security incidents. We started by teaching HackerBot how to use [Splunk](https://www.splunk.com/).

## prerequisites
### Ollama
Ollama is used to host llama3.1 (and other models) locally. Download and run [Llama 3.1](https://ai.meta.com/blog/meta-llama-3-1/) using [Ollama] (https://ollama.com/)

### Splunk Instance
HackerBot helps security analysts by searching data in Splunk. You will need an accessible instance Splunk instance.

## Install

```bash
pip install hackerbot
```

## Use
Set initial configuration:
```bash
hackerbot_cli.py configure
```

Run hackerbot against Splunk:
```bash
hackerbot_cli.py splunk "show me http and https network traffic going to 8.8.8.8"
```

## Development
HackerBot is built using Python 3.11. We use [Poetry](https://python-poetry.org/) to manage dependencies. To install poetry run:
```bash
pip install poetry==1.8.3
```
To install dependencies run:
```bash
poetry install
```
### Tests
To install test dependencies run:
```bash
poetry install --with test
```
To run tests:
```bash
poetry run pytest
```
### Building & Publishing
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

