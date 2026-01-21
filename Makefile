# Use bash for shell commands
SHELL := /bin/bash
.SHELLFLAGS := -c

.PHONY: init install dev test lint format clean help setup start_env all

# Default Python version
PYTHON_VERSION ?= 3.11

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

init: ## Initialize uv and create virtual environment
	@echo "Installing uv..."
	@curl -LsSf https://astral.sh/uv/install.sh | sh
	@echo "Creating virtual environment with Python $(PYTHON_VERSION)..."
	uv venv --python $(PYTHON_VERSION)
	@echo ""
	@echo "✅ uv initialized! Activate your environment with:"
	@echo "   source .venv/bin/activate"

install: ## Install project dependencies using uv
	uv pip install -r requirements.txt

dev: ## Install all dependencies including dev tools
	uv pip install -r requirements.txt
	uv pip install -e .

sync: ## Sync dependencies with uv (faster than install)
	uv pip sync requirements.txt

test: ## Run tests with pytest
	uv run pytest

lint: ## Run linting with ruff
	uv run ruff check src/ tests/

format: ## Format code with black and ruff
	uv run black src/ tests/ notebooks/
	uv run ruff check --fix src/ tests/

typecheck: ## Run type checking with mypy
	uv run mypy src/

clean: ## Clean up cache and build files
	rm -rf .venv
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

start_env: ## One command to init uv, create venv, install deps, and activate
	@echo "Installing uv..."
	@curl -LsSf https://astral.sh/uv/install.sh | sh
	@echo "Creating virtual environment with Python $(PYTHON_VERSION)..."
	uv venv --python $(PYTHON_VERSION)
	@echo "Installing dependencies..."
	uv pip install -r requirements.txt
	@echo ""
	@echo "✅ Setup complete! Launching shell with activated environment..."
	@bash --rcfile <(echo '. ~/.bashrc; source .venv/bin/activate; echo "🐍 Virtual environment activated!"')

all: init install ## Initialize uv and install all dependencies
