# Sir Helio: Omni-Router Purification Plan

## Objective
Unify the semantic routing logic across the Omni-Router matrix, propagate the Zero-Trust privacy shield across all execution entry points, and ensure the LATTICE_RADIANT memory pipeline is uniformly integrated across `intent_router`, `soul_router`, and `runic_router`.

## Background & Motivation
An architectural audit revealed that the Omni-Router architecture is fragmented:
1. Taxonomy parameters (e.g., privacy keywords, intent categories) are scattered between `intent_router.py` and `soul_router.py`.
2. The `runic_router.py` lacks a dynamic privacy shield, creating a vulnerability where sensitive data could be routed to cloud models via explicit runes.
3. The recently established LATTICE_RADIANT Cloud Brain sync via `HydrationManager` is active in `runic_router.py` but absent in the semantic routers (`intent_router` and `soul_router`).

## Scope & Impact
- **Impacted Files:**
  - `control_plane/taxonomy.py` (New File)
  - `control_plane/intent_router.py`
  - `control_plane/soul_router.py`
  - `control_plane/runic_router.py`

## Proposed Solution

### 1. Unified Taxonomy Ledger (`control_plane/taxonomy.py`)
Create a central registry for all semantic categories, intent keywords, terminal mappings, and privacy keywords.
- Extracted from `intent_router.py`: `IntentCategory`, `_INTENT_KEYWORDS`, `INTENT_TERMINAL_MAP`.
- Extracted from `soul_router.py`: `PRIVACY_KEYWORDS`, `KEYWORD_ROUTES`.

### 2. Upgrading `intent_router.py`
- Import taxonomies from `control_plane.taxonomy`.
- In `route_by_intent`, inject `HydrationManager` and push the text (intent) to L1/L2 memory using `store_tissue` to maintain the LATTICE_RADIANT pipeline.

### 3. Upgrading `soul_router.py`
- Import taxonomies from `control_plane.taxonomy`.
- In `SoulRouter.route`, inject `HydrationManager` and persist the routing intent locally or to NotebookLM depending on complexity.

### 4. Upgrading `runic_router.py`
- Import `PRIVACY_KEYWORDS` from `control_plane.taxonomy`.
- Add a pre-routing inspection in `route_rune`: if the explicit rune or parameter contains any privacy keyword, forcefully override the destination knight to `sir_ghost`.

## Implementation Steps
1. Create `control_plane/taxonomy.py` with the consolidated mappings.
2. Refactor `control_plane/intent_router.py` to use `taxonomy.py` and invoke `HydrationManager`.
3. Refactor `control_plane/soul_router.py` to use `taxonomy.py` and invoke `HydrationManager`.
4. Refactor `control_plane/runic_router.py` to implement the Privacy Shield override before resolving the final knight.

## Verification
- Route a task via `runic_router` with a privacy keyword (e.g., "secret") and ensure it resolves to `sir_ghost`.
- Ensure L1/L2 memory context stores are logged correctly via the intent and soul routers during regular dispatch logic.