# Camelot x Kickbox voice vertical slice — NATIVE runtime only.
# Docker artifacts are archived under archive/docker/ and unsupported
# (νKG native-runtime correction). Targets are thin wrappers over
# scripts/{build,dev-up,dev-down,status,logs,smoke}.sh.

SHELL := /bin/bash

.PHONY: build dev-up dev-down status logs smoke test test-ts test-go test-rust clean

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

## test: full slice test suite (TS + Go + Rust, both Rust feature sets)
test: test-ts test-go test-rust

test-ts:
	npx vitest run

test-go:
	cd gateway && gofmt -l . && go vet ./... && go test ./... -count=1

test-rust:
	cd .. && cargo test -p camelot-node-agent
	cd .. && cargo test -p camelot-node-agent --features vulkan

clean: dev-down
	rm -rf .runtime contracts/dist kickbox/dist node_modules
