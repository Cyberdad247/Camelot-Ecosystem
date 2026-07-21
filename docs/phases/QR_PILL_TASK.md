# QR Pill Task Manifest — Bootstrap & Maintenance

**Version**: 1.0.0  
**Last Updated**: 2026-06-15  
**Sovereign Commander**: Vizion (VaShawn O. Head)

---

## Overview

The QR Pill executes tasks in two phases:
1. **Bootstrap Phase** (one-time, on activation)
2. **Maintenance Phase** (recurring, 24h interval)

Each task has:
- **ID**: unique identifier
- **Type**: create_artifact, load_blueprint, initialize_verification, health_check, etc.
- **Description**: human-readable purpose
- **Approval Level**: auto, notification, review, approval, deny
- **Risk Level**: low, medium, high, critical
- **Depends On**: prerequisite tasks
- **Rollback Plan**: how to undo if it fails

---

## Bootstrap Tasks (Phase 1: INITIALIZING → BUILDING)

### Task: bootstrap_1_create_pill_directory
```
ID: bootstrap_1_create_pill_directory
Type: create_artifact
Description: Create .pills/{pill_id}/ directory for pill artifacts
Risk Level: low
Approval Level: auto
Depends On: []
Path: .pills/{pill_id}/
Actions:
  1. Create directory structure
  2. Set permissions (755)
  3. Verify directory exists
Rollback: Delete directory
Status: Ready
```

### Task: bootstrap_2_create_sovereignty_ledger
```
ID: bootstrap_2_create_sovereignty_ledger
Type: initialize_verification
Description: Initialize sovereignty ledger for audit trail
Risk Level: low
Approval Level: auto
Depends On: [bootstrap_1_create_pill_directory]
Path: .pills/{pill_id}/sovereignty_ledger.md
Actions:
  1. Create ledger file
  2. Write header
  3. Log activation event
Rollback: Delete ledger file
Status: Ready
```

### Task: bootstrap_3_load_manifest
```
ID: bootstrap_3_load_manifest
Type: load_blueprint
Description: Load pill manifest (blueprint, tasks, verification)
Risk Level: low
Approval Level: notification
Depends On: [bootstrap_2_create_sovereignty_ledger]
Actions:
  1. Read manifest.json
  2. Validate schema
  3. Parse blueprint
  4. Load task definitions
Rollback: Use default manifest
Status: Ready
```

### Task: bootstrap_4_connect_bifrost_bridge
```
ID: bootstrap_4_connect_bifrost_bridge
Type: system_integration
Description: Establish connection to Bifrost bridge
Risk Level: medium
Approval Level: notification
Depends On: [bootstrap_3_load_manifest]
Actions:
  1. Test Bifrost connectivity
  2. Authenticate with bridge
  3. Register pill ID
  4. Log connection event
Rollback: Disconnect and retry
Status: Ready
```

### Task: bootstrap_5_connect_knight_brain
```
ID: bootstrap_5_connect_knight_brain
Type: system_integration
Description: Connect to Knight brain (knowledge base)
Risk Level: medium
Approval Level: notification
Depends On: [bootstrap_4_connect_bifrost_bridge]
Actions:
  1. Load knowledge base
  2. Validate knight_id
  3. Sync blueprint/task/verification docs
  4. Test connectivity
Rollback: Clear cache and reconnect
Status: Ready
```

### Task: bootstrap_6_create_blueprint_artifact
```
ID: bootstrap_6_create_blueprint_artifact
Type: create_artifact
Description: Create blueprint.json artifact from manifest
Risk Level: low
Approval Level: auto
Depends On: [bootstrap_3_load_manifest]
Path: .pills/{pill_id}/blueprint.json
Actions:
  1. Write manifest.blueprint to file
  2. Include metadata (timestamp, version)
  3. Validate JSON
Rollback: Delete file
Status: Ready
```

