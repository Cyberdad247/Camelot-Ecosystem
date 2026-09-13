-- SPDX-License-Identifier: MIT
-- Phase 2 Enterprise Tenancy Isolation & RLS Enforcement Migration
-- Anchors: Camelot-OS SADD+LLDD v1.2 §9.2, §11.3, §12.2, §15

-- 1. Create IdempotencyStatus Enum
CREATE TYPE "IdempotencyStatus" AS ENUM ('IN_FLIGHT', 'COMMITTED', 'REJECTED');

-- 2. Add tenantId column to existing business tables with default 'tenant_default'
ALTER TABLE "JournalEntry" ADD COLUMN "tenantId" TEXT NOT NULL DEFAULT 'tenant_default';
ALTER TABLE "Transaction" ADD COLUMN "tenantId" TEXT NOT NULL DEFAULT 'tenant_default';
ALTER TABLE "Contact" ADD COLUMN "tenantId" TEXT NOT NULL DEFAULT 'tenant_default';
ALTER TABLE "Tag" ADD COLUMN "tenantId" TEXT NOT NULL DEFAULT 'tenant_default';
ALTER TABLE "EmailSequence" ADD COLUMN "tenantId" TEXT NOT NULL DEFAULT 'tenant_default';
ALTER TABLE "SequenceStep" ADD COLUMN "tenantId" TEXT NOT NULL DEFAULT 'tenant_default';
ALTER TABLE "MessageThread" ADD COLUMN "tenantId" TEXT NOT NULL DEFAULT 'tenant_default';
ALTER TABLE "Message" ADD COLUMN "tenantId" TEXT NOT NULL DEFAULT 'tenant_default';
ALTER TABLE "EchoLog" ADD COLUMN "tenantId" TEXT NOT NULL DEFAULT 'tenant_default';

-- Create Indexes for tenant filtering
CREATE INDEX "JournalEntry_tenantId_idx" ON "JournalEntry"("tenantId");
CREATE INDEX "Transaction_tenantId_idx" ON "Transaction"("tenantId");
CREATE INDEX "Contact_tenantId_idx" ON "Contact"("tenantId");
CREATE INDEX "Tag_tenantId_idx" ON "Tag"("tenantId");
CREATE INDEX "EmailSequence_tenantId_idx" ON "EmailSequence"("tenantId");
CREATE INDEX "SequenceStep_tenantId_idx" ON "SequenceStep"("tenantId");
CREATE INDEX "MessageThread_tenantId_idx" ON "MessageThread"("tenantId");
CREATE INDEX "Message_tenantId_idx" ON "Message"("tenantId");
CREATE INDEX "EchoLog_tenantId_idx" ON "EchoLog"("tenantId");

