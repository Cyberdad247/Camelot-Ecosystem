# SPDX-License-Identifier: MIT
"""
Comprehensive Unit Tests for Camelot-OS Ansible Declarative Infrastructure Runner.
Tests:
- Inventory and host/group variable resolution
- TemplateEngine rendering and conditional evaluation
- Declarative module idempotency (file, copy, template, lineinfile, command, stat, assert, etc.)
- Playbook runner execution (loops, when, notify/handlers, block/rescue/always, tags, check_mode)
- Idempotency verification loop
- SIR_FORGE kinetic workspace scaffolding and build execution
- SIR_DEBUG drift inspection and PIV self-healing loop
"""

from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

import importlib.util
ansible_runner_path = Path(__file__).parent.parent / "02_FORGE" / "KINETIC_ARMORY" / "ansible_runner.py"
spec = importlib.util.spec_from_file_location("ansible_runner", str(ansible_runner_path))
ansible_runner_module = importlib.util.module_from_spec(spec)
sys.modules["ansible_runner"] = ansible_runner_module
spec.loader.exec_module(ansible_runner_module)

Host = ansible_runner_module.Host
Inventory = ansible_runner_module.Inventory
TaskResult = ansible_runner_module.TaskResult
PlayResult = ansible_runner_module.PlayResult
PlaybookExecutionReport = ansible_runner_module.PlaybookExecutionReport
TemplateEngine = ansible_runner_module.TemplateEngine
ModuleRegistry = ansible_runner_module.ModuleRegistry
AnsiblePlaybookRunner = ansible_runner_module.AnsiblePlaybookRunner
SirForgeRunner = ansible_runner_module.SirForgeRunner
SirDebugRunner = ansible_runner_module.SirDebugRunner


# ---------------------------------------------------------------------------
# 1. Inventory Tests
# ---------------------------------------------------------------------------

def test_inventory_localhost_initialization():
    inv = Inventory()
    hosts = inv.get_hosts("all")
    assert any(h.name == "localhost" for h in hosts)
    assert inv.hosts["localhost"].get_var("ansible_connection") == "local"


def test_inventory_add_host_and_group_vars():
    inv = Inventory()
    inv.add_host("worker-1", groups=["workers", "web"], host_vars={"http_port": 8080})
    inv.add_host("worker-2", groups=["workers", "db"], host_vars={"db_port": 5432})
    inv.set_group_var("workers", "cluster_name", "camelot-grid")

    w1 = inv.hosts["worker-1"]
    vars_w1 = inv.get_host_vars(w1)
    assert vars_w1["cluster_name"] == "camelot-grid"
    assert vars_w1["http_port"] == 8080

    workers = inv.get_hosts("workers")
    assert len(workers) == 2


def test_inventory_dict_loader():
    data = {
        "webservers": {
            "hosts": ["web1", "web2"],
            "vars": {"tier": "frontend"}
        }
    }
    inv = Inventory(data)
    assert len(inv.get_hosts("webservers")) == 2
    web1 = inv.hosts["web1"]
    assert inv.get_host_vars(web1)["tier"] == "frontend"


# ---------------------------------------------------------------------------
# 2. TemplateEngine Tests
# ---------------------------------------------------------------------------

def test_template_engine_string_render():
    context = {"user": "Arthur", "role": "King", "level": 100}
    rendered = TemplateEngine.render_string("Hail {{ user }}, {{ role }} of Camelot!", context)
    assert rendered == "Hail Arthur, King of Camelot!"


def test_template_engine_nested_and_data_render():
    context = {"cfg": {"port": 9000, "ssl": True}}
    rendered_dict = TemplateEngine.render_data(
        {"server_port": "{{ cfg.port }}", "active": "{{ cfg.ssl }}"},
        context
    )
    assert rendered_dict["server_port"] == 9000
    assert rendered_dict["active"] is True


def test_template_engine_condition_evaluation():
    context = {"env": "prod", "replicas": 3, "enabled": True}
    assert TemplateEngine.evaluate_condition("env == 'prod'", context) is True
    assert TemplateEngine.evaluate_condition("replicas > 5", context) is False
    assert TemplateEngine.evaluate_condition(["enabled", "replicas >= 3"], context) is True


# ---------------------------------------------------------------------------
# 3. Core Declarative Module Tests
# ---------------------------------------------------------------------------

