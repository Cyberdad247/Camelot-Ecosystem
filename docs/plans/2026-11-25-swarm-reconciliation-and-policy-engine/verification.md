# Camelot-OS Swarm Reconciliation & Policy Engine Verification

Generated: 2026-11-25  
Blueprint: `docs/plans/2026-11-25-swarm-reconciliation-and-policy-engine/blueprint.md`  
Task DAG: `docs/plans/2026-11-25-swarm-reconciliation-and-policy-engine/task.md`

> [!IMPORTANT]
> Run verification blocks **sequentially** to remain strictly under the 8 GB host RAM ceiling (Global Law 3).

---

## 0. Preflight (RAM & Git State)

```powershell
$os = Get-CimInstance Win32_OperatingSystem
$freeGB = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
$usedGB = [math]::Round(($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / 1MB, 2)
Write-Output "RAM Used: ${usedGB} GB | Free: ${freeGB} GB"
git -C C:\Users\vizio\CAMELOT_OS status -sb
```

**Expected:**
- Free RAM >= `0.75 GB` (or trim idle processes before running heavy builds).
- Active branch is `feat/invisioned-marketing-digital-factory`.

---

## 1. Track 1 Verification — Swarm Tracker & Placeholder Hygiene

```powershell
Select-String -Path C:\Users\vizio\CAMELOT_OS\parallel_task_tree.md -Pattern '100\.71\.218\.75|EXECUTING'
git -C C:\Users\vizio\CAMELOT_OS ls-files apps/operations-console
```

**Expected:**
- `Select-String` returns **0 matches** for the stale IP `100.71.218.75` and **0 stale `EXECUTING`** rows in `parallel_task_tree.md`.
- `git ls-files apps/operations-console` confirms only `README.md` and `deployment-notes.md` are tracked in Git (no `.env.*` secrets tracked).

---

## 2. Track 2 Verification — `@camelot/policy-engine` (Thread D)

```powershell
Push-Location C:\Users\vizio\CAMELOT_OS\packages\policy-engine
& C:\Users\vizio\CAMELOT_OS\node_modules\.bin\tsc.cmd --noEmit
Pop-Location

Push-Location C:\Users\vizio\CAMELOT_OS
& C:\Users\vizio\CAMELOT_OS\node_modules\.bin\vitest.cmd run packages/policy-engine/src/index.test.ts
Pop-Location
```

**Expected:**
- `npx tsc --noEmit` exits `0` with 0 TypeScript errors under `strict: true`.
- `npx vitest run` exits `0` with all policy-engine test cases passing, including:
  - Allowed lifecycle transitions & RBAC enforcement
  - `RiskScoreCheck` (`riskEntropy >= 75` → `REQUIRE_MULTI_SIG`)
  - `MemoryCeilingCheck` (`nodeRamUsageMb >= 7168` → denied)
  - `requires_2fa: true` on `EDITING_BY_HUMAN -> EXECUTING`
  - `NoSecretExposure` rejection on raw secret strings
  - Terminal state immutability (`COMPLETED`, `REJECTED`, `CANCELLED`, `CRITICAL_HALT`)

---

## 3. Existing Swarm Threads Regression Check (Threads B & C)

```powershell
Push-Location C:\Users\vizio\CAMELOT_OS\apps\bifrost
go test ./...
Pop-Location

Push-Location C:\Users\vizio\CAMELOT_OS\wasm\ledger-engine
cargo check --quiet
Pop-Location
```

**Expected:**
- `go test ./...` reports `ok github.com/camelot-os/bifrost` (`exit 0`).
- `cargo check --quiet` exits `0` with no compilation errors.

---

## 4. Track 3 Preflight & Gate — `invisioned-marketing`

```powershell
Push-Location C:\Users\vizio\CAMELOT_OS
python -m squires.colony ghost apps/invisioned-marketing
npm --prefix apps/invisioned-marketing run typecheck
Pop-Location
```

**Expected:**
- `squires.colony ghost` reports **0 hardcoded secrets** in `apps/invisioned-marketing`.
- `npm --prefix apps/invisioned-marketing run typecheck` exits `0` with 0 errors.

---

## 5. Provenance & Ledger Integrity Gate

```powershell
Push-Location C:\Users\vizio\CAMELOT_OS
cmd /c .venv\Scripts\camelot.exe --json ledger status
Pop-Location
```

**Expected:**
- Output includes `"mirrors_aligned": true`.
- `PROVENANCE_LEDGER.md` was not edited manually.
