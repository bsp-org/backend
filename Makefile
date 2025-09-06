SHELL := /bin/bash
PYTHON ?= python3.13
VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: venv install run up down logs migrate lint fmt type test cov precommit-install

venv:
	[ -d $(VENV) ] || $(PYTHON) -m venv $(VENV)
	$(PY) -m pip install --upgrade pip

install: venv
	$(PIP) install -r requirements-dev.txt

run:
	$(PY) -m uvicorn app.main:app --reload

lint:
	$(PY) -m ruff check app tests

fmt:
	$(PY) -m ruff format app tests

type:
	$(PY) -m mypy app

test:
	$(PY) -m pytest

cov:
	$(PY) -m coverage run -m pytest
	$(PY) -m coverage report

precommit-install:
	$(PY) -m pre_commit install