def test_module_file_directory_creation_and_idempotency(tmp_path: Path):
    target_dir = tmp_path / "nexus" / "core"
    args = {"path": str(target_dir), "state": "directory"}
    ctx = {"inventory_hostname": "localhost"}

    # 1. First run -> changed = True, dir created
    res1 = ModuleRegistry.get("file")(args, ctx, check_mode=False)
    assert res1.changed is True
    assert target_dir.is_dir()

    # 2. Second run -> changed = False (idempotent no-op)
    res2 = ModuleRegistry.get("file")(args, ctx, check_mode=False)
    assert res2.changed is False


def test_module_file_absent_and_touch(tmp_path: Path):
    target_file = tmp_path / "probe.txt"
    ctx = {"inventory_hostname": "localhost"}

    # Touch
    res_touch = ModuleRegistry.get("file")({"path": str(target_file), "state": "touch"}, ctx, check_mode=False)
    assert res_touch.changed is True
    assert target_file.exists()

    # Absent
    res_absent = ModuleRegistry.get("file")({"path": str(target_file), "state": "absent"}, ctx, check_mode=False)
    assert res_absent.changed is True
    assert not target_file.exists()

    # Absent again -> changed = False
    res_absent_again = ModuleRegistry.get("file")({"path": str(target_file), "state": "absent"}, ctx, check_mode=False)
    assert res_absent_again.changed is False


def test_module_copy_content_and_idempotency(tmp_path: Path):
    dest = tmp_path / "config.json"
    content = '{"mode": "hyperagent", "active": true}'
    args = {"dest": str(dest), "content": content}
    ctx = {"inventory_hostname": "localhost"}

    # First copy
    res1 = ModuleRegistry.get("copy")(args, ctx, check_mode=False)
    assert res1.changed is True
    assert dest.read_text(encoding="utf-8") == content

    # Second copy -> same content -> changed = False
    res2 = ModuleRegistry.get("copy")(args, ctx, check_mode=False)
    assert res2.changed is False


def test_module_template_rendering(tmp_path: Path):
    dest = tmp_path / "manifest.yaml"
    template_str = "service_name: {{ svc_name }}\nport: {{ port }}\n"
    args = {"dest": str(dest), "template_string": template_str}
    ctx = {"inventory_hostname": "localhost", "svc_name": "bifrost", "port": 8011}

    res1 = ModuleRegistry.get("template")(args, ctx, check_mode=False)
    assert res1.changed is True
    assert "service_name: bifrost" in dest.read_text(encoding="utf-8")
    assert "port: 8011" in dest.read_text(encoding="utf-8")

    # Idempotent re-run
    res2 = ModuleRegistry.get("template")(args, ctx, check_mode=False)
    assert res2.changed is False


def test_module_lineinfile(tmp_path: Path):
    target = tmp_path / "hosts.ini"
    target.write_text("127.0.0.1 localhost\n", encoding="utf-8")
    ctx = {"inventory_hostname": "localhost"}

    # Add line
    res1 = ModuleRegistry.get("lineinfile")(
        {"path": str(target), "line": "10.0.0.1 sir_forge"},
        ctx,
        check_mode=False,
    )
    assert res1.changed is True
    assert "10.0.0.1 sir_forge" in target.read_text(encoding="utf-8")

    # Idempotent second run
    res2 = ModuleRegistry.get("lineinfile")(
        {"path": str(target), "line": "10.0.0.1 sir_forge"},
        ctx,
        check_mode=False,
    )
    assert res2.changed is False


def test_module_stat_and_assert(tmp_path: Path):
    test_file = tmp_path / "signal.dat"
    test_file.write_text("OMEGA_CRYSTAL", encoding="utf-8")
    ctx = {"inventory_hostname": "localhost"}

    # stat
    stat_res = ModuleRegistry.get("stat")({"path": str(test_file)}, ctx, check_mode=False)
    assert stat_res.data["stat"]["exists"] is True
    assert stat_res.data["stat"]["size"] > 0
    assert stat_res.data["stat"]["checksum"] is not None

    # assert passed
    ctx["my_var"] = 42
    assert_res = ModuleRegistry.get("assert")({"that": ["my_var == 42", "my_var > 10"]}, ctx, check_mode=False)
    assert assert_res.failed is False

    # assert failed
    assert_fail = ModuleRegistry.get("assert")({"that": ["my_var == 999"]}, ctx, check_mode=False)
    assert assert_fail.failed is True


