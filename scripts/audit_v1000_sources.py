# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Lady M & Lady Apis — Master Audit & Source Grading for Camelot-OS v.1000

import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAW_SOURCES_PATH = Path("01_KERNEL/memory/v1000_sources_raw.json")
OUTPUT_AUDIT_PATH = Path("01_KERNEL/memory/v1000_source_grade_audit.json")

def audit_sources():
    if not RAW_SOURCES_PATH.exists():
        print(f"Error: {RAW_SOURCES_PATH} does not exist.")
        return

    sources = json.load(open(RAW_SOURCES_PATH, encoding="utf-8"))
    print(f"Total Sources to Evaluate: {len(sources)}")

    # 1. Detect Duplicates by normalized title
    title_counts = Counter()
    for s in sources:
        norm = re.sub(r"\s+", " ", s.get("title", "").strip().lower())
        title_counts[norm] += 1

    # 2. Grading Categories:
    # Grade A: Sovereign Core Architecture & Operational Truth
    # Grade B: High-Value Research, Frameworks & Technical Deep-Dives
    # Grade C: Contextual / Peripheral Supporting Material (Needs condensation)
    # Grade D: Outdated / Redundant / Stale Scaffolding (Candidate for consolidation)
    # Grade F: Ephemeral Scrap / Uncurated Note Dumps / External News Noise / Exact Duplicates (Do not meet requirements)

    graded_results = []
    category_tallies = Counter()

    for idx, s in enumerate(sources, 1):
        sid = s["id"]
        title = s.get("title", "Untitled").strip()
        title_lower = title.lower()
        norm_title = re.sub(r"\s+", " ", title_lower)

        is_dup = title_counts[norm_title] > 1
        grade = "B"
        reason = ""
        action = "KEEP"

        # Check for Grade F: Raw note dumps, exact duplicates, ephemeral external news
        if re.match(r"^all notes \d+/\d+/\d+", title_lower):
            grade = "F"
            reason = "Unstructured raw date-stamped note dump; lacks semantic boundaries and dilutes model context."
            action = "CONDENSE_AND_PURGE"
        elif any(news in title_lower for news in ["talent war", "newsletter", "beginner's guide to", "ai magazine", "forbes", "techcrunch", "business insider"]):
            grade = "F"
            reason = "Ephemeral news or generic 101 article with zero sovereign architecture relevance."
            action = "PURGE"
        elif is_dup and any(dupHdr in title_lower for dupHdr in ["all notes", "architecting the future"]):
            grade = "F"
            reason = f"Exact duplicate title across fleet ({title_counts[norm_title]} occurrences)."
            action = "PURGE_DUPLICATE"
        
        # Check for Grade D: Outdated legacy versions, superseded specs
        elif any(leg in title_lower for leg in ["v.999", "v999", "v57", "v300", "v400", "v700", "old", "deprecated", "draft 1", "elder titan"]):
            grade = "D"
            reason = "Superseded legacy protocol/draft; predates v1000.54 Singularity Lattice & WorldTree."
            action = "ARCHIVE_OR_UPDATE"
        elif title.endswith(".tmp") or "scratch" in title_lower or "untitled" in title_lower:
            grade = "D"
            reason = "Temporary scratch artifact or unnamed placeholder."
            action = "PURGE"

        # Check for Grade A: Sovereign Camelot-OS Core
        elif any(core in title_lower for core in [
            "anya", "camelot", "excalibur", "merlin", "boris", "forge", "codex",
            "kernel", "sentinel", "singularity lattice", "world tree", "worldtree",
            "bifrost", "living system constitution", "ast", "zero-trust", "hitl",
            "agentic os", "neurosymbolic", "ouroboros", "scabbard", "cartridge"
        ]):
            grade = "A"
            reason = "Sovereign Core Architecture artifact; foundational to Camelot-OS v.1000."
            action = "ANCHOR_AND_PRESERVE"

        # Check for Grade B: High-Value Research / Technical Reference
        elif any(tech in title_lower for tech in [
            "multi-agent", "agent", "swarm", "notebooklm", "antigravity",
            "modal", "webrtc", "audio", "esp32", "fastmcp", "memory", "rag",
            "prompt", "ui/ux", "graph", "triplet", "vfs", "rust", "python"
        ]):
            grade = "B"
            reason = "High-value technical research & ecosystem implementation substrate."
            action = "INDEX_IN_WORLDTREE"
        else:
            # Grade C: Peripheral
            grade = "C"
            reason = "Peripheral domain reference; acceptable but requires semantic categorization."
            action = "CONDENSE_INTO_CRYSTAL"

        category_tallies[grade] += 1
        graded_results.append({
            "index": idx,
            "id": sid,
            "title": title,
            "grade": grade,
            "reason": reason,
            "action": action,
            "is_duplicate": is_dup
        })

    print("\n--- GRADE DISTRIBUTION ---")
    for g in ["A", "B", "C", "D", "F"]:
        print(f"Grade {g}: {category_tallies[g]:3d} sources ({category_tallies[g]/len(sources)*100:.1f}%)")

    # Save detailed audit report
    OUTPUT_AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_AUDIT_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "total_sources": len(sources),
            "grade_counts": dict(category_tallies),
            "sources": graded_results
        }, f, indent=2)

    print(f"\nWrote full grading audit to {OUTPUT_AUDIT_PATH}")

    # Print sub-threshold sources (Grade D & F)
    sub_threshold = [s for s in graded_results if s["grade"] in ("D", "F")]
    print(f"\n=======================================================")
    print(f"SUB-REQUIREMENT SOURCES: {len(sub_threshold)} Sources (Grade D & F)")
    print(f"=======================================================")
    for s in sub_threshold:
        print(f"[{s['grade']}] #{s['index']:03d} [{s['action']:20s}] {s['title'][:50]:50s} | {s['reason']}")

    return graded_results

if __name__ == "__main__":
    audit_sources()

