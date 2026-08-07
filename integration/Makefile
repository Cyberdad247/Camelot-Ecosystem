# Camelot x Kickbox voice vertical slice.
# Run from integration/ — nothing here touches the rest of the repository.

SHELL := /bin/bash
DEMO_DIR := .demo
LEASE_KEY ?= camelot-demo-key

.PHONY: setup build test test-ts test-go test-rust demo-up demo-down demo-dev demo-dev-down smoke clean

## setup: install JS deps and build every component locally
setup:
	npm install --no-audit --no-fund
	npm run build
	cd gateway && go build -o ../$(DEMO_DIR)/bin/gateway .
	cd .. && cargo build -p camelot-node-agent && cp target/debug/camelot-node-agent integration/$(DEMO_DIR)/bin/

build: setup

## test: full slice test suite (TS + Go + Rust, both Rust feature sets)
test: test-ts test-go test-rust

test-ts:
	npx vitest run

test-go:
	cd gateway && gofmt -l . && go vet ./... && go test ./... -count=1

test-rust:
	cd .. && cargo test -p camelot-node-agent
	cd .. && cargo test -p camelot-node-agent --features vulkan

## demo-up: full stack via Docker Compose (console on :8080)
demo-up:
	docker compose up --build -d
	@echo "Anya Console: http://localhost:8080"

demo-down:
	docker compose down

## demo-dev: bare-process stack, no Docker (console on :8080)
demo-dev:
	@mkdir -p $(DEMO_DIR)/bin
	npm install --no-audit --no-fund >/dev/null
	npm run build >/dev/null
	cd gateway && go build -o ../$(DEMO_DIR)/bin/gateway .
	cd .. && cargo build -q -p camelot-node-agent && cp target/debug/camelot-node-agent integration/$(DEMO_DIR)/bin/
	@GATEWAY_ADDR=:8788 $(DEMO_DIR)/bin/gateway > $(DEMO_DIR)/gateway.log 2>&1 & echo $$! > $(DEMO_DIR)/gateway.pid
	@CAMELOT_NODE_LEASE_KEY=$(LEASE_KEY) NODE_AGENT_ADDR=0.0.0.0:8789 $(DEMO_DIR)/bin/camelot-node-agent > $(DEMO_DIR)/node-agent.log 2>&1 & echo $$! > $(DEMO_DIR)/node-agent.pid
	@python3 -m http.server 8080 --directory . > $(DEMO_DIR)/console.log 2>&1 & echo $$! > $(DEMO_DIR)/console.pid
	@sleep 1
	@echo "Anya Console: http://localhost:8080/kickbox/"
	@echo "Gateway:      http://localhost:8788/healthz"
	@echo "Node agent:   http://localhost:8789/healthz"
	@echo "Stop with:    make demo-dev-down"

demo-dev-down:
	-@for p in gateway node-agent console; do \
		[ -f $(DEMO_DIR)/$$p.pid ] && kill $$(cat $(DEMO_DIR)/$$p.pid) 2>/dev/null; \
		rm -f $(DEMO_DIR)/$$p.pid; \
	done; true

## smoke: end-to-end proof against a running stack (demo-dev or demo-up)
smoke:
	LEASE_KEY=$(LEASE_KEY) ./scripts/smoke.sh

clean: demo-dev-down
	rm -rf $(DEMO_DIR) contracts/dist kickbox/dist node_modules
