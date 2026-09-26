# SPDX-License-Identifier: MIT
"""Adversarial Test Suite — Phase 2 Enterprise Tenancy Isolation & PostgreSQL RLS Enforcement.

Validates the zero-trust tenancy barrier across:
    1. PostgreSQL Migration DDL Rigor (ENABLE + FORCE RLS + RESTRICTIVE policies on
       workspaces, tasks, receipts, capability_leases, bifrost_idempotency_journal).
    2. Connection Handshake (DISCARD TEMP, SET LOCAL tenant_id, principal_id, risk_tier).
    3. Cross-Tenant Read Leak (Tenant A cannot see Tenant B data).
    4. Cross-Tenant Write & Spoofing (Tenant A cannot write/update Tenant B data).
    5. Unset / Unauthenticated Session (NULL tenant yields empty set and rejects writes).
    6. Tenant Identifier Injection (SQL injection and pattern violations blocked).
    7. Idempotency Key Isolation & Payload Mismatch (HTTP 422 IDEMPOTENCY_PAYLOAD_MISMATCH).
    8. Merkle Receipt Chain Cross-Tenant Isolation (No cross-chain linking).
"""
from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from control_plane.dispatch.idempotency_guardian import (
    IdempotencyGuardian,
    IdempotencyDecision,
    IdempotencyPayloadMismatchError,
)
from control_plane.security.connection_handshake import (
    MockPostgresConnection,
    TenancyHandshakeError,
    generate_handshake_sql,
    scoped_tenant_connection,
    validate_handshake_parameters,
)
from control_plane.security.receipt_chain import (
    GENESIS_PARENT_HASH,
    Receipt,
    ReceiptActor,
    ReceiptProof,
    TenantIsolationViolation,
    TenantReceiptChain,
)

MIGRATION_PATH = (
    REPO_ROOT
    / "packages"
    / "db"
    / "migrations"
    / "20260913_enterprise_rls_tenancy"
    / "migration.sql"
)

CORE_ENGINE_TABLES = [
    "workspaces",
    "tasks",
    "receipts",
    "capability_leases",
    "bifrost_idempotency_journal",
    "receipt_chains",
]

LEGACY_DOMAIN_TABLES = [
    "JournalEntry",
    "Transaction",
    "Contact",
    "Tag",
    "EmailSequence",
    "SequenceStep",
    "MessageThread",
    "Message",
    "EchoLog",
]

ALL_MULTI_TENANT_TABLES = CORE_ENGINE_TABLES + LEGACY_DOMAIN_TABLES


# ==============================================================================
# 1. PostgreSQL Migration DDL Rigor Audit
# ==============================================================================

def test_migration_file_exists():
    assert MIGRATION_PATH.exists(), f"Migration file missing at {MIGRATION_PATH}"


def test_ddl_enables_and_forces_rls_on_all_multi_tenant_tables():
    content = MIGRATION_PATH.read_text(encoding="utf-8")

    for table in ALL_MULTI_TENANT_TABLES:
        enable_pattern = rf'ALTER\s+TABLE\s+"{table}"\s+ENABLE\s+ROW\s+LEVEL\s+SECURITY\s*;'
        force_pattern = rf'ALTER\s+TABLE\s+"{table}"\s+FORCE\s+ROW\s+LEVEL\s+SECURITY\s*;'

        assert re.search(enable_pattern, content, re.IGNORECASE), (
            f"Table '{table}' missing 'ENABLE ROW LEVEL SECURITY'"
        )
        assert re.search(force_pattern, content, re.IGNORECASE), (
            f"Table '{table}' missing 'FORCE ROW LEVEL SECURITY' (table owners could bypass RLS!)"
        )


def test_ddl_policies_use_current_setting_and_with_check():
    content = MIGRATION_PATH.read_text(encoding="utf-8")

    for table in ALL_MULTI_TENANT_TABLES:
        policy_decl = rf'CREATE\s+POLICY\s+"[^"]+"\s+ON\s+"{table}"'
        assert re.search(policy_decl, content, re.IGNORECASE), (
            f"Table '{table}' missing CREATE POLICY statement"
        )

    # Invariant: policies must use current_setting('app.current_tenant_id', true)
    setting_matches = re.findall(
        r"current_setting\(\s*'app\.current_tenant_id'\s*,\s*true\s*\)",
        content,
        re.IGNORECASE,
    )
    assert len(setting_matches) >= len(ALL_MULTI_TENANT_TABLES) * 2, (
        f"Expected at least {len(ALL_MULTI_TENANT_TABLES) * 2} occurrences of current_setting, got {len(setting_matches)}"
    )

    # Invariant: AS RESTRICTIVE must be present on every table policy
    restrictive_matches = re.findall(r"AS\s+RESTRICTIVE", content, re.IGNORECASE)
    assert len(restrictive_matches) == len(ALL_MULTI_TENANT_TABLES), (
        f"Expected {len(ALL_MULTI_TENANT_TABLES)} AS RESTRICTIVE policies, got {len(restrictive_matches)}"
    )


