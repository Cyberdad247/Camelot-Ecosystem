# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.

import pytest
from control_plane.cartridges.crm_sync import CRMSyncCartridge
from control_plane.cartridges.finance_ledger import FinanceLedgerCartridge
from control_plane.security.tpm2_vault_unseal import TPM2VaultUnsealDaemon
from control_plane.infra.mesh_sentinel import TailscaleMeshSentinel


def test_crm_sync_enrich_and_permission_gate(tmp_path):
    engine = CRMSyncCartridge()
    
    # 1. Enrich Lead
    lead = engine.enrich_lead(
        contact_name="Sarah Connor",
        email="sconnor@cyberdyne.com",
        company="Cyberdyne Systems",
        raw_notes="Inquiry regarding enterprise volume pricing and custom SLA"
    )
    
    assert lead.status == "QUALIFIED"
    assert lead.intent_score >= 0.70
    assert lead.plan_hash.startswith("sha256:")
    
    # 2. Attempt sync without lease (Must fail)
    with pytest.raises(PermissionError) as exc:
        engine.sync_to_crm(lead.lead_id, lease_token=None)
    assert "[SENTINEL_DENIED]" in str(exc.value)
    
    # 3. Sync with valid lease
    synced_lead = engine.sync_to_crm(lead.lead_id, lease_token="lease_sentinel_valid_001")
    assert synced_lead.status == "SYNCED"
    assert synced_lead.synced_at is not None


def test_finance_ledger_reconciliation(tmp_path):
    engine = FinanceLedgerCartridge()
    
    # 1. Balanced journal entry
    entry_balanced = engine.reconcile_transaction(
        description="Q3 Server Infrastructure Hosting",
        debit_account="Operating_Expenses",
        debit_amount=1500.0,
        credit_account="Accounts_Payable",
        credit_amount=1500.0
    )
    assert entry_balanced.is_balanced is True
    assert entry_balanced.status == "SEALED"
    assert entry_balanced.entry_hash.startswith("sha256:")
    
    # 2. Unbalanced journal entry
    entry_unbalanced = engine.reconcile_transaction(
        description="Faulty Invoice",
        debit_account="Operating_Expenses",
        debit_amount=2000.0,
        credit_account="Accounts_Payable",
        credit_amount=1800.0
    )
    assert entry_unbalanced.is_balanced is False
    assert entry_unbalanced.status == "UNBALANCED"


def test_tpm2_vault_unseal_and_rotation(tmp_path):
    daemon = TPM2VaultUnsealDaemon(state_dir=tmp_path)
    
    # 1. Unseal via PCR0
    record = daemon.auto_unseal_vault()
    assert record.vault_status == "UNSEALED"
    assert record.key_version == 1
    assert len(record.active_key_sig) == 64
    
    # 2. Key Rotation
    rotated = daemon.rotate_signing_key()
    assert rotated.key_version == 2
    assert rotated.vault_status == "UNSEALED"


def test_mesh_sentinel_topology_probe(tmp_path):
    sentinel = TailscaleMeshSentinel(state_dir=tmp_path)
    
    report = sentinel.probe_mesh_topology()
    assert report.total_nodes == 6
    assert report.online_nodes == 6
    assert report.average_mesh_rtt_ms < 50.0
    assert len(report.nodes) == 6
