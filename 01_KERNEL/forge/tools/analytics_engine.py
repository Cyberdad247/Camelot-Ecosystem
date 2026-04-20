# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import json
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

# 🛡️ CONFIGURATION
LOG_DIR = Path(r"C:\Users\vizio\CAMELOT_OS\99_HISTORY\morgana_logs")
OUTPUT_REPORT = Path(r"C:\Users\vizio\CAMELOT_OS\99_HISTORY\analytics_report.md")


def load_logs():
    """Generates a stream of log objects from all JSONL files."""
    events = []
    for log_file in LOG_DIR.glob("*.jsonl"):
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return events


def generate_analytics(events):
    if not events:
        return "No events found."

    total_events = len(events)
    actors = Counter(e.get("actor", "UNKNOWN") for e in events)
    actions = Counter(e.get("action", "UNKNOWN") for e in events)
    statuses = Counter(e.get("status", "UNKNOWN") for e in events)

    # Calculate Velocity (Events in last hour)
    now = datetime.now()
    one_hour_ago = now - timedelta(hours=1)
    recent_events = [e for e in events if datetime.fromisoformat(e["timestamp"]) > one_hour_ago]
    velocity = len(recent_events)

    # Stability Score
    failures = statuses.get("FAILURE", 0)
    stability = ((total_events - failures) / total_events) * 100 if total_events > 0 else 100

    report = f"""# 📊 MORGANA ANALYTICS REPORT
**Generated:** {now.isoformat()}

## 🚀 KEY METRICS
- **Velocity (Last Hour):** {velocity} events/hr
- **Stability Score:** {stability:.2f}%
- **Total Lifetime Events:** {total_events}

## 🎭 ACTOR ACTIVITY
"""
    for actor, count in actors.most_common():
        report += f"- **{actor}:** {count}\n"

    report += "\n## ⚡ ACTION FREQUENCY\n"
    for action, count in actions.most_common():
        report += f"- `{action}`: {count}\n"

    report += "\n## 🛑 HEALTH STATUS\n"
    report += f"- **Success:** {statuses.get('SUCCESS', 0)}\n"
    report += f"- **Failures:** {statuses.get('FAILURE', 0)}\n"

    if failures > 0:
        report += "\n### ⚠️ RECENT FAILURES\n"
        failed_events = [e for e in events if e.get("status") == "FAILURE"][-5:]
        for f in failed_events:
            report += f"- [{f['timestamp']}] **{f['actor']}**: {f['context']}\n"

    return report


if __name__ == "__main__":
    print("🧮 [MORGANA] Crunching numbers...")
    data = load_logs()
    report_content = generate_analytics(data)

    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"✅ [ANALYTICS] Report forged: {OUTPUT_REPORT}")
    print(report_content)