def test_core_engine_tenant_isolation_policy_names():
    """Verify core engine tables use the exact 'tenant_isolation_policy' name."""
    content = MIGRATION_PATH.read_text(encoding="utf-8")
    for table in CORE_ENGINE_TABLES:
        pattern = rf'CREATE\s+POLICY\s+"tenant_isolation_policy"\s+ON\s+"{table}"'
        assert re.search(pattern, content, re.IGNORECASE), (
            f"Core engine table '{table}' missing exact 'tenant_isolation_policy'"
        )


# ==============================================================================
# 2. Connection Handshake Sanitization Tests
# ==============================================================================

def test_connection_handshake_sql_generation():
    """Verify handshake produces DISCARD TEMP and SET LOCAL statements."""
    statements = generate_handshake_sql(
        tenant_id="tenant_omega_01",
        principal_id="actor_sir_codex",
        risk_tier="T2",
    )

    assert statements[0] == "DISCARD TEMP;"
    assert statements[1] == "SET LOCAL app.current_tenant_id = 'tenant_omega_01';"
    assert statements[2] == "SET LOCAL app.current_principal_id = 'actor_sir_codex';"
    assert statements[3] == "SET LOCAL app.current_risk_tier = 'T2';"


def test_connection_handshake_parameter_validation():
    """Verify handshake rejects invalid tenant formats and dangerous characters."""
    with pytest.raises(TenancyHandshakeError):
        validate_handshake_parameters("invalid_tenant", "actor_1", "T1")

    with pytest.raises(TenancyHandshakeError):
        validate_handshake_parameters("tenant_valid", "", "T1")

    with pytest.raises(TenancyHandshakeError):
        validate_handshake_parameters("tenant_valid", "actor_1", "T9_INVALID")


def test_scoped_tenant_connection_context_manager():
    """Verify connection context manager sets and cleans up session attributes."""
    conn = MockPostgresConnection()

    with scoped_tenant_connection(conn, "tenant_scoped_01", "actor_forge", "T1"):
        assert conn._app_current_tenant_id == "tenant_scoped_01"
        assert conn._app_current_principal_id == "actor_forge"
        assert conn._app_current_risk_tier == "T1"
        assert "DISCARD TEMP;" in conn.statements_executed

    # Reset on exit
    assert conn._app_current_tenant_id is None
    assert conn._app_current_principal_id is None
    assert conn._app_current_risk_tier is None
    assert "RESET ALL;" in conn.statements_executed


# ==============================================================================
# 3. In-Memory RLS Session Barrier Emulator
# ==============================================================================