### Task: bootstrap_7_create_task_artifact
```
ID: bootstrap_7_create_task_artifact
Type: create_artifact
Description: Create tasks.json artifact from manifest
Risk Level: low
Approval Level: auto
Depends On: [bootstrap_3_load_manifest]
Path: .pills/{pill_id}/tasks.json
Actions:
  1. Write manifest.tasks to file
  2. Include metadata
  3. Validate JSON
Rollback: Delete file
Status: Ready
```

### Task: bootstrap_8_create_verification_artifact
```
ID: bootstrap_8_create_verification_artifact
Type: create_artifact
Description: Create verification.json artifact from manifest
Risk Level: low
Approval Level: auto
Depends On: [bootstrap_3_load_manifest]
Path: .pills/{pill_id}/verification.json
Actions:
  1. Write manifest.verification to file
  2. Include metadata
  3. Validate JSON
Rollback: Delete file
Status: Ready
```

### Task: bootstrap_9_initialize_health_check
```
ID: bootstrap_9_initialize_health_check
Type: system_check
Description: Run initial health check
Risk Level: low
Approval Level: auto
Depends On: [bootstrap_8_create_verification_artifact]
Actions:
  1. Check Bifrost connectivity
  2. Check Knight brain connectivity
  3. Check artifacts exist
  4. Log health status
Rollback: Retry health check
Status: Ready
```

### Task: bootstrap_10_verify_integrity (CRITICAL)
```
ID: bootstrap_10_verify_integrity
Type: verification
Description: Verify pill integrity via Knight brain
Risk Level: high
Approval Level: review
Depends On: [bootstrap_9_initialize_health_check]
Actions:
  1. Load verification manifest
  2. Run all checks:
     - Manifest schema valid
     - All artifacts present
     - Bifrost connected
     - Knight brain synced
     - Ledger writable
  3. Validate checksums
  4. Log verification result
Rollback: Fix issues and retry
Status: Ready
```

### Task: bootstrap_11_log_activation
```
ID: bootstrap_11_log_activation
Type: ledger_write
Description: Write pill activation to ledger and Bifrost
Risk Level: low
Approval Level: auto
Depends On: [bootstrap_10_verify_integrity]
Actions:
  1. Log to sovereignty_ledger.md
  2. Log to Bifrost ledger
  3. Mark pill as LIVE
  4. Start maintenance scheduler
Rollback: Mark pill as ERROR
Status: Ready
```

---

## Maintenance Tasks (Phase 2+: LIVE state, recurring)

### Task: maintenance_1_health_check (24h)
```
ID: maintenance_1_health_check
Type: system_check
Description: Daily health check (all systems)
Risk Level: low
Approval Level: auto
Interval: 24 hours
Actions:
  1. Check Bifrost bridge
  2. Check Knight brain
  3. Check artifacts
  4. Check ledger
  5. Assess overall health
  6. Update health_history
Healing Actions (if degraded):
  - Reconnect Bifrost
  - Reconnect Knight brain
  - Rebuild artifacts
Status: Ready
```

### Task: maintenance_2_verify_artifacts (24h)
```
ID: maintenance_2_verify_artifacts
Type: verification
Description: Verify all artifacts exist and valid
Risk Level: low
Approval Level: auto
Interval: 24 hours
Depends On: [maintenance_1_health_check]
Actions:
  1. Check blueprint.json exists
  2. Check tasks.json exists
  3. Check verification.json exists
  4. Validate JSON schemas
  5. Check modification dates
Healing Actions:
  - Recreate missing files
  - Restore from backup
Status: Ready
```

### Task: maintenance_3_sync_knowledge (24h)
```
ID: maintenance_3_sync_knowledge
Type: system_sync
Description: Sync Knight brain knowledge base
Risk Level: medium
Approval Level: notification
Interval: 24 hours
Depends On: [maintenance_1_health_check]
Actions:
  1. Load latest blueprint from Knight brain
  2. Load latest tasks from Knight brain
  3. Load latest verification from Knight brain
  4. Update local copies
  5. Log sync event
Rollback: Keep previous versions
Status: Ready
```

