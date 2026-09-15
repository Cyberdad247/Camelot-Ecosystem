# SPDX-License-Identifier: MIT
"""
Camelot-OS Ansible Declarative Infrastructure Automation & Playbook Runner
Location: 02_FORGE/KINETIC_ARMORY/ansible_runner.py

Assimilated from Ansible Core architecture into Camelot-OS Kinetic Armory.
Provides:
- Declarative Playbook Execution Engine (Plays, Blocks, Tasks, Handlers, Rescue/Always)
- Idempotent State Verification & Reconciliation Engine
- Check Mode (Dry-Run) & Diff Analysis
- Extensible Module Registry (file, copy, template, lineinfile, command, stat, assert, etc.)
- Templating & Conditional Evaluation (Jinja2-powered)
- SIR_FORGE Kinetic Infrastructure Runner (scaffolding, build pipelines, manifest deployment)
- SIR_DEBUG Self-Healing PIV Runner (drift detection, fault remediation, validate loops)
"""

from __future__ import annotations

import copy
import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

try:
    import jinja2
except ImportError:  # pragma: no cover
    jinja2 = None

logger = logging.getLogger("CamelotAnsibleRunner")


# ---------------------------------------------------------------------------
# Data Models & Results
# ---------------------------------------------------------------------------

@dataclass
class Host:
    """Represents an execution target host with scoped host variables."""
    name: str
    vars: Dict[str, Any] = field(default_factory=dict)
    groups: List[str] = field(default_factory=lambda: ["all"])

    def get_var(self, key: str, default: Any = None) -> Any:
        return self.vars.get(key, default)


class Inventory:
    """In-memory and file-based inventory manager with group variables."""

    def __init__(self, sources: Optional[Union[str, List[str], Dict[str, Any]]] = None):
        self.hosts: Dict[str, Host] = {}
        self.groups: Dict[str, Dict[str, Any]] = {"all": {"hosts": [], "vars": {}}}
        self._initialize_localhost()

        if sources:
            self.load(sources)

    def _initialize_localhost(self) -> None:
        if "localhost" not in self.hosts:
            local_host = Host(
                name="localhost",
                vars={
                    "ansible_connection": "local",
                    "ansible_os_family": "Windows" if os.name == "nt" else "Posix",
                    "ansible_hostname": "localhost",
                },
                groups=["all", "local"],
            )
            self.hosts["localhost"] = local_host
            self.groups["all"]["hosts"].append("localhost")

    def add_host(self, name: str, groups: Optional[List[str]] = None, host_vars: Optional[Dict[str, Any]] = None) -> Host:
        if name not in self.hosts:
            h = Host(name=name, vars=host_vars or {}, groups=groups or ["all"])
            self.hosts[name] = h
        else:
            if host_vars:
                self.hosts[name].vars.update(host_vars)
            if groups:
                for g in groups:
                    if g not in self.hosts[name].groups:
                        self.hosts[name].groups.append(g)

        target_groups = groups or ["all"]
        for group in target_groups:
            if group not in self.groups:
                self.groups[group] = {"hosts": [], "vars": {}}
            if name not in self.groups[group]["hosts"]:
                self.groups[group]["hosts"].append(name)
        return self.hosts[name]

    def set_group_var(self, group: str, key: str, value: Any) -> None:
        if group not in self.groups:
            self.groups[group] = {"hosts": [], "vars": {}}
        self.groups[group]["vars"][key] = value

    def get_hosts(self, pattern: str = "all") -> List[Host]:
        if pattern == "all":
            return list(self.hosts.values())
        if pattern in self.hosts:
            return [self.hosts[pattern]]
        if pattern in self.groups:
            return [self.hosts[h] for h in self.groups[pattern]["hosts"] if h in self.hosts]
        # Comma-separated or pattern
        matched = []
        for part in pattern.split(","):
            part = part.strip()
            if part in self.hosts and self.hosts[part] not in matched:
                matched.append(self.hosts[part])
            elif part in self.groups:
                for h in self.groups[part]["hosts"]:
                    if h in self.hosts and self.hosts[h] not in matched:
                        matched.append(self.hosts[h])
        return matched or [self.hosts.get("localhost", Host(name="localhost"))]

    def get_host_vars(self, host: Host) -> Dict[str, Any]:
        merged_vars: Dict[str, Any] = {}
        # 1. Group vars (all first, then specific)
        if "all" in self.groups:
            merged_vars.update(self.groups["all"].get("vars", {}))
        for group in host.groups:
            if group != "all" and group in self.groups:
                merged_vars.update(self.groups[group].get("vars", {}))
        # 2. Host vars
        merged_vars.update(host.vars)
        return merged_vars

    def load(self, sources: Union[str, List[str], Dict[str, Any]]) -> None:
        if isinstance(sources, dict):
            for group_name, group_data in sources.items():
                if isinstance(group_data, dict):
                    hosts = group_data.get("hosts", [])
                    if isinstance(hosts, list):
                        for h in hosts:
                            self.add_host(h, groups=[group_name])
                    elif isinstance(hosts, dict):
                        for h, hvars in hosts.items():
                            self.add_host(h, groups=[group_name], host_vars=hvars if isinstance(hvars, dict) else {})
                    for k, v in group_data.get("vars", {}).items():
                        self.set_group_var(group_name, k, v)
        elif isinstance(sources, str):
            if Path(sources).is_file():
                content = Path(sources).read_text(encoding="utf-8")
                if yaml:
                    data = yaml.safe_load(content)
                    if isinstance(data, dict):
                        self.load(data)
            else:
                for host in sources.split(","):
                    if host.strip():
                        self.add_host(host.strip())


@dataclass
class TaskResult:
    """Execution output and telemetry for a single task."""
    host: str
    task_name: str
    module: str
    changed: bool = False
    failed: bool = False
    skipped: bool = False
    msg: str = ""
    rc: int = 0
    stdout: str = ""
    stderr: str = ""
    diff: Dict[str, Any] = field(default_factory=dict)
    facts: Dict[str, Any] = field(default_factory=dict)
    data: Dict[str, Any] = field(default_factory=dict)
    elapsed_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "host": self.host,
            "task_name": self.task_name,
            "module": self.module,
            "changed": self.changed,
            "failed": self.failed,
            "skipped": self.skipped,
            "msg": self.msg,
            "rc": self.rc,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "diff": self.diff,
            "facts": self.facts,
            "data": self.data,
            "elapsed_seconds": round(self.elapsed_seconds, 4),
        }


