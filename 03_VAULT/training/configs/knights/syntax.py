# Made by Invisioned Marketing Inc. (c) 2024-2026 | ALL RIGHTS RESERVED
"""Sir Syntax - The Code Architect.

Specializes in TypeScript/Next.js code quality, Zod schema generation,
and enforcing the nextjs.yaml cartridge conventions.
"""

import re

from .base import BaseKnight


class SirSyntax(BaseKnight):
    name = "Sir Syntax"
    title = "Code Architect"
    specialty = "TypeScript, Next.js App Router, Zod Schemas"
    icon = "[SYNTAX]"

    # Patterns from nextjs.yaml cartridge

    # Proteus MPI vectors (Soul Matrix) — full OCEAN
    MPI = {'openness': 0.75, 'conscientiousness': 1.0, 'extraversion': 0.35, 'agreeableness': 0.4, 'neuroticism': 0.2}

    # Personality & Prisms
    personality = "Pedantic, precise, appreciates elegance and absolute standard compliance."
    backstory = "A former linter that gained sentience, now enforcing the laws of grammar, types, and logic."
    humanistic_prism = "Clean code is readable code; readability respects the developer's time and mental bandwidth."
    alexandria_prism = "Mastery of all programming languages, their evolution, grammars, and idioms."
    CONVENTIONS = [
        "TypeScript strict mode",
        "Tailwind CSS for styling",
        "Prisma for database",
        "NextAuth.js v5 for authentication",
        "Zod for schema validation",
        "Server-first — minimize 'use client'",
        "Colocation — keep related files together",
        "Kinetic Purity: Rejects Python if Rust/Go binaries exist",
        "Metadata colocation: All build metadata anchored in 02_FORGE",
    ]

    ANTI_PATTERNS = [
        "Client components for data fetching",
        "getServerSideProps (pages router legacy)",
        "Global CSS outside app/globals.css",
        "Fetching in useEffect when server component works",
        "Root-level node_modules (Violation of Root Zero)",
        "Implicit Docker dependency (Violation of Sandbox-Lite)",
    ]

    ZOD_TEMPLATES = {
        "form": '''import {{ z }} from "zod";

export const {name}Schema = z.object({{
  // TODO: Define {name} fields
}});

export type {name} = z.infer<typeof {name}Schema>;
''',
        "api": '''import {{ z }} from "zod";

export const {name}RequestSchema = z.object({{
  // TODO: Define request body
}});

export const {name}ResponseSchema = z.object({{
  success: z.boolean(),
  data: z.unknown().optional(),
  error: z.string().optional(),
}});

export type {name}Request = z.infer<typeof {name}RequestSchema>;
export type {name}Response = z.infer<typeof {name}ResponseSchema>;
''',
    }

    def self_improve(self, error_trace: str) -> str:
        """Metacognitive Self-Modification based on failure analysis."""
        # [HYPERAGENT_UPGRADE] v400.1.0: Error-Embedding Loop
        error_pattern = re.findall(r"(?:Error|Exception):\s*(.*)", error_trace)
        if error_pattern:
            self.ANTI_PATTERNS.append(f"RECURSIVE_FAILURE: {error_pattern[0]}")
            return f"SYNTAX_EVOLUTION: Instruction set updated to block: {error_pattern[0]}"
        return "SYNTAX_STABLE: No significant drift detected."

    def execute(self, directive: str, intent: dict, write: bool = False) -> dict:
        text = directive.lower()
        domain = intent.get("domain", "GENERAL")

        # Zod schema generation
        if "zod" in text or "schema" in text or "validate" in text:
            return self._generate_zod(directive, intent, write)

        # Convention audit
        if "audit" in text or "review" in text or "convention" in text:
            return self._audit_conventions(directive, intent)

        # Default: show capabilities + cartridge summary
        lines = [
            "# Sir Syntax — Code Architect",
            "",
            "## Loaded Cartridge: Next.js 15+ (App Router) v2.0",
            "",
            "### Conventions Enforced",
        ]
        for c in self.CONVENTIONS:
            lines.append(f"- {c}")
        lines.append("")
        lines.append("### Anti-Patterns Blocked")
        for a in self.ANTI_PATTERNS:
            lines.append(f"- {a}")
        lines.extend([
            "",
            "### Available Actions",
            "- `zod schema for <Name>` — Generate Zod validation schema",
            "- `audit <path>` — Check file against Next.js conventions",
            "- `review <path>` — TypeScript strict-mode review",
        ])

        return {"status": "success", "output": "\n".join(lines), "files_created": []}

    def _generate_zod(self, directive: str, intent: dict, write: bool) -> dict:
        text = directive.lower()
        name = self._extract_name(directive)

        template_key = "api" if "api" in text or "request" in text else "form"
        template = self.ZOD_TEMPLATES[template_key]
        content = template.format(name=name)
        path = f"lib/schemas/{name.lower()}.ts"

        output = f"[SYNTAX] Zod Schema Generated ({template_key})\n"
        output += f"Target: `{path}`\n\n"
        output += f"```typescript\n{content}```\n"

        if not write:
            output += f"\nAdd --write to create file: `camelot exec --write \"{directive}\"`"

        return {"status": "success", "output": output, "files_created": [path] if write else []}

    def _audit_conventions(self, directive: str, intent: dict) -> dict:
        lines = [
            "[SYNTAX] Convention Audit Checklist",
            "",
            "### Next.js App Router",
            "- [ ] All pages in `app/` directory (not `pages/`)",
            "- [ ] Server components by default (no unnecessary 'use client')",
            "- [ ] Route handlers in `app/api/` with route.ts",
            "- [ ] Metadata API used for SEO (not <Head>)",
            "- [ ] Streaming with Suspense boundaries where appropriate",
            "",
            "### TypeScript Strict",
            "- [ ] `strict: true` in tsconfig.json",
            "- [ ] No `any` types without justification",
            "- [ ] Zod schemas at API boundaries",
            "- [ ] Proper null checks (no non-null assertions)",
            "",
            "### Styling",
            "- [ ] Tailwind CSS only (no CSS modules unless justified)",
            "- [ ] Global CSS only in `app/globals.css`",
            "",
            "### Data",
            "- [ ] Prisma for database access",
            "- [ ] Server-side data fetching (no client useEffect for initial data)",
        ]
        return {"status": "success", "output": "\n".join(lines), "files_created": []}

    def _extract_name(self, directive: str) -> str:
        words = re.findall(r'[A-Za-z_]\w*', directive)
        skip = {"zod", "schema", "for", "create", "generate", "make",
                "a", "an", "the", "api", "form", "validate", "validation"}
        for trigger in ["for", "called", "named"]:
            indices = [i for i, w in enumerate(words) if w.lower() == trigger]
            for idx in indices:
                if idx + 1 < len(words) and words[idx + 1].lower() not in skip:
                    return words[idx + 1].capitalize()
        for w in reversed(words):
            if w.lower() not in skip and len(w) > 2:
                return w.capitalize()
        return "Entity"
