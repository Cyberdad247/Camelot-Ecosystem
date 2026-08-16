#!/usr/bin/env bash
#
# SQLite WAL init for the Camelot Bifrost Hub receipt service.
#
# Creates data/receipts.db (WAL journal mode) with tables that mirror the
# published contracts — packages/contracts/receipt.schema.json and
# receipt-chain.schema.json:
#   receipts       — every receipt (schema_version camelot-receipt/1)
#   chain_heads    — per-tenant chain head (camelot-receipt-chain/1)
#   ledger_anchors — signed anchor records at every Nth entry (§11.3, N=1000;
#                    per-tenant deviation from N is open question §27.5)
#   anchor_eligible (view) — the every-Nth anchor candidates
#
# Idempotent — safe to re-run any time (CREATE ... IF NOT EXISTS).
#
# Usage: sudo ./init-receipt-db.sh
# Env:   APP_DIR=...        control-plane root    (default /opt/camelot/bifrost-hub)
#        ANCHOR_INTERVAL=N  anchor cadence        (default 1000)
#        ADMIN_USER=...     owner of the DB files (default ubuntu)
#
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/camelot/bifrost-hub}"
ANCHOR_INTERVAL="${ANCHOR_INTERVAL:-1000}"
ADMIN_USER="${ADMIN_USER:-ubuntu}"
DB="$APP_DIR/data/receipts.db"

[ "$(id -u)" -eq 0 ] || { echo "error: run as root (sudo)"; exit 1; }
command -v sqlite3 >/dev/null || { echo "error: sqlite3 not installed (bootstrap installs it)"; exit 1; }

mkdir -p "$(dirname "$DB")"

sqlite3 "$DB" <<SQL
-- WAL journal: readers never block the writer; the nightly backup checkpoints it.
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA foreign_keys=ON;
PRAGMA busy_timeout=5000;

CREATE TABLE IF NOT EXISTS receipts (
    receipt_id       TEXT PRIMARY KEY,                 -- ^rcp_[A-Za-z0-9_-]+$
    tenant_id        TEXT NOT NULL,                    -- ^tenant_[A-Za-z0-9_-]+$
    chain_height     INTEGER NOT NULL,                 -- monotonic, per-tenant
    parent_hash      TEXT NOT NULL,                    -- ^sha256:[0-9a-fA-F]{64}$
    self_hash        TEXT NOT NULL,                    -- ^sha256:[0-9a-fA-F]{64}$
    correlation_id   TEXT NOT NULL,
    task_id          TEXT NOT NULL,
    authority_epoch  INTEGER NOT NULL,                 -- reject < trusted epoch (§6.3)
    effect_class     TEXT NOT NULL,                    -- closed set §5.5
    risk_tier        TEXT NOT NULL,                    -- T0..T4
    event            TEXT NOT NULL,                    -- stable verb
    signer           TEXT NOT NULL,                    -- proof.signer (e.g. 'sentinel')
    signature        TEXT NOT NULL,                    -- ^ed25519:...
    actor            TEXT NOT NULL,                    -- JSON {id, role, node_id, trust_band}
    refs             TEXT,                             -- JSON refs block
    payload_redacted TEXT,                             -- JSON role-scoped projection
    timestamp        TEXT NOT NULL,                    -- ISO-8601 UTC
    ledger_anchor_eligible INTEGER NOT NULL DEFAULT 0,
    body             TEXT NOT NULL                     -- full receipt JSON (canonical verify input)
);

-- Per-tenant height continuity: (tenant_id, chain_height) is unique, so a height
-- can only be appended once — no gaps, no rewrites (§11.3 height rule).
CREATE UNIQUE INDEX IF NOT EXISTS idx_receipts_tenant_height
    ON receipts(tenant_id, chain_height);

-- Fast head-of-chain lookup for ingest + anchor writes.
CREATE INDEX IF NOT EXISTS idx_receipts_tenant_height_desc
    ON receipts(tenant_id, chain_height DESC);

CREATE TABLE IF NOT EXISTS chain_heads (
    tenant_id          TEXT PRIMARY KEY,
    chain_height       INTEGER NOT NULL DEFAULT 0,
    head_hash          TEXT NOT NULL,                  -- self_hash of the latest receipt
    anchor_interval    INTEGER NOT NULL DEFAULT ${ANCHOR_INTERVAL},
    last_anchor_height INTEGER NOT NULL DEFAULT 0,
    last_anchor_hash   TEXT NOT NULL,                  -- sha256:0{64} for the first anchor
    verified           INTEGER NOT NULL DEFAULT 0,
    last_verified_at   TEXT,
    replay_protected   INTEGER NOT NULL DEFAULT 0,     -- nonce + timestamp window (§12.2)
    updated_at         TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS ledger_anchors (
    tenant_id           TEXT NOT NULL,
    chain_height        INTEGER NOT NULL,              -- anchor-eligible height (mod N == 0)
    head_hash           TEXT NOT NULL,
    anchor_interval     INTEGER NOT NULL DEFAULT ${ANCHOR_INTERVAL},
    last_anchor_height  INTEGER NOT NULL,
    last_anchor_hash    TEXT NOT NULL,
    signer              TEXT NOT NULL,
    signature           TEXT NOT NULL,                 -- ed25519 over canonical record (T-10, S-4)
    created_at          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    PRIMARY KEY (tenant_id, chain_height),
    FOREIGN KEY (tenant_id, chain_height)
        REFERENCES receipts(tenant_id, chain_height) ON DELETE RESTRICT
);

-- Anchor candidates: every Nth entry (§11.3). View keeps the interval visible
-- and adjustable in one place. Re-run with a new ANCHOR_INTERVAL after
-- DROP VIEW anchor_eligible if the interval changes.
CREATE VIEW IF NOT EXISTS anchor_eligible AS
    SELECT tenant_id, chain_height, self_hash, receipt_id
    FROM receipts
    WHERE chain_height % ${ANCHOR_INTERVAL} = 0
      AND ledger_anchor_eligible = 1;

PRAGMA user_version = 1;   -- schema version marker for future migrations
SQL

# The service runs as $ADMIN_USER; make sure the DB (and any -wal/-shm created
# during init) stays writable by it.
chown -R "$ADMIN_USER":"$ADMIN_USER" "$(dirname "$DB")"

echo "receipt DB ready (WAL): $DB"
echo "  journal_mode   : $(sqlite3 "$DB" 'PRAGMA journal_mode;')"
echo "  anchor_interval: $ANCHOR_INTERVAL (SADD §11.3 default N=1000)"
