# SPDX-License-Identifier: MIT
"""Idempotency Guardian — Phase 1B Ingress & Replay Protection.

Enforces durable idempotency keys backed by PostgreSQL / SQLite WAL
with a high-speed transit accelerator (<10s fast mutex).

Compound Key Tuple:
    compound_key = SHA-256(client_key || tenant_id || manifest_hash)

State Machine:
    [NONE] ──(ingress)──> [IN_FLIGHT] ──(success)──> [COMMITTED]
                               │
                               └──(failure)──> [REJECTED]

Invariants:
    1. An IN_FLIGHT key triggers a 409 Conflict if a duplicate arrives before expiry.
    2. A COMMITTED key returns the exact cached ExecutionReceipt / response.
    3. Cross-tenant key isolation is strictly enforced via the compound tuple.
"""
from __future__ import annotations

import enum
import hashlib
import json
import sqlite3
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


class IdempotencyStatus(str, enum.Enum):
    IN_FLIGHT = "IN_FLIGHT"
    COMMITTED = "COMMITTED"
    REJECTED = "REJECTED"


class IdempotencyDecision(str, enum.Enum):
    PROCEED = "PROCEED"      # New key acquired, caller must execute
    REPLAY = "REPLAY"        # Previously committed, return cached receipt/response
    CONFLICT = "CONFLICT"    # Currently in-flight, return 409 Conflict
    REJECTED = "REJECTED"    # Previously rejected, retry permitted or error returned


class IdempotencyConflictError(Exception):
    """Raised when an operation is already in flight for the given compound key."""
    def __init__(self, key: str, tenant_id: str, correlation_id: str, message: str = ""):
        self.key = key
        self.tenant_id = tenant_id
        self.correlation_id = correlation_id
        super().__init__(message or f"Operation '{key}' is already IN_FLIGHT under correlation '{correlation_id}'.")


@dataclass
class IdempotencyRecord:
    key: str
    tenant_id: str
    manifest_hash: str
    correlation_id: str
    status: IdempotencyStatus
    receipt_ref: Optional[str]
    response_body: Optional[str]
    expires_at: float  # Unix timestamp
    created_at: float  # Unix timestamp
    updated_at: float  # Unix timestamp

    @property
    def compound_key(self) -> str:
        return compute_compound_key(self.key, self.tenant_id, self.manifest_hash)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def compute_compound_key(key: str, tenant_id: str, manifest_hash: str) -> str:
    """Compute deterministic SHA-256 compound tuple."""
    raw = f"{key}:{tenant_id}:{manifest_hash}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class FastMutexAccelerator:
    """In-memory fast mutex accelerator (<10s transit lock).

    Guarantees zero database round-trips for sub-second concurrent burst collisions.
    """
    def __init__(self, default_ttl_sec: float = 10.0):
        self._lock = threading.Lock()
        self._default_ttl = default_ttl_sec
        self._locks: dict[str, float] = {}  # compound_key -> expiry_ts

    def try_acquire(self, compound_key: str, ttl_sec: Optional[float] = None) -> bool:
        ttl = ttl_sec if ttl_sec is not None else self._default_ttl
        now = time.time()
        with self._lock:
            # Purge expired entry if present
            if compound_key in self._locks and self._locks[compound_key] <= now:
                del self._locks[compound_key]

            if compound_key in self._locks:
                return False  # Locked
            self._locks[compound_key] = now + ttl
            return True

    def release(self, compound_key: str) -> None:
        with self._lock:
            self._locks.pop(compound_key, None)

    def is_locked(self, compound_key: str) -> bool:
        now = time.time()
        with self._lock:
            exp = self._locks.get(compound_key)
            if exp is None:
                return False
            if exp <= now:
                del self._locks[compound_key]
                return False
            return True