def test_module_command_creates_guard(tmp_path: Path):
    guard_file = tmp_path / "built.lock"
    guard_file.write_text("locked", encoding="utf-8")
    ctx = {"inventory_hostname": "localhost"}

    # Command with creates=guard_file should skip
    res = ModuleRegistry.get("command")(
        {"cmd": "python -c 'print(1)'", "creates": str(guard_file)},
        ctx,
        check_mode=False,
    )
    assert res.skipped is True
    assert res.changed is False


# ---------------------------------------------------------------------------
# 4. Playbook Runner & Control Flow Tests
# ---------------------------------------------------------------------------

def test_playbook_runner_simple_execution(tmp_path: Path):
    out_file = tmp_path / "hello.txt"
    playbook = [
        {
            "name": "Test Play",
            "hosts": "localhost",
            "vars": {"greeting": "Camelot Forever"},
            "tasks": [
                {
                    "name": "Ping target",
                    "ping": {},
                },
                {
                    "name": "Write greeting",
                    "copy": {"dest": str(out_file), "content": "{{ greeting }}"},
                },
            ],
        }
    ]

    runner = AnsiblePlaybookRunner()
    report = runner.run_playbook(playbook)
    assert report.success is True
    assert report.total_stats["ok"] == 2
    assert report.total_stats["changed"] == 1
    assert out_file.read_text(encoding="utf-8") == "Camelot Forever"


def test_playbook_runner_loop_and_when(tmp_path: Path):
    playbook = [
        {
            "name": "Loop and Conditional Play",
            "hosts": "localhost",
            "vars": {"deploy_env": "production"},
            "tasks": [
                {
                    "name": "Create multiple directories",
                    "file": {"path": str(tmp_path / "{{ item }}"), "state": "directory"},
                    "loop": ["dir1", "dir2", "dir3"],
                },
                {
                    "name": "Skip in production",
                    "file": {"path": str(tmp_path / "dev_only.txt"), "state": "touch"},
                    "when": "deploy_env == 'development'",
                },
                {
                    "name": "Run in production",
                    "file": {"path": str(tmp_path / "prod_only.txt"), "state": "touch"},
                    "when": "deploy_env == 'production'",
                },
            ],
        }
    ]

    runner = AnsiblePlaybookRunner()
    report = runner.run_playbook(playbook)
    assert report.success is True
    assert (tmp_path / "dir1").is_dir()
    assert (tmp_path / "dir2").is_dir()
    assert (tmp_path / "dir3").is_dir()
    assert not (tmp_path / "dev_only.txt").exists()
    assert (tmp_path / "prod_only.txt").exists()


def test_playbook_runner_handlers_and_notify(tmp_path: Path):
    flag_file = tmp_path / "handler_fired.txt"
    target_file = tmp_path / "trigger.txt"

    playbook = [
        {
            "name": "Handler Play",
            "hosts": "localhost",
            "tasks": [
                {
                    "name": "Mutate file to notify handler",
                    "copy": {"dest": str(target_file), "content": "rev-1"},
                    "notify": "restart_service",
                }
            ],
            "handlers": [
                {
                    "name": "restart_service",
                    "copy": {"dest": str(flag_file), "content": "RESTARTED"},
                }
            ],
        }
    ]

    runner = AnsiblePlaybookRunner()
    report = runner.run_playbook(playbook)
    assert report.success is True
    assert flag_file.exists()
    assert flag_file.read_text(encoding="utf-8") == "RESTARTED"


def test_playbook_runner_block_rescue_always(tmp_path: Path):
    rescue_log = tmp_path / "rescued.log"
    always_log = tmp_path / "always.log"

    playbook = [
        {
            "name": "Block Rescue Always Play",
            "hosts": "localhost",
            "tasks": [
                {
                    "block": [
                        {"name": "Deliberate failure", "fail": {"msg": "Kernel Panic Simulation"}},
                    ],
                    "rescue": [
                        {"name": "Perform self-heal", "copy": {"dest": str(rescue_log), "content": "HEALED"}},
                    ],
                    "always": [
                        {"name": "Audit log", "copy": {"dest": str(always_log), "content": "ALWAYS_RAN"}},
                    ],
                }
            ],
        }
    ]

    runner = AnsiblePlaybookRunner()
    report = runner.run_playbook(playbook)
    assert report.success is True
    assert report.total_stats["rescued"] == 1
    assert rescue_log.read_text(encoding="utf-8") == "HEALED"
    assert always_log.read_text(encoding="utf-8") == "ALWAYS_RAN"