class PostgresRLSSessionEmulator:
    """Emulates PostgreSQL Row-Level Security session semantics.

    Strictly reproduces:
        - SET LOCAL app.current_tenant_id = ?
        - UNSET / NULL yields NULL
        - USING clause filters reads
        - WITH CHECK clause validates writes
        - FORCE ROW LEVEL SECURITY prevents bypass
    """

    TENANT_ID_REGEX = re.compile(r"^tenant_[A-Za-z0-9_-]+$")

    def __init__(self):
        self._conn = sqlite3.connect(":memory:")
        self._conn.row_factory = sqlite3.Row
        self._current_tenant: str | None = None
        self._setup_schema()

    def _setup_schema(self):
        self._conn.execute("""
            CREATE TABLE documents (
                id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL
            );
        """)
        self._conn.commit()

    def set_session_tenant(self, tenant_id: str | None) -> None:
        """SET LOCAL app.current_tenant_id = ?"""
        if tenant_id is not None:
            if not self.TENANT_ID_REGEX.match(tenant_id):
                raise ValueError(f"Invalid tenant_id format: '{tenant_id}'")
        self._current_tenant = tenant_id

    def get_session_tenant(self) -> str | None:
        return self._current_tenant

    def insert_document(self, doc_id: str, tenant_id: str, title: str, content: str) -> None:
        """Simulates INSERT with WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true))."""
        active = self.get_session_tenant()
        if active is None or active != tenant_id:
            raise PermissionError(
                f"new row violates row-level security policy for table \"documents\" (active tenant: '{active}', target: '{tenant_id}')"
            )
        self._conn.execute(
            "INSERT INTO documents (id, tenant_id, title, content) VALUES (?, ?, ?, ?)",
            (doc_id, tenant_id, title, content),
        )
        self._conn.commit()

    def select_documents(self) -> list[dict]:
        """Simulates SELECT with USING (tenant_id = current_setting('app.current_tenant_id', true))."""
        active = self.get_session_tenant()
        if active is None:
            return []
        cur = self._conn.execute(
            "SELECT * FROM documents WHERE tenant_id = ?",
            (active,),
        )
        return [dict(row) for row in cur.fetchall()]

    def update_document(self, doc_id: str, new_title: str) -> int:
        """Simulates UPDATE with USING + WITH CHECK."""
        active = self.get_session_tenant()
        if active is None:
            return 0
        cur = self._conn.execute(
            "UPDATE documents SET title = ? WHERE id = ? AND tenant_id = ?",
            (new_title, doc_id, active),
        )
        self._conn.commit()
        return cur.rowcount


# ==============================================================================
# 4. Adversarial Tenancy Attack Tests
# ==============================================================================

def test_cross_tenant_read_leak_adversary():
    """Tenant A attempts to read Tenant B's documents. Must return empty set."""
    db = PostgresRLSSessionEmulator()

    db.set_session_tenant("tenant_alpha")
    db.insert_document("doc_a1", "tenant_alpha", "Alpha Secret Plan", "Top Secret Alpha Content")

    db.set_session_tenant("tenant_beta")
    db.insert_document("doc_b1", "tenant_beta", "Beta Financial Ledger", "Top Secret Beta Content")

    db.set_session_tenant("tenant_alpha")
    docs = db.select_documents()

    assert len(docs) == 1
    assert docs[0]["id"] == "doc_a1"
    assert docs[0]["tenant_id"] == "tenant_alpha"
    assert all(d["tenant_id"] != "tenant_beta" for d in docs)


def test_cross_tenant_write_spoofing_adversary():
    """Tenant Alpha attempts to write a record under Tenant Beta's namespace. Must be blocked."""
    db = PostgresRLSSessionEmulator()
    db.set_session_tenant("tenant_alpha")

    with pytest.raises(PermissionError) as exc_info:
        db.insert_document("doc_spoof", "tenant_beta", "Spoofed Title", "Malicious injection")

    assert "violates row-level security policy" in str(exc_info.value)


def test_unset_tenant_context_adversary():
    """Unauthenticated request (session tenant is NULL). Must reject all writes and return 0 rows."""
    db = PostgresRLSSessionEmulator()

    db.set_session_tenant("tenant_alpha")
    db.insert_document("doc_1", "tenant_alpha", "Notice", "Public notice")

    # Clear tenant session (simulating unauthenticated ingress)
    db.set_session_tenant(None)

    # SELECT returns zero rows
    assert db.select_documents() == []

    # INSERT is blocked
    with pytest.raises(PermissionError):
        db.insert_document("doc_unauth", "tenant_alpha", "Unauthorized", "Blocked")


def test_tenant_identifier_injection_adversary():
    """Adversary attempts SQL injection in the tenant identifier parameter."""
    db = PostgresRLSSessionEmulator()

    malicious_payloads = [
        "tenant_alpha' OR '1'='1",
        "tenant_alpha; DROP TABLE documents;",
        "tenant_/*comment*/alpha",
        "' UNION SELECT * FROM documents --",
        "tenant_alpha\x00malicious",
    ]

    for payload in malicious_payloads:
        with pytest.raises(ValueError) as exc_info:
            db.set_session_tenant(payload)
        assert "Invalid tenant_id format" in str(exc_info.value)


