"""Fix all remaining lint issues after ruff --unsafe-fixes regression."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def p(rel):
    return ROOT / rel


def read(rel):
    return p(rel).read_text(encoding="utf-8")


def write(rel, content):
    p(rel).write_text(content, encoding="utf-8")


# ============================================================
# FIX F821: Revert incorrect _ renames where variable IS used
# ============================================================
print("=== F821 fixes ===")

# 1. kinetic_swarm.py: _agent_id -> agent_id in _find_agent_for_role (line ~132)
c = read("control_plane/kinetic_swarm.py")
# Only revert in _find_agent_for_role, keep _agent_id in get_swarm_status
c = c.replace(
    "        for _agent_id, member in self.members.items():\r\n            if member.swarm_role == role and member.status == \"ready\":\r\n                return agent_id\r\n",
    "        for agent_id, member in self.members.items():\r\n            if member.swarm_role == role and member.status == \"ready\":\r\n                return agent_id\r\n",
    1
)
write("control_plane/kinetic_swarm.py", c)
print("  OK: kinetic_swarm.py - reverted _agent_id in _find_agent_for_role")

# 2. lord_archivist.py: _fail_re -> fail_re in _detect_fail_patterns (line ~128-129)
c = read("control_plane/lord_archivist.py")
# The --unsafe-fixes renamed the definition but not the usage
c = c.replace(
    "    _fail_re = re.compile",
    "    fail_re = re.compile",
    1
)
write("control_plane/lord_archivist.py", c)
print("  OK: lord_archivist.py - reverted _fail_re to fail_re")

# 3. microcubed.py: _safe_house -> safe_house in _load_contract (line ~139-140)
c = read("control_plane/microcubed.py")
c = c.replace(
    "    _safe_house = _safe_house_id(house_id)\r\n    contract_path = STATE_DIR / \"houses\" / safe_house / \"contract.json\"",
    "    safe_house = _safe_house_id(house_id)\r\n    contract_path = STATE_DIR / \"houses\" / safe_house / \"contract.json\"",
    1
)
write("control_plane/microcubed.py", c)
print("  OK: microcubed.py - reverted _safe_house in _load_contract")

# 4. openclaw.py: fix 'l' -> 'line' in filter (line 189)
c = read("control_plane/openclaw.py")
c = c.replace(
    'if "I/O operation on closed file" in l]',
    'if "I/O operation on closed file" in line]',
    1
)
write("control_plane/openclaw.py", c)
print("  OK: openclaw.py - fixed 'l' -> 'line' in filter")

# 5. sir_octavian.py: restore l = m["ledger"] (line 123)
c = read("control_plane/sir_octavian.py")
# The --unsafe-fixes removed the assignment, leaving just m["ledger"]
c = c.replace(
    "    m[\"ledger\"]\r\n    health_icon",
    "    l = m[\"ledger\"]\r\n    health_icon",
    1
)
write("control_plane/sir_octavian.py", c)
print("  OK: sir_octavian.py - restored l = m[\"ledger\"]")

# 6. test_phase_h_autonomous_loop.py: _iteration -> iteration (lines ~133, 224)
c = read("control_plane/test_phase_h_autonomous_loop.py")
# The --unsafe-fixes renamed the assignment but not the usage
c = c.replace("        _iteration = self.loop.run_autonomous_loop_iteration()", "        iteration = self.loop.run_autonomous_loop_iteration()")
write("control_plane/test_phase_h_autonomous_loop.py", c)
print("  OK: test_phase_h_autonomous_loop.py - reverted _iteration")

# 7. test_phase_h_day2_integration.py: _job_id -> job_id (line ~59)
c = read("control_plane/test_phase_h_day2_integration.py")
c = c.replace("        _job_id = self.orch.create_job", "        job_id = self.orch.create_job", 1)
write("control_plane/test_phase_h_day2_integration.py", c)
print("  OK: test_phase_h_day2_integration.py - reverted _job_id")

# 8. test_phase_h_integration.py: revert _signals, _ranked, _constraint
c = read("control_plane/test_phase_h_integration.py")
c = c.replace("        _signals = self.feedback_collector", "        signals = self.feedback_collector", 1)
c = c.replace("        _ranked = self.optimizer.rank_candidates", "        ranked = self.optimizer.rank_candidates", 1)
c = c.replace("        _constraint = self.metrics.add_constraint", "        constraint = self.metrics.add_constraint", 1)
write("control_plane/test_phase_h_integration.py", c)
print("  OK: test_phase_h_integration.py - reverted _signals, _ranked, _constraint")

# 9. test_phase_h_metrics.py: _i -> i (line ~105 - used in loop body)
c = read("control_plane/test_phase_h_metrics.py")
# The --unsafe-fixes renamed `for i in range(100)` to `for _i` but the body uses i
c = c.replace("        for _i in range(100):", "        for i in range(100):", 1)
write("control_plane/test_phase_h_metrics.py", c)
print("  OK: test_phase_h_metrics.py - reverted _i in sampling loop")

# 10. test_phase_h_result_tracker.py: _validation -> validation (line ~108)
c = read("control_plane/test_phase_h_result_tracker.py")
c = c.replace("        _validation = self.tracker.validate_execution_result", "        validation = self.tracker.validate_execution_result", 1)
write("control_plane/test_phase_h_result_tracker.py", c)
print("  OK: test_phase_h_result_tracker.py - reverted _validation")

# 11. test_phase_h_week1_final.py: revert _i -> i where used
c = read("control_plane/test_phase_h_week1_final.py")
# The --unsafe-fixes renamed loop vars but body uses i
c = c.replace("for _i in range(1000):", "for i in range(1000):")
c = c.replace("for _i in range(50):", "for i in range(50):")
c = c.replace("for _i in range(100):", "for i in range(100):")
write("control_plane/test_phase_h_week1_final.py", c)
print("  OK: test_phase_h_week1_final.py - reverted _i in all loops")

# 12. test_phase_h_week2_integration.py: revert _patterns, _health, _baseline
c = read("control_plane/test_phase_h_week2_integration.py")
c = c.replace("        _patterns = self.learner.learn_all_patterns()", "        patterns = self.learner.learn_all_patterns()", 1)
c = c.replace("        _baseline = self.learner.extract_metrics()", "        baseline = self.learner.extract_metrics()", 1)
c = c.replace("        _health = self.dashboard.get_learning_health_status()", "        health = self.dashboard.get_learning_health_status()", 1)
write("control_plane/test_phase_h_week2_integration.py", c)
print("  OK: test_phase_h_week2_integration.py - reverted _patterns, _baseline, _health")


# ============================================================
# FIX E701/E702: Split multiple statements on one line
# ============================================================
print("\n=== E701/E702 fixes ===")

# camelot_cli.py: lines 1273, 1276
c = read("control_plane/camelot_cli.py")
c = c.replace(
    '                    if idx + 1 < len(parts): target_llm = parts[idx+1]\n                elif "--model" in parts:\n                    idx = parts.index("--model")\n                    if idx + 1 < len(parts): target_llm = parts[idx+1]',
    '                    if idx + 1 < len(parts):\n                        target_llm = parts[idx+1]\n                elif "--model" in parts:\n                    idx = parts.index("--model")\n                    if idx + 1 < len(parts):\n                        target_llm = parts[idx+1]'
)
write("control_plane/camelot_cli.py", c)
print("  OK: camelot_cli.py - split E701 one-liners")

# soul_router.py: lines 106, 137, 181, 182, 193, 194, 197, 201
# soul_router.py uses \r\n line endings
c = read("control_plane/soul_router.py")

# Line 106: if not ... raise ValueError
c = c.replace(
    'if not 0.0 <= getattr(self, attr) <= 1.0: raise ValueError(f"{attr} invalid")\r\n',
    'if not 0.0 <= getattr(self, attr) <= 1.0:\r\n                raise ValueError(f"{attr} invalid")\r\n'
)

# Line 137: if len(history) > 10: history.pop(0)
c = c.replace(
    'if len(history) > 10: history.pop(0)\r\n',
    'if len(history) > 10:\r\n            history.pop(0)\r\n'
)

# Line 181: slo_escaped = True; continue
c = c.replace(
    'slo_escaped = True; continue\r\n',
    'slo_escaped = True\r\n                    continue\r\n'
)

# Line 182: matched_knight = kn; break
c = c.replace(
    'matched_knight = kn; break\r\n',
    'matched_knight = kn\r\n                break\r\n'
)

# Line 193: if engine.privacy_level >= 0.8 and privacy < 0.3: continue
c = c.replace(
    'if engine.privacy_level >= 0.8 and privacy < 0.3: continue\r\n',
    'if engine.privacy_level >= 0.8 and privacy < 0.3:\r\n                    continue\r\n'
)

# Line 194: if self.get_average_ttft(engine.knight_id) > self.slo_threshold_ms: continue
c = c.replace(
    'if self.get_average_ttft(engine.knight_id) > self.slo_threshold_ms: continue\r\n',
    'if self.get_average_ttft(engine.knight_id) > self.slo_threshold_ms:\r\n                    continue\r\n'
)

# Line 197: if s > best_score: best_score, ...
c = c.replace(
    'if s > best_score: best_score, best_engine, best_tensor = s, engine, t\r\n',
    'if s > best_score:\r\n                    best_score, best_engine, best_tensor = s, engine, t\r\n'
)

# Line 201: if slo_escaped: reason += ...
c = c.replace(
    'if slo_escaped: reason += " [DUALMAP_ESCAPE]"\r\n',
    'if slo_escaped:\r\n            reason += " [DUALMAP_ESCAPE]"\r\n'
)

write("control_plane/soul_router.py", c)
print("  OK: soul_router.py - split E701/E702 one-liners (8 fixes)")

print("\n=== ALL FIXES APPLIED ===")