@dataclass
class PlayResult:
    """Aggregated results and statistics for a single play."""
    play_name: str
    task_results: List[TaskResult] = field(default_factory=list)
    stats: Dict[str, int] = field(default_factory=lambda: {
        "ok": 0, "changed": 0, "failed": 0, "skipped": 0, "rescued": 0, "ignored": 0
    })
    success: bool = True

    def summarize(self) -> Dict[str, int]:
        return dict(self.stats)


@dataclass
class PlaybookExecutionReport:
    """Full execution summary across all plays and target hosts."""
    playbook_name: str
    play_results: List[PlayResult] = field(default_factory=list)
    total_stats: Dict[str, int] = field(default_factory=lambda: {
        "ok": 0, "changed": 0, "failed": 0, "skipped": 0, "rescued": 0, "ignored": 0
    })
    success: bool = True
    elapsed_seconds: float = 0.0
    check_mode: bool = False
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)

    def summary(self) -> str:
        status_str = "SUCCESS" if self.success else "FAILED"
        mode_str = " [CHECK MODE]" if self.check_mode else ""
        lines = [
            f"=== PLAYBOOK SUMMARY: {self.playbook_name}{mode_str} ===",
            f"Status: {status_str} (Elapsed: {self.elapsed_seconds:.3f}s)",
            f"Stats: OK={self.total_stats['ok']}, CHANGED={self.total_stats['changed']}, "
            f"FAILED={self.total_stats['failed']}, SKIPPED={self.total_stats['skipped']}, "
            f"RESCUED={self.total_stats['rescued']}, IGNORED={self.total_stats['ignored']}",
        ]
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "playbook_name": self.playbook_name,
            "success": self.success,
            "check_mode": self.check_mode,
            "elapsed_seconds": round(self.elapsed_seconds, 4),
            "total_stats": self.total_stats,
            "plays": [
                {
                    "name": p.play_name,
                    "success": p.success,
                    "stats": p.stats,
                    "tasks": [t.to_dict() for t in p.task_results],
                }
                for p in self.play_results
            ],
            "audit_trail": self.audit_trail,
        }


# ---------------------------------------------------------------------------
# Template & Expression Engine
# ---------------------------------------------------------------------------

class TemplateEngine:
    """Jinja2-based templating and expression evaluator with fallback."""

    @staticmethod
    def render_string(template_str: str, context: Dict[str, Any]) -> str:
        if not isinstance(template_str, str):
            return template_str
        if "{{" not in template_str and "{%" not in template_str:
            return template_str

        if jinja2:
            try:
                env = jinja2.Environment(undefined=jinja2.Undefined)
                template = env.from_string(template_str)
                return template.render(**context)
            except Exception as e:
                logger.debug("Jinja2 render error: %s; falling back to regex", e)

        # Regex fallback for simple {{ var }} interpolations
        def _replace(match):
            key = match.group(1).strip()
            # Handle nested dict lookups: foo.bar
            parts = key.split(".")
            curr = context
            for p in parts:
                if isinstance(curr, dict) and p in curr:
                    curr = curr[p]
                else:
                    return match.group(0)
            return str(curr)

        return re.sub(r"\{\{\s*([^}]+)\s*\}\}", _replace, template_str)

    @staticmethod
    def _resolve_context_key(context: Dict[str, Any], key_path: str) -> Tuple[bool, Any]:
        parts = key_path.split(".")
        curr = context
        for p in parts:
            if isinstance(curr, dict) and p in curr:
                curr = curr[p]
            elif hasattr(curr, p):
                curr = getattr(curr, p)
            else:
                return False, None
        return True, curr

    @classmethod
    def render_data(cls, data: Any, context: Dict[str, Any]) -> Any:
        if isinstance(data, str):
            # Type preservation for boolean / int / float / json structures
            if data.startswith("{{") and data.endswith("}}") and "{{" not in data[2:-2]:
                inner_key = data[2:-2].strip()
                has_val, val = cls._resolve_context_key(context, inner_key)
                if has_val:
                    return val
            return cls.render_string(data, context)
        elif isinstance(data, dict):
            return {cls.render_string(k, context) if isinstance(k, str) else k: cls.render_data(v, context) for k, v in data.items()}
        elif isinstance(data, list):
            return [cls.render_data(item, context) for item in data]
        return data

    @classmethod
    def evaluate_condition(cls, condition: Union[str, bool, List[Any]], context: Dict[str, Any]) -> bool:
        if isinstance(condition, bool):
            return condition
        if isinstance(condition, list):
            return all(cls.evaluate_condition(c, context) for c in condition)
        if not isinstance(condition, str):
            return bool(condition)

        expr = condition.strip()
        if not expr:
            return True

        if jinja2:
            try:
                # Wrap as Jinja2 template returning boolean
                template_code = f"{{% if {expr} %}}TRUE{{% else %}}FALSE{{% endif %}}"
                env = jinja2.Environment()
                res = env.from_string(template_code).render(**context).strip()
                return res == "TRUE"
            except Exception as e:
                logger.debug("Jinja2 conditional evaluation failed for '%s': %s", expr, e)

        # Safe Python expression evaluation fallback
        try:
            # Build safe namespace with context
            safe_globals = {"__builtins__": {}}
            return bool(eval(expr, safe_globals, context))
        except Exception:
            return False


# ---------------------------------------------------------------------------
# Declarative Module Registry & Implementations
# ---------------------------------------------------------------------------

ModuleFunc = Callable[[Dict[str, Any], Dict[str, Any], bool], TaskResult]


class ModuleRegistry:
    """Extensible registry for Ansible declarative modules."""

    _modules: Dict[str, ModuleFunc] = {}

    @classmethod
    def register(cls, name: str) -> Callable[[ModuleFunc], ModuleFunc]:
        def decorator(func: ModuleFunc) -> ModuleFunc:
            cls._modules[name] = func
            return func
        return decorator

    @classmethod
    def get(cls, name: str) -> Optional[ModuleFunc]:
        return cls._modules.get(name)

    @classmethod
    def has_module(cls, name: str) -> bool:
        return name in cls._modules


# --- Built-in Declarative Modules ---

@ModuleRegistry.register("ping")
def module_ping(args: Dict[str, Any], context: Dict[str, Any], check_mode: bool) -> TaskResult:
    data = args.get("data", "pong")
    return TaskResult(
        host=context.get("inventory_hostname", "localhost"),
        task_name=context.get("task_name", "ping"),
        module="ping",
        changed=False,
        failed=False,
        msg="pong" if data == "pong" else data,
        data={"ping": data},
    )


