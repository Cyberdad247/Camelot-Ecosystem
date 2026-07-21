# Graphify and NotebookLM Feedback

## What Exists Now

- `control_plane/graphify.py` is a real local module, so graph projection should be implemented against that surface rather than introduced as a new parallel system.
- The repo already has notebook/mirror-oriented infrastructure in `control_plane/cloudbrain_sync.py` and `03_VAULT/training/configs/notebooklm_bridge.py`.
- The safe direction is to keep notebook mirroring read-only, provenance-first, and attached to the existing cloudbrain sync path.

## NotebookLM Source and Hosting

- NotebookLM itself is not published as open source.
- The public hosted product is `https://notebooklm.google/`, operated by Google Labs.
- That means there is no public upstream codebase to fork directly for notebook mirroring.

## Practical Open Alternatives

- `Logseq` for local-first knowledge graph notes.
- `ORKG` for structured research graph hosting.
- `TerminusDB` if the goal is a versioned knowledge graph backend.

## Recommendation

If the target is "Graphify mirroring Cloudbrain," implement it as:

1. A graph export layer from repository and cloudbrain state.
2. A provenance stamp for every mirrored node and edge.
3. A read-only notebook surface for retrieval and synthesis.
4. A separate operator gate for any write action.

## Risk Notes

- Do not assume NotebookLM source availability where none exists.
- Do not couple graph extraction to live mutation hooks.
- Do not hide notebook sync behind a generic sync command without explicit operator labeling.

