# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import argparse
import json
import os
import re
from datetime import datetime


class AuditContext:
    def __init__(self, path):
        self.path = path
        self.meta = {"target": os.path.basename(path), "date": datetime.now().isoformat(), "auditor": "Nano-CLI v1.0"}
        self.phases = {}
        self.score = {"overall": 0, "grade": "F"}


class Architect:
    def audit(self, context):
        topology = {"type": "Unknown", "stack": []}
        for root, dirs, files in os.walk(context.path):
            if "node_modules" in dirs:
                dirs.remove("node_modules")
            if ".git" in dirs:
                dirs.remove(".git")
            
            # Ignite: Ignore build artifacts and hidden dirs
            for ignore in [".next", ".vercel", "dist", "build", "coverage", ".hive"]:
                if ignore in dirs:
                    dirs.remove(ignore)

            if "Dockerfile" in files:
                topology["stack"].append("Docker")
            if "package.json" in files:
                topology["stack"].append("Node.js")
            if "next.config.js" in files or "next.config.ts" in files:
                topology["stack"].append("Next.js")
            if "pyproject.toml" in files or "requirements.txt" in files:
                topology["stack"].append("Python")
            if "Cargo.toml" in files:
                topology["stack"].append("Rust")

        topology["stack"] = list(set(topology["stack"]))
        if "Docker" in topology["stack"] and len(topology["stack"]) > 1:
            topology["type"] = "Containerized App"
        elif len(topology["stack"]) > 0:
            topology["type"] = "Service/App"

        context.phases["architecture"] = topology


class QualityCtrl:
    def audit(self, context):
        quality = {"score": 100, "style": "Foundational"}
        configs = []
        for root, dirs, files in os.walk(context.path):
            if "node_modules" in dirs:
                dirs.remove("node_modules")
            if ".git" in dirs:
                dirs.remove(".git")

            for f in files:
                if f in [".eslintrc", ".prettierrc", "pyrightconfig.json", "ruff.toml", ".flake8"]:
                    configs.append(f)

        quality["configs"] = configs
        if not configs:
            quality["score"] -= 30
            quality["style"] = "Lacks Linters"

        context.phases["quality"] = quality


class TestScout:
    def audit(self, context):
        testing = {"frameworks": [], "test_count": 0}
        patterns = {"Pytest": r"test_.*\.py$", "Jest": r".*\.test\.(js|ts|tsx)$", "Vitest": r".*\.spec\.(js|ts|tsx)$"}

        for root, dirs, files in os.walk(context.path):
            if "node_modules" in dirs:
                dirs.remove("node_modules")
            if ".git" in dirs:
                dirs.remove(".git")

            for f in files:
                for framework, pattern in patterns.items():
                    if re.match(pattern, f):
                        testing["test_count"] += 1
                        if framework not in testing["frameworks"]:
                            testing["frameworks"].append(framework)

        context.phases["testing"] = testing


class SecOps:
    def audit(self, context):
        security = {"vulnerabilities": 0, "critical_findings": []}
        secret_patterns = [
            r"sk-[a-zA-Z0-9]{20,}",  # Generic OpenAI-like
            r"AIza[0-9A-Za-z-_]{35}",  # Google API Key
            r"(?i)password\s*[:=]\s*['\"].*['\"]",
        ]

        for root, dirs, files in os.walk(context.path):
            if "node_modules" in dirs:
                dirs.remove("node_modules")
            if ".git" in dirs:
                dirs.remove(".git")

            for f in files:
                if f.endswith((".py", ".js", ".ts", ".env", ".yaml", ".yml", ".json")):
                    try:
                        with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as file:
                            content = file.read()
                            for pattern in secret_patterns:
                                matches = re.findall(pattern, content)
                                if matches:
                                    security["vulnerabilities"] += len(matches)
                                    security["critical_findings"].append(f"Potential secret in {f}")
                    except:
                        continue

        security["critical_findings"] = list(set(security["critical_findings"]))
        context.phases["security"] = security


class Scribe:
    def audit(self, context):
        docs = {"grade": "F", "missing": []}
        critical_docs = ["README.md", "CONTRIBUTING.md", "LICENSE", "ARCHITECTURE.md"]
        found = []

        for f in os.listdir(context.path):
            if f.upper() in [cd.upper() for cd in critical_docs]:
                found.append(f.upper())

        docs["missing"] = [cd for cd in critical_docs if cd.upper() not in found]
        score = (len(found) / len(critical_docs)) * 100
        if score == 100:
            docs["grade"] = "A"
        elif score >= 75:
            docs["grade"] = "B"
        elif score >= 50:
            docs["grade"] = "C"

        context.phases["documentation"] = docs


class Synthesizer:
    def audit(self, context):
        # Calculate overall score
        q_score = context.phases["quality"].get("score", 0)
        s_score = 100 - (min(context.phases["security"].get("vulnerabilities", 0) * 10, 50))
        d_grade_map = {"A": 100, "B": 80, "C": 60, "D": 40, "F": 0}
        d_score = d_grade_map.get(context.phases["documentation"]["grade"], 0)

        context.score["overall"] = int((q_score + s_score + d_score) / 3)
        if context.score["overall"] >= 90:
            context.score["grade"] = "S"
        elif context.score["overall"] >= 80:
            context.score["grade"] = "A"
        elif context.score["overall"] >= 70:
            context.score["grade"] = "B"
        elif context.score["overall"] >= 60:
            context.score["grade"] = "C"
        else:
            context.score["grade"] = "D"


def run_audit(path, output_file):
    if not os.path.exists(path):
        print(f"Error: Path {path} not found.")
        return

    context = AuditContext(path)
    modules = [Architect(), QualityCtrl(), TestScout(), SecOps(), Scribe(), Synthesizer()]

    print(f"--- Starting Nano-CLI Audit on {path} ---")
    for module in modules:
        print(f"Phase: {module.__class__.__name__}...")
        module.audit(context)

    report = {"meta": context.meta, "phases": context.phases, "score": context.score}

    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"--- Audit Complete. Report saved to {output_file} ---")
    print(f"Overall Score: {context.score['overall']} ({context.score['grade']})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Nano-CLI Repo Auditor")
    parser.add_argument_group("Target").add_argument("--path", required=True, help="Local path to repository")
    parser.add_argument_group("Output").add_argument("--output", default="audit_report.json", help="Output JSON file")

    args = parser.parse_args()
    run_audit(args.path, args.output)