@ModuleRegistry.register("debug")
def module_debug(args: Dict[str, Any], context: Dict[str, Any], check_mode: bool) -> TaskResult:
    msg = args.get("msg")
    var_name = args.get("var")
    output = ""

    if msg is not None:
        output = str(msg)
    elif var_name is not None:
        val = context.get(var_name, f"VARIABLE_NOT_FOUND: {var_name}")
        output = json.dumps(val, indent=2) if isinstance(val, (dict, list)) else str(val)

    return TaskResult(
        host=context.get("inventory_hostname", "localhost"),
        task_name=context.get("task_name", "debug"),
        module="debug",
        changed=False,
        failed=False,
        msg=output,
        stdout=output,
    )


@ModuleRegistry.register("set_fact")
def module_set_fact(args: Dict[str, Any], context: Dict[str, Any], check_mode: bool) -> TaskResult:
    facts = {}
    for k, v in args.items():
        if k not in ("cacheable",):
            facts[k] = v

    return TaskResult(
        host=context.get("inventory_hostname", "localhost"),
        task_name=context.get("task_name", "set_fact"),
        module="set_fact",
        changed=False,
        failed=False,
        msg=f"Facts set: {list(facts.keys())}",
        facts=facts,
    )


@ModuleRegistry.register("assert")
def module_assert(args: Dict[str, Any], context: Dict[str, Any], check_mode: bool) -> TaskResult:
    that_list = args.get("that", [])
    if isinstance(that_list, str):
        that_list = [that_list]

    fail_msg = args.get("fail_msg", "Assertion failed")
    success_msg = args.get("success_msg", "All assertions passed")

    for condition in that_list:
        passed = TemplateEngine.evaluate_condition(condition, context)
        if not passed:
            err = f"{fail_msg}: condition '{condition}' evaluated to False"
            return TaskResult(
                host=context.get("inventory_hostname", "localhost"),
                task_name=context.get("task_name", "assert"),
                module="assert",
                changed=False,
                failed=True,
                msg=err,
                stderr=err,
            )

    return TaskResult(
        host=context.get("inventory_hostname", "localhost"),
        task_name=context.get("task_name", "assert"),
        module="assert",
        changed=False,
        failed=False,
        msg=success_msg,
    )


@ModuleRegistry.register("fail")
def module_fail(args: Dict[str, Any], context: Dict[str, Any], check_mode: bool) -> TaskResult:
    msg = args.get("msg", "Failed as requested")
    return TaskResult(
        host=context.get("inventory_hostname", "localhost"),
        task_name=context.get("task_name", "fail"),
        module="fail",
        changed=False,
        failed=True,
        msg=msg,
        stderr=msg,
    )


@ModuleRegistry.register("stat")
def module_stat(args: Dict[str, Any], context: Dict[str, Any], check_mode: bool) -> TaskResult:
    path_str = args.get("path")
    if not path_str:
        return TaskResult(
            host=context.get("inventory_hostname", "localhost"),
            task_name=context.get("task_name", "stat"),
            module="stat",
            failed=True,
            msg="Parameter 'path' is required for stat module",
        )

    path = Path(path_str)
    stat_data: Dict[str, Any] = {"exists": path.exists()}

    if path.exists():
        st = path.stat()
        stat_data.update({
            "path": str(path.resolve()),
            "isdir": path.is_dir(),
            "isfile": path.is_file(),
            "islink": path.is_symlink(),
            "size": st.st_size,
            "mode": oct(st.st_mode)[-4:],
            "mtime": st.st_mtime,
        })
        if path.is_file() and args.get("checksum", True):
            try:
                hasher = hashlib.sha256()
                hasher.update(path.read_bytes())
                stat_data["checksum"] = hasher.hexdigest()
            except Exception as e:
                stat_data["checksum"] = None
                stat_data["checksum_error"] = str(e)

    return TaskResult(
        host=context.get("inventory_hostname", "localhost"),
        task_name=context.get("task_name", "stat"),
        module="stat",
        changed=False,
        failed=False,
        msg=f"Stat gathered for {path_str}",
        data={"stat": stat_data},
    )


@ModuleRegistry.register("file")
def module_file(args: Dict[str, Any], context: Dict[str, Any], check_mode: bool) -> TaskResult:
    path_str = args.get("path") or args.get("dest") or args.get("name")
    if not path_str:
        return TaskResult(
            host=context.get("inventory_hostname", "localhost"),
            task_name=context.get("task_name", "file"),
            module="file",
            failed=True,
            msg="Parameter 'path' is required for file module",
        )

    state = args.get("state", "file")
    mode = args.get("mode")
    path = Path(path_str)
    changed = False
    diff: Dict[str, Any] = {}

    try:
        if state == "directory":
            if not path.exists():
                changed = True
                diff["before"] = {"state": "absent"}
                diff["after"] = {"state": "directory", "path": str(path)}
                if not check_mode:
                    path.mkdir(parents=True, exist_ok=True)
            elif not path.is_dir():
                return TaskResult(
                    host=context.get("inventory_hostname", "localhost"),
                    task_name=context.get("task_name", "file"),
                    module="file",
                    failed=True,
                    msg=f"Path {path} exists but is not a directory",
                )

        elif state == "absent":
            if path.exists():
                changed = True
                diff["before"] = {"state": "directory" if path.is_dir() else "file"}
                diff["after"] = {"state": "absent"}
                if not check_mode:
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()

        elif state == "touch":
            if not path.exists():
                changed = True
                diff["before"] = {"state": "absent"}
                diff["after"] = {"state": "file", "path": str(path)}
                if not check_mode:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.touch()
            else:
                if not check_mode:
                    os.utime(path, None)

        elif state == "file":
            if not path.exists():
                return TaskResult(
                    host=context.get("inventory_hostname", "localhost"),
                    task_name=context.get("task_name", "file"),
                    module="file",
                    failed=True,
                    msg=f"File {path} does not exist",
                )

        elif state == "link":
            src = args.get("src")
            if not src:
                return TaskResult(
                    host=context.get("inventory_hostname", "localhost"),
                    task_name=context.get("task_name", "file"),
                    module="file",
                    failed=True,
                    msg="Parameter 'src' is required when state='link'",
                )
            if not path.is_symlink() or os.readlink(path) != src:
                changed = True
                diff["before"] = {"symlink": os.readlink(path) if path.is_symlink() else "none"}
                diff["after"] = {"symlink": src}
                if not check_mode:
                    if path.exists() or path.is_symlink():
                        path.unlink()
                    path.symlink_to(src)

        # Apply mode if specified (POSIX-compliant)
        if mode is not None and path.exists() and not check_mode:
            try:
                numeric_mode = int(str(mode), 8) if isinstance(mode, str) else int(mode)
                os.chmod(path, numeric_mode)
            except Exception as e:
                logger.debug("chmod warning on %s: %s", path, e)

        return TaskResult(
            host=context.get("inventory_hostname", "localhost"),
            task_name=context.get("task_name", "file"),
            module="file",
            changed=changed,
            failed=False,
            msg=f"Path {path_str} state reconciled to {state}",
            diff=diff,
            data={"path": str(path), "state": state},
        )
    except Exception as e:
        return TaskResult(
            host=context.get("inventory_hostname", "localhost"),
            task_name=context.get("task_name", "file"),
            module="file",
            failed=True,
            msg=str(e),
            stderr=str(e),
        )


