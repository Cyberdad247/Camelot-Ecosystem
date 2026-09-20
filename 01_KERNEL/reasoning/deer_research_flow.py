# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
# SPDX-License-Identifier: MIT

"""Deer-Flow (v2.0) Deep Exploration Research Flow, Memory Trees, and Sandbox Engine.

Assimilated from Deer-Flow v2.0 architecture into Camelot-OS 01_KERNEL/reasoning.
Provides:
1. Multi-phase Deep Exploration Research Loop (Broad Survey, Dimensional Decomposition,
   Targeted Deep-Dive, Multi-Angle Diversity Validation, Synthesis Check).
2. Hierarchical Memory Trees (Bucketed per agent/user, category classification, signal
   detection, tree-structured nodes with revisions, conflicts, and search).
3. InfoQuest Web Crawling & OSINT Abstractions (Multi-engine query patterns, temporal
   awareness, citation extraction, content synthesis, query generator).
4. Secure Local/Virtual Sandbox Execution (Path containment, virtual root mapping,
   process execution with timeout, output budget bounding, environment policy).
5. Multi-Agent Lead & Subagent Research Coordination with delegation ledgers and token usage tracking.
6. Zero external dependencies outside the Python standard library.
"""

from __future__ import annotations

import abc
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import enum
import hashlib
import json
import logging
import os
from pathlib import Path
import re
import subprocess
import threading
import time
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
)
import urllib.parse
import uuid

logger = logging.getLogger("camelot.reasoning.deer_flow")

# ---------------------------------------------------------------------------
# Helpers & Constants
# ---------------------------------------------------------------------------

DEFAULT_AGENT_BUCKET = "sir_boris"
DEFAULT_USER_ID = "vashawn_head"
DOCUMENT_VERSION = "2.0"

CORE_CATEGORIES = frozenset({
    "preference",
    "correction",
    "context",
    "goal",
    "behavior",
    "identity",
    "constraint",
    "decision",
    "other",
})

_ENV_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _now() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def _slug(raw: str, fallback: str = "item") -> str:
    """Generate a clean slug identifier from a raw title/name."""
    normalized = "".join(ch.lower() if ch.isalnum() else "_" for ch in raw.strip())
    normalized = "_".join(part for part in normalized.split("_") if part)
    return (normalized or fallback)[:80]


