# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
# SPDX-License-Identifier: MIT

"""Recursive Language Model (RLM) and Continual Refinement Engine.

Assimilated from Prime Agent's core architecture into Camelot-OS 01_KERNEL.
Provides:
1. Native recursive sub-agent lifecycle management (admission, depth bounding, handles, registry).
2. Continual Harness State: durable prompts, memories, skills, and subagent specs with versioning & scope (local/global).
3. Continual /refine loop: trajectory review, proposal generation, atomic snapshotting, and reversible rollback.
4. Zero external dependencies outside Python standard library and typing.
"""

from __future__ import annotations

import asyncio
from dataclasses import asdict, dataclass, field, fields
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Union
import uuid

HarnessKind = Literal["prompt", "memory", "skill", "subagent"]
HarnessScope = Literal["local", "global"]
RefinementAction = Literal["create", "update", "delete"]

_KINDS: Tuple[HarnessKind, ...] = ("prompt", "memory", "skill", "subagent")
_DEFAULT_FILE_NAME = "harness_state.json"
_DEFAULT_HARNESS_DIR_NAME = "harness"


def _now() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def _slug(raw: str, fallback: str) -> str:
    """Generate a clean slug identifier from a raw title/name."""
    normalized = "".join(ch.lower() if ch.isalnum() else "_" for ch in raw.strip())
    normalized = "_".join(part for part in normalized.split("_") if part)
    return (normalized or fallback)[:80]


# ---------------------------------------------------------------------------
# RLM Data Structures & Subagent Lifecycle
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RLMSpawnHandle:
    """Handle returned immediately upon task admission into the RLM runtime."""
    rlm_child_id: str
    name: str
    session_dir: Path
    model: str
    depth: int = 1


@dataclass(frozen=True)
class RLMModel:
    """Model descriptor within the RLM registry."""
    provider: str
    id: str
    name: str
    selector: str


@dataclass(frozen=True)
class RLMSubagent:
    """Record of an active or retained child subagent."""
    rlm_child_id: str
    active_session_id: Optional[str]
    session_id: Optional[str]
    session_name: str
    session_dir: Path
    status: str  # "running" | "completed" | "error" | "cancelled"
    depth: int = 1
    created_at: str = field(default_factory=_now)


@dataclass(frozen=True)
class TokenUsage:
    """Usage accounting for child tasks and aggregate parent turns."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0


# ---------------------------------------------------------------------------
# Harness State Data Structures
# ---------------------------------------------------------------------------

@dataclass
class HarnessEntry:
    """A persistent prompt note, memory record, skill, or subagent specification."""
    id: str
    kind: HarnessKind
    title: str
    content: str
    path: str = "general"
    scope: HarnessScope = "local"
    reference: Dict[str, Any] = field(default_factory=dict)
    arguments: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: str = "agent"
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    version: int = 1


@dataclass
class RefinementEvent:
    """Record of an applied refinement pass."""
    id: str
    trigger: str
    changes: List[str]
    evidence: str = ""
    outcome: str = ""
    created_at: str = field(default_factory=_now)


@dataclass
class RefinementEdit:
    """Single proposed create, update, or delete modification to harness state."""
    action: RefinementAction
    kind: HarnessKind
    id: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    path: Optional[str] = None
    reference: Optional[Dict[str, Any]] = None
    arguments: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None


@dataclass
class RefinementProposal:
    """Structured proposal generated from continual refinement review."""
    summary: str
    rationale: str
    expected_outcome: str
    edits: List[RefinementEdit] = field(default_factory=list)


@dataclass
class AppliedRefinementEdit:
    """Result of applying an individual RefinementEdit, with before/after state snapshots."""
    action: RefinementAction
    kind: HarnessKind
    id: str
    applied: bool
    title: Optional[str] = None
    content: Optional[str] = None
    path: Optional[str] = None
    reference: Optional[Dict[str, Any]] = None
    arguments: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None
    before: Optional[HarnessEntry] = None
    after: Optional[HarnessEntry] = None
    error: Optional[str] = None


@dataclass
class RefinementResult:
    """Complete summary and audit trail of an applied refinement."""
    id: str
    summary: str
    rationale: str
    expected_outcome: str
    applied_edits: List[AppliedRefinementEdit]
    harness_state_path: str = ""
    rollback_of: Optional[str] = None
    scope: Optional[HarnessScope] = None
    created_at: str = field(default_factory=_now)


_ENTRY_FIELDS = {f.name for f in fields(HarnessEntry)}
_REFINEMENT_FIELDS = {f.name for f in fields(RefinementEvent)}


def _validate_python_skill_reference(reference: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate that a skill entry has a valid Python import and callable structure."""
    if not isinstance(reference, dict):
        raise ValueError("skill entries require a Python reference dict")
    normalized = dict(reference)
    if normalized.get("type") != "python":
        raise ValueError("skill reference.type must be 'python'")
    if not any(isinstance(normalized.get(k), str) and normalized[k] for k in ("import", "python_import")):
        raise ValueError("skill reference requires a Python import")
    if not any(isinstance(normalized.get(k), str) and normalized[k] for k in ("callable", "call_pattern")):
        raise ValueError("skill reference requires a callable or call_pattern")
    return normalized


