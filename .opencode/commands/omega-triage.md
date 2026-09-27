---
description: OMEGA Triage and Crucible pipeline for CAMELOT-OS. Runs Anya triage, Socratic dialectic, firewall plus Z3 fabrication check, and the 5-probe crucible.
---

Run the OMEGA Triage and Crucible DAG on this payload:

1. Run `python -m control_plane.runes.runic_router --rune OMEGA_TRIAGE --task "$ARGUMENTS"`.
2. Read the verdict: GO_SIGNAL (sealed with the sovereign glyph), REZERO_* (routed back with reasons), or HALT_GATE_BLOCKED (Anya refused).
3. REZERO verdicts are instructions, not failures — return the flaws and probes to the forge, never force past them.
4. For the full report dict run `python -m control_plane.infra.omega_triage_crucible "$ARGUMENTS"`.

Payload: $ARGUMENTS
