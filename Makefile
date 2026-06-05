# Cryptoccino dev helper. Run `make help` for the full list.
#
# Uses Homebrew Ruby via absolute paths so system Ruby (macOS 2.6) is
# never accidentally picked up — that's the same trap as homebrew's
# python where the shell can prefer the system binary even after
# brew install.

SHELL := /bin/bash

RUBY_BREW_PREFIX := /opt/homebrew/opt/ruby
RUBY_BIN         := $(RUBY_BREW_PREFIX)/bin
BUNDLE           := $(RUBY_BIN)/bundle

PY  := .venv/bin/python
PIP := .venv/bin/pip

.DEFAULT_GOAL := help

help: ## Show this help.
	@awk 'BEGIN{FS=":.*## "; printf "Targets:\n"} /^[a-zA-Z_-]+:.*## / {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

check-ruby:
	@if [ ! -x "$(BUNDLE)" ]; then \
		echo "Homebrew Ruby's bundle not found at $(BUNDLE)."; \
		echo "Install it first:  brew install ruby"; \
		exit 1; \
	fi

install: check-ruby ## Install Ruby gems + Python dev deps.
	$(BUNDLE) config set --local path 'vendor/bundle'
	$(BUNDLE) install
	$(PIP) install -r requirements-dev.txt
	@echo
	@echo "All set. Try:  make serve"

serve: check-ruby ## Serve the site at http://localhost:4000 with live-reload.
	$(BUNDLE) exec jekyll serve --baseurl "" --livereload --incremental

build: check-ruby ## One-shot build into _site/.
	$(BUNDLE) exec jekyll build --baseurl ""

prices: ## Refresh assets/data/prices.json + assets/sparklines/*.png.
	$(PY) -m pipeline.prices

test: ## Run the pytest suite.
	$(PY) -m pytest

clean: ## Remove the local site build + Jekyll cache.
	rm -rf _site .jekyll-cache .jekyll-metadata

.PHONY: help check-ruby install serve build prices test clean