# ---------------------------------------------------------------------------
# HarnessState Store
# ---------------------------------------------------------------------------

class HarnessState:
    """CRUD store for reset-free, persistent harness refinement state."""

    def __init__(
        self,
        file_path: Optional[Union[str, Path]] = None,
        *,
        in_memory: bool = False,
        scope: HarnessScope = "local",
        local_write_error: Optional[str] = None,
    ):
        if in_memory:
            self.file_path: Optional[Path] = None
        else:
            self.file_path = Path(file_path).expanduser().resolve() if file_path else None

        self.scope: HarnessScope = scope
        self._local_write_error = local_write_error
        self.entries: Dict[HarnessKind, Dict[str, HarnessEntry]] = {kind: {} for kind in _KINDS}
        self.refinements: List[RefinementEvent] = []
        self._loaded_mtime: Optional[int] = None
        if self.file_path is not None:
            self.load()

    def _ensure_local_writable(self) -> None:
        if self._local_write_error is not None:
            raise RuntimeError(self._local_write_error)

    def _disk_mtime(self) -> Optional[int]:
        if self.file_path is None:
            return None
        try:
            return self.file_path.stat().st_mtime_ns
        except OSError:
            return None

    def _sync_from_disk(self) -> None:
        if self.file_path is not None and self._disk_mtime() != self._loaded_mtime:
            self.load()

    def load(self) -> HarnessState:
        """Load state from disk, handling corrupt/missing files safely."""
        if self.file_path is None or not self.file_path.exists():
            self._loaded_mtime = None
            return self
        mtime = self._disk_mtime()
        try:
            with self.file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            data = {}

        if not isinstance(data, dict):
            data = {}

        entries: Dict[HarnessKind, Dict[str, HarnessEntry]] = {kind: {} for kind in _KINDS}
        raw_entries = data.get("entries", {})
        if isinstance(raw_entries, dict):
            for kind in _KINDS:
                raw_kind = raw_entries.get(kind, {})
                if not isinstance(raw_kind, dict):
                    continue
                for entry_id, raw_entry in raw_kind.items():
                    if not isinstance(raw_entry, dict):
                        continue
                    entry_data = {k: v for k, v in raw_entry.items() if k in _ENTRY_FIELDS}
                    entry_data["id"] = str(entry_id)
                    entry_data["kind"] = kind
                    if not isinstance(entry_data.get("title"), str) or not isinstance(entry_data.get("content"), str):
                        continue
                    if not isinstance(entry_data.get("path"), str):
                        entry_data["path"] = "general"
                    if entry_data.get("scope") not in ("local", "global"):
                        entry_data["scope"] = self.scope
                    if not isinstance(entry_data.get("source"), str):
                        entry_data["source"] = "agent"
                    try:
                        entry_data["version"] = int(entry_data.get("version", 1))
                    except (ValueError, TypeError):
                        entry_data["version"] = 1
                    if not isinstance(entry_data.get("reference"), dict):
                        entry_data["reference"] = {}
                    if not isinstance(entry_data.get("arguments"), dict):
                        entry_data["arguments"] = {}
                    if not isinstance(entry_data.get("metadata"), dict):
                        entry_data["metadata"] = {}
                    entries[kind][str(entry_id)] = HarnessEntry(**entry_data)
        self.entries = entries

        self.refinements = []
        raw_refinements = data.get("refinements", [])
        if isinstance(raw_refinements, list):
            for raw_event in raw_refinements:
                if not isinstance(raw_event, dict):
                    continue
                event_data = {k: v for k, v in raw_event.items() if k in _REFINEMENT_FIELDS}
                if not isinstance(event_data.get("id"), str) or not isinstance(event_data.get("trigger"), str):
                    continue
                changes = event_data.get("changes")
                if isinstance(changes, str):
                    event_data["changes"] = [changes]
                elif isinstance(changes, list):
                    event_data["changes"] = [str(c) for c in changes]
                else:
                    continue
                self.refinements.append(RefinementEvent(**event_data))

        self._loaded_mtime = mtime
        return self

    def save(self) -> HarnessState:
        """Atomically persist harness state to disk."""
        if self.file_path is None:
            return self
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "schema": 1,
            "entries": {
                kind: {entry_id: asdict(entry) for entry_id, entry in records.items()}
                for kind, records in self.entries.items()
            },
            "refinements": [asdict(event) for event in self.refinements],
        }
        temp_path = self.file_path.with_suffix(f".tmp.{os.getpid()}.{uuid.uuid4().hex[:8]}")
        try:
            with temp_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            temp_path.replace(self.file_path)
        finally:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass
        self._loaded_mtime = self._disk_mtime()
        return self

    def upsert(
        self,
        kind: HarnessKind,
        title: str,
        content: str,
        *,
        id: Optional[str] = None,
        path: Optional[str] = None,
        reference: Optional[Dict[str, Any]] = None,
        arguments: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        source: str = "agent",
    ) -> HarnessEntry:
        self._ensure_local_writable()
        self._sync_from_disk()
        if kind not in self.entries:
            raise ValueError(f"unknown harness kind {kind!r}; expected one of {_KINDS}")

        entry_id = id or _slug(title, kind)
        existing = self.entries[kind].get(entry_id)
        if existing:
            existing.title = title
            existing.content = content
            if path is not None:
                existing.path = path
            if reference is not None:
                existing.reference = dict(reference)
            if arguments is not None:
                existing.arguments = dict(arguments)
            if metadata is not None:
                existing.metadata = dict(metadata)
            existing.source = source
            existing.updated_at = _now()
            existing.version += 1
            entry = existing
        else:
            entry = HarnessEntry(
                id=entry_id,
                kind=kind,
                title=title,
                content=content,
                path=path if path is not None else "general",
                scope=self.scope,
                reference=dict(reference or {}),
                arguments=dict(arguments or {}),
                metadata=dict(metadata or {}),
                source=source,
            )
            self.entries[kind][entry_id] = entry
        self.save()
        return entry

    def get(self, kind: HarnessKind, id: str) -> Optional[HarnessEntry]:
        self._sync_from_disk()
        if kind not in self.entries:
            raise ValueError(f"unknown harness kind {kind!r}; expected one of {_KINDS}")
        return self.entries[kind].get(id)

    def delete(self, kind: HarnessKind, id: str) -> bool:
        self._ensure_local_writable()
        self._sync_from_disk()
        if kind not in self.entries:
            raise ValueError(f"unknown harness kind {kind!r}; expected one of {_KINDS}")
        if id not in self.entries[kind]:
            return False
        del self.entries[kind][id]
        self.save()
        return True

    def list(self, kind: Optional[HarnessKind] = None) -> List[HarnessEntry]:
        self._sync_from_disk()
        kinds = [kind] if kind else list(_KINDS)
        records: List[HarnessEntry] = []
        for current_kind in kinds:
            if current_kind not in self.entries:
                raise ValueError(f"unknown harness kind {current_kind!r}; expected one of {_KINDS}")
            records.extend(self.entries[current_kind].values())
        return sorted(records, key=lambda entry: (entry.kind, entry.path, entry.title, entry.id))

    def create(
        self,
        kind: HarnessKind,
        title: str,
        content: str,
        *,
        id: Optional[str] = None,
        path: str = "general",
        reference: Optional[Dict[str, Any]] = None,
        arguments: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        source: str = "agent",
    ) -> HarnessEntry:
        self._ensure_local_writable()
        self._sync_from_disk()
        if kind not in self.entries:
            raise ValueError(f"unknown harness kind {kind!r}; expected one of {_KINDS}")
        entry_id = id or _slug(title, kind)
        if entry_id in self.entries[kind]:
            raise ValueError(f"{kind} entry {entry_id!r} already exists")
        if kind == "skill":
            reference = _validate_python_skill_reference(reference)
        return self.upsert(
            kind,
            title,
            content,
            id=entry_id,
            path=path,
            reference=reference,
            arguments=arguments,
            metadata=metadata,
            source=source,
        )

    def update(
        self,
        kind: HarnessKind,
        id: str,
        title: str,
        content: str,
        *,
        path: Optional[str] = None,
        reference: Optional[Dict[str, Any]] = None,
        arguments: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        source: str = "agent",
    ) -> HarnessEntry:
        self._ensure_local_writable()
        self._sync_from_disk()
        if kind not in self.entries:
            raise ValueError(f"unknown harness kind {kind!r}; expected one of {_KINDS}")
        if id not in self.entries[kind]:
            raise ValueError(f"{kind} entry {id!r} does not exist")
        if kind == "skill" and reference is not None:
            reference = _validate_python_skill_reference(reference)
        return self.upsert(
            kind,
            title,
            content,
            id=id,
            path=path,
            reference=reference,
            arguments=arguments,
            metadata=metadata,
            source=source,
        )

    def record_refinement(
        self,
        trigger: str,
        changes: Union[List[str], str],
        *,
        evidence: str = "",
        outcome: str = "",
        id: Optional[str] = None,
    ) -> RefinementEvent:
        self._ensure_local_writable()
        self._sync_from_disk()
        event_id = id or f"refine_{len(self.refinements) + 1:04d}"
        normalized_changes = [changes] if isinstance(changes, str) else list(changes)
        event = RefinementEvent(
            id=event_id,
            trigger=trigger,
            changes=normalized_changes,
            evidence=evidence,
            outcome=outcome,
        )
        self.refinements.append(event)
        self.save()
        return event

    def overview(self, *, max_entries_per_kind: int = 20) -> str:
        """Format an overview summary of active harness components."""
        self._sync_from_disk()
        lines = [
            f"Harness state ({self.scope}): {self.file_path or 'in-memory'}",
            "Execution contract: Subagents are created via RLM recursion (handle = await rlm.run('prompt')).",
        ]
        for kind in _KINDS:
            records = self.list(kind)[:max_entries_per_kind]
            lines.append(f"{kind}: {len(self.entries[kind])}")
            for entry in records:
                summary = entry.content.strip().replace("\n", " ")
                if len(summary) > 120:
                    summary = f"{summary[:117]}..."
                lines.append(f"  - [{entry.scope}:{entry.id}] {entry.title} ({entry.path}, v{entry.version}): {summary}")
        lines.append(f"refinements: {len(self.refinements)}")
        for event in self.refinements[-5:]:
            lines.append(f"  - [{event.id}] {event.trigger}: {', '.join(event.changes)}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Continual /refine Engine & Logic
# ---------------------------------------------------------------------------

def apply_refinement_proposal(
    state: HarnessState,
    proposal: RefinementProposal,
    options: Optional[Dict[str, Any]] = None,
) -> RefinementResult:
    """Apply a structured refinement proposal to a HarnessState instance with full rollback support."""
    opts = options or {}
    refinement_id = opts.get("id") or f"refine_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:4]}"
    rollback_of = opts.get("rollback_of")
    scope = opts.get("scope") or state.scope

    applied_edits: List[AppliedRefinementEdit] = []

    for edit in proposal.edits:
        computed_id = edit.id or (
            _slug(edit.title or edit.kind, edit.kind) if edit.action == "create" else None
        )
        entry_id = computed_id or ""

        # Validate edit
        if edit.action not in ("create", "update", "delete"):
            applied_edits.append(AppliedRefinementEdit(
                action=edit.action, kind=edit.kind, id=entry_id, applied=False,
                error=f"unsupported action {edit.action}"
            ))
            continue

        if edit.kind not in _KINDS:
            applied_edits.append(AppliedRefinementEdit(
                action=edit.action, kind=edit.kind, id=entry_id, applied=False,
                error=f"unsupported kind {edit.kind}"
            ))
            continue

        if edit.kind == "prompt" and entry_id == "base_system_prompt":
            applied_edits.append(AppliedRefinementEdit(
                action=edit.action, kind=edit.kind, id=entry_id, applied=False,
                error="base system prompt is not editable"
            ))
            continue

        if edit.action != "create" and not edit.id:
            applied_edits.append(AppliedRefinementEdit(
                action=edit.action, kind=edit.kind, id=entry_id, applied=False,
                error=f"{edit.action} requires id"
            ))
            continue

        if edit.action != "delete" and (not edit.title or not edit.content):
            applied_edits.append(AppliedRefinementEdit(
                action=edit.action, kind=edit.kind, id=entry_id, applied=False,
                error=f"{edit.action} requires title and content"
            ))
            continue

        records = state.entries[edit.kind]
        existing = records.get(entry_id)
        before_entry = HarnessEntry(**asdict(existing)) if existing else None

        if edit.action == "delete":
            if not existing:
                applied_edits.append(AppliedRefinementEdit(
                    action=edit.action, kind=edit.kind, id=entry_id, applied=False,
                    error="entry not found"
                ))
                continue
            del records[entry_id]
            applied_edits.append(AppliedRefinementEdit(
                action=edit.action, kind=edit.kind, id=entry_id, applied=True,
                before=before_entry
            ))
            continue

        if edit.action == "create" and existing:
            applied_edits.append(AppliedRefinementEdit(
                action=edit.action, kind=edit.kind, id=entry_id, applied=False,
                before=before_entry, error="entry already exists"
            ))
            continue

        if edit.action == "update" and not existing:
            applied_edits.append(AppliedRefinementEdit(
                action=edit.action, kind=edit.kind, id=entry_id, applied=False,
                error="entry not found"
            ))
            continue

        # Handle skill validation
        ref = edit.reference
        if edit.kind == "skill":
            try:
                ref = _validate_python_skill_reference(edit.reference or (existing.reference if existing else None))
            except ValueError as exc:
                applied_edits.append(AppliedRefinementEdit(
                    action=edit.action, kind=edit.kind, id=entry_id, applied=False,
                    error=str(exc)
                ))
                continue

        created_at = existing.created_at if existing else _now()
        version = (existing.version + 1) if existing else 1
        after_entry = HarnessEntry(
            id=entry_id,
            kind=edit.kind,
            title=edit.title or (existing.title if existing else entry_id),
            content=edit.content or (existing.content if existing else ""),
            path=edit.path or (existing.path if existing else "general"),
            scope=existing.scope if existing else scope,
            reference=ref or {},
            arguments=edit.arguments if edit.arguments is not None else (existing.arguments if existing else {}),
            metadata=edit.metadata if edit.metadata is not None else (existing.metadata if existing else {}),
            source="refine",
            created_at=created_at,
            updated_at=_now(),
            version=version,
        )
        records[entry_id] = after_entry
        applied_edits.append(AppliedRefinementEdit(
            action=edit.action,
            kind=edit.kind,
            id=entry_id,
            applied=True,
            title=edit.title,
            content=edit.content,
            path=edit.path,
            before=before_entry,
            after=HarnessEntry(**asdict(after_entry)),
        ))

    state.save()

    changes = [f"{e.action} {e.kind}:{e.id}" for e in applied_edits if e.applied]
    state.record_refinement(
        trigger=proposal.summary,
        changes=changes,
        evidence=proposal.rationale,
        outcome=proposal.expected_outcome,
        id=refinement_id,
    )

    return RefinementResult(
        id=refinement_id,
        summary=proposal.summary,
        rationale=proposal.rationale,
        expected_outcome=proposal.expected_outcome,
        applied_edits=applied_edits,
        harness_state_path=str(state.file_path or ""),
        rollback_of=rollback_of,
        scope=scope,
    )


def create_rollback_proposal(target_result: RefinementResult) -> RefinementProposal:
    """Invert an applied RefinementResult to create a reversible rollback proposal."""
    edits: List[RefinementEdit] = []
    for edit in reversed(target_result.applied_edits):
        if not edit.applied:
            continue
        if edit.before is not None:
            # Revert update or delete back to previous state
            edits.append(RefinementEdit(
                action="update" if edit.after is not None else "create",
                kind=edit.kind,
                id=edit.id,
                title=edit.before.title,
                content=edit.before.content,
                path=edit.before.path,
                reference=edit.before.reference,
                arguments=edit.before.arguments,
                metadata=edit.before.metadata,
                reason=f"Rollback {target_result.id}",
            ))
        elif edit.after is not None:
            # Delete an entry that was originally created
            edits.append(RefinementEdit(
                action="delete",
                kind=edit.kind,
                id=edit.id,
                reason=f"Rollback {target_result.id}",
            ))

    return RefinementProposal(
        summary=f"Rollback refinement {target_result.id}",
        rationale=f"Restores continual harness state from refinement {target_result.id}",
        expected_outcome="Reverted prior refinement changes.",
        edits=edits,
    )


# ---------------------------------------------------------------------------
# RLM Execution Engine
# ---------------------------------------------------------------------------

class RLMEngine:
    """Core RLM Execution and Orchestration Engine for Camelot-OS.

    Handles:
    - Bounded subagent spawning (RLM recursion with depth limits).
    - Subagent lifecycle registry and token usage attribution.
    - Continual harness management & integration.
    - Host comm bridge dispatch for programmatic skills.
    """

    def __init__(
        self,
        *,
        max_depth: int = 3,
        session_id: Optional[str] = None,
        base_dir: Optional[Union[str, Path]] = None,
        harness_state: Optional[HarnessState] = None,
        model_runner: Optional[Callable[[str, Dict[str, Any]], Any]] = None,
    ):
        self.max_depth = max_depth
        self.session_id = session_id or f"session_{uuid.uuid4().hex[:8]}"
        self.base_dir = Path(base_dir or Path.home() / ".camelot" / "rlm").resolve()
        self.session_dir = self.base_dir / "sessions" / self.session_id
        self.harness = harness_state or HarnessState(
            self.session_dir / _DEFAULT_HARNESS_DIR_NAME / _DEFAULT_FILE_NAME,
            scope="local"
        )
        self.registry: Dict[str, RLMSubagent] = {}
        self.usage_ledger: Dict[str, TokenUsage] = {}
        self.model_runner = model_runner
        self._models: Dict[str, RLMModel] = {
            "gemini-2.5-pro": RLMModel("google", "gemini-2.5-pro", "Gemini 2.5 Pro", "google/gemini-2.5-pro"),
            "gemini-2.5-flash": RLMModel("google", "gemini-2.5-flash", "Gemini 2.5 Flash", "google/gemini-2.5-flash"),
            "gpt-5.5": RLMModel("openai", "gpt-5.5", "GPT-5.5 Codex", "openai/gpt-5.5"),
        }

    def register_model(self, model: RLMModel) -> None:
        """Register a model into the RLM catalog."""
        self._models[model.selector] = model

    def find_models(self, query: str = "", limit: int = 8) -> List[RLMModel]:
        """Search available models in the catalog."""
        q = query.lower()
        results = [
            m for m in self._models.values()
            if not q or q in m.name.lower() or q in m.selector.lower() or q in m.provider.lower()
        ]
        return results[:limit]

    def list_subagents(self) -> List[RLMSubagent]:
        """Return list of active and retained subagents."""
        return list(self.registry.values())

    def get_subagent(self, selector: str) -> Optional[RLMSubagent]:
        """Lookup a subagent by ID or name."""
        for agent in self.registry.values():
            if selector in (agent.rlm_child_id, agent.session_name, agent.session_id, agent.active_session_id):
                return agent
        return None

    def delete_subagent(self, selector: Union[str, RLMSubagent]) -> RLMSubagent:
        """Remove/tombstone a child subagent from the registry."""
        target_id = selector.rlm_child_id if isinstance(selector, RLMSubagent) else selector
        agent = self.get_subagent(target_id)
        if not agent:
            raise KeyError(f"Subagent {target_id!r} not found in registry")
        updated = RLMSubagent(
            rlm_child_id=agent.rlm_child_id,
            active_session_id=None,
            session_id=agent.session_id,
            session_name=agent.session_name,
            session_dir=agent.session_dir,
            status="cancelled",
            depth=agent.depth,
            created_at=agent.created_at,
        )
        del self.registry[agent.rlm_child_id]
        return updated

    def attribute_usage(self, child_id: str, usage: TokenUsage) -> None:
        """Attribute token usage of a child subagent into the parent session."""
        current = self.usage_ledger.get(child_id, TokenUsage())
        self.usage_ledger[child_id] = TokenUsage(
            prompt_tokens=current.prompt_tokens + usage.prompt_tokens,
            completion_tokens=current.completion_tokens + usage.completion_tokens,
            total_tokens=current.total_tokens + usage.total_tokens,
            cost_usd=current.cost_usd + usage.cost_usd,
        )

    def total_usage(self) -> TokenUsage:
        """Calculate total aggregate usage across all subagents."""
        p = sum(u.prompt_tokens for u in self.usage_ledger.values())
        c = sum(u.completion_tokens for u in self.usage_ledger.values())
        t = sum(u.total_tokens for u in self.usage_ledger.values())
        usd = sum(u.cost_usd for u in self.usage_ledger.values())
        return TokenUsage(prompt_tokens=p, completion_tokens=c, total_tokens=t, cost_usd=usd)

    async def run(
        self,
        prompt: str,
        *,
        name: Optional[str] = None,
        model: Optional[str] = None,
        current_depth: int = 0,
        **kwargs: Any,
    ) -> RLMSpawnHandle:
        """Spawn a recursive child agent.

        Admit the task immediately, returning an RLMSpawnHandle. Enforces strict depth limit.
        """
        if not isinstance(prompt, str) or not prompt.strip():
            raise TypeError("prompt must be a non-empty string")

        child_depth = current_depth + 1
        if child_depth > self.max_depth:
            raise RuntimeError(
                f"RLM recursion depth exceeded: depth {child_depth} > max_depth {self.max_depth}"
            )

        resolved_model = model or "gemini-2.5-pro"
        child_id = f"sub_{uuid.uuid4().hex[:8]}"
        child_name = name or f"agent_{child_id}"
        child_dir = self.session_dir / child_id

        # Register child subagent
        subagent = RLMSubagent(
            rlm_child_id=child_id,
            active_session_id=f"act_{uuid.uuid4().hex[:6]}",
            session_id=child_id,
            session_name=child_name,
            session_dir=child_dir,
            status="running",
            depth=child_depth,
        )
        self.registry[child_id] = subagent

        handle = RLMSpawnHandle(
            rlm_child_id=child_id,
            name=child_name,
            session_dir=child_dir,
            model=resolved_model,
            depth=child_depth,
        )

        # Background task simulation/execution if runner provided
        if self.model_runner is not None:
            asyncio.create_task(self._execute_child_background(child_id, prompt, kwargs))

        return handle

    async def _execute_child_background(self, child_id: str, prompt: str, kwargs: Dict[str, Any]) -> None:
        """Execute child in detached background loop and update registry status."""
        try:
            if self.model_runner:
                if asyncio.iscoroutinefunction(self.model_runner):
                    await self.model_runner(prompt, kwargs)
                else:
                    self.model_runner(prompt, kwargs)
            if child_id in self.registry:
                current = self.registry[child_id]
                self.registry[child_id] = RLMSubagent(
                    rlm_child_id=current.rlm_child_id,
                    active_session_id=current.active_session_id,
                    session_id=current.session_id,
                    session_name=current.session_name,
                    session_dir=current.session_dir,
                    status="completed",
                    depth=current.depth,
                    created_at=current.created_at,
                )
        except Exception:
            if child_id in self.registry:
                current = self.registry[child_id]
                self.registry[child_id] = RLMSubagent(
                    rlm_child_id=current.rlm_child_id,
                    active_session_id=current.active_session_id,
                    session_id=current.session_id,
                    session_name=current.session_name,
                    session_dir=current.session_dir,
                    status="error",
                    depth=current.depth,
                    created_at=current.created_at,
                )

    async def refine(
        self,
        proposal_or_text: Union[RefinementProposal, Dict[str, Any], str],
        *,
        rollback_id: Optional[str] = None,
        history: Optional[List[RefinementResult]] = None,
    ) -> RefinementResult:
        """Run a continual refinement pass or rollback."""
        if rollback_id and history:
            target = next((h for h in history if h.id == rollback_id), None)
            if not target:
                raise KeyError(f"Refinement result {rollback_id} not found for rollback")
            proposal = create_rollback_proposal(target)
            return apply_refinement_proposal(self.harness, proposal, {"rollback_of": rollback_id})

        if isinstance(proposal_or_text, RefinementProposal):
            proposal = proposal_or_text
        elif isinstance(proposal_or_text, dict):
            edits = [
                RefinementEdit(
                    action=e["action"],
                    kind=e["kind"],
                    id=e.get("id"),
                    title=e.get("title"),
                    content=e.get("content"),
                    path=e.get("path"),
                    reference=e.get("reference"),
                    arguments=e.get("arguments"),
                    metadata=e.get("metadata"),
                    reason=e.get("reason"),
                )
                for e in proposal_or_text.get("edits", [])
            ]
            proposal = RefinementProposal(
                summary=proposal_or_text.get("summary", "Refinement pass"),
                rationale=proposal_or_text.get("rationale", ""),
                expected_outcome=proposal_or_text.get("expected_outcome", ""),
                edits=edits,
            )
        elif isinstance(proposal_or_text, str):
            # Parse JSON string
            data = json.loads(proposal_or_text)
            return await self.refine(data)
        else:
            raise TypeError("Invalid proposal format")

        return apply_refinement_proposal(self.harness, proposal)

    async def __call__(self, prompt: str, **kwargs: Any) -> RLMSpawnHandle:
        """Callable shorthand for rlm.run()."""
        return await self.run(prompt, **kwargs)


__all__ = [
    "AppliedRefinementEdit",
    "HarnessEntry",
    "HarnessKind",
    "HarnessScope",
    "HarnessState",
    "RefinementAction",
    "RefinementEdit",
    "RefinementEvent",
    "RefinementProposal",
    "RefinementResult",
    "RLMEngine",
    "RLMModel",
    "RLMSpawnHandle",
    "RLMSubagent",
    "TokenUsage",
    "apply_refinement_proposal",
    "create_rollback_proposal",
]
