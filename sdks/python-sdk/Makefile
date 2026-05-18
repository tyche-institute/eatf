.PHONY: install install-dev test lint format clean build publish

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest

test-cov:
	pytest --cov=aletheia --cov-report=html --cov-report=term

lint:
	ruff check aletheia/ tests/
	mypy aletheia/

format:
	black aletheia/ tests/ examples/
	ruff check --fix aletheia/ tests/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:
	python -m build

publish: clean build
	python -m twine upload dist/*

.DEFAULT_GOAL := help

help:
	@echo "Aletheia AI Python SDK - Makefile"
	@echo ""
	@echo "Available commands:"
	@echo "  make install       Install package"
	@echo "  make install-dev   Install with dev dependencies"
	@echo "  make test          Run tests"
	@echo "  make test-cov      Run tests with coverage"
	@echo "  make lint          Run linters"
	@echo "  make format        Format code"
	@echo "  make clean         Clean build artifacts"
	@echo "  make build         Build package"
	@echo "  make publish       Publish to PyPI"
