# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
# SPDX-License-Identifier: MIT

"""Hermes Mixture of Agents (MoA) Routing & Self-Improving Distillation Loop.

Assimilated from Keys-Setup local inference stack into Camelot-OS.
Zero external dependencies outside Python standard library.

Architecture & Components:
  1. Two-Hook Routing Pipeline:
     - pre_llm_call: Classifies tasks (light, multimodal, gen_heavy, moa, escalation)
       and routes to cheapest competent agent.
     - post_llm_call: Captures (task, verdict, chosen_agent, route_type, drafts, cloud_gold)
       and logs to runtime state.
  2. Model Nodes & Competence Roster:
     - Qwen3.6-27B-NVFP4 (light tier: classify, extract, summarize, rewrite, short chat)
     - Nemotron-Omni (perception: multimodal audio/video/image grounding)
     - True Two-Tower / DiffusionGemma (gen_heavy delegate target: diffusion / fast parallel generation)
     - DeepSeek-V4-Flash / Gemma-4-31B (brain: reasoning, aggregation, multi-draft MoA voting)
     - Cloud Frontier (escalation fallback: hard reasoning, security audits, novel tasks)
  3. Transcript Signal Mining & LoRA Distillation:
     - Mined signal kinds: specialist, routing, aggregation, task_outcome.
     - 2.0x Gold Weighting on cloud escalations and corrections.
     - 1.5x Weighting on routing decisions (improves MoA routing logic).
     - 1.2x Weighting on aggregation decisions (improves draft voting logic).
     - 1.0x Weighting on task outcomes.
     - 0.8x Weighting on generic request dumps.
"""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Default Paths (Camelot-OS 03_VAULT Runtime State)
VAULT_RUNTIME_STATE = Path(
    os.getenv(
        "CAMELOT_RUNTIME_STATE",
        Path(__file__).resolve().parents[2] / "03_VAULT" / "runtime_state",
    )
)
DEFAULT_ROUTING_STATE = VAULT_RUNTIME_STATE / "hermes_moa_last_routing.json"
DEFAULT_ROUTING_LOG = VAULT_RUNTIME_STATE / "hermes_moa_routing_log.jsonl"
DEFAULT_MINED_TRAIN_PAIRS = VAULT_RUNTIME_STATE / "hermes_moa_train_pairs.jsonl"
DEFAULT_MOA_MANIFEST = VAULT_RUNTIME_STATE / "hermes_moa_manifest.json"

# Agent Competence & Endpoint Roster
AGENTS: Dict[str, Dict[str, Any]] = {
    "qwen36-nvfp4-a4q": {
        "endpoint": "http://10.100.10.4:8000/v1",
        "fallback_port": 8002,
        "cost": 1,
        "strengths": ["classify", "extract", "summarize", "rewrite", "short_chat", "light"],
        "max_ctx": 256000,
        "role": "light_tier",
    },
    "nemotron-omni": {
        "endpoint": "http://10.100.10.3:8001/v1",
        "fallback_port": 8001,
        "cost": 2,
        "strengths": ["multimodal", "perception", "vision", "audio", "grounding", "image"],
        "max_ctx": 128000,
        "role": "perception_node",
    },
    "deepseek-v4-flash-dspark": {
        "endpoint": "http://10.100.10.1:8000/v1",
        "fallback_port": 8000,
        "cost": 3,
        "strengths": ["reasoning", "routing", "aggregation", "tool_planning", "complex"],
        "max_ctx": 128000,
        "role": "aggregator_brain",
    },
    "twotower-diffusion": {
        "endpoint": "http://10.100.10.3:8010/generate",
        "fallback_port": 8010,
        "cost": 1,
        "strengths": ["gen_heavy", "batch", "bulk", "diffusion", "parallel_generate"],
        "max_ctx": 65536,
        "role": "delegate_target",
    },
}

CLOUD_AGENTS: Dict[str, Dict[str, Any]] = {
    "codex:gpt-5.5": {"cost": 10, "strength": "hard_reasoning"},
    "anthropic/claude-opus-4.8": {"cost": 12, "strength": "audit"},
    "grok": {"cost": 8, "strength": "research"},
}