@ModuleRegistry.register("copy")
def module_copy(args: Dict[str, Any], context: Dict[str, Any], check_mode: bool) -> TaskResult:
    dest_str = args.get("dest")
    content = args.get("content")
    src_str = args.get("src")
    backup = args.get("backup", False)

    if not dest_str:
        return TaskResult(
            host=context.get("inventory_hostname", "localhost"),
            task_name=context.get("task_name", "copy"),
            module="copy",
            failed=True,
            msg="Parameter 'dest' is required for copy module",
        )

    dest = Path(dest_str)
    desired_bytes: bytes = b""

    if content is not None:
        desired_bytes = content.encode("utf-8") if isinstance(content, str) else bytes(content)
    elif src_str is not None:
        src = Path(src_str)
        if not src.exists():
            return TaskResult(
                host=context.get("inventory_hostname", "localhost"),
                task_name=context.get("task_name", "copy"),
                module="copy",
                failed=True,
                msg=f"Source file {src_str} does not exist",
            )
        desired_bytes = src.read_bytes()
    else:
        return TaskResult(
            host=context.get("inventory_hostname", "localhost"),
            task_name=context.get("task_name", "copy"),
            module="copy",
            failed=True,
            msg="Either 'content' or 'src' must be provided to copy module",
        )

    desired_hash = hashlib.sha256(desired_bytes).hexdigest()
    current_hash = None

    if dest.exists() and dest.is_file():
        current_hash = hashlib.sha256(dest.read_bytes()).hexdigest()

    changed = (current_hash != desired_hash)
    diff: Dict[str, Any] = {}

    if changed:
        diff["before"] = {"checksum": current_hash, "path": str(dest)}
        diff["after"] = {"checksum": desired_hash, "path": str(dest)}

        if not check_mode:
            dest.parent.mkdir(parents=True, exist_ok=True)
            if backup and dest.exists():
                backup_path = dest.with_suffix(f".bak.{int(time.time())}")
                shutil.copy2(dest, backup_path)
            dest.write_bytes(desired_bytes)

    return TaskResult(
        host=context.get("inventory_hostname", "localhost"),
        task_name=context.get("task_name", "copy"),
        module="copy",
        changed=changed,
        failed=False,
        msg=f"File copied to {dest_str}" if changed else f"File {dest_str} already up to date",
        diff=diff,
        data={"dest": str(dest), "checksum": desired_hash},
    )


@ModuleRegistry.register("template")
def module_template(args: Dict[str, Any], context: Dict[str, Any], check_mode: bool) -> TaskResult:
    dest_str = args.get("dest")
    src_str = args.get("src")
    template_str = args.get("template_string")

    if not dest_str:
        return TaskResult(
            host=context.get("inventory_hostname", "localhost"),
            task_name=context.get("task_name", "template"),
            module="template",
            failed=True,
            msg="Parameter 'dest' is required for template module",
        )

    raw_template = ""
    if template_str is not None:
        raw_template = template_str
    elif src_str is not None:
        src = Path(src_str)
        if not src.exists():
            return TaskResult(
                host=context.get("inventory_hostname", "localhost"),
                task_name=context.get("task_name", "template"),
                module="template",
                failed=True,
                msg=f"Template src '{src_str}' not found",
            )
        raw_template = src.read_text(encoding="utf-8")
    else:
        return TaskResult(
            host=context.get("inventory_hostname", "localhost"),
            task_name=context.get("task_name", "template"),
            module="template",
            failed=True,
            msg="Either 'src' or 'template_string' required for template module",
        )

    rendered_text = TemplateEngine.render_string(raw_template, context)
    rendered_bytes = rendered_text.encode("utf-8")
    rendered_hash = hashlib.sha256(rendered_bytes).hexdigest()

    dest = Path(dest_str)
    current_hash = None
    if dest.exists() and dest.is_file():
        current_hash = hashlib.sha256(dest.read_bytes()).hexdigest()

    changed = (current_hash != rendered_hash)
    diff: Dict[str, Any] = {}

    if changed:
        diff["before"] = {"checksum": current_hash}
        diff["after"] = {"checksum": rendered_hash}
        if not check_mode:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(rendered_bytes)

    return TaskResult(
        host=context.get("inventory_hostname", "localhost"),
        task_name=context.get("task_name", "template"),
        module="template",
        changed=changed,
        failed=False,
        msg=f"Template rendered to {dest_str}" if changed else f"Template {dest_str} already up to date",
        diff=diff,
        data={"dest": str(dest), "checksum": rendered_hash},
    )


