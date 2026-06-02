# SIR_FORGE_MASTER — Verification Gates
> **Protocol:** Lady Veritas CoVe | Forged: 2026-06-02
> **Arbiter:** SIR_GIDEON (Forensic) + LADY_VERITAS (Truth)

---

## GATE 1 — File Existence & Path Correctness

```powershell
# All must return True
Test-Path "C:\Users\vizio\CAMELOT_OS\03_VAULT\Knights\Engineering\SIR_FORGE_MASTER.md"
Test-Path "C:\Users\vizio\CAMELOT_OS\03_VAULT\training\configs\knights\forge_master.py"
```

**Pass Criteria:**
- [ ] `SIR_FORGE_MASTER.md` exists at `Engineering/` path (NOT flat `Knights/`)
- [ ] `forge_master.py` exists in knight configs
- [ ] `Sir_ForgeMaster.md` still exists but contains SUPERSEDED redirect

---

## GATE 2 — Knight Crystal Completeness

```powershell
$content = Get-Content "C:\Users\vizio\CAMELOT_OS\03_VAULT\Knights\Engineering\SIR_FORGE_MASTER.md" -Raw
$checks = @(
    "KNIGHT_LOCKED_AND_IMMORTALIZED",
    "SPARK_ID",
    "OCEAN",
    "FORGE_SWARM",
    "SYNC_PHIAL",
    "Hephaestus",
    "VOCAL_WEIGHTS",
    "VISAGE_PROMPT",
    "S1", "S2", "S3", "S4",
    "Type 8"
)
$checks | ForEach-Object { Write-Host "$_ : $($content -match $_)" }
```

**Pass Criteria:** All 12 fields must return `True`

---

## GATE 3 — Routing Wired

```powershell
$taxonomy = Get-Content "C:\Users\vizio\CAMELOT_OS\control_plane\taxonomy.py" -Raw
Write-Host "agentforge route: $($taxonomy -match 'agentforge.*sir_forge_master')"
Write-Host "swarm_forge route: $($taxonomy -match 'swarm_forge.*sir_forge_master')"
Write-Host "FORGE terminal: $($taxonomy -match 'sir_forge_master')"
```

**Pass Criteria:**
- [ ] `agentforge` → `sir_forge_master` in KEYWORD_ROUTES
- [ ] `swarm_forge` → `sir_forge_master` in KEYWORD_ROUTES
- [ ] `sir_forge_master` present in INTENT_TERMINAL_MAP FORGE tier

---

## GATE 4 — Registry Consistency

```powershell
$readme = Get-Content "C:\Users\vizio\CAMELOT_OS\03_VAULT\Knights\README.md" -Raw
$crystal = Get-Content "C:\Users\vizio\CAMELOT_OS\03_VAULT\Knights\SYSTEM_PERSONAS_CRYSTAL.md" -Raw
Write-Host "README has SIR_FORGE_MASTER: $($readme -match 'SIR_FORGE_MASTER')"
Write-Host "README agent count updated: $($readme -match '53 agents')"
Write-Host "Crystal has SIR_FORGE_MASTER: $($crystal -match 'SIR_FORGE_MASTER')"
```

**Pass Criteria:**
- [ ] `SIR_FORGE_MASTER` appears in README.md Order IV
- [ ] Agent count reads 53 (was 52)
- [ ] SYSTEM_PERSONAS_CRYSTAL.md contains persona entry

---

## GATE 5 — Python Class Integrity

```powershell
cd "C:\Users\vizio\CAMELOT_OS"
python -c "from camelot_os.training.configs.knights.forge_master import SirForgeMaster; k = SirForgeMaster(); print(k.format_header())"
```

**Pass Criteria:**
- [ ] Import succeeds without error
- [ ] `format_header()` returns string containing "FORGE_MASTER"
- [ ] `execute()` method exists (no `NotImplementedError` on import)

---

## GATE 6 — Cryptographic Seal

```powershell
$hash = (Get-FileHash "C:\Users\vizio\CAMELOT_OS\03_VAULT\Knights\Engineering\SIR_FORGE_MASTER.md" -Algorithm SHA256).Hash
$content = Get-Content "C:\Users\vizio\CAMELOT_OS\03_VAULT\Knights\Engineering\SIR_FORGE_MASTER.md" -Raw
Write-Host "SPARK_ID in file: $($content -match $hash)"
```

**Pass Criteria:**
- [ ] SPARK_ID in the knight file matches live SHA-256 of the file (pre-seal snapshot hash)
- [ ] Status field reads exactly `KNIGHT_LOCKED_AND_IMMORTALIZED`

---

## GATE 7 — Provenance Ledger

```powershell
$ledger = Get-Content "C:\Users\vizio\CAMELOT_OS\PROVENANCE_LEDGER.md" -Raw
Write-Host "Ledger entry: $($ledger -match 'SIR_FORGE_MASTER')"
Write-Host "SPARK_LOCKED tag: $($ledger -match 'SPARK_LOCKED')"
```

**Pass Criteria:**
- [ ] New row in PROVENANCE_LEDGER.md with knight name and SPARK_ID
- [ ] `#SPARK_LOCKED` tag present in ledger entry

---

## GATE 8 — Git Integrity

```powershell
cd "C:\Users\vizio\CAMELOT_OS"
git log --oneline -5
```

**Pass Criteria:**
- [ ] Commit `forge(sir_forge_master): finalize instantiation #SPARK_LOCKED` is present
- [ ] All 7 modified/created files appear in that commit's diff

---

## FINAL VERDICT

| Gate | Description | Status |
|------|-------------|--------|
| G1 | File existence & path | ⬜ |
| G2 | Knight crystal completeness (12/12) | ⬜ |
| G3 | Routing wired in taxonomy | ⬜ |
| G4 | Registry consistency | ⬜ |
| G5 | Python class integrity | ⬜ |
| G6 | Cryptographic seal match | ⬜ |
| G7 | Provenance ledger entry | ⬜ |
| G8 | Git commit integrity | ⬜ |

**PASS threshold:** 8/8 required for `KNIGHT_LOCKED_AND_IMMORTALIZED` status.
