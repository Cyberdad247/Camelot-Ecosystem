#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""CI / pre-commit gate: committed generated artifacts must not drift from the
inputs that produce them.

The sibling gate `scripts/check_omnivoice_router_build.py` covers one artifact
with a structural (parse-and-compare) strategy. This script covers the rest with
two stronger, more general strategies — and it exists because an audit on
2026-09-14 found the repository shipping a *certified* artifact that was simply
false:

    HELIO_PATCH.json claimed `design_tokens_conformance.status == "PASS"` with
    an empty `violations` list, while a fresh regen from current source produced
    `"FAIL"` with three real violations in
    apps/pwa/src/components/LakishaHUD.tsx (`bg-red-400`, `text-red-400`,
    `border-amber-400/40`).

    Nothing noticed, because nothing compared. The pre-existing
    `scripts/ops/check-helio-dry.sh` ran the generator and asserted a top-level
    `.status` key that has NEVER existed in the emitted schema (the top-level
    keys are project / audit_version / design_tokens_conformance /
    security_conformance / performance_conformance). `jq -e '.status == "PASS"'`
    on a missing key is boolean `false`, so that gate could not pass for any
    input — it validated nothing while appearing to validate everything.

A "generator ran successfully" check is not a parity check. This script compares
the artifact against its regenerated form.

Two strategies, declared per target:

  * `regen` — run the generator in its dry-run/no-write mode, capture stdout,
    and compare that to the committed file. Used where a purpose-built generator
    exists (HELIO_PATCH.json).

  * `tsc`  — invoke the PROJECT'S OWN tsconfig via the local TypeScript compiler,
    emit into a temp directory, and compare against the committed artifact.
    Used for committed `*.js` build outputs whose package `main` points at them.

    The TypeScript version is pinned by the relevant lockfile, so emit is
    deterministic; only line endings are normalized before comparison. A genuine
    toolchain bump changes the emit preamble and will ask for a rebuild, which is
    the correct outcome — the committed artifact should match the committed
    toolchain.

Fail-closed: if a target's toolchain is unavailable the gate exits non-zero
rather than silently reporting success. A check that cannot run is not a pass.

The TypeScript resolution order for `tsc` targets is: the project's own
`node_modules`, then the workspace root's, then whatever `CAMELOT_PARITY_TSC`
points at. CI sets that last one to an isolated TypeScript install so the gate
never has to pull the whole monorepo dependency tree just to compile three files.

Exit codes:
    0 — every target is in parity with its inputs
    1 — drift detected (one or more artifacts are stale)
    2 — a required toolchain/input was missing, so parity could not be verified

Self-test:
    --self-test exercises the comparison logic on synthetic pairs in a temp dir:
    it asserts a faithful pair is accepted and that content, line-count, and
    line-ending changes are each classified correctly. It needs no node, no tsc,
    and no network.
