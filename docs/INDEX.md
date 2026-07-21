# 📚 CAMELOT-OS — Documentation Master Index

**Version:** v1000-EXCALIBUR-A (single-host architecture)  
**Last Updated:** 2026-07-20  
**Status:** 🟢 Current

> ⚠️ **Architecture Pivot (June 2026):** CAMELOT-OS moved from a distributed
> 3-node cluster (Redis/Qdrant/Docker) to a single-host local-first architecture
> (SQLite/FirnFlow). Documents marked ⚠️ **HISTORICAL** reference the pre-pivot
> architecture and are preserved for reference only. See
> [`docs/historical/README.md`](historical/README.md) for details.

---

## 🏛️ Root-Level Entry Points (Always Current)

| Document | Purpose |
|----------|---------|
| [`README.md`](../README.md) | Project overview, quick start, architecture summary |
| [`AGENTS.md`](../AGENTS.md) | Agent constitution, knight roster, runic commands |
| [`ACT.md`](../ACT.md) | Northstar Phase 1 & 2 activity log |
| [`harness.md`](../harness.md) | Codex meta-harness adapter contract |
| [`PROVENANCE_LEDGER.md`](../PROVENANCE_LEDGER.md) | Immutable change log (hook-owned) |
| [`TODO.md`](../TODO.md) | Active task tracking |
| [`tasks.md`](../tasks.md) | Remediation task checklist |

---

## 🏗️ Architecture

| Document | Status | Description |
|----------|--------|-------------|
| [`architecture/ARCHITECTURE.md`](architecture/ARCHITECTURE.md) | ⚠️ HISTORICAL | Full 6-phase architecture (references Redis/Qdrant/Docker) |
| [`architecture/ARCHITECTURE_USAGE_GUIDE.md`](architecture/ARCHITECTURE_USAGE_GUIDE.md) | ⚠️ HISTORICAL | Usage patterns for 3-node cluster |
| [`architecture/DESIGN.md`](architecture/DESIGN.md) | ✅ Current | UI/UX design system and tokens |
| [`architecture/blueprint.md`](architecture/blueprint.md) | ✅ Current | Review remediation blueprint |
| [`architecture/entiremap.md`](architecture/entiremap.md) | ✅ Current | Full system map |
| [`architecture/UI_UX_ARCHITECTURE.md`](architecture/UI_UX_ARCHITECTURE.md) | ✅ Current | Frontend component architecture |
| [`architecture/EPIC_UI_DESIGN.md`](architecture/EPIC_UI_DESIGN.md) | ✅ Current | Epic UI design specifications |
| [`architecture/DISTANCE_TRAVEL_ARCHITECTURE.md`](architecture/DISTANCE_TRAVEL_ARCHITECTURE.md) | ⚠️ HISTORICAL | Multi-agent consensus routing (pre-pivot) |
| [`architecture/KNOWLEDGE_PYRAMID_ARCHITECTURE.md`](architecture/KNOWLEDGE_PYRAMID_ARCHITECTURE.md) | ⚠️ HISTORICAL | 3-tier Redis/Qdrant/CloudBrain memory |
| [`architecture/NORTHSTAR_ARCHITECTURE_BRIEF.md`](architecture/NORTHSTAR_ARCHITECTURE_BRIEF.md) | ✅ Current | Northstar Phase 1-2 architecture |
| [`architecture/HIVE_BRIDGE_FINAL.md`](architecture/HIVE_BRIDGE_FINAL.md) | ✅ Current | Hive bridge integration design |
| [`architecture/QR_PILL_BLUEPRINT.md`](architecture/QR_PILL_BLUEPRINT.md) | ✅ Current | QR Pill bootstrap design |
| [`architecture/SOVEREIGNTY_LEDGER.md`](architecture/SOVEREIGNTY_LEDGER.md) | ✅ Current | Sovereignty ledger specification |

---

## 📋 Phases (Planning & Completion)

| Document | Status | Description |
|----------|--------|-------------|
| [`phases/PHASE_F_GUIDE.md`](phases/PHASE_F_GUIDE.md) | ✅ Complete | TOON Symbolect + Kinetic Swarm |
| [`phases/PHASE_G_PLAN.md`](phases/PHASE_G_PLAN.md) | ✅ Complete | Distributed autonomy planning |
| [`phases/PHASE_H_README.md`](phases/PHASE_H_README.md) | ✅ Current | Adaptive learning overview |
| [`phases/PHASE_H_ADAPTIVE_LEARNING.md`](phases/PHASE_H_ADAPTIVE_LEARNING.md) | ✅ Current | Adaptive learning architecture |
| [`phases/PHASE_H_BASELINE.md`](phases/PHASE_H_BASELINE.md) | ✅ Current | Performance baselines |
| [`phases/PHASE_H_WEEK1_OBSERVABILITY.md`](phases/PHASE_H_WEEK1_OBSERVABILITY.md) | ✅ Complete | Week 1 observability stack |
| [`phases/PHASE_H_WEEK1_SIGNOFF.md`](phases/PHASE_H_WEEK1_SIGNOFF.md) | ✅ Complete | Week 1 sign-off |
| [`phases/PHASE_H_WEEK2_FINAL_SIGNOFF.md`](phases/PHASE_H_WEEK2_FINAL_SIGNOFF.md) | ✅ Complete | Week 2 sign-off |
| [`phases/PHASE_H_WEEK3_PLAN.md`](phases/PHASE_H_WEEK3_PLAN.md) | ✅ Current | Week 3 planning |
| [`phases/PYRAMID_IMPLEMENTATION_SUMMARY.md`](phases/PYRAMID_IMPLEMENTATION_SUMMARY.md) | ⚠️ HISTORICAL | Redundant memory pyramid (see architecture docs) |
| [`phases/QR_PILL_TASK.md`](phases/QR_PILL_TASK.md) | ✅ Complete | QR Pill implementation tasks |

