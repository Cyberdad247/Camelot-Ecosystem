-- SPDX-License-Identifier: MIT
-- Phase 2 Enterprise Tenancy Isolation & RLS Enforcement Migration
-- Anchors: Camelot-OS SADD+LLDD v1.2 §9.2, §11.3, §12.2, §15

-- 1. Create IdempotencyStatus Enum
CREATE TYPE "IdempotencyStatus" AS ENUM ('IN_FLIGHT', 'COMPLETED', 'REJECTED');

-- 2. Add tenantId column to existing business tables with default 'tenant_default'
ALTER TABLE "JournalEntry" ADD COLUMN IF NOT EXISTS "tenantId" TEXT NOT NULL DEFAULT 'tenant_default';
ALTER TABLE "Transaction" ADD COLUMN IF NOT EXISTS "tenantId" TEXT NOT NULL DEFAULT 'tenant_default';
ALTER TABLE "Contact" ADD COLUMN IF NOT EXISTS "tenantId" TEXT NOT NULL DEFAULT 'tenant_default';
ALTER TABLE "Tag" ADD COLUMN IF NOT EXISTS "tenantId" TEXT NOT NULL DEFAULT 'tenant_default';
ALTER TABLE "EmailSequence" ADD COLUMN IF NOT EXISTS "tenantId" TEXT NOT NULL DEFAULT 'tenant_default';
ALTER TABLE "SequenceStep" ADD COLUMN IF NOT EXISTS "tenantId" TEXT NOT NULL DEFAULT 'tenant_default';
ALTER TABLE "MessageThread" ADD COLUMN IF NOT EXISTS "tenantId" TEXT NOT NULL DEFAULT 'tenant_default';
ALTER TABLE "Message" ADD COLUMN IF NOT EXISTS "tenantId" TEXT NOT NULL DEFAULT 'tenant_default';
ALTER TABLE "EchoLog" ADD COLUMN IF NOT EXISTS "tenantId" TEXT NOT NULL DEFAULT 'tenant_default';

-- Create Indexes for tenant filtering
CREATE INDEX IF NOT EXISTS "JournalEntry_tenantId_idx" ON "JournalEntry"("tenantId");
CREATE INDEX IF NOT EXISTS "Transaction_tenantId_idx" ON "Transaction"("tenantId");
CREATE INDEX IF NOT EXISTS "Contact_tenantId_idx" ON "Contact"("tenantId");
CREATE INDEX IF NOT EXISTS "Tag_tenantId_idx" ON "Tag"("tenantId");
CREATE INDEX IF NOT EXISTS "EmailSequence_tenantId_idx" ON "EmailSequence"("tenantId");
CREATE INDEX IF NOT EXISTS "SequenceStep_tenantId_idx" ON "SequenceStep"("tenantId");
CREATE INDEX IF NOT EXISTS "MessageThread_tenantId_idx" ON "MessageThread"("tenantId");
CREATE INDEX IF NOT EXISTS "Message_tenantId_idx" ON "Message"("tenantId");
CREATE INDEX IF NOT EXISTS "EchoLog_tenantId_idx" ON "EchoLog"("tenantId");

-- 3. Create Tenant Table (§9.2)
CREATE TABLE IF NOT EXISTS "Tenant" (
    "id" TEXT NOT NULL,
    "schemaVersion" TEXT NOT NULL DEFAULT 'camelot-tenant/1',
    "organizationId" TEXT NOT NULL,
    "agencyId" TEXT NOT NULL,
    "branding" JSONB,
    "avatar" JSONB,
    "enabledModules" TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    "connectorAllowlist" TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    "policyOverrides" JSONB,
    "retentionDraftDays" INTEGER NOT NULL DEFAULT 30,
    "retentionReceiptDays" INTEGER NOT NULL DEFAULT 365,
    "maxRiskTierAllowed" TEXT NOT NULL DEFAULT 'T2',
    "status" TEXT NOT NULL DEFAULT 'active',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Tenant_pkey" PRIMARY KEY ("id")
);

CREATE INDEX IF NOT EXISTS "Tenant_organizationId_idx" ON "Tenant"("organizationId");
CREATE INDEX IF NOT EXISTS "Tenant_status_idx" ON "Tenant"("status");

