# Understand-Anything Assimilation Audit

## Source

- Upstream: `https://github.com/Egonex-AI/Understand-Anything`
- Plugin version observed in `.claude-plugin/plugin.json`: `2.8.2`
- Upstream contract: multi-agent codebase scan, structural graph, dashboard, diff impact, onboarding, domain view, and Karpathy-pattern knowledge wiki support.

## Camelot Fit

Camelot already has overlapping primitives:

- `control_plane/graphify.py` for deterministic triplet extraction into MemCastle.
- `control_plane/notebooklm_graphify_bridge.py` for NotebookLM/Cloudbrain corpus materialization.
- `control_plane/bio_swarm_runtime.py` for Bio-Kinetic Swarm status and evidence.
- `03_VAULT/runtime_state` for Cloudbrain and swarm artifacts.

## Implemented

- `control_plane/understand_anything_assimilation.py`
- `bin/understand_anything_assimilate.py`
- `tests/control_plane/test_understand_anything_assimilation.py`

## Behavior

The Camelot adapter writes:

- `.understand-anything/knowledge-graph.json`
- `.understand-anything/config.json`
- `.understand-anything/CAMELOT_ASSIMILATION_REPORT.md`

It includes:

- bounded source-file graph nodes
- Python import edges
- selected Cloudbrain runtime artifacts
- external NotebookLM metadata without copying secrets
- Bio-Kinetic Swarm runtime status
- dynamic Camelot version metadata

## Security Boundary

NotebookLM and `.camelot` external state are referenced by metadata only. The adapter does not copy browser tokens, credential files, or secret values into the repo graph.