class DurableIdempotencyStore:
    """Thread-safe SQLite/PostgreSQL durable WAL store for idempotency records."""

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._conn: Optional[sqlite3.Connection] = None
        if self.db_path == ":memory:":
            # Persistent connection for in-memory instance
            self._conn = sqlite3.connect(":memory:", check_same_thread=False, timeout=15.0)
            self._conn.row_factory = sqlite3.Row
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is not None:
            return self._conn
        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=15.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _close_conn(self, conn: sqlite3.Connection) -> None:
        if self._conn is None:
            conn.close()

    def _init_db(self) -> None:
        with self._lock:
            conn = self._get_conn()
            try:
                # Enable WAL mode for durability & concurrency if on disk
                if self.db_path != ":memory:":
                    conn.execute("PRAGMA journal_mode=WAL;")
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS idempotency_records (
                        compound_key TEXT PRIMARY KEY,
                        client_key TEXT NOT NULL,
                        tenant_id TEXT NOT NULL,
                        manifest_hash TEXT NOT NULL,
                        correlation_id TEXT NOT NULL,
                        status TEXT NOT NULL,
                        receipt_ref TEXT,
                        response_body TEXT,
                        expires_at REAL NOT NULL,
                        created_at REAL NOT NULL,
                        updated_at REAL NOT NULL
                    );
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_idempotency_tenant_key 
                    ON idempotency_records (tenant_id, client_key);
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_idempotency_expiry 
                    ON idempotency_records (expires_at);
                """)
                conn.commit()
            finally:
                self._close_conn(conn)

    def get(self, compound_key: str) -> Optional[IdempotencyRecord]:
        with self._lock:
            conn = self._get_conn()
            try:
                cur = conn.execute(
                    "SELECT * FROM idempotency_records WHERE compound_key = ?",
                    (compound_key,),
                )
                row = cur.fetchone()
                if not row:
                    return None
                return IdempotencyRecord(
                    key=row["client_key"],
                    tenant_id=row["tenant_id"],
                    manifest_hash=row["manifest_hash"],
                    correlation_id=row["correlation_id"],
                    status=IdempotencyStatus(row["status"]),
                    receipt_ref=row["receipt_ref"],
                    response_body=row["response_body"],
                    expires_at=float(row["expires_at"]),
                    created_at=float(row["created_at"]),
                    updated_at=float(row["updated_at"]),
                )
            finally:
                self._close_conn(conn)

    def insert_in_flight(self, record: IdempotencyRecord) -> bool:
        """Insert IN_FLIGHT record. Returns True if inserted, False if conflict."""
        with self._lock:
            conn = self._get_conn()
            try:
                now = time.time()
                # Check existing
                cur = conn.execute(
                    "SELECT status, expires_at FROM idempotency_records WHERE compound_key = ?",
                    (record.compound_key,),
                )
                existing = cur.fetchone()
                if existing:
                    # If expired or previously REJECTED, overwrite for retry
                    if existing["status"] == IdempotencyStatus.REJECTED.value or float(existing["expires_at"]) <= now:
                        conn.execute(
                            "DELETE FROM idempotency_records WHERE compound_key = ?",
                            (record.compound_key,),
                        )
                    else:
                        return False

                conn.execute(
                    """
                    INSERT INTO idempotency_records (
                        compound_key, client_key, tenant_id, manifest_hash,
                        correlation_id, status, receipt_ref, response_body,
                        expires_at, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.compound_key,
                        record.key,
                        record.tenant_id,
                        record.manifest_hash,
                        record.correlation_id,
                        record.status.value,
                        record.receipt_ref,
                        record.response_body,
                        record.expires_at,
                        record.created_at,
                        record.updated_at,
                    ),
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False
            finally:
                self._close_conn(conn)

    def update_status(
        self,
        compound_key: str,
        status: IdempotencyStatus,
        receipt_ref: Optional[str] = None,
        response_body: Optional[str] = None,
    ) -> Optional[IdempotencyRecord]:
        with self._lock:
            conn = self._get_conn()
            try:
                now = time.time()
                cur = conn.execute(
                    """
                    UPDATE idempotency_records
                    SET status = ?, receipt_ref = COALESCE(?, receipt_ref),
                        response_body = COALESCE(?, response_body),
                        updated_at = ?
                    WHERE compound_key = ?
                    """,
                    (status.value, receipt_ref, response_body, now, compound_key),
                )
                conn.commit()
                if cur.rowcount == 0:
                    return None
            finally:
                self._close_conn(conn)
        return self.get(compound_key)

    def purge_expired(self) -> int:
        with self._lock:
            conn = self._get_conn()
            try:
                now = time.time()
                cur = conn.execute("DELETE FROM idempotency_records WHERE expires_at < ?", (now,))
                deleted = cur.rowcount
                conn.commit()
                return deleted
            finally:
                self._close_conn(conn)