### Task: maintenance_4_ledger_rotation (7d)
```
ID: maintenance_4_ledger_rotation
Type: ledger_maintenance
Description: Rotate ledger (compress old entries)
Risk Level: low
Approval Level: auto
Interval: 7 days
Actions:
  1. Archive ledger entries older than 30d
  2. Create summary of archived entries
  3. Create new ledger file
  4. Log rotation
Rollback: Keep full ledger
Status: Ready
```

### Task: maintenance_5_synthesis_update (7d)
```
ID: maintenance_5_synthesis_update
Type: knowledge_update
Description: Run CloudBrain synthesis (weekly)
Risk Level: medium
Approval Level: notification
Interval: 7 days
Depends On: [maintenance_3_sync_knowledge]
Actions:
  1. Query Qdrant for past 7 days
  2. Cluster dispatch events
  3. Synthesize learnings via CloudBrain
  4. Update blueprints
  5. Log synthesis results
Status: Ready
```

### Task: maintenance_6_self_heal (on-demand)
```
ID: maintenance_6_self_heal
Type: system_recovery
Description: Self-heal detected issues
Risk Level: medium
Approval Level: review (if critical)
Depends On: [maintenance_1_health_check]
Trigger: Health status degraded or critical
Actions:
  1. Assess issue type
  2. Select healing action
  3. Execute healing
  4. Re-run health check
  5. If still degraded → escalate to Sovereign Commander
Escalation: Request Vizion approval if healing fails
Status: Ready
```

---

## Task Dependencies (Directed Acyclic Graph)

```
Bootstrap Sequence:
bootstrap_1_create_pill_directory
  ↓
bootstrap_2_create_sovereignty_ledger
  ├→ bootstrap_3_load_manifest
  │    ├→ bootstrap_6_create_blueprint_artifact
  │    ├→ bootstrap_7_create_task_artifact
  │    └→ bootstrap_8_create_verification_artifact
  │         ↓
  │    bootstrap_9_initialize_health_check
  │         ↓
  │    bootstrap_10_verify_integrity
  │         ↓
  │    bootstrap_11_log_activation
  │
  └→ bootstrap_4_connect_bifrost_bridge
       ↓
  bootstrap_5_connect_knight_brain

Maintenance Sequence (parallel):
maintenance_1_health_check
  ├→ maintenance_2_verify_artifacts
  ├→ maintenance_3_sync_knowledge
  ├→ maintenance_4_ledger_rotation (weekly)
  ├→ maintenance_5_synthesis_update (weekly)
  └→ maintenance_6_self_heal (on-demand)
```

---

## Task Status Tracking

| Task ID | Status | Last Run | Next Run | Health |
|---------|--------|----------|----------|--------|
| bootstrap_1_create_pill_directory | Ready | - | On activation | - |
| bootstrap_2_create_sovereignty_ledger | Ready | - | On activation | - |
| ... | Ready | - | On activation | - |
| maintenance_1_health_check | Ready | - | Every 24h | Healthy |
| maintenance_2_verify_artifacts | Ready | - | Every 24h | Healthy |
| ... | Ready | - | On schedule | Healthy |

---

## Rollback Plan

If a task fails:
1. Log failure to ledger with timestamp
2. Execute rollback action (if defined)
3. If bootstrapping: halt and report error
4. If maintenance: retry or escalate to Sovereign Commander
5. If critical: enter ERROR state and wait for human intervention

---

## Task Execution Guarantees

- **Atomicity**: Each task is atomic (all-or-nothing)
- **Ordering**: Tasks execute in dependency order
- **Idempotence**: Safe to re-run without side effects
- **Logging**: All executions logged
- **Approval**: Critical tasks require approval
- **Healing**: Failed tasks trigger healing attempts
