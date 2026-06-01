# Rebuild Portable Binary Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Generate a fresh, up-to-date `camelot.exe` that incorporates the EXCALIBUR silicon kernel and the Sovereign Purification fixes.

**Architecture:** Use the existing `scripts/build_portable.py` orchestrator to invoke PyInstaller with the `camelot.spec` configuration. This embeds the current workspace state, including the new `02_FORGE/excalibur-dev` artifacts and `hydration_manager.py` fixes, into a single-file executable via the `_MEIPASS` asset root.

**Tech Stack:** Python 3.13, PyInstaller 6.x, `scripts/build_portable.py`.

---

### Task 1: Build Environment Verification

**Files:**
- Test: `scripts/build_portable.py` (run check)

**Step 1: Check PyInstaller availability**
Run: `python scripts/build_portable.py --check-only` (if implemented, else check manually)
Expected: PASS if PyInstaller is in venv.

**Step 2: Commit environment state**
```bash
git add scripts/build_portable.py
git commit -m "chore(build): verify build environment for portable refresh"
```

---

### Task 2: Execute Portable Build

**Files:**
- Modify: `dist/camelot.exe` (generated)

**Step 1: Run build script**
Run: `python scripts/build_portable.py`
Expected: Completion of PyInstaller bundling. Log should show "dist/camelot.exe created".

**Step 2: Verify file size growth**
Run: `(Get-Item dist/camelot.exe).Length / 1MB`
Expected: ~15.4MB to ~16.5MB (accounting for new EXCALIBUR dependencies).

---

### Task 3: Smoke Test Suite (Isolated)

**Files:**
- Test: `dist/camelot.exe`

**Step 1: Verify version and state in isolation**
Run: 
```powershell
$d = New-Item -ItemType Directory -Path "$env:TEMP\camelot-smoke-$(Get-Random)"
Copy-Item dist\camelot.exe $d
& "$d\camelot.exe" --version
& "$d\camelot.exe" --list
```
Expected: Version matches current repo state; list shows all active runes including EXCALIBUR components.

**Step 2: Verify Purification Fix (Hydration)**
Run: `& "$d\camelot.exe" --json cockpit refresh`
Expected: Success (No JSONDecodeError from L0 hydration).

---

### Task 4: Ledger Crystallization

**Files:**
- Modify: `PROVENANCE_LEDGER.md`

**Step 1: Update Ledger**
Manual Update: Add Entry #P4_BUILD_REFRESH documenting the new binary hash and date.

**Step 2: Final Sync**
Run: `python -m control_plane.cloudbrain_sync`
Expected: Cloud Brain confirms updated binary availability.

**Step 3: Commit**
```bash
git add PROVENANCE_LEDGER.md
git commit -m "chore(ledger): crystallize portable binary refresh #P4_BUILD_REFRESH"
```