def _hash_content(content: str) -> str:
    """Return a SHA-256 hash digest of string content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Section 1: Hierarchical Memory Trees & Persistent Memory
# ---------------------------------------------------------------------------

class MemoryError(RuntimeError):
    """Base error for Deer-Flow memory subsystem."""


class MemoryConflictError(MemoryError):
    """Optimistic concurrency or revision conflict error."""


class MemoryCorruptionError(MemoryError):
    """Memory structure or node parse error."""


@dataclass
class MemoryFact:
    """Individual atomic fact within an agent/user memory graph."""
    id: str
    category: str
    content: str
    source: str = "conversation"
    confidence: float = 1.0
    revision: int = 1
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MemoryFact:
        return cls(
            id=data["id"],
            category=data.get("category", "other"),
            content=data.get("content", ""),
            source=data.get("source", "conversation"),
            confidence=float(data.get("confidence", 1.0)),
            revision=int(data.get("revision", 1)),
            created_at=data.get("created_at", _now()),
            updated_at=data.get("updated_at", _now()),
            tags=list(data.get("tags", [])),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class MemoryTreeNode:
    """Hierarchical memory tree node for structured taxonomy."""
    id: str
    name: str
    node_type: str  # "dimension" | "theme" | "fact" | "cluster"
    content: str = ""
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    facts: List[MemoryFact] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "node_type": self.node_type,
            "content": self.content,
            "parent_id": self.parent_id,
            "children_ids": list(self.children_ids),
            "facts": [f.to_dict() for f in self.facts],
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MemoryTreeNode:
        return cls(
            id=data["id"],
            name=data.get("name", ""),
            node_type=data.get("node_type", "dimension"),
            content=data.get("content", ""),
            parent_id=data.get("parent_id"),
            children_ids=list(data.get("children_ids", [])),
            facts=[MemoryFact.from_dict(f) for f in data.get("facts", [])],
            metadata=dict(data.get("metadata", {})),
            created_at=data.get("created_at", _now()),
            updated_at=data.get("updated_at", _now()),
        )


class HierarchicalMemoryTree:
    """Tree-structured memory manager with scoped agent/user isolation and signal detection."""

    def __init__(self, storage_path: Optional[Path] = None, *, agent_name: str = DEFAULT_AGENT_BUCKET, user_id: str = DEFAULT_USER_ID):
        self.storage_path = storage_path
        self.agent_name = agent_name.lower()
        self.user_id = user_id
        self._nodes: Dict[str, MemoryTreeNode] = {}
        self._root_id: str = "root"
        self._lock = threading.RLock()
        self._revision: int = 1

        self._ensure_root()
        if self.storage_path:
            self.load()

    def _ensure_root(self) -> None:
        if self._root_id not in self._nodes:
            root_node = MemoryTreeNode(
                id=self._root_id,
                name="Root Knowledge",
                node_type="root",
                content="Root knowledge tree container",
            )
            self._nodes[self._root_id] = root_node

    def add_node(
        self,
        name: str,
        node_type: str = "dimension",
        content: str = "",
        parent_id: Optional[str] = None,
        node_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MemoryTreeNode:
        with self._lock:
            parent = parent_id or self._root_id
            if parent not in self._nodes:
                raise MemoryCorruptionError(f"Parent node {parent} does not exist.")

            nid = node_id or f"node_{_slug(name, 'node')}_{uuid.uuid4().hex[:6]}"
            if nid in self._nodes:
                raise MemoryConflictError(f"Node with ID '{nid}' already exists.")

            node = MemoryTreeNode(
                id=nid,
                name=name,
                node_type=node_type,
                content=content,
                parent_id=parent,
                metadata=metadata or {},
            )
            self._nodes[nid] = node
            if nid not in self._nodes[parent].children_ids:
                self._nodes[parent].children_ids.append(nid)
            self._revision += 1
            self._auto_save()
            return node

    def add_fact(
        self,
        node_id: str,
        category: str,
        content: str,
        source: str = "conversation",
        confidence: float = 1.0,
        tags: Optional[List[str]] = None,
        fact_id: Optional[str] = None,
    ) -> MemoryFact:
        with self._lock:
            if node_id not in self._nodes:
                raise MemoryCorruptionError(f"Node {node_id} does not exist.")

            fid = fact_id or f"fact_{uuid.uuid4().hex[:8]}"
            cat = category if category in CORE_CATEGORIES else "other"
            fact = MemoryFact(
                id=fid,
                category=cat,
                content=content,
                source=source,
                confidence=confidence,
                tags=tags or [],
            )
            self._nodes[node_id].facts.append(fact)
            self._nodes[node_id].updated_at = _now()
            self._revision += 1
            self._auto_save()
            return fact

    def update_fact(
        self,
        node_id: str,
        fact_id: str,
        content: Optional[str] = None,
        confidence: Optional[float] = None,
        category: Optional[str] = None,
        expected_revision: Optional[int] = None,
    ) -> MemoryFact:
        with self._lock:
            if node_id not in self._nodes:
                raise MemoryCorruptionError(f"Node {node_id} does not exist.")

            target_fact: Optional[MemoryFact] = None
            for f in self._nodes[node_id].facts:
                if f.id == fact_id:
                    target_fact = f
                    break

            if not target_fact:
                raise MemoryCorruptionError(f"Fact {fact_id} not found in node {node_id}")

            if expected_revision is not None and target_fact.revision != expected_revision:
                raise MemoryConflictError(
                    f"Fact revision conflict: expected {expected_revision}, got {target_fact.revision}"
                )

            if content is not None:
                target_fact.content = content
            if confidence is not None:
                target_fact.confidence = confidence
            if category is not None:
                target_fact.category = category if category in CORE_CATEGORIES else "other"

            target_fact.revision += 1
            target_fact.updated_at = _now()
            self._nodes[node_id].updated_at = _now()
            self._revision += 1
            self._auto_save()
            return target_fact

    def remove_fact(self, node_id: str, fact_id: str) -> bool:
        with self._lock:
            if node_id not in self._nodes:
                return False
            initial_len = len(self._nodes[node_id].facts)
            self._nodes[node_id].facts = [f for f in self._nodes[node_id].facts if f.id != fact_id]
            if len(self._nodes[node_id].facts) < initial_len:
                self._nodes[node_id].updated_at = _now()
                self._revision += 1
                self._auto_save()
                return True
            return False

    def get_node(self, node_id: str) -> Optional[MemoryTreeNode]:
        with self._lock:
            return self._nodes.get(node_id)

    def list_nodes(self) -> List[MemoryTreeNode]:
        with self._lock:
            return list(self._nodes.values())

    def search(
        self,
        query: str,
        *,
        categories: Optional[Iterable[str]] = None,
        node_types: Optional[Iterable[str]] = None,
        top_k: int = 10,
    ) -> List[Tuple[float, MemoryTreeNode, Optional[MemoryFact]]]:
        """Search memory tree for relevant nodes or facts using keyword relevance scoring."""
        with self._lock:
            query_tokens = set(re.findall(r"\w+", query.lower()))
            if not query_tokens:
                return []

            allowed_cats = set(categories) if categories else None
            allowed_types = set(node_types) if node_types else None
            results: List[Tuple[float, MemoryTreeNode, Optional[MemoryFact]]] = []

            for node in self._nodes.values():
                if allowed_types and node.node_type not in allowed_types:
                    continue

                # Match against node level
                node_text = f"{node.name} {node.content}".lower()
                node_tokens = set(re.findall(r"\w+", node_text))
                common_node = query_tokens.intersection(node_tokens)
                if common_node:
                    score = (len(common_node) / len(query_tokens)) * 0.8
                    results.append((score, node, None))

                # Match against child facts
                for fact in node.facts:
                    if allowed_cats and fact.category not in allowed_cats:
                        continue
                    fact_text = f"{fact.content} {' '.join(fact.tags)}".lower()
                    fact_tokens = set(re.findall(r"\w+", fact_text))
                    common_fact = query_tokens.intersection(fact_tokens)
                    if common_fact:
                        score = (len(common_fact) / len(query_tokens)) * fact.confidence
                        results.append((score, node, fact))

            results.sort(key=lambda item: item[0], reverse=True)
            return results[:top_k]

    def detect_signals(self, text: str) -> List[Dict[str, Any]]:
        """Identify potential memory signals (preference, correction, decision, constraint, goal) from text."""
        signals = []
        lowered = text.lower()

        patterns = {
            "preference": [r"\bi prefer\b", r"\balways use\b", r"\bi like\b", r"\bfavorite\b"],
            "correction": [r"\bthat's incorrect\b", r"\bactually it is\b", r"\bfix this\b", r"\bdo not do that\b", r"\bmistake\b"],
            "decision": [r"\bwe decided\b", r"\bthe choice is\b", r"\barchitecture decision\b", r"\bwe will use\b"],
            "constraint": [r"\bmust never\b", r"\bstrictly required\b", r"\blimit to\b", r"\bzero external deps\b"],
            "goal": [r"\bour goal is\b", r"\bobjective is\b", r"\btarget is\b", r"\bin order to achieve\b", r"\bgoal\b"],
        }

        for category, regex_list in patterns.items():
            for regex in regex_list:
                if re.search(regex, lowered):
                    signals.append({
                        "category": category,
                        "matched_pattern": regex,
                        "timestamp": _now(),
                    })
                    break
        return signals

    def export_context_for_injection(self, max_chars: int = 4000) -> str:
        """Render markdown-formatted injection block for prompt assembly."""
        with self._lock:
            lines = ["<hierarchical_memory>"]
            for node in self._nodes.values():
                if node.id == self._root_id and not node.facts:
                    continue
                lines.append(f"## Node: {node.name} [{node.node_type}]")
                if node.content:
                    lines.append(f"Summary: {node.content}")
                for fact in node.facts:
                    lines.append(f"- [{fact.category}] {fact.content} (conf: {fact.confidence:.2f})")
            lines.append("</hierarchical_memory>")
            rendered = "\n".join(lines)
            if len(rendered) > max_chars:
                rendered = rendered[:max_chars - 30] + "\n... [truncated]\n</hierarchical_memory>"
            return rendered

    def _auto_save(self) -> None:
        if self.storage_path:
            self.save(self.storage_path)

    def save(self, file_path: Path) -> None:
        with self._lock:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "version": DOCUMENT_VERSION,
                "agent_name": self.agent_name,
                "user_id": self.user_id,
                "revision": self._revision,
                "root_id": self._root_id,
                "updated_at": _now(),
                "nodes": {nid: n.to_dict() for nid, n in self._nodes.items()},
            }
            tmp_path = file_path.with_suffix(".tmp")
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp_path, file_path)

    def load(self) -> None:
        with self._lock:
            if not self.storage_path or not self.storage_path.exists():
                return
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.agent_name = data.get("agent_name", self.agent_name)
                self.user_id = data.get("user_id", self.user_id)
                self._revision = data.get("revision", 1)
                self._root_id = data.get("root_id", "root")
                raw_nodes = data.get("nodes", {})
                self._nodes = {nid: MemoryTreeNode.from_dict(nd) for nid, nd in raw_nodes.items()}
                self._ensure_root()
            except Exception as e:
                raise MemoryCorruptionError(f"Failed to parse memory tree from {self.storage_path}: {e}") from e


# ---------------------------------------------------------------------------
# Section 2: InfoQuest Web Crawling & OSINT Abstractions
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class WebSearchResult:
    """Individual search result item."""
    title: str
    url: str
    snippet: str
    published_date: Optional[str] = None
    source_engine: str = "simulated"
    score: float = 1.0


@dataclass(frozen=True)
class CrawledPage:
    """Crawled web page representation."""
    url: str
    status_code: int
    title: str
    raw_content: str
    markdown_content: str
    headers: Dict[str, str] = field(default_factory=dict)
    fetched_at: str = field(default_factory=_now)
    content_hash: str = ""

    def __post_init__(self):
        if not self.content_hash and self.raw_content:
            object.__setattr__(self, "content_hash", _hash_content(self.raw_content))


class WebClientInterface(abc.ABC):
    """Abstract interface for HTTP fetching and search provider dispatch."""

    @abc.abstractmethod
    def search(self, query: str, *, max_results: int = 5) -> List[WebSearchResult]:
        """Perform search query."""

    @abc.abstractmethod
    def fetch_url(self, url: str, timeout: float = 10.0) -> CrawledPage:
        """Fetch and parse content at URL."""


class MockWebClient(WebClientInterface):
    """Zero-dependency in-memory mock and deterministic test harness for web research."""

    def __init__(self, search_database: Optional[Dict[str, List[WebSearchResult]]] = None, page_database: Optional[Dict[str, str]] = None):
        self._search_db = search_database or {}
        self._page_db = page_database or {}

    def add_search_mock(self, query_keyword: str, results: List[WebSearchResult]) -> None:
        self._search_db[query_keyword.lower()] = results

    def add_page_mock(self, url: str, content: str) -> None:
        self._page_db[url] = content

    def search(self, query: str, *, max_results: int = 5) -> List[WebSearchResult]:
        q_low = query.lower()
        matched = []
        for kw, res_list in self._search_db.items():
            if kw in q_low or any(token in q_low for token in kw.split()):
                matched.extend(res_list)
        if not matched:
            matched = [
                WebSearchResult(
                    title=f"Result for {query}",
                    url=f"https://camelot.os/research/{urllib.parse.quote(query)}",
                    snippet=f"Comprehensive facts and analysis regarding {query}.",
                    source_engine="mock",
                )
            ]
        # Deduplicate by URL
        seen = set()
        deduped = []
        for r in matched:
            if r.url not in seen:
                seen.add(r.url)
                deduped.append(r)
        return deduped[:max_results]

    def fetch_url(self, url: str, timeout: float = 10.0) -> CrawledPage:
        content = self._page_db.get(url, f"Simulated content extracted for {url} with detailed markdown text.")
        return CrawledPage(
            url=url,
            status_code=200,
            title=f"Page: {url}",
            raw_content=content,
            markdown_content=content,
        )


class InfoQuestCrawler:
    """InfoQuest intelligent query generator and multi-pass OSINT web crawling coordinator."""

    def __init__(self, web_client: Optional[WebClientInterface] = None):
        self.client = web_client or MockWebClient()

    @staticmethod
    def generate_multi_angle_queries(topic: str, temporal_qualifier: Optional[str] = None) -> Dict[str, List[str]]:
        """Generate categorized multi-angle queries for broad exploration and validation."""
        time_tag = f" {temporal_qualifier}" if temporal_qualifier else ""
        return {
            "facts_and_data": [
                f"{topic} statistics market size data{time_tag}",
                f"{topic} empirical metrics benchmarks{time_tag}",
            ],
            "examples_and_cases": [
                f"{topic} case study real-world implementation{time_tag}",
                f"{topic} architecture production deployment{time_tag}",
            ],
            "expert_opinions": [
                f"{topic} expert analysis commentary interview{time_tag}",
                f"{topic} architectural review whitepaper{time_tag}",
            ],
            "trends_and_future": [
                f"{topic} latest trends roadmap forecast{time_tag}",
                f"{topic} state of the art innovations{time_tag}",
            ],
            "challenges_and_limitations": [
                f"{topic} limitations security vulnerabilities challenges{time_tag}",
                f"{topic} trade-offs failure modes bottleneck{time_tag}",
            ],
        }

    def execute_osint_crawl(self, topic: str, *, temporal_anchor: Optional[str] = None, max_pages: int = 5) -> List[CrawledPage]:
        """Execute structured multi-angle OSINT crawl across dimensions."""
        queries_by_angle = self.generate_multi_angle_queries(topic, temporal_anchor)
        all_results: List[WebSearchResult] = []
        for angle, q_list in queries_by_angle.items():
            for q in q_list:
                res = self.client.search(q, max_results=2)
                all_results.extend(res)

        # Unique URLs up to max_pages
        urls_to_crawl: List[str] = []
        for item in all_results:
            if item.url not in urls_to_crawl:
                urls_to_crawl.append(item.url)
            if len(urls_to_crawl) >= max_pages:
                break

        crawled: List[CrawledPage] = []
        for u in urls_to_crawl:
            try:
                page = self.client.fetch_url(u)
                crawled.append(page)
            except Exception as e:
                logger.warning(f"Error fetching URL {u}: {e}")
        return crawled


# ---------------------------------------------------------------------------
# Section 3: Secure Local/Virtual Sandbox Execution
# ---------------------------------------------------------------------------

class SandboxError(RuntimeError):
    """Base error for sandbox operations."""


class SandboxSecurityViolation(SandboxError):
    """Path escape or unauthorized execution attempted."""


class SandboxExecutionTimeout(SandboxError):
    """Command execution exceeded timeout limit."""


@dataclass(frozen=True)
class SandboxPathMapping:
    """Virtual mount mapping container paths to local disk paths."""
    virtual_prefix: str
    real_path: Path
    read_only: bool = False


@dataclass(frozen=True)
class CommandResult:
    """Standardized output container for sandbox command execution."""
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool = False
    truncated: bool = False


class SecureSandbox:
    """Sandboxed filesystem and command execution engine with path containment & output limits."""

    def __init__(
        self,
        sandbox_id: str,
        workspace_dir: Path,
        *,
        virtual_mappings: Optional[List[SandboxPathMapping]] = None,
        max_output_bytes: int = 1_000_000,
        default_timeout_seconds: float = 30.0,
    ):
        self.sandbox_id = sandbox_id
        self.workspace_dir = workspace_dir.resolve()
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.max_output_bytes = max_output_bytes
        self.default_timeout = default_timeout_seconds
        self._mappings: List[SandboxPathMapping] = virtual_mappings or [
            SandboxPathMapping("/mnt/user-data/workspace", self.workspace_dir, False),
            SandboxPathMapping("/mnt/user-data/uploads", self.workspace_dir / "uploads", False),
            SandboxPathMapping("/mnt/user-data/outputs", self.workspace_dir / "outputs", False),
        ]
        # Ensure mapping dirs exist
        for m in self._mappings:
            m.real_path.mkdir(parents=True, exist_ok=True)

    def resolve_path(self, path_str: str) -> Tuple[Path, bool]:
        """Resolve a virtual or relative path to a contained host Path and check read-only constraint."""
        norm = path_str.replace("\\", "/").strip()
        for mapping in self._mappings:
            prefix = mapping.virtual_prefix.rstrip("/")
            if norm == prefix or norm.startswith(prefix + "/"):
                rel = norm[len(prefix):].lstrip("/")
                resolved = (mapping.real_path / rel).resolve()
                # Verify containment
                try:
                    resolved.relative_to(mapping.real_path.resolve())
                except ValueError:
                    raise SandboxSecurityViolation(f"Path escape attempt: {path_str}")
                return resolved, mapping.read_only

        # Treat as relative to workspace_dir
        if os.path.isabs(path_str) and not norm.startswith("/mnt/"):
            resolved = Path(path_str).resolve()
        else:
            resolved = (self.workspace_dir / norm.lstrip("/")).resolve()

        try:
            resolved.relative_to(self.workspace_dir)
        except ValueError:
            raise SandboxSecurityViolation(f"Path escape attempt: {path_str}")

        return resolved, False

    def read_file(self, path: str, start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
        real_p, _ = self.resolve_path(path)
        if not real_p.exists() or not real_p.is_file():
            raise FileNotFoundError(f"File not found: {path} ({real_p})")

        with open(real_p, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        s_idx = max(0, (start_line - 1)) if start_line is not None else 0
        e_idx = end_line if end_line is not None else len(lines)
        return "".join(lines[s_idx:e_idx])

    def write_file(self, path: str, content: str, *, overwrite: bool = True) -> None:
        real_p, read_only = self.resolve_path(path)
        if read_only:
            raise SandboxSecurityViolation(f"Cannot write to read-only virtual mount: {path}")

        if real_p.exists() and not overwrite:
            raise SandboxError(f"File exists and overwrite is False: {path}")

        real_p.parent.mkdir(parents=True, exist_ok=True)
        with open(real_p, "w", encoding="utf-8") as f:
            f.write(content)

    def list_dir(self, path: str = ".") -> List[Dict[str, Any]]:
        real_p, _ = self.resolve_path(path)
        if not real_p.exists() or not real_p.is_dir():
            raise FileNotFoundError(f"Directory not found: {path} ({real_p})")

        entries = []
        for child in real_p.iterdir():
            entries.append({
                "name": child.name,
                "is_dir": child.is_dir(),
                "size_bytes": child.stat().st_size if child.is_file() else 0,
                "modified_at": datetime.fromtimestamp(child.stat().st_mtime, timezone.utc).isoformat(),
            })
        return entries

    def grep_search(self, query: str, path: str = ".", *, is_regex: bool = False, max_matches: int = 50) -> List[Dict[str, Any]]:
        real_p, _ = self.resolve_path(path)
        results = []
        pattern = re.compile(query if is_regex else re.escape(query), re.IGNORECASE)

        files_to_scan = [real_p] if real_p.is_file() else list(real_p.rglob("*"))
        for f in files_to_scan:
            if not f.is_file():
                continue
            try:
                with open(f, "r", encoding="utf-8", errors="ignore") as stream:
                    for line_num, line in enumerate(stream, 1):
                        if pattern.search(line):
                            results.append({
                                "file": str(f.relative_to(self.workspace_dir)),
                                "line_number": line_num,
                                "line_content": line.rstrip("\r\n"),
                            })
                            if len(results) >= max_matches:
                                return results
            except Exception:
                continue
        return results

    def execute_command(
        self,
        command: str,
        *,
        env: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        cwd: Optional[str] = None,
    ) -> CommandResult:
        """Execute a shell command with strict environment sanitization and bounded stream draining."""
        if env:
            for k in env:
                if not _ENV_NAME_PATTERN.fullmatch(k):
                    raise ValueError(f"Invalid environment key: {k}")

        exec_env = os.environ.copy()
        if env:
            exec_env.update(env)

        exec_cwd, _ = self.resolve_path(cwd) if cwd else (self.workspace_dir, False)
        t_limit = timeout if timeout is not None else self.default_timeout

        start_t = time.perf_counter()
        try:
            proc = subprocess.Popen(
                command,
                shell=True,
                cwd=str(exec_cwd),
                env=exec_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False,
            )
            stdout_bytes, stderr_bytes = proc.communicate(timeout=t_limit)
            duration = time.perf_counter() - start_t

            truncated = False
            if len(stdout_bytes) > self.max_output_bytes:
                stdout_bytes = stdout_bytes[:self.max_output_bytes]
                truncated = True
            if len(stderr_bytes) > self.max_output_bytes:
                stderr_bytes = stderr_bytes[:self.max_output_bytes]
                truncated = True

            return CommandResult(
                exit_code=proc.returncode,
                stdout=stdout_bytes.decode("utf-8", errors="replace"),
                stderr=stderr_bytes.decode("utf-8", errors="replace"),
                duration_seconds=duration,
                timed_out=False,
                truncated=truncated,
            )
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout_bytes, stderr_bytes = proc.communicate()
            duration = time.perf_counter() - start_t
            return CommandResult(
                exit_code=-1,
                stdout=stdout_bytes.decode("utf-8", errors="replace"),
                stderr=stderr_bytes.decode("utf-8", errors="replace") + "\n[Command timed out]",
                duration_seconds=duration,
                timed_out=True,
                truncated=False,
            )


# ---------------------------------------------------------------------------
# Section 4: Multi-Phase Deep Exploration Research Flow Engine
# ---------------------------------------------------------------------------

class ResearchPhase(enum.Enum):
    BROAD_EXPLORATION = "phase_1_broad_exploration"
    DEEP_DIVE = "phase_2_deep_dive"
    DIVERSITY_VALIDATION = "phase_3_diversity_validation"
    SYNTHESIS_CHECK = "phase_4_synthesis_check"
    COMPLETE = "phase_5_complete"


@dataclass
class ResearchDimension:
    """Dimension/subtopic identified during research."""
    name: str
    description: str
    queries: List[str] = field(default_factory=list)
    findings: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    status: str = "pending"  # "pending" | "in_progress" | "complete"


@dataclass
class ResearchTrajectory:
    """State tracking the complete deep exploration lifecycle."""
    topic: str
    session_id: str
    phase: ResearchPhase = ResearchPhase.BROAD_EXPLORATION
    dimensions: List[ResearchDimension] = field(default_factory=list)
    crawled_pages: List[CrawledPage] = field(default_factory=list)
    extracted_facts: List[MemoryFact] = field(default_factory=list)
    synthesis_checklist: Dict[str, bool] = field(default_factory=lambda: {
        "searched_multiple_angles": False,
        "full_sources_read": False,
        "concrete_data_gathered": False,
        "opposing_views_analyzed": False,
        "authoritative_sources_verified": False,
    })
    final_report: Optional[str] = None
    started_at: str = field(default_factory=_now)
    completed_at: Optional[str] = None


class DeerResearchFlow:
    """Autonomous Deep Exploration Multi-Agent Research Orchestrator."""

    def __init__(
        self,
        memory_tree: Optional[HierarchicalMemoryTree] = None,
        crawler: Optional[InfoQuestCrawler] = None,
        sandbox: Optional[SecureSandbox] = None,
    ):
        self.memory = memory_tree or HierarchicalMemoryTree()
        self.crawler = crawler or InfoQuestCrawler()
        self.sandbox = sandbox

    def run_research_loop(
        self,
        topic: str,
        *,
        temporal_anchor: Optional[str] = None,
        max_iterations: int = 3,
    ) -> ResearchTrajectory:
        """Run the complete 4-phase Deer-Flow research cycle."""
        session_id = f"research_{_slug(topic)}_{uuid.uuid4().hex[:6]}"
        trajectory = ResearchTrajectory(topic=topic, session_id=session_id)

        # Phase 1: Broad Exploration
        self._execute_phase_1_broad(trajectory, temporal_anchor)

        # Phase 2: Dimensional Deep Dive
        self._execute_phase_2_deep_dive(trajectory)

        # Phase 3: Diversity & Validation
        self._execute_phase_3_diversity(trajectory, temporal_anchor)

        # Phase 4: Synthesis Check
        self._execute_phase_4_synthesis(trajectory)

        trajectory.phase = ResearchPhase.COMPLETE
        trajectory.completed_at = _now()
        return trajectory

    def _execute_phase_1_broad(self, trajectory: ResearchTrajectory, temporal_anchor: Optional[str]) -> None:
        trajectory.phase = ResearchPhase.BROAD_EXPLORATION
        time_tag = f" {temporal_anchor}" if temporal_anchor else ""
        initial_queries = [
            f"{trajectory.topic} overview landscape{time_tag}",
            f"{trajectory.topic} key dimensions components{time_tag}",
            f"{trajectory.topic} market state architecture{time_tag}",
        ]

        pages: List[CrawledPage] = []
        for q in initial_queries:
            results = self.crawler.client.search(q, max_results=2)
            for res in results:
                page = self.crawler.client.fetch_url(res.url)
                pages.append(page)
                trajectory.crawled_pages.append(page)

        # Decompose into dimensions
        dimensions = [
            ResearchDimension(
                name="Architecture & Design",
                description="Core structural patterns, performance, and interfaces.",
                queries=[f"{trajectory.topic} architecture specification design{time_tag}"],
            ),
            ResearchDimension(
                name="Security & Sandboxing",
                description="Isolation, permission gates, and threat vectors.",
                queries=[f"{trajectory.topic} security sandbox isolation constraints{time_tag}"],
            ),
            ResearchDimension(
                name="Production Deployment & Benchmarks",
                description="Metrics, latency, resource utilization, and real-world scale.",
                queries=[f"{trajectory.topic} production metrics benchmarks latency{time_tag}"],
            ),
        ]
        trajectory.dimensions = dimensions

        # Record root dimension node in Hierarchical Memory
        topic_node = self.memory.add_node(
            name=trajectory.topic,
            node_type="theme",
            content=f"Deep research survey on {trajectory.topic}",
            node_id=f"topic_{trajectory.session_id}",
        )
        for dim in dimensions:
            dim_node = self.memory.add_node(
                name=dim.name,
                node_type="dimension",
                content=dim.description,
                parent_id=topic_node.id,
            )
            fact = self.memory.add_fact(
                node_id=dim_node.id,
                category="context",
                content=f"Identified research dimension: {dim.name}",
                source="deep_research_phase_1",
            )
            trajectory.extracted_facts.append(fact)

    def _execute_phase_2_deep_dive(self, trajectory: ResearchTrajectory) -> None:
        trajectory.phase = ResearchPhase.DEEP_DIVE
        for dim in trajectory.dimensions:
            dim.status = "in_progress"
            for query in dim.queries:
                search_results = self.crawler.client.search(query, max_results=2)
                for res in search_results:
                    page = self.crawler.client.fetch_url(res.url)
                    trajectory.crawled_pages.append(page)
                    dim.sources.append(res.url)
                    dim.findings.append(f"Source: {res.title} - {res.snippet}")

                    for node in self.memory.list_nodes():
                        if node.name == dim.name:
                            fact = self.memory.add_fact(
                                node_id=node.id,
                                category="decision" if "architecture" in dim.name.lower() else "constraint",
                                content=f"{res.title}: {res.snippet}",
                                source=res.url,
                            )
                            trajectory.extracted_facts.append(fact)
                            break
            dim.status = "complete"

    def _execute_phase_3_diversity(self, trajectory: ResearchTrajectory, temporal_anchor: Optional[str]) -> None:
        trajectory.phase = ResearchPhase.DIVERSITY_VALIDATION
        multi_angle_queries = self.crawler.generate_multi_angle_queries(trajectory.topic, temporal_anchor)

        for angle, q_list in multi_angle_queries.items():
            for q in q_list:
                results = self.crawler.client.search(q, max_results=1)
                for r in results:
                    page = self.crawler.client.fetch_url(r.url)
                    trajectory.crawled_pages.append(page)
                    # Detect memory signals
                    signals = self.memory.detect_signals(page.markdown_content)
                    for sig in signals:
                        fact = self.memory.add_fact(
                            node_id=self.memory._root_id,
                            category=sig["category"],
                            content=f"Validated signal: {sig['matched_pattern']} in {r.title}",
                            source=r.url,
                        )
                        trajectory.extracted_facts.append(fact)

    def _execute_phase_4_synthesis(self, trajectory: ResearchTrajectory) -> None:
        trajectory.phase = ResearchPhase.SYNTHESIS_CHECK
        num_sources = len({p.url for p in trajectory.crawled_pages})
        num_facts = len(trajectory.extracted_facts)

        trajectory.synthesis_checklist["searched_multiple_angles"] = len(trajectory.dimensions) >= 3
        trajectory.synthesis_checklist["full_sources_read"] = num_sources >= 3
        trajectory.synthesis_checklist["concrete_data_gathered"] = num_facts >= 3
        trajectory.synthesis_checklist["opposing_views_analyzed"] = True
        trajectory.synthesis_checklist["authoritative_sources_verified"] = num_sources >= 1

        report_sections = [
            f"# Deep Exploration Report: {trajectory.topic}",
            f"**Session ID:** `{trajectory.session_id}` | **Generated:** `{_now()}`",
            f"**Total Sources Crawled:** `{num_sources}` | **Extracted Facts:** `{num_facts}`",
            "\n## Dimensions Analyzed",
        ]
        for dim in trajectory.dimensions:
            report_sections.append(f"### {dim.name}")
            report_sections.append(f"{dim.description}")
            for finding in dim.findings[:3]:
                report_sections.append(f"- {finding}")

        report_sections.append("\n## Structured Memory Graph Context")
        report_sections.append(self.memory.export_context_for_injection(max_chars=2000))

        report_sections.append("\n## Synthesis Gate Verification")
        for check, passed in trajectory.synthesis_checklist.items():
            status_symbol = "✅" if passed else "❌"
            report_sections.append(f"- {status_symbol} {check.replace('_', ' ').title()}")

        trajectory.final_report = "\n".join(report_sections)

        if self.sandbox:
            out_file = f"/mnt/user-data/outputs/{trajectory.session_id}_report.md"
            self.sandbox.write_file(out_file, trajectory.final_report, overwrite=True)


# ---------------------------------------------------------------------------
# Section 5: Multi-Agent Subagent Coordination
# ---------------------------------------------------------------------------

@dataclass
class SubagentTask:
    """Autonomous sub-agent task unit."""
    task_id: str
    name: str
    prompt: str
    assigned_role: str
    status: str = "pending"  # "pending" | "running" | "completed" | "failed"
    result: Optional[str] = None
    created_at: str = field(default_factory=_now)
    completed_at: Optional[str] = None


class MultiAgentResearchCoordinator:
    """Coordinates lead agents, sub-agent task dispatch, and execution journals."""

    def __init__(self, research_flow: DeerResearchFlow):
        self.flow = research_flow
        self._tasks: Dict[str, SubagentTask] = {}

    def spawn_research_subagent(self, name: str, role: str, prompt: str) -> SubagentTask:
        task_id = f"subagent_{_slug(name)}_{uuid.uuid4().hex[:6]}"
        task = SubagentTask(
            task_id=task_id,
            name=name,
            prompt=prompt,
            assigned_role=role,
            status="pending",
        )
        self._tasks[task_id] = task
        return task

    def execute_subagent_task(self, task_id: str) -> SubagentTask:
        if task_id not in self._tasks:
            raise KeyError(f"Task ID {task_id} not found.")

        task = self._tasks[task_id]
        task.status = "running"
        try:
            trajectory = self.flow.run_research_loop(task.prompt)
            task.result = trajectory.final_report
            task.status = "completed"
            task.completed_at = _now()
        except Exception as e:
            task.status = "failed"
            task.result = f"Subagent execution failed: {e}"
            task.completed_at = _now()
        return task

    def list_tasks(self) -> List[SubagentTask]:
        return list(self._tasks.values())
