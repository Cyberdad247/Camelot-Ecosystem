#!/usr/bin/env python3
"""Camelot Apex OS -- CLI Orchestrator.

Thin client for the CAMELOT_OS kernel. Routes directives through
Anya (compiler), Merlin (router), and the Knights of the Round Table.

When CAMELOT_OS is available at ~/CAMELOT_OS, integrates:
  - Iron Gate HITL for critical actions
  - Warden zero-trust security
  - Zenith hostile pattern scanning
  - MGV reasoning engine
  - OS-level cartridges (ANT, BEAVER, HAWK, SPIDER, COGNITIVE, ORACLE)
  - Provenance Ledger logging

Falls back to local implementations when kernel is unavailable.

Usage:
    camelot exec "your directive here"
    camelot exec --write "Create an API route for users"
    camelot exec --llm "Build a FastAPI auth module"
    camelot ask "How do I deploy with Docker?"
    camelot ask --provider gemini "Explain transformers"
    camelot llm                       # List LLM providers
    camelot quarantine status         # DefenseGrid quarantine
    camelot knights
    camelot history
    camelot stats
    camelot export -o backup.json
    camelot cartridges
    camelot bridge
    camelot vault list
"""

import sys
import os
import json
import time
import argparse
import importlib

def _read_version():
    """Read version from VERSION file, fallback to 400.1.0."""
    version_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "VERSION")
    version_file = os.path.normpath(version_file)
    if os.path.exists(version_file):
        with open(version_file, "r") as f:
            return f.read().strip()
    return "400.1.0"

__version__ = _read_version()

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Ensure camelot directory is on path
CAMELOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CAMELOT_DIR)

from anya import compile_intent
from merlin import route, verify_registry
from ouroboros import log_execution, get_history, get_stats, export_all

# Bridge (optional — graceful if CAMELOT_OS not present)
try:
    import bridge
    _bridge_available = True
except ImportError:
    _bridge_available = False

# Constants
CARTRIDGE_DIR = os.path.join(CAMELOT_DIR, "cartridges")
KNIGHTS_DIR = os.path.join(CAMELOT_DIR, "knights")
MAX_BAR_LEN = 30

# Knight class registry
_knight_registry = {}


def _discover_knights():
    """Dynamically discover and load knight classes from knights/ directory."""
    global _knight_registry
    if _knight_registry:
        return

    from knights.base import BaseKnight

    for filename in os.listdir(KNIGHTS_DIR):
        if filename.startswith("_") or not filename.endswith(".py") or filename == "base.py":
            continue
        module_name = filename[:-3]
        try:
            mod = importlib.import_module(f"knights.{module_name}")
            for attr_name in dir(mod):
                obj = getattr(mod, attr_name)
                if isinstance(obj, type) and issubclass(obj, BaseKnight) and obj is not BaseKnight:
                    _knight_registry[module_name] = obj()
        except Exception as e:
            print(f"  Warning: Failed to load knight '{module_name}': {e}")

    errors = verify_registry()
    for err in errors:
        print(f"  Warning: {err}")


def _load_cartridges():
    """Load cartridges from both local dir and CAMELOT_OS kernel."""
    cartridges = {}

    # 1. Load local cartridges
    if os.path.isdir(CARTRIDGE_DIR):
        for filename in os.listdir(CARTRIDGE_DIR):
            filepath = os.path.join(CARTRIDGE_DIR, filename)
            if filename.endswith((".yaml", ".yml")):
                try:
                    import yaml
                    with open(filepath, "r", encoding="utf-8") as f:
                        cartridges[filename] = yaml.safe_load(f)
                except ImportError:
                    with open(filepath, "r", encoding="utf-8") as f:
                        cartridges[filename] = {"_raw": f.read(), "name": filename}
                except Exception as e:
                    cartridges[filename] = {"_error": str(e), "name": filename}
            elif filename.endswith(".json"):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        cartridges[filename] = json.load(f)
                except Exception as e:
                    cartridges[filename] = {"_error": str(e), "name": filename}
            elif filename.endswith(".md"):
                with open(filepath, "r", encoding="utf-8") as f:
                    cartridges[filename] = {"_raw": f.read(), "name": filename}

    # 2. Merge OS cartridges (ANT, BEAVER, HAWK, etc.)
    if _bridge_available:
        os_carts = bridge.get_os_cartridges()
        for name, data in os_carts.items():
            key = f"[OS] {name}"
            cartridges[key] = {
                "name": name,
                "domain": "SOVEREIGN",
                "description": data.get("description", ""),
                "lead": data.get("lead", ""),
                "knights": data.get("knights", []),
                "source": "CAMELOT_OS",
            }

    return cartridges