*See [`docs/phases/`](phases/) for all 24 phase-related documents.*

---

## 📖 Guides

| Document | Status | Description |
|----------|--------|-------------|
| [`guides/OPERATIONS_MANUAL.md`](guides/OPERATIONS_MANUAL.md) | ⚠️ HISTORICAL | Operations runbook (references Redis/Docker) |
| [`guides/DEPLOYMENT_GUIDE.md`](guides/DEPLOYMENT_GUIDE.md) | ⚠️ HISTORICAL | Docker-based deployment guide |
| [`guides/BARE_METAL_DEPLOYMENT.md`](guides/BARE_METAL_DEPLOYMENT.md) | ⚠️ HISTORICAL | 3-node bare metal deployment |
| [`guides/BIFROST_INTEGRATION_GUIDE.md`](guides/BIFROST_INTEGRATION_GUIDE.md) | ✅ Current | Bifrost integration guide |
| [`guides/HELP.md`](guides/HELP.md) | ✅ Current | Task reference and help |
| [`guides/KNIGHT_INTERACTION_GUIDE.md`](guides/KNIGHT_INTERACTION_GUIDE.md) | ✅ Current | Knight interaction patterns |
| [`guides/INTEGRATION_GUIDE.md`](guides/INTEGRATION_GUIDE.md) | ✅ Current | Integration guide |
| [`guides/QR_PILL_MOBILE_GUIDE.md`](guides/QR_PILL_MOBILE_GUIDE.md) | ✅ Current | Mobile QR distribution guide |
| [`guides/START_TESTING.md`](guides/START_TESTING.md) | ✅ Current | Testing quick start |
| [`guides/TESTING_QUICKSTART.md`](guides/TESTING_QUICKSTART.md) | ✅ Current | Test suite quick start |
| [`guides/MONITORING_LIVE.md`](guides/MONITORING_LIVE.md) | ⚠️ HISTORICAL | 3-node cluster monitoring |
| [`guides/LIVE_MONITORING_DASHBOARD.md`](guides/LIVE_MONITORING_DASHBOARD.md) | ⚠️ HISTORICAL | Cluster dashboard setup |
| [`guides/PRODUCTION_READINESS_GUIDE.md`](guides/PRODUCTION_READINESS_GUIDE.md) | ⚠️ HISTORICAL | Pre-pivot readiness checklist |

*See [`docs/guides/`](guides/) for all 33 guides.*

---

## 📊 Reports

| Document | Status | Description |
|----------|--------|-------------|
| [`reports/HARDENING_REPORT.md`](reports/HARDENING_REPORT.md) | ✅ Current | Security hardening validation |
| [`reports/DISTANCE_TRAVEL_TEST_RESULTS.md`](reports/DISTANCE_TRAVEL_TEST_RESULTS.md) | ⚠️ HISTORICAL | Pre-pivot agent test results |
| [`reports/verification.md`](reports/verification.md) | ✅ Current | System verification results |
| [`reports/titan_audit_report.md`](reports/titan_audit_report.md) | ✅ Current | Titan audit report |
| [`reports/TITAN_AUDIT_OMEGA_2026-07-06.md`](reports/TITAN_AUDIT_OMEGA_2026-07-06.md) | ✅ Current | Omega audit 2026-07-06 |
| [`reports/NAVIGATOR_REPORT_2026-07-06.md`](reports/NAVIGATOR_REPORT_2026-07-06.md) | ✅ Current | Navigator index report |
| [`reports/colony_report.md`](reports/colony_report.md) | ✅ Current | Colony intelligence scan |

*See [`docs/reports/`](reports/) for all 71 reports and audit artifacts.*

---

## 🏛️ Historical Archives

| Document | Description |
|----------|-------------|
| [`historical/README.md`](historical/README.md) | **Why these docs are historical** |
| [`historical/COMPLETE_DELIVERY_SUMMARY.md`](historical/COMPLETE_DELIVERY_SUMMARY.md) | Pre-pivot delivery summary |
| [`historical/DELIVERY_MANIFEST.md`](historical/DELIVERY_MANIFEST.md) | Pre-pivot delivery manifest |
| [`historical/EXECUTION_COMPLETE.md`](historical/EXECUTION_COMPLETE.md) | Pre-pivot execution report |

---

## 📐 Reference

| Document | Status | Description |
|----------|--------|-------------|
| [`reference/UNIVERSAL.md`](reference/UNIVERSAL.md) | ✅ Current | Universal system definition |
| [`reference/UNIVERSAL_BOOTSTRAP_UKG_NANO.md`](reference/UNIVERSAL_BOOTSTRAP_UKG_NANO.md) | ✅ Current | UKG Nano crystal bootstrap |

---

## 🔍 How to Read This Index

- ✅ **Current** — Reflects the live v1000-EXCALIBUR-A single-host architecture
- ⚠️ **HISTORICAL** — References the deprecated Redis/Qdrant/Docker/3-node architecture; preserved for reference only
- ✅ **Complete** — Phase/sprint is finished and signed off

**Rule of thumb:** If it mentions Redis, Qdrant, Docker, or a 3-node cluster, it's historical. Trust the live source code in `control_plane/`, `01_KERNEL/`, and `02_FORGE/` over any archived document.
