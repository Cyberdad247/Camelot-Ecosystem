# Fixture: untrusted_memory_promotion

Untrusted external content (Tier 4 quarantine, e.g. NotebookLM, opened
documents, scraped pages) attempts promotion to Tier 1/2 verified memory
without VFS admission and a retrieval lease.

Verify: `memory_promotion_verified` fails; promotion denied; content stays
in quarantine; no verified-memory claim made (§15.1, §15.3).