-- 3. Create Tenant Table (§9.2)
CREATE TABLE "Tenant" (
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

CREATE INDEX "Tenant_organizationId_idx" ON "Tenant"("organizationId");
CREATE INDEX "Tenant_status_idx" ON "Tenant"("status");

-- 4. Create IdempotencyRecord Table (Phase 1B §12.2)
CREATE TABLE "IdempotencyRecord" (
    "key" TEXT NOT NULL,
    "tenantId" TEXT NOT NULL,
    "manifestHash" TEXT NOT NULL,
    "correlationId" TEXT NOT NULL,
    "status" "IdempotencyStatus" NOT NULL DEFAULT 'IN_FLIGHT',
    "receiptRef" TEXT,
    "responseBody" TEXT,
    "expiresAt" TIMESTAMP(3) NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "IdempotencyRecord_pkey" PRIMARY KEY ("key")
);

CREATE INDEX "IdempotencyRecord_tenant_manifest_idx" ON "IdempotencyRecord"("tenantId", "manifestHash");
CREATE INDEX "IdempotencyRecord_expiresAt_idx" ON "IdempotencyRecord"("expiresAt");

-- 5. Create ReceiptChain Table (Phase 1B §11.3)
CREATE TABLE "ReceiptChain" (
    "tenantId" TEXT NOT NULL,
    "schemaVersion" TEXT NOT NULL DEFAULT 'camelot-receipt-chain/1',
    "chainHeight" INTEGER NOT NULL DEFAULT 0,
    "headHash" TEXT NOT NULL,
    "anchorInterval" INTEGER NOT NULL DEFAULT 1000,
    "lastAnchorHeight" INTEGER NOT NULL DEFAULT 0,
    "lastAnchorHash" TEXT NOT NULL,
    "anchorTarget" TEXT,
    "verified" BOOLEAN NOT NULL DEFAULT true,
    "lastVerifiedAt" TIMESTAMP(3),
    "replayProtected" BOOLEAN NOT NULL DEFAULT true,
    "proofSigner" TEXT,
    "proofSignature" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "ReceiptChain_pkey" PRIMARY KEY ("tenantId")
);

CREATE INDEX "ReceiptChain_chainHeight_idx" ON "ReceiptChain"("chainHeight");

-- 6. Create Receipt Table (Phase 1B §11.3)
CREATE TABLE "Receipt" (
    "id" TEXT NOT NULL,
    "schemaVersion" TEXT NOT NULL DEFAULT 'camelot-receipt/2',
    "parentHash" TEXT NOT NULL,
    "selfHash" TEXT NOT NULL,
    "chainHeight" INTEGER NOT NULL,
    "tenantId" TEXT NOT NULL,
    "correlationId" TEXT NOT NULL,
    "taskId" TEXT NOT NULL,
    "authorityEpoch" INTEGER NOT NULL,
    "authorityVector" INTEGER[] NOT NULL,
    "effectClass" TEXT NOT NULL,
    "declaredRiskTier" TEXT NOT NULL,
    "timestamp" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "actorId" TEXT NOT NULL,
    "actorRole" TEXT NOT NULL,
    "actorNodeId" TEXT NOT NULL,
    "actorTrustBand" TEXT NOT NULL,
    "event" TEXT NOT NULL,
    "manifestHash" TEXT,
    "leaseId" TEXT,
    "parentReceiptId" TEXT,
    "payloadRedacted" JSONB,
    "proofSigner" TEXT NOT NULL,
    "proofSignature" TEXT NOT NULL,
    "ledgerAnchorEligible" BOOLEAN NOT NULL DEFAULT false,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Receipt_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "Receipt_tenant_chain_fkey" FOREIGN KEY ("tenantId") REFERENCES "ReceiptChain"("tenantId") ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE UNIQUE INDEX "Receipt_tenant_height_key" ON "Receipt"("tenantId", "chainHeight");
CREATE INDEX "Receipt_tenant_parentHash_idx" ON "Receipt"("tenantId", "parentHash");
CREATE INDEX "Receipt_correlationId_idx" ON "Receipt"("correlationId");
CREATE INDEX "Receipt_selfHash_idx" ON "Receipt"("selfHash");

-- ─────────────────────────────────────────────────────────────────────────────
-- ROW-LEVEL SECURITY ENFORCEMENT (Phase 2 Iron Gate)
-- ─────────────────────────────────────────────────────────────────────────────

-- 7. Enable and FORCE Row-Level Security on all 12 Multi-Tenant Tables
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

ALTER TABLE "IdempotencyRecord" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "IdempotencyRecord" FORCE ROW LEVEL SECURITY;

ALTER TABLE "ReceiptChain" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "ReceiptChain" FORCE ROW LEVEL SECURITY;

ALTER TABLE "Receipt" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Receipt" FORCE ROW LEVEL SECURITY;

-- 8. Restrictive Isolation Policies
-- Invariant: If current_setting('app.current_tenant_id', true) is NULL (unauthenticated),
-- comparison evaluates to NULL/FALSE, blocking ALL reads and writes unconditionally.

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

CREATE POLICY "tenant_isolation_idempotency" ON "IdempotencyRecord"
    AS RESTRICTIVE FOR ALL
    USING ("tenantId" = current_setting('app.current_tenant_id', true))
    WITH CHECK ("tenantId" = current_setting('app.current_tenant_id', true));

CREATE POLICY "tenant_isolation_receipt_chain" ON "ReceiptChain"
    AS RESTRICTIVE FOR ALL
    USING ("tenantId" = current_setting('app.current_tenant_id', true))
    WITH CHECK ("tenantId" = current_setting('app.current_tenant_id', true));

CREATE POLICY "tenant_isolation_receipt" ON "Receipt"
    AS RESTRICTIVE FOR ALL
    USING ("tenantId" = current_setting('app.current_tenant_id', true))
    WITH CHECK ("tenantId" = current_setting('app.current_tenant_id', true));
