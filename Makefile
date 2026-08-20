# AvoLex — commandes locales (sans Docker)
# Prérequis : Python 3.12, PostgreSQL 16, Redis, make (ou équivalents README)

PYTHON ?= python
PIP ?= pip
VENV ?= .venv
PY := $(VENV)/Scripts/python
PIP_VENV := $(VENV)/Scripts/pip

ifeq ($(OS),Windows_NT)
	PY := $(VENV)/Scripts/python.exe
	PIP_VENV := $(VENV)/Scripts/pip.exe
else
	PY := $(VENV)/bin/python
	PIP_VENV := $(VENV)/bin/pip
endif

.PHONY: help venv install env migrate run worker beat test lint format typecheck pre-commit seed check

help:
	@echo "AvoLex — cibles Make (local, sans Docker)"
	@echo "  make venv       Créer le virtualenv .venv"
	@echo "  make install    Installer requirements/dev.txt"
	@echo "  make env        Copier .env.example -> .env si absent"
	@echo "  make migrate    Appliquer les migrations"
	@echo "  make run        Lancer le serveur de développement"
	@echo "  make worker     Lancer Celery worker"
	@echo "  make beat       Lancer Celery beat"
	@echo "  make test       Lancer pytest"
	@echo "  make lint       ruff check"
	@echo "  make format     ruff format"
	@echo "  make typecheck  mypy --strict"
	@echo "  make pre-commit Installer les hooks pre-commit"
	@echo "  make check      lint + typecheck + test"

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	$(PIP_VENV) install --upgrade pip
	$(PIP_VENV) install -r requirements/dev.txt

env:
	@if [ ! -f .env ]; then cp .env.example .env; echo "Créé .env"; else echo ".env existe déjà"; fi

migrate:
	$(PY) manage.py migrate

run:
	$(PY) manage.py runserver

worker:
	$(PY) -m celery -A config worker -l info

beat:
	$(PY) -m celery -A config beat -l info

test:
	$(PY) -m pytest

lint:
	$(PY) -m ruff check apps config tests
	$(PY) -m ruff format --check apps config tests

format:
	$(PY) -m ruff check --fix apps config tests
	$(PY) -m ruff format apps config tests

typecheck:
	$(PY) -m mypy apps config

pre-commit:
	$(PY) -m pre_commit install

seed:
	@echo "Fixtures de démo : disponibles à une étape ultérieure (make seed)."

check: lint typecheck test