-- 4. Create bifrost_idempotency_journal Table (Phase 1B §12.2)
CREATE TABLE IF NOT EXISTS "bifrost_idempotency_journal" (
    "client_key" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "manifest_hash" TEXT NOT NULL,
    "correlation_id" TEXT NOT NULL,
    "status" "IdempotencyStatus" NOT NULL DEFAULT 'IN_FLIGHT',
    "receipt_ref" TEXT,
    "response_body" TEXT,
    "expires_at" TIMESTAMP(3) NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "bifrost_idempotency_journal_pkey" PRIMARY KEY ("tenant_id", "client_key")
);

CREATE INDEX IF NOT EXISTS "bifrost_idemp_tenant_manifest_idx" ON "bifrost_idempotency_journal"("tenant_id", "manifest_hash");
CREATE INDEX IF NOT EXISTS "bifrost_idemp_expiresAt_idx" ON "bifrost_idempotency_journal"("expires_at");

-- 5. Create Core Engine Tables: workspaces, tasks, capability_leases, receipts
CREATE TABLE IF NOT EXISTS "workspaces" (
    "id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "namespace_prefix" TEXT,
    "source_policy" JSONB,
    "status" TEXT NOT NULL DEFAULT 'active',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "workspaces_pkey" PRIMARY KEY ("id")
);

CREATE INDEX IF NOT EXISTS "workspaces_tenant_id_idx" ON "workspaces"("tenant_id");

CREATE TABLE IF NOT EXISTS "tasks" (
    "id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "workspace_id" TEXT,
    "correlation_id" TEXT NOT NULL,
    "objective" TEXT NOT NULL,
    "symbolect_tree_ref" TEXT,
    "manifest_id" TEXT,
    "lease_id" TEXT,
    "status" TEXT NOT NULL DEFAULT 'draft',
    "actor" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "expires_at" TIMESTAMP(3),
    "receipt_refs" TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],

    CONSTRAINT "tasks_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "tasks_workspace_fkey" FOREIGN KEY ("workspace_id") REFERENCES "workspaces"("id") ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS "tasks_tenant_id_idx" ON "tasks"("tenant_id");
CREATE INDEX IF NOT EXISTS "tasks_workspace_id_idx" ON "tasks"("workspace_id");
CREATE INDEX IF NOT EXISTS "tasks_correlation_id_idx" ON "tasks"("correlation_id");