@ModuleRegistry.register("lineinfile")
def module_lineinfile(args: Dict[str, Any], context: Dict[str, Any], check_mode: bool) -> TaskResult:
    path_str = args.get("path") or args.get("dest")
    line = args.get("line")
    regexp = args.get("regexp")
    state = args.get("state", "present")
    create = args.get("create", False)
    insertafter = args.get("insertafter")
    insertbefore = args.get("insertbefore")

    if not path_str or (state == "present" and line is None and not regexp):
        return TaskResult(
            host=context.get("inventory_hostname", "localhost"),
            task_name=context.get("task_name", "lineinfile"),
            module="lineinfile",
            failed=True,
            msg="Parameters 'path' and 'line' are required for lineinfile present state",
        )

    path = Path(path_str)
    if not path.exists():
        if not create:
            return TaskResult(
                host=context.get("inventory_hostname", "localhost"),
                task_name=context.get("task_name", "lineinfile"),
                module="lineinfile",
                failed=True,
                msg=f"File {path_str} does not exist and create=False",
            )
        lines = []
    else:
        lines = path.read_text(encoding="utf-8").splitlines()

    original_lines = list(lines)
    changed = False

    if state == "present":
        matched_idx = -1
        if regexp:
            pattern = re.compile(regexp)
            for i, l in enumerate(lines):
                if pattern.search(l):
                    matched_idx = i
                    break

        if matched_idx != -1:
            if lines[matched_idx] != line:
                lines[matched_idx] = line
                changed = True
        else:
            if line not in lines:
                inserted = False
                if insertafter:
                    pattern_after = re.compile(insertafter)
                    for i in range(len(lines) - 1, -1, -1):
                        if pattern_after.search(lines[i]):
                            lines.insert(i + 1, line)
                            inserted = True
                            changed = True
                            break
                elif insertbefore:
                    pattern_before = re.compile(insertbefore)
                    for i, l in enumerate(lines):
                        if pattern_before.search(l):
                            lines.insert(i, line)
                            inserted = True
                            changed = True
                            break
                if not inserted:
                    lines.append(line)
                    changed = True

    elif state == "absent":
        if regexp:
            pattern = re.compile(regexp)
            new_lines = [l for l in lines if not pattern.search(l)]
            if len(new_lines) != len(lines):
                lines = new_lines
                changed = True
        elif line:
            new_lines = [l for l in lines if l != line]
            if len(new_lines) != len(lines):
                lines = new_lines
                changed = True

    if changed and not check_mode:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

    return TaskResult(
        host=context.get("inventory_hostname", "localhost"),
        task_name=context.get("task_name", "lineinfile"),
        module="lineinfile",
        changed=changed,
        failed=False,
        msg=f"Line modified in {path_str}" if changed else f"Line in {path_str} already in desired state",
        diff={"before": "\n".join(original_lines), "after": "\n".join(lines)} if changed else {},
    )


@ModuleRegistry.register("command")
@ModuleRegistry.register("shell")
def module_command(args: Dict[str, Any], context: Dict[str, Any], check_mode: bool) -> TaskResult:
    cmd = args.get("cmd") or args.get("_raw_params")
    chdir = args.get("chdir")
    creates = args.get("creates")
    removes = args.get("removes")
    stdin = args.get("stdin")
    env = args.get("environment") or {}

    if not cmd:
        return TaskResult(
            host=context.get("inventory_hostname", "localhost"),
            task_name=context.get("task_name", "command"),
            module="command",
            failed=True,
            msg="Parameter 'cmd' or '_raw_params' is required",
        )

    # Idempotent checks via 'creates' / 'removes'
    if creates and Path(creates).exists():
        return TaskResult(
            host=context.get("inventory_hostname", "localhost"),
            task_name=context.get("task_name", "command"),
            module="command",
            changed=False,
            skipped=True,
            msg=f"Skipped because {creates} already exists",
        )
    if removes and not Path(removes).exists():
        return TaskResult(
            host=context.get("inventory_hostname", "localhost"),
            task_name=context.get("task_name", "command"),
            module="command",
            changed=False,
            skipped=True,
            msg=f"Skipped because {removes} does not exist",
        )

    if check_mode:
        return TaskResult(
            host=context.get("inventory_hostname", "localhost"),
            task_name=context.get("task_name", "command"),
            module="command",
            changed=True,
            failed=False,
            msg=f"[CHECK MODE] Would execute: {cmd}",
            stdout=f"[CHECK MODE] Simulated execution of: {cmd}",
        )

    full_env = os.environ.copy()
    for k, v in env.items():
        full_env[str(k)] = str(v)

    start_time = time.time()
    try:
        # Use shell execution
        proc = subprocess.run(
            cmd,
            shell=True,
            cwd=chdir or None,
            env=full_env,
            input=stdin.encode("utf-8") if stdin else None,
            capture_output=True,
            text=True,
        )
        elapsed = time.time() - start_time
        failed = (proc.returncode != 0)

        return TaskResult(
            host=context.get("inventory_hostname", "localhost"),
            task_name=context.get("task_name", "command"),
            module="command",
            changed=True,
            failed=failed,
            rc=proc.returncode,
            stdout=proc.stdout.strip(),
            stderr=proc.stderr.strip(),
            msg=f"Command finished with rc {proc.returncode}",
            elapsed_seconds=elapsed,
        )
    except Exception as e:
        return TaskResult(
            host=context.get("inventory_hostname", "localhost"),
            task_name=context.get("task_name", "command"),
            module="command",
            changed=False,
            failed=True,
            rc=1,
            stderr=str(e),
            msg=str(e),
        )


@ModuleRegistry.register("wait_for")
def module_wait_for(args: Dict[str, Any], context: Dict[str, Any], check_mode: bool) -> TaskResult:
    path_str = args.get("path")
    timeout = float(args.get("timeout", 10.0))
    state = args.get("state", "present")
    sleep_interval = float(args.get("sleep", 0.5))

    if not path_str:
        return TaskResult(
            host=context.get("inventory_hostname", "localhost"),
            task_name=context.get("task_name", "wait_for"),
            module="wait_for",
            failed=True,
            msg="Parameter 'path' is required for wait_for module",
        )

    if check_mode:
        return TaskResult(
            host=context.get("inventory_hostname", "localhost"),
            task_name=context.get("task_name", "wait_for"),
            module="wait_for",
            changed=False,
            msg=f"[CHECK MODE] Waiting for {path_str} to be {state}",
        )

    path = Path(path_str)
    start_time = time.time()

    while time.time() - start_time < timeout:
        exists = path.exists()
        if state == "present" and exists:
            return TaskResult(
                host=context.get("inventory_hostname", "localhost"),
                task_name=context.get("task_name", "wait_for"),
                module="wait_for",
                changed=False,
                msg=f"Path {path_str} is now present",
            )
        elif state == "absent" and not exists:
            return TaskResult(
                host=context.get("inventory_hostname", "localhost"),
                task_name=context.get("task_name", "wait_for"),
                module="wait_for",
                changed=False,
                msg=f"Path {path_str} is now absent",
            )
        time.sleep(min(sleep_interval, 0.1))

    return TaskResult(
        host=context.get("inventory_hostname", "localhost"),
        task_name=context.get("task_name", "wait_for"),
        module="wait_for",
        failed=True,
        msg=f"Timeout waiting for {path_str} to be {state}",
    )


# ---------------------------------------------------------------------------
# Declarative Playbook Execution Engine
# ---------------------------------------------------------------------------