# Regex Classifiers for Intelligent MoA Routing
LIGHT_PATTERNS = re.compile(
    r"^(classif|extract|summar|rewrit|short|transl|format|pars|convert|list|"
    r"what is|who is|define|explain briefly|yes|no|true|false|hello|hi)\b",
    re.IGNORECASE,
)
LIGHT_LENGTH_THRESHOLD = 100

MULTIMODAL_PATTERNS = re.compile(
    r"\b(image|picture|photo|screenshot|audio|video|speech|voice|see|look|describe.*(image|photo|screen))\b",
    re.IGNORECASE,
)

GEN_HEAVY_PATTERNS = re.compile(
    r"\b(generat\w*|produc\w*|creat\w*|write\w*|batch|bulk|many|repetitive|diffus\w*|render\w*)\b",
    re.IGNORECASE,
)

HARD_PATTERNS = re.compile(
    r"\b(audit|security|vulnerab|exploit|research|deep.*(analys|review)|"
    r"complex|difficult|hard|novel|unprecedented)\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Classification & Routing
# ---------------------------------------------------------------------------


def classify_task(task_text: str) -> str:
    """Classify a task into a routing category.

    Order of evaluation:
      1. gen_heavy -> diffusion / two-tower delegate target
      2. hard -> cloud escalation target
      3. multimodal -> perception node
      4. light -> lightweight fast model (<100 chars or light keywords)
      5. moa -> multi-draft / ambiguous aggregator fan-out
    """
    if not task_text:
        return "light"

    first_line = task_text.split("\n")[0].strip()

    if GEN_HEAVY_PATTERNS.search(task_text):
        return "gen_heavy"

    if HARD_PATTERNS.search(task_text):
        return "hard"

    if MULTIMODAL_PATTERNS.search(task_text):
        return "multimodal"

    if LIGHT_PATTERNS.match(first_line) or len(task_text) < LIGHT_LENGTH_THRESHOLD:
        return "light"

    return "moa"


def route_task(
    task_text: str, has_multimodal_input: bool = False
) -> Tuple[str, str, Optional[str]]:
    """Determine the best agent for a task according to the cheapest competent agent policy.

    Returns:
      (chosen_agent, route_type, cloud_gold)
    """
    if has_multimodal_input:
        return "nemotron-omni", "perception", None

    category = classify_task(task_text)

    if category == "light":
        return "qwen36-nvfp4-a4q", "light", None

    if category == "multimodal":
        return "nemotron-omni", "perception", None

    if category == "gen_heavy":
        # Routes to DSV4F which delegates to Two-Tower diffusion target
        return "deepseek-v4-flash-dspark", "gen_heavy", None

    if category == "hard":
        # Escalate to cloud frontier (marks 2.0x gold weighting signal)
        return "deepseek-v4-flash-dspark", "escalation", "cloud"

    # Default: MoA fan-out
    return "deepseek-v4-flash-dspark", "moa", None


# ---------------------------------------------------------------------------
# Pre and Post LLM Call Hooks
# ---------------------------------------------------------------------------


class HermesMoAHookPipeline:
    """Two-hook pipeline for intelligent MoA routing and supervision capture."""

    def __init__(
        self,
        state_file: Union[str, Path] = DEFAULT_ROUTING_STATE,
        log_file: Union[str, Path] = DEFAULT_ROUTING_LOG,
    ):
        self.state_file = Path(state_file)
        self.log_file = Path(log_file)
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def extract_task_and_multimodal(
        self, payload: Dict[str, Any]
    ) -> Tuple[str, bool, Optional[str]]:
        """Extract task text, multimodal flag, and session_id from payload."""
        extra = payload.get("extra", {})
        if isinstance(extra, str):
            try:
                extra = json.loads(extra.replace("'", '"'))
            except Exception:
                extra = {}
        extra = extra or {}

        task = (
            extra.get("user_message")
            or extra.get("prompt")
            or extra.get("task")
            or payload.get("task")
            or payload.get("prompt")
            or ""
        )
        has_multimodal = False
        session_id = payload.get("session_id") or extra.get("session_id")

        if not task:
            messages = extra.get("messages") or payload.get("messages") or []
            if isinstance(messages, list):
                for m in reversed(messages):
                    if isinstance(m, dict) and m.get("role") == "user":
                        content = m.get("content", "")
                        if isinstance(content, list):
                            has_multimodal = any(
                                isinstance(p, dict)
                                and p.get("type") in ("image_url", "image", "audio", "video")
                                for p in content
                            )
                            task = json.dumps(content)[:8000]
                        elif isinstance(content, str):
                            task = content[:8000]
                        break

        return str(task), has_multimodal, session_id

    def pre_llm_call(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Pre-LLM call classifier: routes task and writes state artifact."""
        task, has_multimodal, session_id = self.extract_task_and_multimodal(payload)
        chosen_agent, route_type, cloud_gold = route_task(task, has_multimodal)

        iso_ts = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
        decision = {
            "chosen_agent": chosen_agent,
            "route_type": route_type,
            "cloud_gold": cloud_gold,
            "ts": iso_ts,
            "session_id": session_id,
            "task": task[:2000] if task else "",
        }

        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(decision, f, indent=2)
        except Exception:
            pass

        return decision

    def post_llm_call(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Post-LLM call supervision capture: records transcript & supervision signal."""
        extra = payload.get("extra", {})
        if isinstance(extra, str):
            try:
                extra = json.loads(extra.replace("'", '"'))
            except Exception:
                extra = {}
        extra = extra or {}

        # Read last routing state if present
        routing: Dict[str, Any] = {}
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    routing = json.load(f)
            except Exception:
                pass

        task, has_multimodal, session_id = self.extract_task_and_multimodal(payload)
        if not task and routing.get("task"):
            task = routing["task"]

        verdict = (
            extra.get("assistant_response")
            or extra.get("response")
            or extra.get("completion")
            or payload.get("verdict")
            or payload.get("response")
            or ""
        )

        # Fallback to messages array
        if not task or not verdict:
            messages = extra.get("messages") or payload.get("messages") or []
            if isinstance(messages, list):
                for m in reversed(messages):
                    if isinstance(m, dict):
                        if m.get("role") == "user" and not task:
                            c = m.get("content", "")
                            task = c if isinstance(c, str) else json.dumps(c)[:8000]
                        if m.get("role") == "assistant" and not verdict:
                            c = m.get("content", "")
                            verdict = c if isinstance(c, str) else json.dumps(c)[:8000]

        if not task and not verdict:
            return None

        chosen_agent = routing.get("chosen_agent") or extra.get("model") or payload.get("model") or "unknown"
        route_type = routing.get("route_type", "unknown")
        cloud_gold = routing.get("cloud_gold")
        drafts = payload.get("drafts") or extra.get("drafts") or []

        iso_ts = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
        row = {
            "ts": iso_ts,
            "session_id": session_id or routing.get("session_id"),
            "task": task,
            "chosen_agent": chosen_agent,
            "route_type": route_type,
            "drafts": drafts if isinstance(drafts, list) else [],
            "verdict": verdict,
            "cloud_gold": cloud_gold,
        }

        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        except Exception:
            pass

        return row


# ---------------------------------------------------------------------------
# Transcript Signal Miner & Distillation
# ---------------------------------------------------------------------------


class HermesSignalMiner:
    """Mines transcripts, logs, and databases into weighted LoRA training pairs."""

    def __init__(self) -> None:
        self.pairs: List[Dict[str, Any]] = []

    def clear(self) -> None:
        self.pairs.clear()

    def add_pair(
        self,
        messages: List[Dict[str, str]],
        source: str,
        kind: str,
        weight: float,
    ) -> None:
        """Add a weighted training pair if valid."""
        if not messages or not any(m.get("content") for m in messages):
            return
        self.pairs.append({
            "messages": messages,
            "source": source,
            "kind": kind,
            "weight": float(weight),
        })

    def mine_routing_log(self, path: Union[str, Path]) -> int:
        """Mine routing log with 2.0x gold weighting on escalations and 1.5x on routing decisions."""
        p = Path(path)
        if not p.exists():
            return 0

        count = 0
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except Exception:
                    continue

                task = r.get("task")
                if not task:
                    continue

                gold = r.get("cloud_gold")
                if gold:
                    # Cloud escalation / corrected signal (2.0x gold weighting)
                    self.add_pair(
                        [
                            {"role": "user", "content": task},
                            {"role": "assistant", "content": str(r.get("verdict") or gold)},
                        ],
                        source="routing_log",
                        kind="specialist",
                        weight=2.0,
                    )
                    count += 1

                # Routing decision pair: teaches WHICH agent handles which task (1.5x weighting)
                agent = r.get("chosen_agent")
                if agent:
                    self.add_pair(
                        [
                            {
                                "role": "user",
                                "content": f"Route this task to the cheapest competent agent.\nTASK: {task}",
                            },
                            {"role": "assistant", "content": f"route: {agent}"},
                        ],
                        source="routing_log",
                        kind="routing",
                        weight=1.5,
                    )
                    count += 1

                # Aggregation preference: teaches aggregator draft voting (1.2x weighting)
                drafts = r.get("drafts")
                verdict = r.get("verdict")
                if isinstance(drafts, list) and len(drafts) > 1 and verdict:
                    self.add_pair(
                        [
                            {
                                "role": "user",
                                "content": "Pick the best answer for:\n"
                                + task
                                + "\n\nCANDIDATES:\n"
                                + "\n---\n".join(str(x) for x in drafts),
                            },
                            {"role": "assistant", "content": str(verdict)},
                        ],
                        source="routing_log",
                        kind="aggregation",
                        weight=1.2,
                    )
                    count += 1

        return count

    def mine_kanban(self, path: Union[str, Path]) -> int:
        """Mine completed tasks from a SQLite database (1.0x weighting)."""
        p = Path(path)
        if not p.exists():
            return 0

        count = 0
        try:
            conn = sqlite3.connect(f"file:{p.resolve()}?mode=ro", uri=True)
            cursor = conn.cursor()
            for tid, title, body, status in cursor.execute(
                "select id, title, body, status from tasks"
            ):
                if (status or "").lower() in ("done", "completed", "closed") and title:
                    res = ""
                    try:
                        comment_rows = cursor.execute(
                            "select body from task_comments where task_id=? order by created_at",
                            (tid,),
                        ).fetchall()
                        res = "\n".join(r[0] for r in comment_rows if r and r[0])[:4000]
                    except Exception:
                        res = ""
                    out = res or (body or "")
                    self.add_pair(
                        [
                            {
                                "role": "user",
                                "content": (title + "\n\n" + (body or "")).strip(),
                            },
                            {"role": "assistant", "content": out.strip()},
                        ],
                        source="kanban",
                        kind="task_outcome",
                        weight=1.0,
                    )
                    count += 1
            conn.close()
        except Exception:
            pass

        return count

    def mine_request_dumps(self, globpat: str) -> int:
        """Mine captured request/response JSON dumps (0.8x weighting)."""
        count = 0
        for f in glob.glob(globpat):
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    d = json.load(fh)
            except Exception:
                continue

            msgs = d.get("messages") or d.get("request", {}).get("messages")
            if isinstance(msgs, list) and msgs:
                reply = d.get("response") or d.get("completion")
                if isinstance(reply, dict):
                    reply = (
                        reply.get("choices", [{}])[0].get("message", {}) or {}
                    ).get("content")
                if reply:
                    self.add_pair(
                        msgs + [{"role": "assistant", "content": str(reply)}],
                        source="request_dump",
                        kind="specialist",
                        weight=0.8,
                    )
                    count += 1
        return count

    def save_train_pairs(self, out_path: Union[str, Path]) -> int:
        """Export all mined training pairs to JSONL."""
        out = Path(out_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            for row in self.pairs:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        return len(self.pairs)

    def summary_stats(self) -> Dict[str, Any]:
        """Compute breakdown of mined pairs by kind and total weight."""
        by_kind: Dict[str, int] = {}
        total_weight = 0.0
        for row in self.pairs:
            kind = row["kind"]
            by_kind[kind] = by_kind.get(kind, 0) + 1
            total_weight += row.get("weight", 1.0)
        return {
            "total_pairs": len(self.pairs),
            "by_kind": by_kind,
            "total_weight": round(total_weight, 2),
        }


# ---------------------------------------------------------------------------
# Camelot-OS Runtime State Manifest Exporter
# ---------------------------------------------------------------------------


def generate_moa_manifest(
    manifest_path: Union[str, Path] = DEFAULT_MOA_MANIFEST,
) -> Dict[str, Any]:
    """Generate and persist the Camelot-OS Hermes MoA system manifest."""
    manifest = {
        "status": "OK",
        "system": "CAMELOT_OS_HERMES_MOA",
        "version": "1.0.0",
        "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "routing_policy": "cheapest_competent_agent",
        "target_local_share": 0.90,
        "nodes": {
            "light_tier": {
                "model": "qwen36-nvfp4-a4q",
                "competence": AGENTS["qwen36-nvfp4-a4q"]["strengths"],
                "cost_tier": 1,
            },
            "perception": {
                "model": "nemotron-omni",
                "competence": AGENTS["nemotron-omni"]["strengths"],
                "cost_tier": 2,
            },
            "aggregator_brain": {
                "model": "deepseek-v4-flash-dspark",
                "competence": AGENTS["deepseek-v4-flash-dspark"]["strengths"],
                "cost_tier": 3,
            },
            "two_tower_diffusion": {
                "model": "twotower-diffusion",
                "competence": AGENTS["twotower-diffusion"]["strengths"],
                "cost_tier": 1,
                "api": "/generate",
            },
            "escalation_cloud": {
                "providers": list(CLOUD_AGENTS.keys()),
                "cost_tier": 10,
                "gold_weight": 2.0,
            },
        },
        "lora_distillation": {
            "trigger_threshold": 50,
            "student_model": "gemma-4-12b",
            "gold_weight": 2.0,
            "routing_weight": 1.5,
            "aggregation_weight": 1.2,
        },
    }

    out = Path(manifest_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return manifest


# ---------------------------------------------------------------------------
# CLI Entrypoint for Pre/Post Hooks & Miner
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Hermes MoA Loop for Camelot-OS")
    subparsers = parser.add_subparsers(dest="command")

    # Hook: pre_llm_call
    pre_p = subparsers.add_parser("pre_llm_call", help="Run pre-LLM routing hook")
    pre_p.add_argument("--payload", help="JSON payload or stdin if empty")

    # Hook: post_llm_call
    post_p = subparsers.add_parser("post_llm_call", help="Run post-LLM supervision hook")
    post_p.add_argument("--payload", help="JSON payload or stdin if empty")

    # Miner
    mine_p = subparsers.add_parser("mine", help="Mine signal into training pairs")
    mine_p.add_argument("--routing-log", default=str(DEFAULT_ROUTING_LOG))
    mine_p.add_argument("--kanban-db", default="")
    mine_p.add_argument("--request-dumps", default="")
    mine_p.add_argument("--out", default=str(DEFAULT_MINED_TRAIN_PAIRS))

    # Manifest
    subparsers.add_parser("manifest", help="Generate MoA runtime state manifest")

    args = parser.parse_args()
    pipeline = HermesMoAHookPipeline()

    if args.command == "pre_llm_call":
        raw = args.payload if args.payload else sys.stdin.read()
        try:
            payload = json.loads(raw) if raw.strip() else {}
        except Exception:
            payload = {}
        pipeline.pre_llm_call(payload)

    elif args.command == "post_llm_call":
        raw = args.payload if args.payload else sys.stdin.read()
        try:
            payload = json.loads(raw) if raw.strip() else {}
        except Exception:
            payload = {}
        pipeline.post_llm_call(payload)

    elif args.command == "mine":
        miner = HermesSignalMiner()
        k_count = miner.mine_kanban(args.kanban_db) if args.kanban_db else 0
        r_count = miner.mine_request_dumps(args.request_dumps) if args.request_dumps else 0
        g_count = miner.mine_routing_log(args.routing_log) if args.routing_log else 0
        total = miner.save_train_pairs(args.out)
        stats = miner.summary_stats()
        print(
            f"[mine] kanban={k_count} request_dumps={r_count} routing_log={g_count} "
            f"-> {total} pairs {stats['by_kind']} (total_weight={stats['total_weight']}) -> {args.out}"
        )

    elif args.command == "manifest":
        manifest = generate_moa_manifest()
        print(f"[manifest] Saved Hermes MoA manifest -> {DEFAULT_MOA_MANIFEST}")
        print(json.dumps(manifest, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
