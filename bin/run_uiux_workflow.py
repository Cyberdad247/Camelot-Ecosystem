"""Execute the UI/UX cloudbrain workflow JSON."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

DEFAULT_WORKFLOW = Path(r"C:\Users\vizio\CAMELOT_OS\01_KERNEL\workflows\uiux_cloudbrain_sync.json")
REPORT_FILE = Path(r"C:\Users\vizio\CAMELOT_OS\99_HISTORY\WORKFLOW_REPORT_UIUX.md")
_REPO_ROOT = Path(__file__).resolve().parents[1]


class WorkflowRunner:
    def __init__(self, workflow_file: Path):
        self.workflow_file = workflow_file
        self.results: dict[str, dict[str, str]] = {}

    def execute_task(self, task: dict[str, object]) -> bool:
        name = str(task["name"])
        task_type = str(task["type"])
        print(f"[WORKFLOW] Executing task: {name}")
        start_time = datetime.now()

        if task_type == "SIMPLE":
            cmd = str(task["command"])
            cwd = str(task.get("cwd", "."))
            # WARNING: shell=True is required here because cmd is a shell-style
            # string from the workflow JSON. Only run workflow files from trusted,
            # access-controlled paths — never from user-supplied input.
            process = subprocess.run(
                cmd,
                cwd=cwd,
                shell=True,
                capture_output=True,
                text=True,
            )
            output = (process.stdout or "") + (process.stderr or "")
            success = process.returncode == 0
            self.results[name] = {
                "status": "SUCCESS" if success else "FAILURE",
                "output": output,
                "duration": f"{(datetime.now() - start_time).total_seconds():.2f}",
            }
            print("  [OK] task passed" if success else "  [FAIL] task failed")
            return success

        if task_type == "AI_ANALYSIS":
            ref_task = str(task.get("input_ref", ""))
            if ref_task not in self.results:
                self.results[name] = {"status": "SKIPPED", "output": "Missing input_ref task"}
                print("  [WARN] skipping analysis (missing input ref)")
                return True

            input_data = self.results[ref_task]["output"]
            prompt = str(task.get("prompt", ""))
            analysis = self._analyze(prompt, input_data)
            self.results[name] = {"status": "SUCCESS", "output": analysis}
            print("  [OK] analysis complete")
            return True

        self.results[name] = {"status": "SKIPPED", "output": f"Unsupported task type: {task_type}"}
        return True

    def _analyze(self, prompt: str, input_data: str) -> str:
        try:
            from google import genai

            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise RuntimeError("GOOGLE_API_KEY not set")
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=f"{prompt}\n\nCONTEXT:\n{input_data[:5000]}",
            )
            return response.text or ""
        except Exception as exc:
            return (
                "Local analysis fallback:\n"
                f"- Gemini unavailable: {type(exc).__name__}: {exc}\n"
                f"- Input length: {len(input_data)}\n"
                "- Recommend checking workflow output and notebook sync artifacts."
            )

    def run(self) -> int:
        with self.workflow_file.open("r", encoding="utf-8") as f:
            workflow = json.load(f)

        print(f"[WORKFLOW] Starting workflow: {workflow['name']}")
        for task in workflow["tasks"]:
            success = self.execute_task(task)
            if not success and task.get("stop_on_failure", False):
                print("[STOP] workflow halted")
                break

        self._write_report(workflow)
        return 0

    def _write_report(self, workflow: dict[str, object]) -> None:
        report = [f"# WORKFLOW REPORT: {workflow['name']}", f"**Date:** {datetime.now().isoformat()}", ""]
        for task_name, result in self.results.items():
            status = result["status"]
            icon = "OK" if status == "SUCCESS" else "FAIL" if status == "FAILURE" else "WARN"
            report.append(f"## {icon} {task_name}")
            report.append(f"**Status:** {status}")
            if "duration" in result:
                report.append(f"**Duration:** {result['duration']}s")
            report.append("")
            report.append("**Output:**")
            report.append("```")
            report.append(result["output"][:2000])
            report.append("```")
            report.append("")

        REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
        REPORT_FILE.write_text("\n".join(report), encoding="utf-8")
        print(f"[REPORT] Generated: {REPORT_FILE}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the UI/UX cloudbrain workflow.")
    parser.add_argument("--workflow", default=str(DEFAULT_WORKFLOW), help="Path to the workflow JSON file.")
    args = parser.parse_args()
    workflow_path = Path(args.workflow).resolve()
    try:
        workflow_path.relative_to(_REPO_ROOT)
    except ValueError:
        raise SystemExit(
            f"ERROR: workflow file must be inside the repo root ({_REPO_ROOT}).\n"
            f"Refusing to execute untrusted path: {workflow_path}"
        )
    return WorkflowRunner(workflow_path).run()


if __name__ == "__main__":
    raise SystemExit(main())
