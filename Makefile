SHELL := /bin/bash
PYTHON ?= python3.13
VENV := .venv
PY := uv run python
PIP := $(VENV)/bin/pip

.PHONY: venv install run up down logs migrate lint fmt type test cov precommit-install

venv:
	[ -d $(VENV) ] || uv venv .venv

install: venv
	uv sync

run:
	$(PY) -m uvicorn src.main:app --reload

lint:
	$(PY) -m ruff check src tests

fmt:
	$(PY) -m ruff format src tests

type:
	$(PY) -m mypy src

test:
	$(PY) -m pytest

cov:
	$(PY) -m coverage run -m pytest
	$(PY) -m coverage report

precommit-install:
	$(PY) -m pre_commit install