def test_playbook_runner_check_mode_dry_run(tmp_path: Path):
    target = tmp_path / "never_created.txt"
    playbook = [
        {
            "name": "Dry Run Play",
            "hosts": "localhost",
            "tasks": [
                {"name": "Create phantom file", "copy": {"dest": str(target), "content": "ghost"}},
            ],
        }
    ]

    runner = AnsiblePlaybookRunner()
    report = runner.run_playbook(playbook, check_mode=True)
    assert report.check_mode is True
    assert report.total_stats["changed"] == 1
    assert not target.exists()  # Disk was not modified


def test_verify_idempotency_loop(tmp_path: Path):
    target = tmp_path / "idempotent_test.json"
    playbook = [
        {
            "name": "Idempotent Play",
            "hosts": "localhost",
            "tasks": [
                {"name": "Write config", "copy": {"dest": str(target), "content": '{"version": 1}'}},
                {"name": "Verify file", "stat": {"path": str(target)}},
            ],
        }
    ]

    runner = AnsiblePlaybookRunner()
    is_idempotent, r1, r2 = runner.verify_idempotency(playbook)
    assert is_idempotent is True
    assert r1.total_stats["changed"] == 1
    assert r2.total_stats["changed"] == 0
    assert r2.total_stats["failed"] == 0


# ---------------------------------------------------------------------------
# 5. SIR_FORGE & SIR_DEBUG Runner Tests
# ---------------------------------------------------------------------------

def test_sir_forge_scaffold_workspace(tmp_path: Path):
    ws_root = tmp_path / "forge_project"
    forge = SirForgeRunner()

    report = forge.scaffold_workspace(
        target_dir=ws_root,
        directories=["src", "config", "docs"],
        files={"README.md": "# Project Forge", "config/settings.json": "{}"},
        templates={"src/version.py": "__version__ = '{{ version }}'"},
        context={"version": "1.0.0"},
    )

    assert report.success is True
    assert (ws_root / "src").is_dir()
    assert (ws_root / "README.md").read_text(encoding="utf-8") == "# Project Forge"
    assert "__version__ = '1.0.0'" in (ws_root / "src" / "version.py").read_text(encoding="utf-8")


def test_sir_debug_piv_loop(tmp_path: Path):
    health_file = tmp_path / "system_health.txt"
    debugger = SirDebugRunner()

    plan_playbook = [
        {
            "name": "Remediate Health State",
            "hosts": "localhost",
            "tasks": [
                {"name": "Write OK status", "copy": {"dest": str(health_file), "content": "SYSTEM_HEALTHY"}},
                {"name": "Register fact", "set_fact": {"health_status": "OK"}},
            ],
        }
    ]

    validation_asserts = [
        "health_status == 'OK'",
    ]

    res = debugger.piv_loop(plan_playbook, validation_asserts=validation_asserts, max_attempts=2)
    assert res["success"] is True
    assert res["final_status"] == "HEALED"
    assert health_file.read_text(encoding="utf-8") == "SYSTEM_HEALTHY"


def test_playbook_runner_register_and_assert(tmp_path: Path):
    target = tmp_path / "registered.txt"
    playbook = [
        {
            "name": "Register and Assert Play",
            "hosts": "localhost",
            "tasks": [
                {
                    "name": "Create file and register result",
                    "copy": {"dest": str(target), "content": "ALPHA_DATA"},
                    "register": "alpha_res",
                },
                {
                    "name": "Verify registered variable in assert",
                    "assert": {
                        "that": [
                            "alpha_res.changed == True",
                            "alpha_res.failed == False",
                            "alpha_res.module == 'copy'",
                        ]
                    },
                },
            ],
        }
    ]

    runner = AnsiblePlaybookRunner()
    report = runner.run_playbook(playbook)
    assert report.success is True
    assert report.total_stats["ok"] == 2


