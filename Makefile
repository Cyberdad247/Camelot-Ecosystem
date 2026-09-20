# SPDX-License-Identifier: MIT
# CAMELOT-OS native runbook for the Operator Console (slice #2).
# Design §15. Native local processes only — no Docker.

BIFROST := cd apps/bifrost
PWA := cd apps/pwa
OPERATOR_FIXTURE_TASK ?= operator-console-approval

.PHONY: dev-up status smoke operator-console operator-console-fixture-readonly \
        operator-console-fixture-approval operator-console-fixture-tamper \
        benchmark-operator-console logs dev-down win-status win-smoke

dev-up: ## Start native service set: Bifrost (fixture mode) + PWA
	@echo "[operator] starting Bifrost (fixture=$(OPERATOR_FIXTURE_TASK)) + PWA"
	@OPERATOR_FIXTURE_TASK=$(OPERATOR_FIXTURE_TASK) $(BIFROST) && npm run dev & \
	$(PWA) && npm run dev

status: ## Report native service health (POSIX: curl)
	@curl -s http://127.0.0.1:3001/health || echo "bifrost down"
	@curl -s http://127.0.0.1:3000/ || echo "pwa down"

win-status: ## Report native service health (Windows PowerShell, no curl/make fork)
	@powershell -NoProfile -Command "try { (New-Object System.Net.Sockets.TcpClient).BeginConnect('127.0.0.1',3001,$null,$null).AsyncWaitHandle.WaitOne(2000) } catch { $$false }" | findstr /i true >NUL && echo bifrost up || echo bifrost down
	@powershell -NoProfile -Command "try { (New-Object System.Net.Sockets.TcpClient).BeginConnect('127.0.0.1',3000,$null,$null).AsyncWaitHandle.WaitOne(2000) } catch { $$false }" | findstr /i true >NUL && echo pwa up || echo pwa down

win-smoke: ## Windows-safe rapid loop: scoped vitest + PWA typecheck (no make fork)
	cd apps/bifrost && npm run test:bifrost
	cd apps/pwa && npm run typecheck

smoke: ## Bifrost unit tests + PWA data-layer tests + typechecks
	$(BIFROST) && node ../../node_modules/vitest/vitest.mjs run src/operator
	$(PWA) && node ../../node_modules/vitest/vitest.mjs run src/lib/operator_console
	$(PWA) && npm run typecheck

operator-console: ## Run the PWA dev server for the console
	$(PWA) && npm run dev

operator-console-fixture-readonly:
	@OPERATOR_FIXTURE_TASK=operator-console-readonly-audit $(MAKE) dev-up

operator-console-fixture-approval:
	@OPERATOR_FIXTURE_TASK=operator-console-approval $(MAKE) dev-up

operator-console-fixture-tamper:
	@OPERATOR_FIXTURE_TASK=operator-console-integrity-failure $(MAKE) dev-up

benchmark-operator-console: ## p95 event-to-render latency + resource budget
	bash harness/benchmarks/operator-console-event-latency.sh
	bash harness/benchmarks/operator-console-resource-budget.sh

logs: ## Tail Bifrost logs for a task
	@echo "TASK_ID=$(TASK_ID) — see apps/bifrost output (native console)"

dev-down: ## Stop the native service set
	@echo "[operator] stopping native services (Ctrl-C the foreground procs)"