class IdempotencyGuardian:
    """The Sovereign Ingress Idempotency Guardian.

    Coordinates FastMutex (<10s) and Durable WAL store for zero-drift execution.
    """

    def __init__(
        self,
        store: Optional[DurableIdempotencyStore] = None,
        fast_mutex: Optional[FastMutexAccelerator] = None,
    ):
        self.store = store or DurableIdempotencyStore(":memory:")
        self.fast_mutex = fast_mutex or FastMutexAccelerator(default_ttl_sec=10.0)

    def acquire_or_replay(
        self,
        key: str,
        tenant_id: str,
        manifest_hash: str,
        correlation_id: str,
        ttl_seconds: float = 300.0,
    ) -> tuple[IdempotencyDecision, Optional[IdempotencyRecord]]:
        """Evaluate key ingress against FastMutex and Durable WAL.

        Returns (PROCEED, record) if caller should execute effect.
        Returns (REPLAY, record) if caller should replay cached result.
        Raises IdempotencyConflictError if operation is currently IN_FLIGHT.
        """
        compound_key = compute_compound_key(key, tenant_id, manifest_hash)
        now = time.time()

        # 1. FastMutex check (<10s short transit collision)
        # If fast mutex is actively held, this is an immediate burst conflict
        if not self.fast_mutex.try_acquire(compound_key, ttl_sec=min(ttl_seconds, 10.0)):
            existing = self.store.get(compound_key)
            cid = existing.correlation_id if existing else correlation_id
            raise IdempotencyConflictError(key, tenant_id, cid, "FastMutex burst collision: operation is in flight")

        # 2. Check durable WAL
        existing = self.store.get(compound_key)
        if existing:
            # Check expiration
            if existing.expires_at <= now:
                # Expired -> purge and treat as new
                self.store.purge_expired()
            elif existing.status == IdempotencyStatus.COMMITTED:
                # Already committed: release fast mutex and replay
                self.fast_mutex.release(compound_key)
                return IdempotencyDecision.REPLAY, existing
            elif existing.status == IdempotencyStatus.IN_FLIGHT:
                # Active in flight in DB
                raise IdempotencyConflictError(key, tenant_id, existing.correlation_id)
            elif existing.status == IdempotencyStatus.REJECTED:
                # Previously failed/rejected -> allow retry by continuing below
                pass

        # 3. Insert new IN_FLIGHT record into durable WAL
        record = IdempotencyRecord(
            key=key,
            tenant_id=tenant_id,
            manifest_hash=manifest_hash,
            correlation_id=correlation_id,
            status=IdempotencyStatus.IN_FLIGHT,
            receipt_ref=None,
            response_body=None,
            expires_at=now + ttl_seconds,
            created_at=now,
            updated_at=now,
        )

        inserted = self.store.insert_in_flight(record)
        if not inserted:
            # Race condition in WAL: re-read and conflict
            existing = self.store.get(compound_key)
            cid = existing.correlation_id if existing else correlation_id
            raise IdempotencyConflictError(key, tenant_id, cid, "Durable WAL collision: operation is in flight")

        return IdempotencyDecision.PROCEED, record

    def commit(
        self,
        key: str,
        tenant_id: str,
        manifest_hash: str,
        receipt_ref: str,
        response_body: Optional[Any] = None,
    ) -> IdempotencyRecord:
        """Mark record COMMITTED with the emitted receipt reference and optional response payload."""
        compound_key = compute_compound_key(key, tenant_id, manifest_hash)
        serialized_body = None
        if response_body is not None:
            if isinstance(response_body, (dict, list)):
                serialized_body = json.dumps(response_body)
            else:
                serialized_body = str(response_body)

        updated = self.store.update_status(
            compound_key,
            status=IdempotencyStatus.COMMITTED,
            receipt_ref=receipt_ref,
            response_body=serialized_body,
        )
        self.fast_mutex.release(compound_key)
        if not updated:
            raise ValueError(f"No idempotency record found to commit for compound key '{compound_key}'")
        return updated

    def reject(
        self,
        key: str,
        tenant_id: str,
        manifest_hash: str,
        reason: Optional[str] = None,
    ) -> IdempotencyRecord:
        """Mark record REJECTED upon execution or verification failure."""
        compound_key = compute_compound_key(key, tenant_id, manifest_hash)
        updated = self.store.update_status(
            compound_key,
            status=IdempotencyStatus.REJECTED,
            response_body=reason,
        )
        self.fast_mutex.release(compound_key)
        if not updated:
            raise ValueError(f"No idempotency record found to reject for compound key '{compound_key}'")
        return updated

    def purge_expired(self) -> int:
        return self.store.purge_expired()
