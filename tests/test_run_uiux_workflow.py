import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.abspath('.')) # noqa: E402
from bin.run_uiux_workflow import WorkflowRunner

def test_workflow_runner_simple_task():
    with TemporaryDirectory() as tmpdir:
        workflow_path = Path(tmpdir) / "test_workflow.json"

        # Determine appropriate echo command format based on platform
        cmd_str = "echo 'hello world'" if os.name == 'posix' else "echo hello world"

        workflow_data = {
            "name": "test_workflow",
            "version": 1,
            "tasks": [
                {
                    "name": "test_echo",
                    "type": "SIMPLE",
                    "command": cmd_str,
                    "cwd": tmpdir,
                    "capture_output": True
                }
            ]
        }
        with open(workflow_path, "w", encoding="utf-8") as f:
            json.dump(workflow_data, f)

        runner = WorkflowRunner(workflow_path)

        task = workflow_data["tasks"][0]
        success = runner.execute_task(task)
        assert success is True

        result = runner.results["test_echo"]
        assert result["status"] == "SUCCESS"
        assert "hello world" in result["output"]

if __name__ == "__main__":
    test_workflow_runner_simple_task()
