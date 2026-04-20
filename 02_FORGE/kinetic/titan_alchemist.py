# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
⚗️ TITAN ALCHEMIST (Kinetic Layer)
Purpose: Scans for 'Lead' (ineificiencies) to transmute into 'Gold' (Optimization).
Act as: Sir Alchemist.
"""
import os
import ast
import argparse

def analyze_file(file_path):
    issues = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.splitlines()
            
        tree = ast.parse(content)
        
        # Check 1: Large Files
        if len(lines) > 300:
            issues.append(f"⚠️  Bloat Detected: {len(lines)} lines (Limit: 300)")
            
        # Check 2: Sync IO in Async context (Naive check)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if hasattr(node.func, 'id') and node.func.id in ['open', 'sleep']:
                    issues.append(f"⚠️  Potential Blocking I/O: `{node.func.id}` usage.")
                    
    except Exception as e:
        issues.append(f"❌ Analysis Failed: {e}")
        
    return issues

def scan_directory(target_dir):
    report = []
    report.append("# ⚗️ Transmutation Report")
    report.append(f"Target: `{target_dir}`\n")
    
    print(f"⚗️  Sir Alchemist scanning {target_dir}...")
    
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                issues = analyze_file(path)
                if issues:
                    report.append(f"### {file}")
                    for issue in issues:
                        report.append(f"- {issue}")
                    report.append("")
                    
    return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Titan Alchemist: Code Optimizer")
    parser.add_argument("--target", default=".", help="Directory to scan")
    args = parser.parse_args()
    
    report_content = scan_directory(args.target)
    
    with open("TRANSMUTATION_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print("✨ Transmutation Scan Complete. See TRANSMUTATION_REPORT.md")

if __name__ == "__main__":
    main()