# ── Formatting helpers ──────────────────────────────────────────────

def _header(text, char="=", width=60):
    print(f"\n{char * width}")
    print(f"  {text}")
    print(f"{char * width}")


def _section(icon, title, content=""):
    print(f"\n{icon} {title}")
    if content:
        print(f"  {content}")


def _kv(key, value, indent=4):
    print(f"{' ' * indent}{key}: {value}")


# ── Commands ─────────────────────────────────────────────────────────

MAX_DIRECTIVE_LEN = 2000  # Prevent excessively long input


def _sanitize_input(text: str, max_len: int = MAX_DIRECTIVE_LEN) -> str:
    """Truncate and strip control characters from user input."""
    # Strip null bytes and control chars (except newlines/tabs)
    cleaned = "".join(c for c in text if c == "\n" or c == "\t" or (ord(c) >= 32))
    return cleaned[:max_len]


def cmd_exec(directive, write_files=False, use_llm=False, llm_provider=None):
    """Execute a directive through the full pipeline."""
    directive = _sanitize_input(directive)
    if not directive.strip():
        print("  Error: Empty directive.")
        return
    kernel_mode = _bridge_available and bridge.is_available()
    mode_label = "KERNEL" if kernel_mode else "LOCAL"
    if use_llm:
        mode_label += "+LLM"
    _header(f"CAMELOT APEX OS [{mode_label}]", "=")

    # Stage 1: Anya compiles intent
    _section(">>", "Anya Compiler -- analyzing directive...")
    compiled = compile_intent(directive)
    _kv("Intent", compiled["intent"])
    _kv("Domain", compiled["domain"])
    _kv("Complexity", f"{compiled['complexity']}/5")
    if compiled["runic"]:
        _kv("Runic Command", "YES")

    # Load and match cartridges
    cartridges = _load_cartridges()
    matched_carts = []
    for name, data in cartridges.items():
        if isinstance(data, dict) and data.get("domain") == compiled["domain"]:
            matched_carts.append(name)
            compiled["cartridge"] = data
    if matched_carts:
        _kv("Cartridge", ", ".join(matched_carts))

    # Stage 2: Merlin routes (includes MGV analysis if kernel available)
    _section("**", "Merlin Router -- selecting knight...")
    routing = route(compiled)
    knight_name = routing["knight"]
    module_key = routing["module"]
    risk = routing["risk"]
    mgv = routing.get("mgv")
    _kv("Assigned", knight_name)
    _kv("Risk Level", f"{risk['level']} (via {risk.get('source', 'local')})")

    if mgv:
        _kv("MGV Complexity", mgv.get("complexity", "?"))
        _kv("MGV Risk", mgv.get("risk_level", "?"))

    # Security gate: Iron Gate (kernel) or AgentArmor (local)
    if risk["requires_approval"]:
        if kernel_mode:
            _section("!!", "Iron Gate -- HITL APPROVAL REQUIRED")
            print(f"    Triggers: {', '.join(str(t) for t in risk['triggers'])}")
            approved = bridge.iron_gate_approve(directive[:100], risk["level"])
            if not approved:
                print("\n  X Execution blocked by Iron Gate.")
                log_execution(directive, compiled["intent"], compiled["domain"],
                              compiled["complexity"], knight_name, "blocked",
                              "Blocked by Iron Gate")
                bridge.log_provenance("CLI", f"BLOCKED: {directive[:80]}", "IRON_GATE")
                return
        else:
            _section("!!", "AgentArmor -- HIGH RISK DETECTED")
            print(f"    Triggers: {', '.join(str(t) for t in risk['triggers'])}")
            confirm = input("    Proceed? (y/N): ").strip().lower()
            if confirm != "y":
                print("\n  X Execution aborted by AgentArmor.")
                log_execution(directive, compiled["intent"], compiled["domain"],
                              compiled["complexity"], knight_name, "blocked",
                              "Blocked by AgentArmor")
                return

    # Stage 3: Knight executes
    _discover_knights()
    knight = _knight_registry.get(module_key)
    if not knight:
        msg = f"Knight module '{module_key}' not found."
        print(f"\n  X {msg}")
        log_execution(directive, compiled["intent"], compiled["domain"],
                      compiled["complexity"], knight_name, "error", msg)
        return

    _section(knight.icon, f"{knight.name} -- executing...")
    if write_files:
        _kv("Mode", "WRITE (files will be created on disk)")
    print()

    start = time.time()
    try:
        result = knight.execute(directive, compiled, write=write_files)
        duration_ms = int((time.time() - start) * 1000)
        status = result.get("status", "success")
    except Exception as e:
        duration_ms = int((time.time() - start) * 1000)
        # Sanitize error — don't expose full internal paths
        err_msg = str(e)
        home = os.path.expanduser("~")
        if home in err_msg:
            err_msg = err_msg.replace(home, "~")
        result = {"status": "error", "output": err_msg, "files_created": []}
        status = "error"

    # Warden output sanitization (kernel mode)
    if kernel_mode and status == "success":
        warden = bridge.get_warden()
        if warden:
            try:
                output_text = result.get("output", "")
                result["output"] = warden.sanitize_llm_output(output_text, allow_code=True)
            except Exception as e:
                _kv("Warden", f"Sanitization warning: {e}")

    # LLM enhancement: send knight output + directive to LLM for enrichment
    if use_llm and status == "success":
        _section(">>", "LLM Enhancement...")
        try:
            from llm_router import chat as llm_chat
            system_prompt = (
                f"You are a Camelot OS knight assistant ({knight_name}). "
                f"The user gave this directive: {directive}\n"
                f"A template was generated. Enhance it with real, actionable content. "
                f"Be concise and production-ready. Return only the improved output."
            )
            llm_messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": result.get("output", "")},
            ]
            llm_result = llm_chat(llm_messages, provider=llm_provider)
            if llm_result.get("content") and not llm_result.get("error"):
                result["output"] = llm_result["content"]
                _kv("LLM", f"{llm_result['provider']}/{llm_result['model']} "
                     f"({llm_result['duration_ms']}ms)")
            elif llm_result.get("error"):
                _kv("LLM", f"Fallback to template ({llm_result['error'][:60]})")
        except ImportError:
            _kv("LLM", "llm_router not available")
        except Exception as e:
            _kv("LLM", f"Enhancement failed: {e}")

    # Output
    print("-" * 60)
    print(result.get("output", ""))
    print("-" * 60)

    files = result.get("files_created", [])
    if files:
        _section(">>", "Files:")
        for f in files:
            written = os.path.exists(f) if write_files else False
            marker = "[written]" if written else "[template]"
            print(f"    {marker} {f}")

    # Log to Ouroboros
    log_execution(
        directive, compiled["intent"], compiled["domain"],
        compiled["complexity"], knight_name, status,
        result.get("output", "")[:500],
        duration_ms, files
    )

    # Log to CAMELOT_OS Provenance Ledger
    if kernel_mode:
        bridge.log_provenance(
            f"CLI/{knight_name}",
            f"{compiled['intent']}: {directive[:60]}",
            status.upper()
        )

    # Store in Titan Omega flux memory (kernel mode)
    if kernel_mode:
        bridge.memory_store(
            knight_name,
            f"{compiled['intent']}: {directive[:80]} [{status}]",
        )

    if status == "success":
        _section("OK", f"Execution complete ({duration_ms}ms)")
    else:
        _section("ERR", f"Execution failed ({duration_ms}ms)")


