# Camelot x Kickbox voice vertical slice — NATIVE runtime only.
# Docker artifacts are archived under archive/docker/ and unsupported
# (νKG native-runtime correction). Targets are thin wrappers over
# scripts/{build,dev-up,dev-down,status,logs,smoke}.sh.

SHELL := /bin/bash

.PHONY: build dev-up dev-down status logs smoke benchmark verify-local-only generate check-generated test test-ts test-go test-rust clean

build:
	./scripts/build.sh

dev-up:
	./scripts/dev-up.sh

dev-down:
	./scripts/dev-down.sh

status:
	./scripts/status.sh

logs:
	./scripts/logs.sh

smoke:
	./scripts/smoke.sh

benchmark:
	./scripts/benchmark.sh

## verify-local-only: mesh-off invariant (forces the conditions; no false PASS)
verify-local-only:
	./scripts/verify-local-only.sh

## generate: regenerate the Go registry + TS catalog from skills.manifest.json
generate:
	node contracts/gen/generate.mjs

## check-generated: fail if the committed generated files drifted from the manifest
check-generated:
	./scripts/check-generated.sh

## test: full slice test suite (manifest drift + TS + Go + Rust, both Rust feature sets)
test: check-generated test-ts test-go test-rust

test-ts:
	npx vitest run

test-go:
	# gofmt -l prints offenders but exits 0 — the check has to be the emptiness
	# of its output, or unformatted code sails through `make test`.
	cd gateway && test -z "$$(gofmt -l .)" || { echo "gofmt: unformatted files:"; gofmt -l gateway; exit 1; }
	cd gateway && go vet ./... && go test ./... -count=1

test-rust:
	cd .. && cargo test -p camelot-node-agent
	cd .. && cargo test -p camelot-node-agent --features vulkan

clean: dev-down
	rm -rf .run contracts/dist kickbox/dist node_modules
