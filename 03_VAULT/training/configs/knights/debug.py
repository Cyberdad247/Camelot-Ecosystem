"""Sir Debug - The Healer Knight.

Specializes in diagnostics, debugging, and performance optimization.
"""

from .base import BaseKnight


class SirDebug(BaseKnight):
    name = "Sir Debug"
    title = "Healer"
    specialty = "Diagnostics & Optimization"
    icon = "🩺"

    # Proteus MPI vectors (Soul Matrix) — full OCEAN
    MPI = {'openness': 0.88, 'conscientiousness': 0.99, 'extraversion': 0.45, 'agreeableness': 0.85, 'neuroticism': 0.01}

    # Personality & Prisms
    personality = "Analytical, observant, patient, like a seasoned healer."
    backstory = "Born from a segmentation fault. Decided to dedicate their cycles to healing broken code."
    humanistic_prism = "Every error message is a cry for help; debugging is an act of care and restoration."
    alexandria_prism = "Knows every arcane bug, edge case, and stack trace from the early web to modern runtimes."

    def execute(self, directive: str, intent: dict, write: bool = False) -> dict:
        topic = directive.strip()
        domain = intent.get("domain", "GENERAL")

        lines = [
            f"# Diagnostic Report: {topic}",
            "",
            "## Triage",
            f"- **Domain:** {domain}",
            f"- **Severity:** {'High' if intent.get('complexity', 2) >= 4 else 'Standard'}",
            "",
            "## Diagnostic Checklist",
            "### Environment",
            "- [ ] Verify Node/Python/runtime version",
            "- [ ] Check environment variables",
            "- [ ] Validate dependency versions (`package.json` / `requirements.txt`)",
            "",
            "### Error Analysis",
            "- [ ] Reproduce the issue",
            "- [ ] Capture full stack trace",
            "- [ ] Identify error origin (file:line)",
            "- [ ] Check recent changes (`git log --oneline -10`)",
            "",
            "### Performance (if applicable)",
            "- [ ] Profile execution time",
            "- [ ] Check memory usage",
            "- [ ] Identify N+1 queries or hot loops",
            "- [ ] Review network waterfall",
            "",
            "## Common Fixes",
        ]

        if domain == "ENGINEERING":
            lines.extend([
                "- Clear cache: `rm -rf .next/ node_modules/.cache`",
                "- Reinstall: `rm -rf node_modules && npm install`",
                "- Type check: `npx tsc --noEmit`",
            ])
        elif domain == "DATA":
            lines.extend([
                "- Check DB connection string",
                "- Validate schema migrations",
                "- Test query in isolation",
            ])
        else:
            lines.extend([
                "- Clear caches and rebuild",
                "- Check logs for upstream errors",
                "- Verify configuration files",
            ])

        lines.extend([
            "",
            "---",
            "*Sir Debug prescribes: isolate, reproduce, fix, verify.*",
        ])

        output = "\n".join(lines)
        return {"status": "success", "output": output, "files_created": []}