def cmd_knights():
    """List all available knights."""
    _header("KNIGHTS OF THE ROUND TABLE")
    _discover_knights()
    for key, knight in _knight_registry.items():
        print(f"\n  {knight.format_header()}")
        print(f"    Module: {key}")
    stats = get_stats()
    if stats:
        print("\n  -- Performance --")
        for s in stats:
            blocked = s.get('blocked', 0)
            print(f"    {s['knight']}: {s['total_runs']} runs, "
                  f"{s['successes']} ok, {s['failures']} err, "
                  f"{blocked} blocked, "
                  f"avg {s['avg_duration_ms']:.0f}ms")
    print()


def cmd_history(limit=20):
    """Show execution history."""
    _header("OUROBOROS MEMORY -- EXECUTION LOG")
    history = get_history(limit)
    if not history:
        print("\n  No executions recorded yet.\n")
        return
    for entry in history:
        ts = entry["timestamp"][:19]
        status = entry["status"]
        if status == "success":
            status_icon = "[OK]"
        elif status == "blocked":
            status_icon = "[BLOCKED]"
        else:
            status_icon = "[ERR]"
        print(f"\n  {status_icon} [{ts}] {entry['knight']}")
        print(f"     {entry['directive'][:80]}")
        print(f"     Intent: {entry['intent']} | Domain: {entry['domain']} | "
              f"Complexity: {entry['complexity']}/5 | {entry['duration_ms']}ms")
    print()


