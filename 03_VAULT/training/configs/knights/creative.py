"""Lady Muse - The Creative Knight.

Specializes in design specifications, UI/UX, and creative direction.
"""

from .base import BaseKnight


class LadyMuse(BaseKnight):
    name = "Lady Muse"
    title = "Creative"
    specialty = "Design & Creative Direction"
    icon = "🎨"

    def execute(self, directive: str, intent: dict, write: bool = False) -> dict:
        topic = directive.strip()

        sections = [
            f"# Design Specification: {topic}",
            "",
            "## Design Philosophy",
            "- Clean, minimal interface",
            "- Accessibility-first (WCAG 2.1 AA)",
            "- Mobile-responsive by default",
            "",
            "## Color Palette",
            "| Role      | Value   | Usage            |",
            "|-----------|---------|------------------|",
            "| Primary   | #2563EB | Actions, links   |",
            "| Secondary | #7C3AED | Accents          |",
            "| Neutral   | #1F2937 | Text, borders    |",
            "| Success   | #059669 | Confirmations    |",
            "| Error     | #DC2626 | Errors, alerts   |",
            "",
            "## Typography",
            "- Headings: Inter (600-700 weight)",
            "- Body: Inter (400 weight)",
            "- Code: JetBrains Mono",
            "",
            "## Component Guidelines",
            "- Border radius: 8px (cards), 6px (buttons), 4px (inputs)",
            "- Spacing scale: 4px base unit",
            "- Shadow: 0 1px 3px rgba(0,0,0,0.1)",
            "",
            "## Layout",
            "- Max content width: 1280px",
            "- Grid: 12-column responsive",
            "- Breakpoints: 640px / 768px / 1024px / 1280px",
            "",
            "---",
            "*Lady Muse suggests: pair this spec with Sir Forge to generate components.*",
        ]

        output = "\n".join(sections)
        return {"status": "success", "output": output, "files_created": []}
