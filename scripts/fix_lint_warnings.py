"""Fix all 86 ruff lint warnings in control_plane/."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def fix_file(rel_path, replacements):
    """Apply a list of (old, new) string replacements to a file."""
    fp = ROOT / rel_path
    c = fp.read_text(encoding="utf-8")
    for old, new in replacements:
        if old not in c:
            print(f"  WARN: '{old[:60]}...' not found in {rel_path}")
            continue
        c = c.replace(old, new, 1)
    fp.write_text(c, encoding="utf-8")
    print(f"  OK: {rel_path}")


def fix_all(rel_path, old, new):
    """Apply a replacement to ALL occurrences."""
    fp = ROOT / rel_path
    c = fp.read_text(encoding="utf-8")
    count = c.count(old)
    if count == 0:
        print(f"  WARN: '{old[:60]}...' not found in {rel_path}")
        return
    c = c.replace(old, new)
    fp.write_text(c, encoding="utf-8")
    print(f"  OK: {rel_path} ({count} occurrences)")


def regex_fix(rel_path, pattern, replacement):
    """Apply a regex replacement."""
    fp = ROOT / rel_path
    c = fp.read_text(encoding="utf-8")
    new, count = re.subn(pattern, replacement, c)
    if count == 0:
        print(f"  WARN: regex not matched in {rel_path}")
        return
    fp.write_text(new, encoding="utf-8")
    print(f"  OK: {rel_path} ({count} matches)")


# ============================================================
# 1. F401: Add noqa comments for intentional try/except imports
# ============================================================
print("\n=== F401: Unused imports (add noqa) ===")

fix_file("control_plane/bifrost.py", [
    (
        "from control_plane.sovereign_inference import SIE, HITLBlock, SIEHooks",
        "from control_plane.sovereign_inference import SIE, HITLBlock, SIEHooks  # noqa: F401"
    )
])

fix_file("control_plane/heimdall_knight.py", [
    (
        "from .knight_agent import KnightCapability, get_capability",
        "from .knight_agent import KnightCapability, get_capability  # noqa: F401"
    )
])

# system_analyzer.py: 6 availability-check imports
fix_all("control_plane/system_analyzer.py", "import numpy\n", "import numpy  # noqa: F401\n")
fix_all("control_plane/system_analyzer.py", "import torch\n", "import torch  # noqa: F401\n")
fix_all("control_plane/system_analyzer.py", "import tensorflow\n", "import tensorflow  # noqa: F401\n")
fix_all("control_plane/system_analyzer.py", "import onnx\n", "import onnx  # noqa: F401\n")
fix_all("control_plane/system_analyzer.py", "import redis\n", "import redis  # noqa: F401\n")
fix_all("control_plane/system_analyzer.py", "import qdrant_client\n", "import qdrant_client  # noqa: F401\n")

# ============================================================
# 2. E402: Add noqa for intentional late imports
# ============================================================
print("\n=== E402: Late imports (add noqa) ===")

fix_file("control_plane/nano_swarm_runtime.py", [
    ("import logging as _logging\n", "import logging as _logging  # noqa: E402\n"),
    ("import time as _time\n", "import time as _time  # noqa: E402\n"),
    ("from dataclasses import dataclass\nfrom typing import Callable, Optional\n",
     "from dataclasses import dataclass  # noqa: E402\nfrom typing import Callable, Optional  # noqa: E402\n"),
])

fix_file("control_plane/sir_octavian.py", [
    ("from enum import Enum as _Enum\n", "from enum import Enum as _Enum  # noqa: E402\n"),
    ("from typing import Optional as _Optional\n", "from typing import Optional as _Optional  # noqa: E402\n"),
])

fix_file("control_plane/soul_oversight.py", [
    ("from dataclasses import dataclass\n", "from dataclasses import dataclass  # noqa: E402\n"),
])

# ============================================================
# 3. F823: Fix json referenced before assignment in worker.py
# ============================================================
print("\n=== F823: Fix json shadowing in worker.py ===")

# Remove redundant local 'import json' in _exec_ollama and _exec_anthropic
fp = ROOT / "control_plane/worker.py"
c = fp.read_text(encoding="utf-8")
# Replace both occurrences of the local import json block
old_block = '        import json\n        import urllib.error\n        import urllib.request'
new_block = '        import urllib.error\n        import urllib.request'
count = c.count(old_block)
c = c.replace(old_block, new_block)
fp.write_text(c, encoding="utf-8")
print(f"  OK: worker.py (removed {count} redundant 'import json')")

# ============================================================
# 4. F841: Prefix unused variables with _
# ============================================================
print("\n=== F841: Unused variables (prefix with _) ===")

fix_file("control_plane/boot_sequence.py", [
    ("    launch_cmd = (\n", "    _launch_cmd = (\n"),
])

fix_file("control_plane/cli_intercept.py", [
    ("        knight = decision.knight_id", "        _knight = decision.knight_id"),
])

fix_file("control_plane/cloudbrain_synthesis.py", [
    ("                    updated_blueprint = f\"\"\"", "                    _updated_blueprint = f\"\"\""),
    ("                    path = kb._cache", "                    _path = kb._cache"),
])

fix_file("control_plane/event_bridge.py", [
    ("        sender = event.payload", "        _sender = event.payload"),
])

fix_file("control_plane/inspira_metrics.py", [
    ("        sep = ", "        _sep = "),
])

fix_file("control_plane/kinetic_swarm.py", [
    ("                role = SwarmRole", "                _role = SwarmRole"),
])

fix_file("control_plane/lord_archivist.py", [
    ("    done_re = re.compile", "    _done_re = re.compile"),
    ("    fail_re = re.compile", "    _fail_re = re.compile"),
])

fix_file("control_plane/microcubed.py", [
    ("    safe_house = _safe_house_id", "    _safe_house = _safe_house_id"),
])

fix_file("control_plane/phase_h_optimizer.py", [
    ("        error_rate = metrics.get", "        _error_rate = metrics.get"),
])

fix_file("control_plane/qr_pill_orchestrator.py", [
    ("            endpoint = service_def.health_check.endpoint", "            _endpoint = service_def.health_check.endpoint"),
])

# rbac_matrix.py: tier, role, can_spawn, action
regex_fix("control_plane/rbac_matrix.py", r"        tier = knight\.get", "        _tier = knight.get")
regex_fix("control_plane/rbac_matrix.py", r"        role = knight\.get", "        _role = knight.get")
regex_fix("control_plane/rbac_matrix.py", r"        can_spawn = knight\.get", "        _can_spawn = knight.get")
regex_fix("control_plane/rbac_matrix.py", r"            action = rule\.get", "            _action = rule.get")

# test_phase_h_autonomous_loop.py: iteration x2
fix_all("control_plane/test_phase_h_autonomous_loop.py", "        iteration = self.loop.run_autonomous_loop_iteration()\n",
        "        _iteration = self.loop.run_autonomous_loop_iteration()\n")

# test_phase_h_day2_integration.py: job_id
fix_file("control_plane/test_phase_h_day2_integration.py", [
    ("        job_id = self.orch.create_job", "        _job_id = self.orch.create_job"),
])

# test_phase_h_day4_hardening.py: jobs
fix_file("control_plane/test_phase_h_day4_hardening.py", [
    ("            jobs = orch.list_jobs()", "            _jobs = orch.list_jobs()"),
])

# test_phase_h_integration.py: signals, ranked, constraint
fix_file("control_plane/test_phase_h_integration.py", [
    ("        signals = self.feedback_collector", "        _signals = self.feedback_collector"),
    ("        ranked = self.optimizer.rank_candidates", "        _ranked = self.optimizer.rank_candidates"),
    ("        constraint = self.metrics.add_constraint", "        _constraint = self.metrics.add_constraint"),
])

# test_phase_h_load.py: exec_result, rb_result
fix_file("control_plane/test_phase_h_load.py", [
    ("        exec_result = self.executor.execute_candidate", "        _exec_result = self.executor.execute_candidate"),
    ("            rb_result = self.rollback.execute_rollback", "            _rb_result = self.rollback.execute_rollback"),
])

# test_phase_h_metrics.py: old_time
fix_file("control_plane/test_phase_h_metrics.py", [
    ("        old_time = time.time()", "        _old_time = time.time()"),
])

# test_phase_h_result_tracker.py: validation
fix_file("control_plane/test_phase_h_result_tracker.py", [
    ("        validation = self.tracker.validate_execution_result", "        _validation = self.tracker.validate_execution_result"),
])

# test_phase_h_week2_integration.py: patterns, baseline, health
fix_file("control_plane/test_phase_h_week2_integration.py", [
    ("        patterns = self.learner.learn_all_patterns()", "        _patterns = self.learner.learn_all_patterns()"),
    ("        baseline = self.learner.extract_metrics()", "        _baseline = self.learner.extract_metrics()"),
    ("        health = self.dashboard.get_learning_health_status()", "        _health = self.dashboard.get_learning_health_status()"),
])

# ============================================================
# 5. B007: Prefix unused loop variables with _
# ============================================================
print("\n=== B007: Unused loop variables (prefix with _) ===")

# bifrost.py:507 - tid
fix_file("control_plane/bifrost.py", [
    ("        async for tid, chunk in bifrost.route_and_stream", "        async for _tid, chunk in bifrost.route_and_stream"),
])

# distributed_ledger_consensus.py:303 - seq
fix_file("control_plane/distributed_ledger_consensus.py", [
    ("            for seq, state in self.log.items():", "            for _seq, state in self.log.items():"),
])

# kinetic_swarm.py:228 - agent_id
fix_file("control_plane/kinetic_swarm.py", [
    ("        for agent_id, member in self.members.items():", "        for _agent_id, member in self.members.items():"),
])

# qr_pill.py:345 - artifact_id
fix_file("control_plane/qr_pill.py", [
    ("        for artifact_id, artifact_path in self.artifacts.items():", "        for _artifact_id, artifact_path in self.artifacts.items():"),
])

# symbiotic_maintenance.py:166,174 - size, digest
fix_file("control_plane/symbiotic_maintenance.py", [
    ("    for size, paths in duplicate_candidates.items():", "    for _size, paths in duplicate_candidates.items():"),
    ("        for digest, dupes in digests.items():", "        for _digest, dupes in digests.items():"),
])

# worker.py:308 - lang
fix_file("control_plane/worker.py", [
    ("    for lang, filename, code in named:", "    for _lang, filename, code in named:"),
])

# test_phase_h_day4_hardening.py:237,295 - i x2
fix_all("control_plane/test_phase_h_day4_hardening.py", "                for i in range(count):", "                for _i in range(count):")
fix_all("control_plane/test_phase_h_day4_hardening.py", "        for i in range(50):", "        for _i in range(50):")

# test_phase_h_load.py:103,118 - i x2
fix_file("control_plane/test_phase_h_load.py", [
    ("        for i in range(50):", "        for _i in range(50):"),
    ("        for i in range(20):", "        for _i in range(20):"),
])

# test_phase_h_metrics.py:183 - i
fix_all("control_plane/test_phase_h_metrics.py", "        for i in range(100):", "        for _i in range(100):")

# test_phase_h_week1_final.py:120,145,187 - i x3
fix_all("control_plane/test_phase_h_week1_final.py", "            for i in range(1000):", "            for _i in range(1000):")
fix_all("control_plane/test_phase_h_week1_final.py", "        for i in range(50):", "        for _i in range(50):")
fix_all("control_plane/test_phase_h_week1_final.py", "        for i in range(100):", "        for _i in range(100):")

# ============================================================
# 6. E741: Rename ambiguous variable 'l'
# ============================================================
print("\n=== E741: Ambiguous variable names ===")

# openclaw.py:189 - l -> line
fix_file("control_plane/openclaw.py", [
    ("io_errors = [l for l in lines if", "io_errors = [line for line in lines if"),
])

# sir_octavian.py:123 - l -> ledger
fix_file("control_plane/sir_octavian.py", [
    ("    l = m[\"ledger\"]", "    ledger = m[\"ledger\"]"),
])

# worker.py:236,240,302 - l -> line
fp = ROOT / "control_plane/worker.py"
c = fp.read_text(encoding="utf-8")
# Line 236: lines = [l for l in ...]
c = c.replace(
    'lines = [l for l in QUEUE_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]',
    'lines = [line for line in QUEUE_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]',
    1
)
# Line 240: pending = sum(1 for l in lines ...)
c = c.replace(
    '1 for l in lines',
    '1 for line in lines',
    1
)
# Line 302: named = [(l, f, c) for l, f, c in blocks if f]
c = c.replace(
    'named = [(l, f, c) for l, f, c in blocks if f]',
    'named = [(lang, fname, code) for lang, fname, code in blocks if fname]',
    1
)
# Also fix the lambda that references l
c = c.replace(
    'if (lambda d: d.get("id", "") not in done)(json.loads(l) if l else {})',
    'if (lambda d: d.get("id", "") not in done)(json.loads(line) if line else {})',
    1
)
fp.write_text(c, encoding="utf-8")
print("  OK: worker.py (renamed 'l' to meaningful names)")

# ============================================================
# 7. E701/E702: Split multiple statements on one line
# ============================================================
print("\n=== E701/E702: Multiple statements on one line ===")

# camelot_cli.py:1269,1272,1275
fix_file("control_plane/camelot_cli.py", [
    ('                    if idx + 1 < len(parts): target_provider = parts[idx+1]\n',
     '                    if idx + 1 < len(parts):\n                        target_provider = parts[idx+1]\n'),
    ('                    if idx + 1 < len(parts): target_llm = parts[idx+1]\n                elif " --model" in parts:\n                    idx = parts.index("--model")\n                    if idx + 1 < len(parts): target_llm = parts[idx+1]\n',
     '                    if idx + 1 < len(parts):\n                        target_llm = parts[idx+1]\n                elif "--model" in parts:\n                    idx = parts.index("--model")\n                    if idx + 1 < len(parts):\n                        target_llm = parts[idx+1]\n'),
])

# dependency_engine.py:242
fix_file("control_plane/dependency_engine.py", [
    ('                in_deps = True; continue\n',
     '                in_deps = True\n                continue\n'),
])

# excalibur_preflight.py:228,230
fix_file("control_plane/excalibur_preflight.py", [
    ('        violations.append("missing toolchain: rustc"); missing.append("rustc")\n',
     '        violations.append("missing toolchain: rustc")\n        missing.append("rustc")\n'),
    ('        violations.append("missing toolchain: cargo"); missing.append("cargo")\n',
     '        violations.append("missing toolchain: cargo")\n        missing.append("cargo")\n'),
])

# soul_router.py:106,137,181,182,193,194,197,201
fix_file("control_plane/soul_router.py", [
    ('            if not 0.0 <= getattr(self, attr) <= 1.0: raise ValueError(f"{attr} invalid")\r\n',
     '            if not 0.0 <= getattr(self, attr) <= 1.0:\r\n                raise ValueError(f"{attr} invalid")\r\n'),
    ('        if len(history) > 10: history.pop(0)\r\n',
     '        if len(history) > 10:\r\n            history.pop(0)\r\n'),
    ('                    slo_escaped = True; continue\r\n',
     '                    slo_escaped = True\r\n                    continue\r\n'),
    ('                matched_knight = kn; break\r\n',
     '                matched_knight = kn\r\n                break\r\n'),
    ('                if engine.privacy_level >= 0.8 and privacy < 0.3: continue\r\n',
     '                if engine.privacy_level >= 0.8 and privacy < 0.3:\r\n                    continue\r\n'),
    ('                if self.get_average_ttft(engine.knight_id) > self.slo_threshold_ms: continue\r\n',
     '                if self.get_average_ttft(engine.knight_id) > self.slo_threshold_ms:\r\n                    continue\r\n'),
    ('                if s > best_score: best_score, best_engine, best_tensor = s, engine, t\r\n',
     '                if s > best_score:\r\n                    best_score, best_engine, best_tensor = s, engine, t\r\n'),
    ('        if slo_escaped: reason += " [DUALMAP_ESCAPE]"\r\n',
     '        if slo_escaped:\r\n            reason += " [DUALMAP_ESCAPE]"\r\n'),
])

# ============================================================
# 8. B905: zip() without strict=
# ============================================================
print("\n=== B905: zip() without strict= ===")

# harness.py:269,691
fix_file("control_plane/harness.py", [
    ('name: ok for (name, _, _), ok in zip(BOOT_PROBES, results)\n',
     'name: ok for (name, _, _), ok in zip(BOOT_PROBES, results, strict=True)\n'),
])

# leech_lattice_packing.py:68
fix_file("control_plane/leech_lattice_packing.py", [
    ('sum_squares = sum((c1 - c2) ** 2 for c1, c2 in zip(coord1, coord2))',
     'sum_squares = sum((c1 - c2) ** 2 for c1, c2 in zip(coord1, coord2, strict=True))'),
])

# ============================================================
# 9. I001: Unsorted imports
# ============================================================
print("\n=== I001: Unsorted imports ===")
# The I001 in camelot_cli.py line 2162 is inside a try/except block,
# which ruff can't auto-sort. Add noqa.
fix_file("control_plane/camelot_cli.py", [
    ('            from .glyph_registry import list_glyphs, load_stack, expand_atom, audit_atom, execute_atom\n',
     '            from .glyph_registry import list_glyphs, load_stack, expand_atom, audit_atom, execute_atom  # noqa: I001\n'),
])

print("\n=== ALL FIXES APPLIED ===")