def cmd_stats():
    """Show knight performance statistics."""
    _header("ROUND TABLE STATISTICS")
    stats = get_stats()
    if not stats:
        print("\n  No statistics recorded yet.\n")
        return
    total_runs = sum(s["total_runs"] for s in stats)
    total_ok = sum(s["successes"] for s in stats)
    total_blocked = sum(s.get("blocked", 0) for s in stats)
    pct = (total_ok / total_runs) * 100 if total_runs else 0
    print(f"\n  Total Executions: {total_runs}")
    print(f"  Success Rate: {total_ok}/{total_runs} ({pct:.0f}%)")
    if total_blocked:
        print(f"  Blocked by Security Gate: {total_blocked}")
    print()
    for s in stats:
        bar_len = min(s["total_runs"], MAX_BAR_LEN)
        bar = "#" * bar_len
        blocked = s.get("blocked", 0)
        print(f"  {s['knight']:20s} | {bar} {s['total_runs']} "
              f"({s['successes']}ok/{s['failures']}err/{blocked}blk) "
              f"avg {s['avg_duration_ms']:.0f}ms")
    print()


def cmd_export(output_path):
    """Export all Ouroboros data to JSON."""
    # Validate output path — must resolve within CWD or home
    abs_out = os.path.realpath(os.path.abspath(output_path))
    safe_bases = [os.path.realpath(os.getcwd()), os.path.realpath(os.path.expanduser("~"))]
    if not any(abs_out.startswith(b + os.sep) or abs_out == b for b in safe_bases):
        print(f"ERR Export path must be within home directory or CWD.")
        return
    if not output_path.endswith(".json"):
        print("ERR Export path must end with .json")
        return
    try:
        data = export_all()
        out_dir = os.path.dirname(abs_out)
        if out_dir and not os.path.isdir(out_dir):
            os.makedirs(out_dir, exist_ok=True)
        with open(abs_out, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        print(f"OK Exported {len(data['history'])} executions and "
              f"{len(data['stats'])} knight stats to {output_path}")
    except (OSError, TypeError) as e:
        print(f"ERR Export failed: {e}")


def cmd_cartridges():
    """List cartridges from local dir + CAMELOT_OS kernel."""
    _header("KNOWLEDGE CARTRIDGES")
    cartridges = _load_cartridges()
    if not cartridges:
        print("\n  No cartridges loaded.\n")
        return

    # Separate local vs OS cartridges
    local = {k: v for k, v in cartridges.items() if not k.startswith("[OS]")}
    os_carts = {k: v for k, v in cartridges.items() if k.startswith("[OS]")}

    if local:
        print("\n  -- Local Cartridges --")
        for filename, data in sorted(local.items()):
            filepath = os.path.join(CARTRIDGE_DIR, filename)
            size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
            name = data.get("name", filename) if isinstance(data, dict) else filename
            domain = data.get("domain", "?") if isinstance(data, dict) else "?"
            print(f"  [{domain:15s}] {name} ({size}b)")

    if os_carts:
        print("\n  -- CAMELOT_OS Kernel Cartridges --")
        for key, data in sorted(os_carts.items()):
            name = data.get("name", key)
            desc = data.get("description", "")
            lead = data.get("lead", "?")
            knights = data.get("knights", [])
            print(f"  [{name:10s}] {desc}")
            print(f"              Lead: {lead} | Knights: {', '.join(knights[:3])}...")

    print()


def cmd_bridge():
    """Show CAMELOT_OS bridge status."""
    _header("CAMELOT_OS BRIDGE STATUS")
    if not _bridge_available:
        print("\n  Bridge module not loaded.")
        print("  Set CAMELOT_OS_ROOT env var or place kernel at ~/CAMELOT_OS\n")
        return

    status = bridge.get_bridge_status()
    print(f"\n  OS Root: {status['os_root']}")
    print(f"  Kernel Available: {'YES' if status['os_available'] else 'NO'}")

    # Group components by category
    categories = {
        "Security": ["iron_gate", "warden", "zenith"],
        "Reasoning": ["mgv", "planning_engine", "council_debate"],
        "Infrastructure": ["excalibur", "think_tank", "cartridges_os"],
        "Storage": ["vault", "titan_omega"],
    }

    for category, comps in categories.items():
        print(f"\n  -- {category} --")
        for comp in comps:
            state = status["components"].get(comp, "unknown")
            icon = "[+]" if state == "active" else "[-]"
            print(f"    {icon} {comp:20s} {state}")

    active = sum(1 for s in status["components"].values() if s == "active")
    total = len(status["components"])
    print(f"\n  Integration: {active}/{total} components active")

    if status["os_available"]:
        warden = bridge.get_warden()
        if warden:
            ws = warden.get_status()
            print(f"  Warden Lockdown: {'ACTIVE' if ws['lockdown_mode'] else 'inactive'}")
            print(f"  Recent Security Events: {ws['recent_events']}")
    print()


def cmd_vault(vault_args):
    """Interface with CAMELOT_OS Vault Manager."""
    if not _bridge_available or not bridge.is_available():
        print("  Vault requires CAMELOT_OS kernel connection.")
        return

    VaultClass = bridge.get_vault_class()
    if not VaultClass:
        print("  Vault Manager not available (master key not initialized).")
        print("  Run: python ~/CAMELOT_OS/03_VAULT/vault_manager.py init")
        return

    action = vault_args[0] if vault_args else "list"
    try:
        vault = VaultClass()
        if action == "list":
            _header("VAULT CREDENTIALS")
            creds = vault.list_credentials()
            if not creds:
                print("\n  No credentials stored.\n")
                return
            for name, meta in creds.items():
                print(f"  {name}:")
                print(f"    Created: {meta['created_at'][:19]}")
                print(f"    Accessed: {meta['access_count']} times")
            print()
        elif action == "set" and len(vault_args) >= 3:
            vault.set(vault_args[1], vault_args[2])
        elif action == "get" and len(vault_args) >= 2:
            val = vault.get(vault_args[1])
            if val:
                print(f"  {vault_args[1]}: {val}")
            else:
                print(f"  Credential '{vault_args[1]}' not found.")
        elif action == "delete" and len(vault_args) >= 2:
            vault.delete(vault_args[1])
        else:
            print("  Usage: camelot vault [list|set|get|delete] [args...]")
    except Exception as e:
        print(f"  Vault error: {e}")


def cmd_warden(warden_args):
    """Interface with CAMELOT_OS Warden security system."""
    _header("WARDEN SECURITY SYSTEM")
    if not _bridge_available:
        print("\n  Warden requires CAMELOT_OS kernel connection.\n")
        return

    cmd = " ".join(warden_args) if warden_args else "status"
    result = bridge.warden_command(cmd)
    print(f"\n{result}\n")


def cmd_memory(memory_args):
    """Interface with Titan Omega knowledge graph and flux memory."""
    _header("TITAN OMEGA MEMORY")
    if not _bridge_available or not bridge.is_available():
        print("\n  Memory requires CAMELOT_OS kernel connection.\n")
        return

    action = memory_args[0] if memory_args else "status"

    if action == "status":
        omega = bridge.get_titan_omega()
        if not omega:
            print("\n  Titan Omega not loaded.\n")
            return
        graph = omega.get("graph")
        flux = omega.get("flux")
        if graph:
            node_count = len(graph.graph.nodes()) if hasattr(graph, "graph") else "?"
            print(f"\n  Knowledge Graph: {node_count} nodes")
        if flux:
            session = flux.get_session_events("cli")
            print(f"  Flux (cli session): {len(session)} events")
        print()

    elif action == "query" and len(memory_args) >= 2:
        pattern_str = " ".join(memory_args[1:])
        try:
            pattern = json.loads(pattern_str)
        except json.JSONDecodeError:
            # Treat as a simple type query
            pattern = {"type": pattern_str}
        results = bridge.memory_query(pattern)
        if not results:
            print("\n  No matching nodes.\n")
            return
        for node in results:
            if hasattr(node, "__dict__"):
                print(f"  - {node.__dict__}")
            else:
                print(f"  - {node}")
        print()

    elif action == "session":
        session_id = memory_args[1] if len(memory_args) >= 2 else "cli"
        events = bridge.memory_get_session(session_id)
        if not events:
            print(f"\n  No events in session '{session_id}'.\n")
            return
        for ev in events:
            print(f"  - {ev}")
        print()

    elif action == "store" and len(memory_args) >= 3:
        entity = memory_args[1]
        event = " ".join(memory_args[2:])
        ok = bridge.memory_store(entity, event)
        if ok:
            print(f"\n  Stored event for '{entity}'.\n")
        else:
            print("\n  Failed to store event.\n")

    else:
        print("\n  Usage: camelot memory [status|query|session|store] [args...]")
        print("    status              -- Show memory system status")
        print("    query <pattern>     -- Query knowledge graph (JSON or type string)")
        print("    session [id]        -- Show flux session events")
        print("    store <entity> <event> -- Store event in flux memory\n")


def cmd_plan(plan_args):
    """Interface with CAMELOT_OS Planning Engine."""
    _header("PLANNING ENGINE")
    if not _bridge_available or not bridge.is_available():
        print("\n  Planning requires CAMELOT_OS kernel connection.\n")
        return

    engine = bridge.get_planning_engine()
    if not engine:
        print("\n  Planning Engine not loaded.\n")
        return

    action = plan_args[0] if plan_args else "list"

    if action == "list":
        plans = engine.active_plans if hasattr(engine, "active_plans") else {}
        if not plans:
            print("\n  No active plans.\n")
            return
        for pid, plan in plans.items():
            obj = plan.get("objective", "?") if isinstance(plan, dict) else str(plan)
            print(f"  [{pid[:8]}] {obj}")
        print()

    elif action == "create" and len(plan_args) >= 2:
        objective = " ".join(plan_args[1:])
        # Auto-generate task breakdown from objective
        tasks = [
            {"name": "Research & Analysis", "description": f"Research requirements for: {objective}"},
            {"name": "Design", "description": "Design solution architecture"},
            {"name": "Implementation", "description": "Implement the solution"},
            {"name": "Testing", "description": "Test and validate"},
            {"name": "Review", "description": "Final review and documentation"},
        ]
        result = bridge.create_plan(objective, tasks)
        if result:
            print(f"\n  Plan created: {result}")
        else:
            print("\n  Failed to create plan.\n")

    elif action == "next" and len(plan_args) >= 2:
        plan_id = plan_args[1]
        action_item = bridge.get_next_action(plan_id)
        if action_item:
            print(f"\n  Next: {action_item}\n")
        else:
            print("\n  No pending actions (plan complete or not found).\n")

    elif action == "complete" and len(plan_args) >= 3:
        ok = bridge.complete_task(plan_args[1], plan_args[2])
        print(f"\n  {'Task completed.' if ok else 'Failed to complete task.'}\n")

    elif action == "export" and len(plan_args) >= 2:
        data = bridge.export_plan(plan_args[1])
        if data:
            print(json.dumps(data, indent=2, default=str))
        else:
            print("\n  Plan not found.\n")

    else:
        print("\n  Usage: camelot plan [list|create|next|complete|export] [args...]")
        print("    list                       -- List active plans")
        print("    create <objective>         -- Create a new plan")
        print("    next <plan_id>             -- Get next action")
        print("    complete <plan_id> <task>  -- Mark task complete")
        print("    export <plan_id>           -- Export plan as JSON\n")


def cmd_kernel(kernel_args):
    """Send an intent directly to the Excalibur kernel."""
    _header("EXCALIBUR KERNEL")
    if not _bridge_available or not bridge.is_available():
        print("\n  Kernel requires CAMELOT_OS connection.\n")
        return

    if not kernel_args:
        print("\n  Usage: camelot kernel <intent string>\n")
        return

    intent = " ".join(kernel_args)
    _section(">>", f"Routing intent: {intent}")

    result = bridge.kernel_process_intent(intent)
    if isinstance(result, dict):
        print()
        for k, v in result.items():
            _kv(k, v)
    else:
        print(f"\n  {result}")
    print()

    # Log to provenance
    bridge.log_provenance("CLI/Excalibur", f"KERNEL_INTENT: {intent[:60]}", "ROUTED")


def cmd_ask(prompt, provider=None, model=None):
    """Ask an LLM directly through the router."""
    _header("LLM QUERY")
    try:
        from llm_router import chat as llm_chat
    except ImportError:
        print("\n  LLM router not available (missing llm_router.py or httpx).\n")
        return

    if not prompt:
        print("\n  Usage: camelot ask <question> [--provider gemini] [--model gpt-4o]\n")
        return

    system = ("You are a Camelot OS assistant. Be concise, direct, and helpful. "
              "Respond in markdown format when appropriate.")
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt},
    ]

    _section(">>", f"Routing to {'auto' if not provider else provider}...")
    start = time.time()
    result = llm_chat(messages, provider=provider, model=model)
    elapsed = int((time.time() - start) * 1000)

    if result.get("error"):
        print(f"\n  Error: {result['error']}")
        if result.get("fallback_errors"):
            for err in result["fallback_errors"]:
                print(f"    {err}")
        print()
        return

    _kv("Provider", f"{result['provider']}/{result['model']}")
    _kv("Tokens", f"{result['usage'].get('completion_tokens', '?')} ({elapsed}ms)")
    print()
    print("-" * 60)
    print(result["content"])
    print("-" * 60)

    if result.get("fallback_errors"):
        _section(">>", f"Fallback chain: {len(result['fallback_errors'])} providers skipped")

    # Log
    log_execution(prompt, "ASK", "LLM", 1, f"LLM/{result['provider']}",
                  "success", result["content"][:500], elapsed)
    print()