def test_playbook_runner_tag_filtering(tmp_path: Path):
    t1_file = tmp_path / "tag1.txt"
    t2_file = tmp_path / "tag2.txt"

    playbook = [
        {
            "name": "Tag Filtering Play",
            "hosts": "localhost",
            "tasks": [
                {
                    "name": "Task with tag1",
                    "copy": {"dest": str(t1_file), "content": "T1"},
                    "tags": ["build", "fast"],
                },
                {
                    "name": "Task with tag2",
                    "copy": {"dest": str(t2_file), "content": "T2"},
                    "tags": ["slow", "nightly"],
                },
            ],
        }
    ]

    runner = AnsiblePlaybookRunner()
    # Run only 'fast'
    rep1 = runner.run_playbook(playbook, tags=["fast"])
    assert rep1.success is True
    assert t1_file.exists()
    assert not t2_file.exists()

    # Skip 'build'
    t1_file.unlink()
    rep2 = runner.run_playbook(playbook, skip_tags=["build"])
    assert rep2.success is True
    assert not t1_file.exists()
    assert t2_file.exists()


def test_playbook_runner_changed_when_failed_when(tmp_path: Path):
    playbook = [
        {
            "name": "Changed and Failed When Play",
            "hosts": "localhost",
            "tasks": [
                {
                    "name": "Override changed state to False",
                    "ping": {},
                    "changed_when": "False",
                },
                {
                    "name": "Override changed state to True",
                    "ping": {},
                    "changed_when": "True",
                },
            ],
        }
    ]

    runner = AnsiblePlaybookRunner()
    report = runner.run_playbook(playbook)
    assert report.success is True
    assert report.total_stats["changed"] == 1


def test_playbook_runner_ignore_errors():
    playbook = [
        {
            "name": "Ignore Errors Play",
            "hosts": "localhost",
            "tasks": [
                {
                    "name": "Failing task that is ignored",
                    "fail": {"msg": "Suppressed error"},
                    "ignore_errors": True,
                },
                {
                    "name": "Subsequent task still executes",
                    "ping": {},
                },
            ],
        }
    ]

    runner = AnsiblePlaybookRunner()
    report = runner.run_playbook(playbook)
    assert report.success is True
    assert report.total_stats["ignored"] == 1
    assert report.total_stats["ok"] == 1


def test_custom_module_registration():
    @ModuleRegistry.register("custom_echo")
    def module_custom_echo(args, context, check_mode):
        text = args.get("text", "")
        return TaskResult(
            host=context.get("inventory_hostname", "localhost"),
            task_name=context.get("task_name", "custom_echo"),
            module="custom_echo",
            changed=True,
            msg=f"CUSTOM: {text}",
            data={"echo": text},
        )

    playbook = [
        {
            "name": "Custom Module Play",
            "hosts": "localhost",
            "tasks": [
                {
                    "name": "Execute custom echo",
                    "custom_echo": {"text": "Camelot Kinetic Module"},
                }
            ],
        }
    ]

    runner = AnsiblePlaybookRunner()
    report = runner.run_playbook(playbook)
    assert report.success is True
    assert report.play_results[0].task_results[0].msg == "CUSTOM: Camelot Kinetic Module"


def test_sir_forge_kinetic_build_dag(tmp_path: Path):
    build_flag = tmp_path / "build_output.txt"
    forge = SirForgeRunner()

    steps = [
        {
            "name": "Generate artifact",
            "cmd": f"python -c \"import pathlib; pathlib.Path(r'{build_flag}').write_text('BUILT', encoding='utf-8')\"",
        },
        {
            "name": "Test artifact presence",
            "cmd": f"python -c \"import pathlib; assert pathlib.Path(r'{build_flag}').exists()\"",
        },
    ]

    report = forge.execute_kinetic_build("TestBuild", steps=steps)
    assert report.success is True
    assert build_flag.read_text(encoding="utf-8") == "BUILT"


def test_sir_debug_inspect_drift(tmp_path: Path):
    expected_file = tmp_path / "drift_target.txt"
    debugger = SirDebugRunner()

    desired_playbook = [
        {
            "name": "Inspect Drift",
            "hosts": "localhost",
            "tasks": [
                {"name": "Ensure drift file exists", "copy": {"dest": str(expected_file), "content": "DRIFT_VAL"}},
            ],
        }
    ]

    drift_report = debugger.inspect_system_drift(desired_playbook)
    assert drift_report.check_mode is True
    assert drift_report.total_stats["changed"] == 1
    assert not expected_file.exists()