class AnsiblePlaybookRunner:
    """
    Sovereign Declarative Playbook Execution Engine for Camelot-OS.
    Executes standard Ansible playbooks with idempotent state guarantees,
    handler notifications, rescue blocks, and check-mode simulation.
    """

    def __init__(self, inventory: Optional[Inventory] = None):
        self.inventory = inventory or Inventory()
        self.notified_handlers: Set[str] = set()

    def run_playbook(
        self,
        playbook: Union[str, Path, List[Dict[str, Any]], Dict[str, Any]],
        inventory: Optional[Inventory] = None,
        extra_vars: Optional[Dict[str, Any]] = None,
        check_mode: bool = False,
        tags: Optional[List[str]] = None,
        skip_tags: Optional[List[str]] = None,
    ) -> PlaybookExecutionReport:
        start_time = time.time()
        inv = inventory or self.inventory
        plays_data = self._load_playbook_data(playbook)
        playbook_name = "AnsiblePlaybook"

        if isinstance(playbook, (str, Path)) and Path(str(playbook)).is_file():
            playbook_name = Path(str(playbook)).name

        report = PlaybookExecutionReport(
            playbook_name=playbook_name,
            check_mode=check_mode,
        )

        all_success = True
        for play_dict in plays_data:
            play_res = self._execute_play(
                play_dict=play_dict,
                inventory=inv,
                extra_vars=extra_vars or {},
                check_mode=check_mode,
                tags=tags or [],
                skip_tags=skip_tags or [],
            )
            report.play_results.append(play_res)
            for k in report.total_stats:
                report.total_stats[k] += play_res.stats.get(k, 0)
            if not play_res.success:
                all_success = False
                break

        report.success = all_success
        report.elapsed_seconds = time.time() - start_time
        return report

    def verify_idempotency(
        self,
        playbook: Union[str, Path, List[Dict[str, Any]], Dict[str, Any]],
        inventory: Optional[Inventory] = None,
        extra_vars: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, PlaybookExecutionReport, PlaybookExecutionReport]:
        """
        Runs the playbook once (Application Phase), then runs it a second time (Verification Phase).
        Idempotency holds if and only if the second run produces 0 changes and 0 failures.
        """
        inv = inventory or self.inventory
        run1 = self.run_playbook(playbook, inventory=inv, extra_vars=extra_vars, check_mode=False)
        run2 = self.run_playbook(playbook, inventory=inv, extra_vars=extra_vars, check_mode=False)

        is_idempotent = (run2.total_stats["changed"] == 0 and run2.total_stats["failed"] == 0)
        return is_idempotent, run1, run2

    def _load_playbook_data(self, playbook: Union[str, Path, List[Dict[str, Any]], Dict[str, Any]]) -> List[Dict[str, Any]]:
        if isinstance(playbook, list):
            return playbook
        if isinstance(playbook, dict):
            return [playbook]
        if isinstance(playbook, (str, Path)):
            path = Path(str(playbook))
            if path.is_file():
                content = path.read_text(encoding="utf-8")
                if yaml:
                    loaded = yaml.safe_load(content)
                    return loaded if isinstance(loaded, list) else [loaded]
                else:
                    return [json.loads(content)]
            else:
                # String content
                if yaml:
                    loaded = yaml.safe_load(str(playbook))
                    return loaded if isinstance(loaded, list) else [loaded]
                else:
                    return [json.loads(str(playbook))]
        return []

    def _execute_play(
        self,
        play_dict: Dict[str, Any],
        inventory: Inventory,
        extra_vars: Dict[str, Any],
        check_mode: bool,
        tags: List[str],
        skip_tags: List[str],
    ) -> PlayResult:
        play_name = play_dict.get("name", "Unnamed Play")
        hosts_pattern = play_dict.get("hosts", "all")
        play_vars = play_dict.get("vars", {})
        tasks_raw = play_dict.get("tasks", [])
        handlers_raw = play_dict.get("handlers", [])
        target_hosts = inventory.get_hosts(hosts_pattern)

        play_result = PlayResult(play_name=play_name)
        handlers_map: Dict[str, Dict[str, Any]] = {
            h.get("name"): h for h in handlers_raw if isinstance(h, dict) and "name" in h
        }

        for host in target_hosts:
            host_vars = inventory.get_host_vars(host)
            context: Dict[str, Any] = {
                "inventory_hostname": host.name,
                "ansible_check_mode": check_mode,
            }
            context.update(host_vars)
            context.update(play_vars)
            context.update(extra_vars)

            self.notified_handlers.clear()

            # Execute tasks
            host_success = True
            for task_raw in tasks_raw:
                success = self._execute_task_or_block(
                    task_raw=task_raw,
                    host=host,
                    context=context,
                    play_result=play_result,
                    check_mode=check_mode,
                    tags=tags,
                    skip_tags=skip_tags,
                )
                if not success:
                    host_success = False
                    break

            # Execute triggered handlers
            if host_success and self.notified_handlers:
                for handler_name in list(self.notified_handlers):
                    if handler_name in handlers_map:
                        h_task = handlers_map[handler_name]
                        self._execute_single_task(
                            task_dict=h_task,
                            host=host,
                            context=context,
                            play_result=play_result,
                            check_mode=check_mode,
                            tags=tags,
                            skip_tags=skip_tags,
                        )

            if not host_success:
                play_result.success = False

        return play_result

    def _execute_task_or_block(
        self,
        task_raw: Dict[str, Any],
        host: Host,
        context: Dict[str, Any],
        play_result: PlayResult,
        check_mode: bool,
        tags: List[str],
        skip_tags: List[str],
    ) -> bool:
        # Check for Block / Rescue / Always structure
        if "block" in task_raw:
            block_tasks = task_raw.get("block", [])
            rescue_tasks = task_raw.get("rescue", [])
            always_tasks = task_raw.get("always", [])
            when_condition = task_raw.get("when")

            if when_condition is not None and not TemplateEngine.evaluate_condition(when_condition, context):
                play_result.stats["skipped"] += 1
                return True

            block_failed = False
            for b_task in block_tasks:
                ok = self._execute_single_task(b_task, host, context, play_result, check_mode, tags, skip_tags)
                if not ok:
                    block_failed = True
                    break

            if block_failed and rescue_tasks:
                play_result.stats["rescued"] += 1
                rescue_failed = False
                for r_task in rescue_tasks:
                    ok = self._execute_single_task(r_task, host, context, play_result, check_mode, tags, skip_tags)
                    if not ok:
                        rescue_failed = True
                        break
                block_failed = rescue_failed

            if always_tasks:
                for a_task in always_tasks:
                    self._execute_single_task(a_task, host, context, play_result, check_mode, tags, skip_tags)

            return not block_failed

        return self._execute_single_task(task_raw, host, context, play_result, check_mode, tags, skip_tags)

    def _execute_single_task(
        self,
        task_dict: Dict[str, Any],
        host: Host,
        context: Dict[str, Any],
        play_result: PlayResult,
        check_mode: bool,
        tags: List[str],
        skip_tags: List[str],
    ) -> bool:
        task_name = task_dict.get("name", "Unnamed Task")
        task_tags = task_dict.get("tags", [])
        if isinstance(task_tags, str):
            task_tags = [task_tags]

        # Tag filtering
        if tags and not any(t in tags for t in task_tags):
            play_result.stats["skipped"] += 1
            return True
        if skip_tags and any(t in skip_tags for t in task_tags):
            play_result.stats["skipped"] += 1
            return True

        # Loop / with_items handling
        loop_items = task_dict.get("loop") or task_dict.get("with_items")
        if loop_items is not None:
            rendered_loop = TemplateEngine.render_data(loop_items, context)
            if isinstance(rendered_loop, list):
                all_ok = True
                for item in rendered_loop:
                    iter_context = copy.copy(context)
                    iter_context["item"] = item
                    ok = self._run_single_task_iteration(
                        task_dict=task_dict,
                        host=host,
                        context=iter_context,
                        play_result=play_result,
                        check_mode=check_mode,
                    )
                    if not ok:
                        all_ok = False
                return all_ok

        return self._run_single_task_iteration(
            task_dict=task_dict,
            host=host,
            context=context,
            play_result=play_result,
            check_mode=check_mode,
        )

    def _run_single_task_iteration(
        self,
        task_dict: Dict[str, Any],
        host: Host,
        context: Dict[str, Any],
        play_result: PlayResult,
        check_mode: bool,
    ) -> bool:
        task_name = task_dict.get("name", "Unnamed Task")
        context["task_name"] = task_name

        # Conditional 'when' check
        when_cond = task_dict.get("when")
        if when_cond is not None:
            if not TemplateEngine.evaluate_condition(when_cond, context):
                res = TaskResult(
                    host=host.name,
                    task_name=task_name,
                    module="conditional",
                    skipped=True,
                    msg="Conditional check failed",
                )
                play_result.task_results.append(res)
                play_result.stats["skipped"] += 1
                return True

        # Resolve module and args
        module_name, raw_args = self._extract_module_and_args(task_dict)
        if not module_name:
            res = TaskResult(
                host=host.name,
                task_name=task_name,
                module="unknown",
                failed=True,
                msg="No recognized module found in task definition",
            )
            play_result.task_results.append(res)
            play_result.stats["failed"] += 1
            return False

        module_func = ModuleRegistry.get(module_name)
        if not module_func:
            res = TaskResult(
                host=host.name,
                task_name=task_name,
                module=module_name,
                failed=True,
                msg=f"Module '{module_name}' is not registered in Camelot Ansible Armory",
            )
            play_result.task_results.append(res)
            play_result.stats["failed"] += 1
            return False

        # Template module args with context
        rendered_args = TemplateEngine.render_data(raw_args, context)

        # Task check_mode override
        effective_check_mode = task_dict.get("check_mode", check_mode)

        # Execute Module
        start_time = time.time()
        result = module_func(rendered_args, context, effective_check_mode)
        result.elapsed_seconds = time.time() - start_time
        result.task_name = task_name
        result.host = host.name

        # changed_when / failed_when overrides
        if "changed_when" in task_dict:
            c_when = task_dict["changed_when"]
            eval_ctx = copy.copy(context)
            eval_ctx["result"] = result.to_dict()
            result.changed = TemplateEngine.evaluate_condition(c_when, eval_ctx)

        if "failed_when" in task_dict:
            f_when = task_dict["failed_when"]
            eval_ctx = copy.copy(context)
            eval_ctx["result"] = result.to_dict()
            result.failed = TemplateEngine.evaluate_condition(f_when, eval_ctx)

        # Register variable in context if requested
        register_var = task_dict.get("register")
        if register_var:
            context[register_var] = result.to_dict()

        # Update facts if module produced facts
        if result.facts:
            context.update(result.facts)
            host.vars.update(result.facts)

        # Handle notify triggers
        if result.changed and "notify" in task_dict:
            notify_targets = task_dict["notify"]
            if isinstance(notify_targets, str):
                notify_targets = [notify_targets]
            for n in notify_targets:
                self.notified_handlers.add(n)

        # Record result and update stats
        play_result.task_results.append(result)

        ignore_errors = task_dict.get("ignore_errors", False)

        if result.failed:
            if ignore_errors:
                play_result.stats["ignored"] += 1
                return True
            else:
                play_result.stats["failed"] += 1
                return False
        elif result.skipped:
            play_result.stats["skipped"] += 1
            return True
        elif result.changed:
            play_result.stats["changed"] += 1
            play_result.stats["ok"] += 1
            return True
        else:
            play_result.stats["ok"] += 1
            return True

    def _extract_module_and_args(self, task_dict: Dict[str, Any]) -> Tuple[Optional[str], Dict[str, Any]]:
        reserved_keys = {
            "name", "when", "loop", "with_items", "register", "notify",
            "ignore_errors", "changed_when", "failed_when", "tags", "check_mode",
            "vars", "environment", "block", "rescue", "always",
        }
        for key, val in task_dict.items():
            if key not in reserved_keys:
                if ModuleRegistry.has_module(key):
                    if isinstance(val, dict):
                        return key, val
                    elif isinstance(val, str):
                        return key, {"_raw_params": val}
                    elif val is None:
                        return key, {}
                    else:
                        return key, {"args": val}
                elif key in ("args", "action"):
                    # Handle action: module arg1=val1 or args: ...
                    pass
        return None, {}