def cmd_llm():
    """List LLM provider status."""
    _header("LLM PROVIDERS")
    try:
        from llm_router import list_available
    except ImportError:
        print("\n  LLM router not available.\n")
        return

    providers = list_available()
    for p in providers:
        status = p["status"]
        if "ready" in status:
            icon = "[+]"
        elif status == "no_key":
            icon = "[?]"
        else:
            icon = "[-]"
        print(f"  {icon} {p['name']:12s} {status:20s} default: {p['default_model']}")
        if p["models"]:
            print(f"       models: {', '.join(str(m) for m in p['models'][:5])}")

    ready = sum(1 for p in providers if "ready" in p["status"])
    print(f"\n  {ready}/{len(providers)} providers ready")
    print("  Set API keys via environment variables to enable more providers.")
    print("  Example: export GOOGLE_API_KEY=... / export OPENAI_API_KEY=...\n")


def cmd_quarantine(quarantine_args):
    """Interface with DefenseGrid Quarantine."""
    _header("DEFENSEGRID QUARANTINE")
    quarantine_dir = os.path.expanduser("~/CAMELOT_DefenseGrid_Quarantine")

    if not os.path.isdir(quarantine_dir):
        print("\n  No quarantine directory found.\n")
        return

    action = quarantine_args[0] if quarantine_args else "status"

    if action == "status":
        # Read assessment
        assessment = os.path.join(quarantine_dir, "organizer_review", "ASSESSMENT.txt")
        if os.path.exists(assessment):
            with open(assessment, "r", encoding="utf-8") as f:
                print(f"\n{f.read()}")
        else:
            print("\n  No assessment file found.")

        # Count items per category
        for subdir in ["containment", "duplicates", "organizer_review", "temp_cleanup"]:
            path = os.path.join(quarantine_dir, subdir)
            if os.path.isdir(path):
                count = sum(1 for _, _, files in os.walk(path) for _ in files)
                print(f"  {subdir}: {count} items")
        print()

    elif action == "scan":
        print("\n  Scanning quarantine contents...\n")
        for root, dirs, files in os.walk(quarantine_dir):
            for f in files:
                filepath = os.path.join(root, f)
                rel = os.path.relpath(filepath, quarantine_dir)
                size = os.path.getsize(filepath)
                risk = "HIGH" if any(ext in f.lower() for ext in
                                     [".exe", ".key", ".pem", "login data",
                                      "credentials", "token"]) else "LOW"
                icon = "!!" if risk == "HIGH" else "  "
                print(f"  {icon} [{risk:4s}] {rel} ({size:,}b)")
        print()

    elif action == "purge-temp":
        rec_file = os.path.join(quarantine_dir, "organizer_review",
                                "TEMP_CLEANUP_RECOMMENDATION.txt")
        if os.path.exists(rec_file):
            with open(rec_file, "r", encoding="utf-8") as f:
                print(f"\n{f.read()}")
        print("  [!] Run with --confirm to delete safe-to-delete items.")
        print("  [!] This action is irreversible.\n")

    else:
        print("\n  Usage: camelot quarantine [status|scan|purge-temp]")
        print("    status     -- Show assessment and item counts")
        print("    scan       -- Scan all quarantined files with risk levels")
        print("    purge-temp -- Show cleanup recommendations\n")


