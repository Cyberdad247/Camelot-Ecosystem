# Made by Invisioned Marketing Inc. (c) 2024-2026 | ALL RIGHTS RESERVED
"""Baron Vaelen - The Iron Industrialist v2.0.

Specializes in infrastructure hardening, delivery velocity, CI/CD pipeline
design, containerization, and deployment automation.
"""

import re
from .base import BaseKnight


class BaronVaelen(BaseKnight):
    name = "Baron Vaelen"
    title = "Iron Industrialist"
    specialty = "Infrastructure Hardening & Delivery Velocity"
    icon = "[VAELEN]"

    DOCKERFILE_TEMPLATE = '''# ── Stage 1: Build ──────────────────────────────────────────
FROM {base_image} AS builder
WORKDIR /app
{install_deps}
{build_cmd}

# ── Stage 2: Runtime ───────────────────────────────────────
FROM {runtime_image} AS runtime
WORKDIR /app
{copy_artifacts}
{expose}
{entrypoint}
'''

    GITHUB_ACTIONS_TEMPLATE = '''name: {name} CI/CD
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup {runtime}
        uses: {setup_action}
        with:
          {setup_config}

      - name: Install dependencies
        run: {install_cmd}

      - name: Lint
        run: {lint_cmd}

      - name: Test
        run: {test_cmd}

      - name: Build
        run: {build_cmd}
'''

    STACK_CONFIGS = {
        "nextjs": {
            "base_image": "node:20-alpine",
            "runtime_image": "node:20-alpine",
            "install_deps": "COPY package.json pnpm-lock.yaml ./\nRUN corepack enable && pnpm install --frozen-lockfile",
            "build_cmd": "COPY . .\nRUN pnpm build",
            "copy_artifacts": "COPY --from=builder /app/.next ./.next\nCOPY --from=builder /app/node_modules ./node_modules\nCOPY --from=builder /app/package.json ./",
            "expose": "EXPOSE 3000",
            "entrypoint": 'CMD ["pnpm", "start"]',
            "runtime": "Node.js 20",
            "setup_action": "actions/setup-node@v4",
            "setup_config": "node-version: 20\ncache: pnpm",
            "install_cmd": "corepack enable && pnpm install --frozen-lockfile",
            "lint_cmd": "pnpm lint",
            "test_cmd": "pnpm test",
            "ci_build_cmd": "pnpm build",
        },
        "python": {
            "base_image": "python:3.12-slim",
            "runtime_image": "python:3.12-slim",
            "install_deps": "COPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt",
            "build_cmd": "COPY . .",
            "copy_artifacts": "COPY --from=builder /app /app\nCOPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12",
            "expose": "EXPOSE 8000",
            "entrypoint": 'CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]',
            "runtime": "Python 3.12",
            "setup_action": "actions/setup-python@v5",
            "setup_config": "python-version: '3.12'",
            "install_cmd": "pip install -r requirements.txt -r requirements-dev.txt",
            "lint_cmd": "ruff check .",
            "test_cmd": "pytest -x --tb=short",
            "ci_build_cmd": "echo 'No build step for Python API'",
        },
        "rust": {
            "base_image": "rust:1.80-slim",
            "runtime_image": "debian:bookworm-slim",
            "install_deps": "COPY Cargo.toml Cargo.lock ./\nRUN mkdir src && echo 'fn main(){}' > src/main.rs && cargo build --release && rm -rf src",
            "build_cmd": "COPY src ./src\nRUN cargo build --release",
            "copy_artifacts": "COPY --from=builder /app/target/release/{name} /usr/local/bin/",
            "expose": "EXPOSE 3001",
            "entrypoint": 'CMD ["{name}"]',
            "runtime": "Rust 1.80",
            "setup_action": "dtolnay/rust-toolchain@stable",
            "setup_config": "toolchain: stable",
            "install_cmd": "cargo fetch",
            "lint_cmd": "cargo clippy -- -D warnings",
            "test_cmd": "cargo test",
            "ci_build_cmd": "cargo build --release",
        },
    }

    def execute(self, directive: str, intent: dict, write: bool = False) -> dict:
        text = directive.lower()

        if "dockerfile" in text or "docker" in text or "container" in text:
            return self._generate_dockerfile(directive, intent, write)

        if "ci" in text or "github action" in text or "pipeline" in text or "workflow" in text:
            return self._generate_ci(directive, intent, write)

        if "harden" in text or "security" in text or "checklist" in text:
            return self._hardening_checklist()

        lines = [
            "# Baron Vaelen — Iron Industrialist v2.0",
            "",
            "## Domains",
            "- **Containerization**: Multi-stage Dockerfiles (Node, Python, Rust)",
            "- **CI/CD**: GitHub Actions pipelines with lint/test/build",
            "- **Hardening**: Production security checklist",
            "- **Delivery Velocity**: Build caching, parallel jobs, artifact management",
            "",
            "## Available Actions",
            "- `dockerfile for <stack>` — Generate multi-stage Dockerfile (nextjs/python/rust)",
            "- `ci pipeline for <stack>` — Generate GitHub Actions workflow",
            "- `hardening checklist` — Production infrastructure security audit",
        ]
        return {"status": "success", "output": "\n".join(lines), "files_created": []}

    def _detect_stack(self, text: str) -> str:
        if any(k in text for k in ("rust", "cargo", "axum", "kinetic")):
            return "rust"
        if any(k in text for k in ("python", "fastapi", "uvicorn", "flask")):
            return "python"
        return "nextjs"

    def _generate_dockerfile(self, directive: str, intent: dict, write: bool) -> dict:
        stack = self._detect_stack(directive.lower())
        cfg = self.STACK_CONFIGS[stack]
        name = self._extract_name(directive) or stack

        content = self.DOCKERFILE_TEMPLATE.format(
            name=name.lower(), **{k: cfg[k] for k in
            ("base_image", "runtime_image", "install_deps", "build_cmd",
             "copy_artifacts", "expose", "entrypoint")}
        )
        # Replace {name} in copy_artifacts for Rust
        content = content.replace("{name}", name.lower())
        path = "Dockerfile"

        output = f"[VAELEN] Dockerfile ({stack})\n"
        output += f"Target: `{path}`\n\n```dockerfile\n{content}```\n"
        if not write:
            output += "\nAdd --write to create file on disk."
        return {"status": "success", "output": output, "files_created": [path] if write else []}

    def _generate_ci(self, directive: str, intent: dict, write: bool) -> dict:
        stack = self._detect_stack(directive.lower())
        cfg = self.STACK_CONFIGS[stack]
        name = self._extract_name(directive) or "Project"

        content = self.GITHUB_ACTIONS_TEMPLATE.format(
            name=name,
            runtime=cfg["runtime"],
            setup_action=cfg["setup_action"],
            setup_config=cfg["setup_config"],
            install_cmd=cfg["install_cmd"],
            lint_cmd=cfg["lint_cmd"],
            test_cmd=cfg["test_cmd"],
            build_cmd=cfg["ci_build_cmd"],
        )
        path = f".github/workflows/{name.lower().replace(' ', '-')}-ci.yml"

        output = f"[VAELEN] CI/CD Pipeline ({stack})\n"
        output += f"Target: `{path}`\n\n```yaml\n{content}```\n"
        if not write:
            output += "\nAdd --write to create file on disk."
        return {"status": "success", "output": output, "files_created": [path] if write else []}

    def _hardening_checklist(self) -> dict:
        lines = [
            "[VAELEN] Production Hardening Checklist",
            "",
            "### Secrets Management",
            "- [ ] No secrets in source code or env files committed to git",
            "- [ ] Vault or cloud secret manager for production credentials",
            "- [ ] API keys rotated on schedule",
            "",
            "### Container Security",
            "- [ ] Non-root user in Dockerfile",
            "- [ ] Multi-stage build (no build tools in runtime image)",
            "- [ ] Pinned base image tags (no :latest in production)",
            "- [ ] Read-only filesystem where possible",
            "",
            "### Network",
            "- [ ] TLS everywhere (no plain HTTP in production)",
            "- [ ] Rate limiting on public endpoints",
            "- [ ] CORS configured to specific origins",
            "- [ ] Security headers (CSP, HSTS, X-Frame-Options)",
            "",
            "### Monitoring",
            "- [ ] Health check endpoint (/healthz)",
            "- [ ] Structured logging (JSON format)",
            "- [ ] Error tracking (Sentry or equivalent)",
            "- [ ] Uptime monitoring with alerting",
            "",
            "### CI/CD",
            "- [ ] Branch protection on main (require PR review)",
            "- [ ] Automated tests gate deployment",
            "- [ ] Dependency vulnerability scanning (Dependabot/Snyk)",
            "- [ ] No force-push to production branches",
        ]
        return {"status": "success", "output": "\n".join(lines), "files_created": []}

    def _extract_name(self, directive: str) -> str:
        words = re.findall(r'[A-Za-z_]\w*', directive)
        skip = {"dockerfile", "docker", "container", "ci", "github", "action",
                "pipeline", "workflow", "for", "create", "generate", "make",
                "a", "an", "the", "new", "harden", "checklist"}
        for trigger in ["for", "called", "named"]:
            indices = [i for i, w in enumerate(words) if w.lower() == trigger]
            for idx in indices:
                if idx + 1 < len(words) and words[idx + 1].lower() not in skip:
                    return words[idx + 1]
        for w in reversed(words):
            if w.lower() not in skip and len(w) > 2:
                return w
        return None