def test_idempotency_payload_mismatch_adversary():
    """Reusing identical idempotency key with deviated payload triggers HTTP 422 IDEMPOTENCY_PAYLOAD_MISMATCH."""
    guardian = IdempotencyGuardian()
    key = "key_adversary_001"
    tenant_id = "tenant_victim"
    manifest_original = "sha256:" + "a" * 64
    manifest_tampered = "sha256:" + "b" * 64

    guardian.acquire_or_replay(key, tenant_id, manifest_original, "cor_1")

    with pytest.raises(IdempotencyPayloadMismatchError) as exc_info:
        guardian.acquire_or_replay(key, tenant_id, manifest_tampered, "cor_2")

    assert exc_info.value.status_code == 422
    assert exc_info.value.error_code == "IDEMPOTENCY_PAYLOAD_MISMATCH"


def test_idempotency_cross_tenant_isolation_adversary():
    """Tenant A and Tenant B use the exact same client idempotency key.

    Tenant B must not receive Tenant A's cached response, and Tenant A's execution
    must not block Tenant B from executing.
    """
    guardian = IdempotencyGuardian()
    shared_key = "idemp_client_key_001"
    manifest_hash = "sha256:1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff"

    # Tenant Alpha executes first
    dec_a, rec_a = guardian.acquire_or_replay(shared_key, "tenant_alpha", manifest_hash, "cor_a1")
    assert dec_a == IdempotencyDecision.PROCEED
    guardian.commit(shared_key, "tenant_alpha", manifest_hash, "rcp_alpha_001", {"tenant": "alpha", "balance": 500})

    # Tenant Beta executes with the identical key
    dec_b, rec_b = guardian.acquire_or_replay(shared_key, "tenant_beta", manifest_hash, "cor_b1")
    assert dec_b == IdempotencyDecision.PROCEED, "Tenant Beta should proceed independently!"
    guardian.commit(shared_key, "tenant_beta", manifest_hash, "rcp_beta_001", {"tenant": "beta", "balance": 9999})

    # When Tenant Alpha replays, it receives ONLY Alpha's balance
    _, replay_a = guardian.acquire_or_replay(shared_key, "tenant_alpha", manifest_hash, "cor_a2")
    assert replay_a.receipt_ref == "rcp_alpha_001"
    assert "500" in replay_a.response_body
    assert "beta" not in replay_a.response_body

    # When Tenant Beta replays, it receives ONLY Beta's balance
    _, replay_b = guardian.acquire_or_replay(shared_key, "tenant_beta", manifest_hash, "cor_b2")
    assert replay_b.receipt_ref == "rcp_beta_001"
    assert "9999" in replay_b.response_body
    assert "alpha" not in replay_b.response_body


def test_merkle_receipt_chain_cross_tenant_adversary():
    """Adversary attempts to link Tenant Beta's receipt to Tenant Alpha's Merkle chain."""
    chain_alpha = TenantReceiptChain("tenant_alpha")
    r_genesis_alpha = Receipt(
        receipt_id="rcp_alpha_genesis",
        tenant_id="tenant_alpha",
        correlation_id="cor_a0",
        task_id="task_a0",
        chain_height=0,
        parent_hash=GENESIS_PARENT_HASH,
        authority_epoch=1,
        authority_vector=[1, 1, 0, 1, 1, 1],
        effect_class="workspace.patch",
        declared_risk_tier="T0",
        actor=ReceiptActor("sir-sentinel", "security_warden", "cybertronia-1", "attested"),
        event="chain.genesis",
        proof=ReceiptProof("sentinel", "ed25519:sig"),
    )
    chain_alpha.append(r_genesis_alpha)

    # Malicious attempt to append a receipt with tenant_id = 'tenant_beta'
    r_malicious = Receipt(
        receipt_id="rcp_beta_cross",
        tenant_id="tenant_beta",
        correlation_id="cor_attack",
        task_id="task_attack",
        chain_height=1,
        parent_hash=chain_alpha.head_hash,
        authority_epoch=1,
        authority_vector=[1, 1, 0, 1, 1, 1],
        effect_class="workspace.patch",
        declared_risk_tier="T0",
        actor=ReceiptActor("sir-sentinel", "security_warden", "cybertronia-1", "attested"),
        event="cross.tenant.attack",
        proof=ReceiptProof("sentinel", "ed25519:sig"),
    )

    with pytest.raises(TenantIsolationViolation) as exc_info:
        chain_alpha.append(r_malicious)

    assert "Cannot append receipt for tenant 'tenant_beta' to chain for tenant 'tenant_alpha'" in str(exc_info.value)
