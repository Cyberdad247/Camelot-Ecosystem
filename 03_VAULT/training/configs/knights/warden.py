"""Sir Zenith - The Warden Knight.

Specializes in security audits, vulnerability assessment, and hardening.
"""

from .base import BaseKnight


class SirZenith(BaseKnight):
    name = "Sir Zenith"
    title = "Warden"
    specialty = "Security Audits & Validation"
    icon = "🛡️"

    CHECKLIST = [
        ("Authentication", [
            "Password hashing (bcrypt/argon2)",
            "JWT token expiration and rotation",
            "Multi-factor authentication support",
            "Session management and invalidation",
        ]),
        ("Authorization", [
            "Role-based access control (RBAC)",
            "Resource-level permissions",
            "API endpoint protection",
            "Principle of least privilege",
        ]),
        ("Input Validation", [
            "SQL injection prevention (parameterized queries)",
            "XSS prevention (output encoding)",
            "CSRF token implementation",
            "File upload validation",
        ]),
        ("Data Protection", [
            "Encryption at rest (AES-256)",
            "Encryption in transit (TLS 1.3)",
            "Secrets management (no hardcoded keys)",
            "PII handling compliance",
        ]),
        ("Infrastructure", [
            "CORS configuration",
            "Rate limiting",
            "Security headers (CSP, HSTS, etc.)",
            "Dependency vulnerability scanning",
        ]),
    ]

    def execute(self, directive: str, intent: dict, write: bool = False) -> dict:
        topic = directive.strip()

        lines = [
            f"# Security Audit: {topic}",
            "",
            f"**Scope:** {intent.get('domain', 'GENERAL')}",
            f"**Risk Level:** {'HIGH' if intent.get('complexity', 2) >= 4 else 'STANDARD'}",
            "",
        ]

        for category, items in self.CHECKLIST:
            lines.append(f"## {category}")
            for item in items:
                lines.append(f"- [ ] {item}")
            lines.append("")

        lines.extend([
            "## Recommendations",
            "1. Run `npm audit` / `pip audit` for dependency vulnerabilities",
            "2. Enable security linting (eslint-plugin-security / bandit)",
            "3. Implement logging and monitoring for security events",
            "",
            "---",
            "*Sir Zenith stands watch. No vulnerability shall pass unchallenged.*",
        ])

        output = "\n".join(lines)
        return {"status": "success", "output": output, "files_created": []}
