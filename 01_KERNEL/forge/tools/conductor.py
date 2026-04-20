# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path

from google import genai

# 🛡️ CONFIGURATION
WORKFLOW_FILE = Path(r"C:\Users\vizio\CAMELOT_OS\01_KERNEL\workflows\validation_workflow.json")
REPORT_FILE = Path(r"C:\Users\vizio\CAMELOT_OS\99_HISTORY\WORKFLOW_REPORT.md")

# Initialize Gemini
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


class Conductor:
    def __init__(self):
        self.results = {}

    async def execute_task(self, task):
        print(f"⚡ [CONDUCTOR] Executing Task: {task['name']}...")
        start_time = datetime.now()

        if task["type"] == "SIMPLE":
            try:
                # Execute Shell Command
                process = await asyncio.create_subprocess_shell(
                    task["command"],
                    cwd=task.get("cwd", "."),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await process.communicate()

                output = stdout.decode() + stderr.decode()
                success = process.returncode == 0

                self.results[task["name"]] = {
                    "status": "SUCCESS" if success else "FAILURE",
                    "output": output,
                    "duration": (datetime.now() - start_time).total_seconds(),
                }

                if success:
                    print("   ✅ Task Passed.")
                else:
                    print("   ❌ Task Failed.")

                return success

            except Exception as e:
                self.results[task["name"]] = {"status": "ERROR", "output": str(e)}
                print(f"   ❌ Task Error: {e}")
                return False

        elif task["type"] == "AI_ANALYSIS":
            # Get input from referenced task
            ref_task = task.get("input_ref")
            if not ref_task or ref_task not in self.results:
                print("   ⚠️ Skipping Analysis (No input ref)")
                return True

            input_data = self.results[ref_task]["output"]

            # Only analyze if there was a failure or if forced
            if self.results[ref_task]["status"] == "SUCCESS" and not task.get("force", False):
                print("   ⏩ Skipping Analysis (Previous task succeeded)")
                self.results[task["name"]] = {"status": "SKIPPED", "output": "No failure to analyze."}
                return True

            print("   🧠 [GEMINI] Analyzing failure...")
            try:
                prompt = f"{task['prompt']}\n\nCONTEXT:\n{input_data[:5000]}"  # Limit context
                response = await client.models.generate_content(model="gemini-2.0-flash-exp", contents=prompt)

                analysis = response.text
                self.results[task["name"]] = {"status": "SUCCESS", "output": analysis}
                print("   ✅ Analysis Complete.")
                return True
            except Exception as e:
                print(f"   ❌ Analysis Failed: {e}")
                return False

    async def run_workflow(self):
        with open(WORKFLOW_FILE, "r") as f:
            workflow = json.load(f)

        print(f"🎼 [CONDUCTOR] Starting Workflow: {workflow['name']}")

        for task in workflow["tasks"]:
            success = await self.execute_task(task)
            if not success and task.get("stop_on_failure", False):
                print("🛑 Workflow Halted.")
                break

        self.generate_report(workflow)

    def generate_report(self, workflow):
        report = f"# 🎼 CONDUCTOR REPORT: {workflow['name']}\n"
        report += f"**Date:** {datetime.now().isoformat()}\n\n"

        for task_name, result in self.results.items():
            icon = "✅" if result["status"] == "SUCCESS" else "❌" if result["status"] == "FAILURE" else "⚠️"
            report += f"## {icon} {task_name}\n"
            report += f"**Status:** {result['status']}\n"
            if "duration" in result:
                report += f"**Duration:** {result['duration']:.2f}s\n"

            report += "\n**Output:**\n"
            report += f"```\n{result['output'][:2000]}\n```\n"  # Truncate large outputs

            if result["status"] == "FAILURE":
                report += "\n> **ACTION REQUIRED:** Check Analysis.\n"

        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"📜 Report generated: {REPORT_FILE}")


if __name__ == "__main__":
    asyncio.run(Conductor().run_workflow())