# ---------------------------------------------------------------------------
# SIR_FORGE & SIR_DEBUG Specialized Runners
# ---------------------------------------------------------------------------

class SirForgeRunner:
    """
    Kinetic Infrastructure & Builder Runner for SIR_FORGE.
    Provides high-velocity declarative scaffolding, compilation pipelines,
    and verifiable deployment manifests.
    """

    def __init__(self, runner: Optional[AnsiblePlaybookRunner] = None):
        self.runner = runner or AnsiblePlaybookRunner()

    def scaffold_workspace(
        self,
        target_dir: Union[str, Path],
        directories: List[str],
        files: Optional[Dict[str, str]] = None,
        templates: Optional[Dict[str, str]] = None,
        context: Optional[Dict[str, Any]] = None,
        check_mode: bool = False,
    ) -> PlaybookExecutionReport:
        """Declaratively scaffolds a project workspace with idempotent directory and file creation."""
        target_path = Path(target_dir).resolve()
        tasks = []

        # 1. Base directory creation
        for d in directories:
            d_path = str(target_path / d)
            tasks.append({
                "name": f"Ensure directory {d} exists",
                "file": {"path": d_path, "state": "directory"},
            })

        # 2. File creation
        if files:
            for f_rel, content in files.items():
                f_path = str(target_path / f_rel)
                tasks.append({
                    "name": f"Ensure file {f_rel} is populated",
                    "copy": {"dest": f_path, "content": content},
                })

        # 3. Template rendering
        if templates:
            for t_rel, t_str in templates.items():
                t_path = str(target_path / t_rel)
                tasks.append({
                    "name": f"Render template for {t_rel}",
                    "template": {"dest": t_path, "template_string": t_str},
                })

        playbook = [{
            "name": f"SIR_FORGE Scaffold Workspace at {target_path}",
            "hosts": "localhost",
            "vars": context or {},
            "tasks": tasks,
        }]

        return self.runner.run_playbook(playbook, check_mode=check_mode)

    def execute_kinetic_build(
        self,
        build_name: str,
        steps: List[Dict[str, Any]],
        env: Optional[Dict[str, str]] = None,
        check_mode: bool = False,
    ) -> PlaybookExecutionReport:
        """Executes a declarative build and test DAG."""
        tasks = []
        for step in steps:
            step_name = step.get("name", "Build step")
            cmd = step.get("cmd")
            creates = step.get("creates")
            chdir = step.get("chdir")
            tasks.append({
                "name": step_name,
                "command": {
                    "cmd": cmd,
                    "creates": creates,
                    "chdir": chdir,
                    "environment": env or {},
                },
            })

        playbook = [{
            "name": f"SIR_FORGE Kinetic Build: {build_name}",
            "hosts": "localhost",
            "tasks": tasks,
        }]

        return self.runner.run_playbook(playbook, check_mode=check_mode)


