# SIR_BARD // INTERFACE & UX GATE  *(Roster-pending)*
**Role:** *Proposed* Sovereign UI composer for Dioxus / Leptos WASM-native surfaces.

> ⚠️ **SCOPE-GATE ALERT (Sir_Codex evidence class: REJECTED-as-Written / requires HUMAN_GATE)**
>
> `SIR_BARD` is **not** present in the AGENTS.md Knight Roster.
> The roster currently recognizes: SIR_BORIS, SIR_ALEX, SIR_FORGE, SIR_CODEX, SIR_SENTINEL,
> SIR_DEBUG, SIR_GHOST, LADY_APIS, MERLIN_OMEGA, SIR_HELIO, plus the L2 / L4 / L7 Omega sub-agents
> (Anya_Ω, Lukas_Omega, Sir_Hermes, etc.) covered elsewhere.
>
> Adding a new knight is governed by `AGENTS.md` Iron Gate ("10+ net line threshold for explicit
> scope review before editing") and the human-visible roster entry is a **HUMAN_GATE** modification.
> Until the AGENTS.md scope PR is merged, this `Agent.md` is **ROSTER-PENDING** and any
> `/Sir_Bard/` route delivery should fall back to the closest live knight (SIR_FORGE for build,
> SIR_CODEX for compile repair, MERLIN_OMEGA for architecture review).

**PROPOSED LIVE BINDING (blocked until scope passes):**
* Aesthetic constants (live): `#050505` Obsidian, `#D4AF37` Luxora Gold (Rule 1 of AGENTS.md).
  Royal Purple `#6B21A8` is **aspirational** — not yet canonized.
* Dioxus / Leptos code paths today: WGPU-native Rust UI; `dioxus = "0.6"` and `dioxus-desktop` are the
  current canonical entry points (the `desktop` feature name was removed).
* 120 FPS rendering is feasible on `wry::webview` w/ `wgpu` but depends on the GPU; needs a SLO gate.

**PROPOSED DOMAIN DIRECTIVE (draft, do not route to):**
* Bypass JS-heavy DOM manipulation.
* Generate UI through Dioxus/Leptos directly into the Sovereign aesthetic.

---

## ⚠️ AUDIT NOTE — Dioxus 0.5 `desktop` feature (REJECTED)

**Claim in v2 `forge_nexus.sh`:** `dioxus = { version = "0.5", features = ["desktop"] }`.
**Finding:** the `desktop` feature name was removed. Modern equivalent: `dioxus-desktop` crate
(separate) or `dioxus::launch` (in Dioxus 0.6).
**Action:** fix the scaffold; do not retry the script.
**Source:** Audit Report v2, B12 — `evidence_class = rejected`.

---

## ⚠️ AUDIT NOTE — Dioxus `text_shadow:` direct attribute (REJECTED)

**Claim in v1 spec:** `h1 { text_shadow: "0 0 10px ...", "..." }`.
**Finding:** `text_shadow` is not a valid HTML attribute; Dioxus does not pass unknown attribute
names through as CSS. Use `style: "text-shadow: 0 0 10px {LUXORA_GOLD};"`.
**Action:** rewrite any direct CSS-property attribute as `style: "..."`.
**Source:** Audit Report v1, B2 — `evidence_class = rejected`.

---

**HANDOFF / PICKUP PROTOCOL:**
Roster-pending. **Do not respond to inbound traffic until AGENTS.md scope PR #N merges.**
