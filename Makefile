# Cryptoccino dev helper. Run `make help` for the full list.
#
# Brings Homebrew Ruby in via PATH so the user doesn't need to edit ~/.zshrc.
# If Ruby isn't installed via Homebrew (`brew install ruby`), targets that
# need Ruby will print a clear setup hint.

SHELL := /bin/bash

RUBY_BREW_PREFIX := /opt/homebrew/opt/ruby
RUBY_BIN         := $(RUBY_BREW_PREFIX)/bin
export PATH      := $(RUBY_BIN):$(PATH)

PY  := .venv/bin/python
PIP := .venv/bin/pip

.DEFAULT_GOAL := help

help: ## Show this help.
	@awk 'BEGIN{FS=":.*## "; printf "Targets:\n"} /^[a-zA-Z_-]+:.*## / {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

check-ruby:
	@if [ ! -d "$(RUBY_BREW_PREFIX)" ]; then \
		echo "Homebrew Ruby not found at $(RUBY_BREW_PREFIX)."; \
		echo "Install it first:  brew install ruby"; \
		exit 1; \
	fi

install: check-ruby ## Install Ruby gems + Python dev deps.
	bundle config set --local path 'vendor/bundle'
	bundle install
	$(PIP) install -r requirements-dev.txt
	@echo
	@echo "All set. Try:  make serve"

serve: check-ruby ## Serve the site at http://localhost:4000 with live-reload.
	bundle exec jekyll serve --baseurl "" --livereload --incremental

build: check-ruby ## One-shot build into _site/.
	bundle exec jekyll build --baseurl ""

prices: ## Refresh assets/data/prices.json + assets/sparklines/*.png.
	$(PY) -m pipeline.prices

test: ## Run the pytest suite.
	$(PY) -m pytest

clean: ## Remove the local site build + Jekyll cache.
	rm -rf _site .jekyll-cache .jekyll-metadata

.PHONY: help check-ruby install serve build prices test clean
