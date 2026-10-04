ENV_NAME ?= dftgnn
HOOKS := $(shell git rev-parse --git-common-dir)/hooks

.PHONY: env test lint audit-history paper clean

env:
	mamba env create -y -f env/environment-local.yml || mamba env update -y -n $(ENV_NAME) -f env/environment-local.yml
	mamba run -n $(ENV_NAME) pip install -e . --no-deps

test:
	mamba run -n $(ENV_NAME) pytest -q

lint:
	mamba run -n $(ENV_NAME) ruff check src tests

# runs the pre-push checks over every commit reachable from HEAD
audit-history:
	@$(HOOKS)/_audit.sh HEAD && echo "audit-history: clean"

paper:
	@echo "paper: placeholder (LaTeX build not yet configured)"

clean:
	rm -rf .pytest_cache .ruff_cache build dist src/*.egg-info
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