CREATE TABLE IF NOT EXISTS "capability_leases" (
    "id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "task_id" TEXT NOT NULL,
    "correlation_id" TEXT NOT NULL,
    "manifest_hash" TEXT NOT NULL,
    "authority_epoch" INTEGER NOT NULL,
    "authority_vector" INTEGER[] NOT NULL,
    "effect_class" TEXT NOT NULL,
    "declared_risk_tier" TEXT NOT NULL,
    "subject" JSONB NOT NULL,
    "permissions" JSONB NOT NULL,
    "limits" JSONB NOT NULL,
    "properties" JSONB,
    "derived_capabilities_provenance" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "expires_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "capability_leases_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "capability_leases_task_fkey" FOREIGN KEY ("task_id") REFERENCES "tasks"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS "capability_leases_tenant_id_idx" ON "capability_leases"("tenant_id");
CREATE INDEX IF NOT EXISTS "capability_leases_task_id_idx" ON "capability_leases"("task_id");

-- 6. Create receipt_chains Table (Phase 1B §11.3)
CREATE TABLE IF NOT EXISTS "receipt_chains" (
    "tenant_id" TEXT NOT NULL,
    "schema_version" TEXT NOT NULL DEFAULT 'camelot-receipt-chain/1',
    "chain_height" INTEGER NOT NULL DEFAULT 0,
    "head_hash" TEXT NOT NULL,
    "anchor_interval" INTEGER NOT NULL DEFAULT 1000,
    "last_anchor_height" INTEGER NOT NULL DEFAULT 0,
    "last_anchor_hash" TEXT NOT NULL,
    "anchor_target" TEXT,
    "verified" BOOLEAN NOT NULL DEFAULT true,
    "last_verified_at" TIMESTAMP(3),
    "replay_protected" BOOLEAN NOT NULL DEFAULT true,
    "proof_signer" TEXT,
    "proof_signature" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "receipt_chains_pkey" PRIMARY KEY ("tenant_id")
);

CREATE INDEX IF NOT EXISTS "receipt_chains_chain_height_idx" ON "receipt_chains"("chain_height");

-- 7. Create receipts Table (Phase 1B §11.3)
CREATE TABLE IF NOT EXISTS "receipts" (
    "id" TEXT NOT NULL,
    "schema_version" TEXT NOT NULL DEFAULT 'camelot-receipt/2',
    "parent_hash" TEXT NOT NULL,
    "self_hash" TEXT NOT NULL,
    "chain_height" INTEGER NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "correlation_id" TEXT NOT NULL,
    "task_id" TEXT NOT NULL,
    "authority_epoch" INTEGER NOT NULL,
    "authority_vector" INTEGER[] NOT NULL,
    "effect_class" TEXT NOT NULL,
    "declared_risk_tier" TEXT NOT NULL,
    "timestamp" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "actor_id" TEXT NOT NULL,
    "actor_role" TEXT NOT NULL,
    "actor_node_id" TEXT NOT NULL,
    "actor_trust_band" TEXT NOT NULL,
    "event" TEXT NOT NULL,
    "manifest_hash" TEXT,
    "lease_id" TEXT,
    "parent_receipt_id" TEXT,
    "payload_redacted" JSONB,
    "proof_signer" TEXT NOT NULL,
    "proof_signature" TEXT NOT NULL,
    "ledger_anchor_eligible" BOOLEAN NOT NULL DEFAULT false,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "receipts_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "receipts_tenant_chain_fkey" FOREIGN KEY ("tenant_id") REFERENCES "receipt_chains"("tenant_id") ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS "receipts_tenant_height_key" ON "receipts"("tenant_id", "chain_height");
CREATE INDEX IF NOT EXISTS "receipts_tenant_parent_hash_idx" ON "receipts"("tenant_id", "parent_hash");
CREATE INDEX IF NOT EXISTS "receipts_correlation_id_idx" ON "receipts"("correlation_id");
CREATE INDEX IF NOT EXISTS "receipts_self_hash_idx" ON "receipts"("self_hash");

-- ─────────────────────────────────────────────────────────────────────────────
-- ROW-LEVEL SECURITY ENFORCEMENT (Phase 2 Iron Gate)
-- ─────────────────────────────────────────────────────────────────────────────

-- 8. Enable and FORCE Row-Level Security on all multi-tenant tables
ALTER TABLE "workspaces" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "workspaces" FORCE ROW LEVEL SECURITY;

ALTER TABLE "tasks" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "tasks" FORCE ROW LEVEL SECURITY;

ALTER TABLE "receipts" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "receipts" FORCE ROW LEVEL SECURITY;

ALTER TABLE "capability_leases" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "capability_leases" FORCE ROW LEVEL SECURITY;

ALTER TABLE "bifrost_idempotency_journal" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "bifrost_idempotency_journal" FORCE ROW LEVEL SECURITY;

ALTER TABLE "receipt_chains" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "receipt_chains" FORCE ROW LEVEL SECURITY;

ALTER TABLE "JournalEntry" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "JournalEntry" FORCE ROW LEVEL SECURITY;

ALTER TABLE "Transaction" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Transaction" FORCE ROW LEVEL SECURITY;

ALTER TABLE "Contact" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Contact" FORCE ROW LEVEL SECURITY;

ALTER TABLE "Tag" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Tag" FORCE ROW LEVEL SECURITY;

ALTER TABLE "EmailSequence" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "EmailSequence" FORCE ROW LEVEL SECURITY;

ALTER TABLE "SequenceStep" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "SequenceStep" FORCE ROW LEVEL SECURITY;

ALTER TABLE "MessageThread" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "MessageThread" FORCE ROW LEVEL SECURITY;

ALTER TABLE "Message" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Message" FORCE ROW LEVEL SECURITY;

ALTER TABLE "EchoLog" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "EchoLog" FORCE ROW LEVEL SECURITY;

-- 9. Restrictive Isolation Policies
-- Invariant: If current_setting('app.current_tenant_id', true) is NULL (unauthenticated),
-- comparison evaluates to NULL/FALSE, blocking ALL reads and writes unconditionally.

CREATE POLICY "tenant_isolation_policy" ON "workspaces"
    AS RESTRICTIVE FOR ALL
    USING ("tenant_id" = current_setting('app.current_tenant_id', true))
    WITH CHECK ("tenant_id" = current_setting('app.current_tenant_id', true));

CREATE POLICY "tenant_isolation_policy" ON "tasks"
    AS RESTRICTIVE FOR ALL
    USING ("tenant_id" = current_setting('app.current_tenant_id', true))
    WITH CHECK ("tenant_id" = current_setting('app.current_tenant_id', true));

CREATE POLICY "tenant_isolation_policy" ON "receipts"
    AS RESTRICTIVE FOR ALL
    USING ("tenant_id" = current_setting('app.current_tenant_id', true))
    WITH CHECK ("tenant_id" = current_setting('app.current_tenant_id', true));

CREATE POLICY "tenant_isolation_policy" ON "capability_leases"
    AS RESTRICTIVE FOR ALL
    USING ("tenant_id" = current_setting('app.current_tenant_id', true))
    WITH CHECK ("tenant_id" = current_setting('app.current_tenant_id', true));

CREATE POLICY "tenant_isolation_policy" ON "bifrost_idempotency_journal"
    AS RESTRICTIVE FOR ALL
    USING ("tenant_id" = current_setting('app.current_tenant_id', true))
    WITH CHECK ("tenant_id" = current_setting('app.current_tenant_id', true));

CREATE POLICY "tenant_isolation_policy" ON "receipt_chains"
    AS RESTRICTIVE FOR ALL
    USING ("tenant_id" = current_setting('app.current_tenant_id', true))
    WITH CHECK ("tenant_id" = current_setting('app.current_tenant_id', true));

CREATE POLICY "tenant_isolation_journal_entry" ON "JournalEntry"
    AS RESTRICTIVE FOR ALL
    USING ("tenantId" = current_setting('app.current_tenant_id', true))
    WITH CHECK ("tenantId" = current_setting('app.current_tenant_id', true));

CREATE POLICY "tenant_isolation_transaction" ON "Transaction"
    AS RESTRICTIVE FOR ALL
    USING ("tenantId" = current_setting('app.current_tenant_id', true))
    WITH CHECK ("tenantId" = current_setting('app.current_tenant_id', true));

CREATE POLICY "tenant_isolation_contact" ON "Contact"
    AS RESTRICTIVE FOR ALL
    USING ("tenantId" = current_setting('app.current_tenant_id', true))
    WITH CHECK ("tenantId" = current_setting('app.current_tenant_id', true));

CREATE POLICY "tenant_isolation_tag" ON "Tag"
    AS RESTRICTIVE FOR ALL
    USING ("tenantId" = current_setting('app.current_tenant_id', true))
    WITH CHECK ("tenantId" = current_setting('app.current_tenant_id', true));

CREATE POLICY "tenant_isolation_email_seq" ON "EmailSequence"
    AS RESTRICTIVE FOR ALL
    USING ("tenantId" = current_setting('app.current_tenant_id', true))
    WITH CHECK ("tenantId" = current_setting('app.current_tenant_id', true));

CREATE POLICY "tenant_isolation_seq_step" ON "SequenceStep"
    AS RESTRICTIVE FOR ALL
    USING ("tenantId" = current_setting('app.current_tenant_id', true))
    WITH CHECK ("tenantId" = current_setting('app.current_tenant_id', true));

CREATE POLICY "tenant_isolation_msg_thread" ON "MessageThread"
    AS RESTRICTIVE FOR ALL
    USING ("tenantId" = current_setting('app.current_tenant_id', true))
    WITH CHECK ("tenantId" = current_setting('app.current_tenant_id', true));

CREATE POLICY "tenant_isolation_message" ON "Message"
    AS RESTRICTIVE FOR ALL
    USING ("tenantId" = current_setting('app.current_tenant_id', true))
    WITH CHECK ("tenantId" = current_setting('app.current_tenant_id', true));

CREATE POLICY "tenant_isolation_echo_log" ON "EchoLog"
    AS RESTRICTIVE FOR ALL
    USING ("tenantId" = current_setting('app.current_tenant_id', true))
    WITH CHECK ("tenantId" = current_setting('app.current_tenant_id', true));
