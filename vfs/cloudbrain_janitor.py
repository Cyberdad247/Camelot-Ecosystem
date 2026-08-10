# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — VFS Cloudbrain Janitorial Service
"""
Organizes the NotebookLM system across Anya, Merlin, and Camelot v1000.
Implements VFS Token Reduction by distilling high-entropy code paths into
compressed Anya Glyphs, purging redundancy from the Cloudbrain.
"""

import logging
import os
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
LOG = logging.getLogger("Notebook_Janitor")

CAMELOT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(CAMELOT_ROOT / "01_KERNEL"))
sys.path.append(str(CAMELOT_ROOT))

# Load the Core VFS / Brain bridges
try:
    from memory.cloudbrain_connector import CloudBrainConnector, KNIGHT_NOTEBOOKS
except ImportError:
    LOG.error("Failed to import CloudBrainConnector.")
    CloudBrainConnector = None

try:
    from vfs.anya_glyph_engine import VFSGlyphEngine
except ImportError:
    LOG.error("Failed to import VFSGlyphEngine.")
    VFSGlyphEngine = None

try:
    from forge.assimilation.core.handlers import assimilate_repo
except ImportError:
    LOG.error("Failed to import assimilate_repo protocol.")
    assimilate_repo = None


class CloudbrainJanitor:
    """Autonomously audits the VFS and maintains NotebookLM token economy."""

    def __init__(self):
        # Target all available Cloudbrain nodes dynamically via Worldtree mapping
        if CloudBrainConnector:
            self.target_notebooks = list(KNIGHT_NOTEBOOKS.keys())
        else:
            self.target_notebooks = []
            
        self.connectors = {}
        
        if CloudBrainConnector:
            for knight in self.target_notebooks:
                if knight in KNIGHT_NOTEBOOKS:
                    self.connectors[knight] = CloudBrainConnector(knight_id=knight)
                    LOG.info(f"VFS Janitor connected to Cloudbrain Node: {knight}")

    def compute_token_density(self, path: Path) -> int:
        """Heuristic calculation for file token density."""
        try:
            size = path.stat().st_size
            return size // 4  # Roughly 4 bytes per token
        except OSError:
            return 0

    def run_token_reduction_sweep(self, max_tokens: int = 100000):
        """Sweep the VFS and compress dense paths into Anya Glyphs to reduce Cloudbrain bloat."""
        LOG.info("🧹 Initiating VFS Token Reduction Sweep...")
        
        ignore_dirs = {".git", "__pycache__", ".venv", "node_modules", "target", ".pytest_cache", ".ruff_cache"}
        total_tokens = 0
        heavy_paths = []

        for root, dirs, files in os.walk(CAMELOT_ROOT):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for file in files:
                fp = Path(root) / file
                if fp.suffix in {'.py', '.md', '.json', '.ts', '.tsx', '.rs', '.go'}:
                    tokens = self.compute_token_density(fp)
                    total_tokens += tokens
                    if tokens > 5000:  # Dense artifact
                        heavy_paths.append((fp, tokens))

        LOG.info(f"VFS Total Raw Token Density: ~{total_tokens} tokens")
        LOG.info(f"Identified {len(heavy_paths)} High-Density Artifacts for Glyph Compression.")

        # Trigger Anya Glyph Distillation for Heavy Paths
        if VFSGlyphEngine:
            for fp, tokens in heavy_paths[:5]:  # Limit to top 5 for the sweep
                rel_path = fp.relative_to(CAMELOT_ROOT).as_posix()
                LOG.info(f"Constricting: {rel_path} ({tokens} tokens) -> Anya Glyph")
                
                glyph = VFSGlyphEngine.construct_vfs_glyph(
                    intent_focus="Distill structural logic for Token Reduction", 
                    path=rel_path
                )
                
                if glyph and self.connectors:
                    compressed_payload = glyph.model_dump_json(indent=2)
                    # Push the compressed glyph to the target Cloudbrains
                    for name, cb in self.connectors.items():
                        cb.push_to_notebook(
                            artifact_type="note",
                            content=compressed_payload,
                            title=f"Glyph Compressed: {rel_path}"
                        )
                    LOG.info(f"✅ Successfully seeded compressed Glyph to {len(self.connectors)} Cloudbrains.")
                
                # ── Trigger //ASSIMILATION Protocol for Deep Knowledge Graph Sync ──
                if assimilate_repo:
                    LOG.info(f"⚡ Engaging //ASSIMILATION Protocol on {rel_path} (Harmony Gate)")
                    try:
                        # Assumes assimilate_repo can handle the path gracefully
                        result = assimilate_repo(
                            repo_path=str(fp),
                            tags=["vfs-janitor", "token-reduction"],
                            origin="cloudbrain_janitor"
                        )
                        
                        if result and getattr(result, "report_path", None):
                            report_content = f"Assimilation Status: {result.status}\nLedger ID: {getattr(result, 'ledger_entry_id', 'N/A')}\n"
                            try:
                                if os.path.exists(result.report_path):
                                    with open(result.report_path, "r", encoding="utf-8") as rf:
                                        report_content += rf.read()
                            except Exception:
                                pass
                                
                            # Push the Assimilation Report to the Notebooks
                            for name, cb in self.connectors.items():
                                cb.push_to_notebook(
                                    artifact_type="source",
                                    content=report_content,
                                    title=f"Assimilation Report: {rel_path}"
                                )
                            LOG.info(f"✅ Synced //ASSIMILATION Report to Cloudbrains.")
                    except Exception as e:
                        LOG.error(f"//ASSIMILATION Protocol failed on {rel_path}: {e}")
        
        # Simulated Janitorial Purge of Redundant Cloudbrain Data
        self._purge_redundant_notebook_data()

    def _purge_redundant_notebook_data(self):
        """Simulate deletion of unstructured source documents from NotebookLM."""
        LOG.info("🗑️ Running Janitorial Purge on NotebookLM...")
        for name, cb in self.connectors.items():
            # In a real implementation, we would call NotebookLM API to list and delete old sources
            # e.g., cb.ws.list_sources() -> cb.ws.delete_source(id)
            LOG.info(f"[{name}] Audited memory space. Purged 0 redundant sources (Dry Run).")
        
        LOG.info("✅ VFS Janitorial Sequence Complete. System Entropy stabilized.")


if __name__ == "__main__":
    janitor = CloudbrainJanitor()
    janitor.run_token_reduction_sweep()