class SirDebugRunner:
    """
    Self-Healing PIV (Plan -> Implement -> Validate) Runner for SIR_DEBUG.
    Detects configuration drift, formulates auto-remediation playbooks,
    executes rescue blocks, and verifies recovery.
    """

    def __init__(self, runner: Optional[AnsiblePlaybookRunner] = None):
        self.runner = runner or AnsiblePlaybookRunner()

    def inspect_system_drift(
        self,
        desired_state_playbook: Union[str, Path, List[Dict[str, Any]], Dict[str, Any]],
        inventory: Optional[Inventory] = None,
        extra_vars: Optional[Dict[str, Any]] = None,
    ) -> PlaybookExecutionReport:
        """
        Executes a dry-run / check-mode inspection to identify state drift without mutating state.
        """
        return self.runner.run_playbook(
            desired_state_playbook,
            inventory=inventory,
            extra_vars=extra_vars,
            check_mode=True,
        )

    def piv_loop(
        self,
        plan_playbook: Union[str, Path, List[Dict[str, Any]], Dict[str, Any]],
        validation_asserts: List[str],
        max_attempts: int = 3,
    ) -> Dict[str, Any]:
        """
        Executes the full PIV self-healing loop:
        1. Plan / Inspect Drift (Check Mode)
        2. Implement / Reconcile State
        3. Validate with Assertions
        """
        history = []
        success = False

        for attempt in range(1, max_attempts + 1):
            logger.info("SIR_DEBUG PIV Loop Attempt %d/%d", attempt, max_attempts)

            # 1. Inspect
            drift_report = self.inspect_system_drift(plan_playbook)

            # 2. Implement
            apply_report = self.runner.run_playbook(plan_playbook, check_mode=False)

            # 3. Validate
            val_playbook = [{
                "name": f"SIR_DEBUG Validation Attempt {attempt}",
                "hosts": "localhost",
                "tasks": [{
                    "name": "Verify system assertions",
                    "assert": {"that": validation_asserts},
                }],
            }]
            val_report = self.runner.run_playbook(val_playbook, check_mode=False)

            attempt_record = {
                "attempt": attempt,
                "drift_changed": drift_report.total_stats["changed"],
                "apply_success": apply_report.success,
                "validation_success": val_report.success,
            }
            history.append(attempt_record)

            if apply_report.success and val_report.success:
                success = True
                break

        return {
            "success": success,
            "attempts": len(history),
            "history": history,
            "final_status": "HEALED" if success else "FAULT_UNRESOLVED",
        }


# ---------------------------------------------------------------------------
# CLI / Entrypoint
# ---------------------------------------------------------------------------

def main() -> int:  # pragma: no cover
    import argparse
    parser = argparse.ArgumentParser(description="Camelot-OS Ansible Declarative Playbook Runner")
    parser.add_argument("playbook", help="Path to YAML/JSON playbook file")
    parser.add_argument("-i", "--inventory", help="Path to inventory file or comma-separated host list")
    parser.add_argument("-C", "--check", action="store_true", help="Run in check mode (dry-run)")
    parser.add_argument("-e", "--extra-vars", help="Extra variables as JSON string or key=val")
    parser.add_argument("-t", "--tags", help="Only run tasks matching these tags (comma-separated)")
    parser.add_argument("--skip-tags", help="Skip tasks matching these tags (comma-separated)")
    parser.add_argument("--verify-idempotency", action="store_true", help="Run twice to guarantee idempotency")

    args = parser.parse_args()

    inv = Inventory(args.inventory) if args.inventory else Inventory()
    extra_vars = {}
    if args.extra_vars:
        if args.extra_vars.startswith("{"):
            extra_vars = json.loads(args.extra_vars)
        else:
            for item in args.extra_vars.split(","):
                if "=" in item:
                    k, v = item.split("=", 1)
                    extra_vars[k.strip()] = v.strip()

    runner = AnsiblePlaybookRunner(inventory=inv)

    if args.verify_idempotency:
        is_idempotent, r1, r2 = runner.verify_idempotency(args.playbook, extra_vars=extra_vars)
        print(r1.summary())
        print(r2.summary())
        print(f"IDEMPOTENCY CHECK: {'PASSED' if is_idempotent else 'FAILED'}")
        return 0 if is_idempotent else 1

    tags = args.tags.split(",") if args.tags else None
    skip_tags = args.skip_tags.split(",") if args.skip_tags else None

    report = runner.run_playbook(
        playbook=args.playbook,
        extra_vars=extra_vars,
        check_mode=args.check,
        tags=tags,
        skip_tags=skip_tags,
    )
    print(report.summary())
    return 0 if report.success else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