"""

from __future__ import annotations

import argparse
import difflib
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXIT_OK = 0
EXIT_DRIFT = 1
EXIT_CANNOT_VERIFY = 2


@dataclass(frozen=True)
class Target:
    """One committed artifact plus the recipe that regenerates it."""

    key: str
    strategy: str  # "regen" | "tsc"
    artifact: Path
    regen_hint: str
    # strategy == "regen"
    command: tuple[str, ...] = ()
    env: dict[str, str] = field(default_factory=dict)
    # strategy == "tsc"
    project_dir: Path | None = None
    emitted_rel: str = ""


TARGETS: tuple[Target, ...] = (
    Target(
        key="helio-patch",
        strategy="regen",
        artifact=ROOT / "HELIO_PATCH.json",
        command=("node", "scripts/regen-helio-patch.mjs"),
        env={"HELIO_DRY_RUN": "1"},
        regen_hint="HELIO_DRY_RUN=1 node scripts/regen-helio-patch.mjs > HELIO_PATCH.json",
    ),
    Target(
        key="edge-router",
        strategy="tsc",
        artifact=ROOT / "02_FORGE/KINETIC_ARMORY/edge-router/edge-router.js",
        project_dir=ROOT / "02_FORGE/KINETIC_ARMORY/edge-router",
        emitted_rel="edge-router.js",
        regen_hint="cd 02_FORGE/KINETIC_ARMORY/edge-router && npm run build",
    ),
    Target(
        key="vscode-extension",
        strategy="tsc",
        artifact=ROOT / "extensions/camelot-vscode/out/extension.js",
        project_dir=ROOT / "extensions/camelot-vscode",
        emitted_rel="extension.js",
        regen_hint="cd extensions/camelot-vscode && npm run build",
    ),
)


def normalize(text: str) -> str:
    """Make emit comparison toolchain-agnostic without hiding real changes.

    Only the two differences that are not authored content are removed: a UTF-8
    BOM (tsc writes one on some platforms) and line endings (Windows checkouts
    hold CRLF while a POSIX emit produces LF). Trailing whitespace is stripped so
    an editor's whitespace trimming cannot masquerade as drift.
    """
    text = text.lstrip("\ufeff")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip() for line in text.split("\n")).rstrip("\n") + "\n"


def diff_summary(expected: str, actual: str, limit: int = 12) -> list[str]:
    """First N differing lines, labelled with which side is which."""
    expected_n = normalize(expected).splitlines()
    actual_n = normalize(actual).splitlines()
    if expected_n == actual_n:
        return []
    out: list[str] = []
    for line in difflib.unified_diff(
        expected_n, actual_n, fromfile="regenerated", tofile="committed", lineterm="", n=0
    ):
        if line.startswith(("---", "+++")):
            continue
        out.append(line)
        if len(out) >= limit:
            out.append("  ... (truncated)")
            break
    return out


def find_tsc(project_dir: Path) -> Path | None:
    """Prefer the project's own compiler, then the workspace root, then the
    explicitly configured one."""
    candidates = [
        project_dir / "node_modules" / "typescript" / "bin" / "tsc",
        ROOT / "node_modules" / "typescript" / "bin" / "tsc",
    ]
    override = os.environ.get("CAMELOT_PARITY_TSC")
    if override:
        candidates.append(Path(override) if Path(override).is_absolute() else ROOT / override)
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def regenerate(target: Target) -> tuple[str | None, str | None]:
    """Return (regenerated_text, error). Exactly one of the two is non-None."""
    if target.strategy == "regen":
        if shutil.which(target.command[0]) is None:
            return None, f"'{target.command[0]}' is not on PATH"
        proc = subprocess.run(
            list(target.command),
            cwd=ROOT,
            env={**os.environ, **target.env},
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            return None, f"generator exited {proc.returncode}: {proc.stderr.strip()[:400]}"
        if not proc.stdout.strip():
            return None, "generator produced no stdout (does it support dry-run?)"
        return proc.stdout, None

    if target.strategy == "tsc":
        assert target.project_dir is not None
        tsc = find_tsc(target.project_dir)
        if tsc is None:
            return None, (
                f"no TypeScript compiler found for {target.project_dir.relative_to(ROOT)} "
                "(run `npm ci`)"
            )
        if shutil.which("node") is None:
            return None, "'node' is not on PATH"
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                ["node", str(tsc), "-p", "tsconfig.json", "--outDir", tmp],
                cwd=target.project_dir,
                capture_output=True,
                text=True,
            )
            emitted = Path(tmp) / target.emitted_rel
            # tsc can exit non-zero on type errors yet still emit; only treat a
            # missing emit as a failure to verify.
            if not emitted.is_file():
                detail = (proc.stdout + proc.stderr).strip()[:400]
                return None, f"tsc emitted no {target.emitted_rel} (exit {proc.returncode}): {detail}"
            return emitted.read_text(encoding="utf-8", errors="replace"), None

    return None, f"unknown strategy {target.strategy!r}"


def check(target: Target) -> tuple[bool, list[str], str | None]:
    """Return (ok, findings, cannot_verify_reason)."""
    if not target.artifact.is_file():
        return False, [], f"committed artifact not found: {target.artifact.relative_to(ROOT)}"

    committed = target.artifact.read_text(encoding="utf-8", errors="replace")
    fresh, error = regenerate(target)
    if fresh is None:
        return False, [], error

    findings = diff_summary(fresh, committed)
    return (not findings), findings, None


def _run_case(name: str, expected: str, actual: str, expect_clean: bool) -> bool:
    findings = diff_summary(expected, actual)
    ok = (not findings) if expect_clean else bool(findings)
    print(f"  [{'OK  ' if ok else 'FAIL'}] {name}")
    return ok


def self_test() -> int:
    print("check_generated_artifact_parity --self-test")
    base = '{\n  "a": "PASS",\n  "b": [1, 2]\n}\n'
    results = [
        _run_case("faithful pair is accepted", base, base, True),
        _run_case(
            "line-ending-only difference is not drift",
            "line one\nline two\n",
            "line one\r\nline two\r\n",
            True,
        ),
        _run_case(
            "BOM-only difference is not drift",
            '{"a": 1}\n',
            '\ufeff{"a": 1}\n',
            True,
        ),
        _run_case(
            "trailing-whitespace difference is not drift",
            '{"a": 1}\n',
            '{"a": 1}   \n',
            True,
        ),
        _run_case(
            "changed value is drift",
            '{"status": "PASS", "violations": []}\n',
            '{"status": "FAIL", "violations": [{"line": 18}]}\n',
            False,
        ),
        _run_case(
            "extra regenerated line is drift",
            '{\n  "a": 1,\n  "b": 2\n}\n',
            '{\n  "a": 1\n}\n',
            False,
        ),
        _run_case(
            "empty committed artifact is drift",
            '{\n  "a": 1\n}\n',
            "\n",
            False,
        ),
    ]
    with tempfile.TemporaryDirectory() as tmp:
        probe = Path(tmp) / "probe.txt"
        probe.write_text("ok\n", encoding="utf-8")
        print(f"  [OK  ] temp dir writable ({probe.parent.name})")

    if all(results):
        print("self-test PASSED")
        return EXIT_OK
    print("self-test FAILED")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--target",
        action="append",
        default=None,
        help="Limit the run to the named target(s); default is all.",
    )
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    targets = TARGETS
    if args.target:
        wanted = set(args.target)
        targets = tuple(t for t in TARGETS if t.key in wanted)
        unknown = wanted - {t.key for t in TARGETS}
        if unknown:
            print(f"[FAIL] unknown target(s): {', '.join(sorted(unknown))}")
            print(f"       known: {', '.join(t.key for t in TARGETS)}")
            return EXIT_CANNOT_VERIFY

    drifted: list[str] = []
    unverifiable: list[tuple[str, str]] = []

    for target in targets:
        ok, findings, error = check(target)
        rel = target.artifact.relative_to(ROOT).as_posix()
        if error is not None:
            unverifiable.append((target.key, error))
            print(f"[SKIP] {target.key}: cannot verify — {error}")
            continue
        if ok:
            print(f"[OK] {target.key}: {rel} matches its regenerated form")
            continue
        drifted.append(target.key)
        print(f"[DRIFT] {target.key}: {rel} is stale relative to its inputs")
        for finding in findings:
            print(f"        {finding}")
        print(f"        regenerate: {target.regen_hint}")

    if drifted:
        print("")
        print(f"::error ::{len(drifted)} generated artifact(s) drifted from their inputs: "
              f"{', '.join(drifted)}")
    if unverifiable:
        print("")
        print("::error ::could not verify: " + ", ".join(k for k, _ in unverifiable))

    if drifted or unverifiable:
        return EXIT_DRIFT
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
