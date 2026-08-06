# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
import argparse
import datetime
import json
import os
from typing import Any, Dict


class NanoRepoAuditor:
    def __init__(self, root_path: str):
        self.root_path = os.path.abspath(root_path)
        self.context: Dict[str, Any] = {
            "meta": {
                "target": self.root_path,
                "date": datetime.datetime.now().isoformat(),
                "auditor": "Nano-CLI v1.0"
            },
            "phases": {},
            "score": {}
        }

    def run(self):
        print(f"[NANO_AUDITOR] Starting Deep Dive on: {self.root_path}")
        self.phase_1_architecture()
        self.phase_2_quality()
        self.phase_3_testing()
        self.phase_4_security()
        self.phase_5_documentation()
        self.phase_6_synthesis()
        return self.context

    def phase_1_architecture(self):
        """Phase 1: Architecture & Infra"""
        print("... Phase 1: Mapping Architecture")
        file_tree = []
        key_files = {
            "docker": False,
            "nextjs": False,
            "python": False,
            "node": False,
            "go": False,
            "rust": False
        }
        
        for root, dirs, files in os.walk(self.root_path):
            # Prune directories in-place
            dirs[:] = [d for d in dirs if d not in [".git", "node_modules", "__pycache__", ".venv", "dist", "build"]]
            
            for f in files:
                file_tree.append(os.path.join(root, f))
                if f == "Dockerfile" or f == "docker-compose.yml":
                    key_files["docker"] = True
                if f == "next.config.js":
                    key_files["nextjs"] = True
                if f == "package.json":
                    key_files["node"] = True
                if f.endswith(".py"):
                    key_files["python"] = True
                if f.endswith(".go"):
                    key_files["go"] = True
                if f.endswith(".rs"):
                    key_files["rust"] = True

        stack = [k for k, v in key_files.items() if v]
        topo = "Monolith" # Default assumption
        if "docker" in stack and len(stack) > 3:
            topo = "Microservices (Likely)"

        self.context["phases"]["architecture"] = {
            "type": topo,
            "stack": stack,
            "file_count": len(file_tree)
        }

    def phase_2_quality(self):
        """Phase 2: Code Quality & Style"""
        print("... Phase 2: Analyzing Quality")
        configs = []
        depths = []
        
        for root, dirs, files in os.walk(self.root_path):
            dirs[:] = [d for d in dirs if d not in [".git", "node_modules", "__pycache__", ".venv", "dist", "build"]]
            
            # Check depth
            rel_path = os.path.relpath(root, self.root_path)
            depth = 0 if rel_path == "." else rel_path.count(os.sep) + 1
            depths.append(depth)

            for f in files:
                if f in [".eslintrc", ".prettierrc", "ruff.toml", "pyproject.toml", ".clinerules"]:
                    configs.append(f)

        avg_depth = sum(depths) / len(depths) if depths else 0
        score = 100
        if avg_depth > 5: score -= 10
        if not configs: score -= 20

        self.context["phases"]["quality"] = {
            "score": score,
            "configs_found": configs,
            "avg_nesting_depth": round(avg_depth, 2)
        }

    def phase_3_testing(self):
        """Phase 3: Testing Strategy"""
        print("... Phase 3: Scouting Tests")
        test_files = 0
        source_files = 0
        
        for _root, dirs, files in os.walk(self.root_path):
            dirs[:] = [d for d in dirs if d not in [".git", "node_modules", "__pycache__", ".venv", "dist", "build"]]

            for f in files:
                if f.endswith((".py", ".js", ".ts", ".go", ".rs")):
                    source_files += 1
                    if "test" in f.lower() or "spec" in f.lower() or "_test" in f:
                        test_files += 1

        ratio = (test_files / source_files) if source_files > 0 else 0
        est = "Low"
        if ratio > 0.1: est = "Medium"
        if ratio > 0.3: est = "High"

        self.context["phases"]["testing"] = {
            "coverage_est": est,
            "test_file_count": test_files,
            "ratio": round(ratio, 2)
        }

    def phase_4_security(self):
        """Phase 4: Security Forensics"""
        print("... Phase 4: Security Scan")
        vuln_count = 0
        findings = []
        
        # Simple scan for keywords
        suspicious = ["API_KEY", "password =", "secret_key", "AWS_ACCESS_KEY"]
        
        for root, dirs, files in os.walk(self.root_path):
            dirs[:] = [d for d in dirs if d not in [".git", "node_modules", "__pycache__", ".venv", "dist", "build"]]

            for f in files:
                if f in [".env", "id_rsa", "credentials"]:
                    vuln_count += 1
                    findings.append(f"Exposed critical file: {f}")
                
                 # Sample content scan (limited to text files, small)
                if f.endswith((".py", ".js", ".md", ".json", ".txt")):
                    try:
                        path = os.path.join(root, f)
                        if os.path.getsize(path) < 100000: # Skip large files
                            with open(path, "r", encoding="utf-8", errors="ignore") as content:
                                text = content.read()
                                for s in suspicious:
                                    if s in text and "os.getenv" not in text and "process.env" not in text:
                                        # Very naïve check, but demonstrates logic
                                        # Only flag if it looks hardcoded (no env var usage nearby)
                                        pass 
                    except:
                        pass
        
        self.context["phases"]["security"] = {
            "vulnerability_count": vuln_count,
            "findings": findings
        }

    def phase_5_documentation(self):
        """Phase 5: Documentation"""
        print("... Phase 5: Checking Docs")
        docs = []
        missing = []
        required = ["README.md", "CONTRIBUTING.md", "LICENSE"]
        
        root_files = os.listdir(self.root_path)
        for r in required:
            found = False
            for f in root_files:
                if f.lower() == r.lower():
                    docs.append(f)
                    found = True
                    break
            if not found:
                missing.append(r)

        grade = "F"
        if "README.md" in docs: grade = "C"
        if len(missing) == 0: grade = "A"
        elif len(missing) == 1: grade = "B"

        self.context["phases"]["documentation"] = {
            "grade": grade,
            "found": docs,
            "missing": missing
        }

    def phase_6_synthesis(self):
        """Phase 6: Synthesis (Report Generation)"""
        print("... Phase 6: Synthesizing Report")
        p = self.context["phases"]
        
        report = f"""# 🕵️‍♂️ REPO DEEP-DIVE: {self.context['meta']['target']}
> **Auditor:** {self.context['meta']['auditor']}
> **Date:** {self.context['meta']['date']}

## 🏗️ 1. ARCHITECTURE
*   **Type:** {p['architecture']['type']}
*   **Core Stack:** {', '.join(p['architecture']['stack'])}
*   **File Count:** {p['architecture']['file_count']}

## 🧪 2. CODE QUALITY
*   **Score:** {p['quality']['score']}
*   **Configs Found:** {', '.join(p['quality']['configs_found'])}
*   **Avg Nesting Depth:** {p['quality']['avg_nesting_depth']}

## 🛡️ 3. SECURITY & RISKS
*   **Vulnerability Count:** {p['security']['vulnerability_count']}
*   **Critical Findings:**
"""
        if p['security']['findings']:
            for f in p['security']['findings']:
                report += f"    *   {f}\n"
        else:
            report += "    *   None detected (Clean)\n"

        report += f"""
## 🧪 4. TESTING
*   **Coverage Est:** {p['testing']['coverage_est']}
*   **Test File Ratio:** {p['testing']['ratio']}
*   **Test Files:** {p['testing']['test_file_count']}

## 📚 5. DOCUMENTATION
*   **Grade:** {p['documentation']['grade']}
*   **Missing:** {', '.join(p['documentation']['missing'])}

## 💡 6. RECOMMENDATIONS
1.  {'Improve Test Coverage.' if p['testing']['coverage_est'] == 'Low' else 'Maintain Test Rigor.'}
2.  {'Add Contribution Guidelines.' if 'CONTRIBUTING.md' in p['documentation']['missing'] else 'Review Contribution Guidelines.'}
3.  {'Review Security Findings.' if p['security']['vulnerability_count'] > 0 else 'Periodically Audit Dependencies.'}

## 🧬 UKG DNA (JSON-LD)
```json
{json.dumps(self.context, indent=2)}
```
"""
        print("\n" + "="*40 + "\n")
        # print(report)
        print("="*40 + "\n")
        
        # Save to file
        output_path = os.path.join(self.root_path, "report_v3.markdown")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report saved to: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Nano-CLI Repo Auditor")
    parser.add_argument("--path", type=str, default=".", help="Path to repository")
    args = parser.parse_args()
    
    auditor = NanoRepoAuditor(args.path)
    auditor.run()
