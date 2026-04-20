# 🛡️ CHIMERA OS: TROUBLESHOOTING STRATEGY & REMEDIATION PLAN

**Date:** 2025-12-22
**Source:** `report.json` (Audit v32.8.10)
**Objective:** System Hardening & Optimization

---

## 🚨 PRIORITY 1: SECURITY HARDENING (The Chivalry Gate)

### Issue: Unauthenticated RCE & Admin Access (SEC-002, SEC-003)
**Scope:** `dashboard/backend/main.py`, `dashboard/backend/api_websocket.py`
**Root Cause:** Endpoints `/api/decree` and `/admin/system_prompt` lack authentication middleware.
**Log Events:** Monitor `POST /api/decree` and `POST /admin/system_prompt` for source IPs.
**Analyze Metrics:** Track "Unauthorized Access Attempts" vs "Successful Decrees".

**Test Hypotheses (Reproduction):**
```bash
# Attempt to execute a shell command without auth
curl -X POST "http://localhost:5001/api/decree" -H "Content-Type: application/json" -d '{"intent": "forge file test.py with content print(1)"}'
```

**Implementation Fixes:**
1.  **Middleware:** Implement `verify_api_key` dependency in FastAPI.
2.  **Enforcement:** Require `X-Chimera-Key` header for all state-changing endpoints.
3.  **Role-Based Access:** Limit `/admin` routes to `ADMIN` role only.

**Verify Resolution:**
- Re-run `curl` command. Expect `401 Unauthorized`.
- Run with valid header `X-Chimera-Key: <valid_key>`. Expect `200 OK`.

---

### Issue: Hardcoded Secrets (SEC-001)
**Scope:** `.env` file and `main.py` defaults.
**Root Cause:** Sensitive keys (Gemini, Chimera) stored in plain text/version control.
**Log Events:** N/A (Static Analysis).
**Analyze Metrics:** N/A.

**Test Hypotheses:**
- Check `.gitignore` for `.env` exclusion.
- Scan git history for accidental commits of `.env`.

**Implementation Fixes:**
1.  **Secret Injection:** Update `boot_prod.ps1` to inject secrets from a secure vault or environment variables at runtime.
2.  **Validation:** Ensure `main.py` crashes if secrets are missing (Fail Secure) rather than using defaults.

**Verify Resolution:**
- Attempt to start app without env vars. System should exit with `CRITICAL: Secrets Missing`.

---

## 🛡️ PRIORITY 2: DATA INTEGRITY (The Vault)

### Issue: Directory Traversal in Artifacts (SEC-005)
**Scope:** `kernel/Data_Pipeline/storage.py` (`Ledger.record_artifact`)
**Root Cause:** `filename` argument in `record_artifact` is passed directly to `os.path.join` without sanitization.
**Log Events:** Log all `record_artifact` calls with filename parameters.

**Test Hypotheses (Reproduction):**
```python
Ledger.record_artifact("../../system32/evil.exe", "...", "Hacker", "1.0")
```

**Implementation Fixes:**
1.  **Sanitization:** Use `os.path.basename()` to strip paths.
2.  **Path Validation:** Verify absolute path starts with `artifacts_dir` root.

**Verify Resolution:**
- Attempt traversal write. Expect `ValueError: Invalid artifact path`.

---

## ⚡ PRIORITY 3: PERFORMANCE OPTIMIZATION (Speed of Thought)

### Issue: Sequential WebSocket Broadcasting (PERF-001)
**Scope:** `dashboard/backend/api_websocket.py` (`ConnectionManager.broadcast`)
**Root Cause:** `await connection.send_json()` is called in a loop, blocking subsequent sends until previous ones complete.
**Analyze Metrics:** Measure "Event Propagation Latency" (Time from Merlin Emit -> Client Receive).

**Test Hypotheses:**
- Connect 100 clients. Emit 1 event. Measure time for 100th client to receive.

**Implementation Fixes:**
1.  **Concurrency:** Replace loop with `asyncio.gather(*[connection.send_json(...)])`.
2.  **Exception Handling:** Ensure one failed client doesn't crash the broadcast.

**Verify Resolution:**
- Latency for 100th client should be ~equal to 1st client (network permitting).

---

### Issue: Inefficient Neural Archive Search (PERF-002)
**Scope:** `kernel/Data_Pipeline/storage.py` (`recall_wisdom`)
**Root Cause:** SQL `LIKE %query%` prevents index usage, causing full table scans.
**Analyze Metrics:** "Recall Latency" vs "Artifact Count".

**Implementation Fixes:**
1.  **FTS5:** Enable SQLite Full-Text Search extension.
2.  **Schema Migration:** Create virtual table `artifacts_fts`.
3.  **Query Optimization:** Use `MATCH` operator instead of `LIKE`.

**Verify Resolution:**
- Query latency remains flat (<50ms) as artifact count grows to 10,000+.

---

## 📝 EXECUTION ORDER

1.  **Phase 1 (Security):** Fix Auth & Directory Traversal (SEC-002, SEC-003, SEC-005). *Critical for safety.*
2.  **Phase 2 (Performance):** Fix WebSocket Broadcasting (PERF-001). *Quick win.*
3.  **Phase 3 (Optimization):** Upgrade Neural Archive (PERF-002). *Long-term scalability.*
