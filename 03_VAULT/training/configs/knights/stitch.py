# Made by Invisioned Marketing Inc. (c) 2024-2026 | ALL RIGHTS RESERVED
"""Sir Stitch - The Interface Architect.

Specializes in transforming intent into functional UI/UX: React components,
layout systems, accessibility, and design system consistency.
"""

import re
from .base import BaseKnight


class SirStitch(BaseKnight):
    name = "Sir Stitch"
    title = "Interface Architect"
    specialty = "UI/UX Component Design & Layout Systems"
    icon = "[STITCH]"

    # Proteus MPI vectors (Soul Matrix) — full OCEAN
    MPI = {'openness': 0.95, 'conscientiousness': 0.85, 'extraversion': 0.75, 'agreeableness': 0.9, 'neuroticism': 0.15}

    # Personality & Prisms
    personality = "Empathetic, artistic, detail-oriented, focuses on the seams between systems."
    backstory = "Started as a CSS preprocessor, learned the psychology of colors and spacing to build perfect interfaces."
    humanistic_prism = "The interface is the only part of the system the user touches; it must be perfect and intuitive."
    alexandria_prism = "An archive of design systems, human-computer interaction studies, typography, and accessibility."

    COMPONENT_TEMPLATE = '''"use client";

import {{ useState }} from "react";
import {{ cn }} from "@/lib/utils";

interface {name}Props {{
  className?: string;
  children?: React.ReactNode;
}}

export function {name}({{ className, children }}: {name}Props) {{
  return (
    <div
      className={{cn(
        "relative flex flex-col gap-4 rounded-lg border bg-card p-6 shadow-sm",
        className
      )}}
      role="region"
      aria-label="{name}"
    >
      {{children}}
    </div>
  );
}}
'''

    PAGE_TEMPLATE = '''import {{ Suspense }} from "react";
import {{ Metadata }} from "next";

export const metadata: Metadata = {{
  title: "{name}",
  description: "{name} page",
}};

function {name}Loading() {{
  return (
    <div className="flex min-h-[400px] items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
    </div>
  );
}}

async function {name}Content() {{
  // TODO: Server-side data fetching
  return (
    <main className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold tracking-tight">{name}</h1>
      {{/* TODO: Implement page content */}}
    </main>
  );
}}

export default function {name}Page() {{
  return (
    <Suspense fallback={{<{name}Loading />}}>
      <{name}Content />
    </Suspense>
  );
}}
'''

    LAYOUT_TEMPLATE = '''interface {name}LayoutProps {{
  children: React.ReactNode;
  sidebar?: React.ReactNode;
}}

export default function {name}Layout({{ children, sidebar }}: {name}LayoutProps) {{
  return (
    <div className="flex min-h-screen">
      {{sidebar && (
        <aside className="hidden w-64 shrink-0 border-r bg-muted/40 lg:block">
          {{sidebar}}
        </aside>
      )}}
      <div className="flex-1">{{children}}</div>
    </div>
  );
}}
'''

    def execute(self, directive: str, intent: dict, write: bool = False) -> dict:
        text = directive.lower()

        if "page" in text:
            return self._generate(directive, "page", self.PAGE_TEMPLATE, "app/{name_lower}/page.tsx", write)

        if "layout" in text:
            return self._generate(directive, "layout", self.LAYOUT_TEMPLATE, "app/{name_lower}/layout.tsx", write)

        if "component" in text or "ui" in text:
            return self._generate(directive, "component", self.COMPONENT_TEMPLATE, "components/ui/{name_lower}.tsx", write)

        # Accessibility audit mode
        if "a11y" in text or "accessibility" in text or "audit" in text:
            return self._a11y_checklist()

        lines = [
            "# Sir Stitch — Interface Architect",
            "",
            "## Capabilities",
            "- **Components**: Accessible React components with Tailwind + cn()",
            "- **Pages**: Next.js App Router pages with Suspense boundaries",
            "- **Layouts**: Responsive layout shells with sidebar slots",
            "- **A11y Audit**: WCAG 2.1 AA checklist generation",
            "",
            "## Available Actions",
            "- `component for <Name>` — Generate accessible UI component",
            "- `page for <Name>` — Generate Next.js server page with Suspense",
            "- `layout for <Name>` — Generate layout with sidebar slot",
            "- `a11y audit` — Generate accessibility checklist",
        ]
        return {"status": "success", "output": "\n".join(lines), "files_created": []}

    def _generate(self, directive: str, kind: str, template: str, path_pattern: str, write: bool) -> dict:
        name = self._extract_name(directive)
        content = template.format(name=name, name_lower=name.lower())
        path = path_pattern.format(name=name, name_lower=name.lower())

        output = f"[STITCH] {kind.title()}: {name}\n"
        output += f"Target: `{path}`\n\n```tsx\n{content}```\n"
        if not write:
            output += f"\nAdd --write to create file on disk."
        return {"status": "success", "output": output, "files_created": [path] if write else []}

    def _a11y_checklist(self) -> dict:
        lines = [
            "[STITCH] Accessibility Audit — WCAG 2.1 AA",
            "",
            "### Perceivable",
            "- [ ] All images have descriptive alt text",
            "- [ ] Color is not the sole means of conveying information",
            "- [ ] Text contrast ratio >= 4.5:1 (3:1 for large text)",
            "- [ ] Content reflows at 320px without horizontal scroll",
            "",
            "### Operable",
            "- [ ] All interactive elements keyboard-accessible",
            "- [ ] Focus indicators visible on all focusable elements",
            "- [ ] No keyboard traps",
            "- [ ] Skip-to-content link present",
            "",
            "### Understandable",
            "- [ ] Language attribute set on <html>",
            "- [ ] Form inputs have associated <label> elements",
            "- [ ] Error messages are descriptive and linked to fields",
            "",
            "### Robust",
            "- [ ] Valid HTML (no duplicate IDs)",
            "- [ ] ARIA roles/attributes used correctly",
            "- [ ] Components work with screen readers (test with NVDA/VoiceOver)",
        ]
        return {"status": "success", "output": "\n".join(lines), "files_created": []}

    def _extract_name(self, directive: str) -> str:
        words = re.findall(r'[A-Za-z_]\w*', directive)
        skip = {"component", "page", "layout", "ui", "for", "create",
                "generate", "make", "a", "an", "the", "new", "stitch"}
        for trigger in ["for", "called", "named"]:
            indices = [i for i, w in enumerate(words) if w.lower() == trigger]
            for idx in indices:
                if idx + 1 < len(words) and words[idx + 1].lower() not in skip:
                    return words[idx + 1].capitalize()
        for w in reversed(words):
            if w.lower() not in skip and len(w) > 2:
                return w.capitalize()
        return "Widget"