# ── Main ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="camelot",
        description="Camelot Apex OS -- Round Table CLI",
    )
    sub = parser.add_subparsers(dest="command")

    # exec
    p_exec = sub.add_parser("exec", help="Execute a directive")
    p_exec.add_argument("directive", help="The directive to execute")
    p_exec.add_argument("--write", action="store_true",
                        help="Write generated files to disk (Sir Forge)")
    p_exec.add_argument("--llm", action="store_true",
                        help="Enhance output with LLM (uses fallback chain)")
    p_exec.add_argument("--provider", "-p", default=None,
                        help="LLM provider (gemini, openai, ollama, grok, mistral)")

    # ask (direct LLM query)
    p_ask = sub.add_parser("ask", help="Ask LLM directly")
    p_ask.add_argument("prompt", nargs="+", help="Your question")
    p_ask.add_argument("--provider", "-p", default=None, help="LLM provider")
    p_ask.add_argument("--model", "-m", default=None, help="Specific model")

    # llm (list providers)
    sub.add_parser("llm", help="List LLM providers and status")

    # knights
    sub.add_parser("knights", help="List available knights")

    # history
    p_hist = sub.add_parser("history", help="Show execution history")
    p_hist.add_argument("-n", type=int, default=20, help="Number of entries")

    # stats
    sub.add_parser("stats", help="Show performance statistics")

    # export
    p_exp = sub.add_parser("export", help="Export memory to JSON")
    p_exp.add_argument("-o", "--output", default="camelot_export.json", help="Output file")

    # cartridges
    sub.add_parser("cartridges", help="List knowledge cartridges")

    # bridge
    sub.add_parser("bridge", help="Show CAMELOT_OS bridge status")

    # vault
    p_vault = sub.add_parser("vault", help="Manage CAMELOT_OS vault")
    p_vault.add_argument("vault_args", nargs="*", default=["list"],
                         help="[list|set|get|delete] [args...]")

    # warden
    p_warden = sub.add_parser("warden", help="Warden security system")
    p_warden.add_argument("warden_args", nargs="*", default=["status"],
                          help="[status|lockdown|unlock|audit|spotlight]")

    # memory
    p_memory = sub.add_parser("memory", help="Titan Omega memory system")
    p_memory.add_argument("memory_args", nargs="*", default=["status"],
                          help="[status|query|session|store] [args...]")

    # plan
    p_plan = sub.add_parser("plan", help="CAMELOT_OS Planning Engine")
    p_plan.add_argument("plan_args", nargs="*", default=["list"],
                        help="[list|create|next|complete|export] [args...]")

    # kernel
    p_kernel = sub.add_parser("kernel", help="Send intent to Excalibur kernel")
    p_kernel.add_argument("kernel_args", nargs="*", default=[],
                          help="Intent string to route through Excalibur")

    # quarantine
    p_quarantine = sub.add_parser("quarantine", help="DefenseGrid quarantine management")
    p_quarantine.add_argument("quarantine_args", nargs="*", default=["status"],
                              help="[status|scan|purge-temp]")

    args = parser.parse_args()

    if args.command == "exec":
        cmd_exec(args.directive, write_files=args.write,
                 use_llm=args.llm, llm_provider=args.provider)
    elif args.command == "ask":
        cmd_ask(" ".join(args.prompt), provider=args.provider, model=args.model)
    elif args.command == "llm":
        cmd_llm()
    elif args.command == "knights":
        cmd_knights()
    elif args.command == "history":
        cmd_history(args.n)
    elif args.command == "stats":
        cmd_stats()
    elif args.command == "export":
        cmd_export(args.output)
    elif args.command == "cartridges":
        cmd_cartridges()
    elif args.command == "bridge":
        cmd_bridge()
    elif args.command == "vault":
        cmd_vault(args.vault_args)
    elif args.command == "warden":
        cmd_warden(args.warden_args)
    elif args.command == "memory":
        cmd_memory(args.memory_args)
    elif args.command == "plan":
        cmd_plan(args.plan_args)
    elif args.command == "kernel":
        cmd_kernel(args.kernel_args)
    elif args.command == "quarantine":
        cmd_quarantine(args.quarantine_args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
