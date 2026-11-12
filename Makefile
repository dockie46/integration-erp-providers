SHELL := /bin/bash

.PHONY: help init test clean

help:
	@echo "Targets: init, test, clean"

init:
	@uv sync
	@echo "Not active — run: source .venv/bin/activate"

test: init
	@uv run pytest

clean:
	@rm -rf .venv .ruff_cache .pytest_cache
	@find . -type d -name '__pycache__' -not -path './.git/*' -exec rm -rf {} + 2>/dev/null || true

