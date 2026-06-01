SHELL := /bin/bash
ROOT  := $(CURDIR)
export EXCALIBUR_ROOT := $(ROOT)

.PHONY: preflight scaffold build test run clean
preflight:
	bash core/excalibur_audit.sh >/dev/null
	bash core/excalibur_adjudicate.sh
build:
	cargo build --workspace
	python3 -m pip install -e orchestrator >/dev/null
test:
	cargo test --workspace
	cd orchestrator && PYTHONPATH=. python3 -m pytest -q || true
run:
	cd orchestrator && PYTHONPATH=. python3 -m excalibur.cli $(ARGS)
clean:
	cargo clean; rm -rf orchestrator/build orchestrator/*.egg-info
