# Camelot-OS on Omarchy — Distro Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a bootable x86_64 Camelot-OS ISO built from the Omarchy stack that installs unattended, boots a native systemd agent stack with zero Docker anywhere, and publishes a sealed release manifest to the VPS hub for Hermes to consume.

**Architecture:** One primitive replaces Docker everywhere: `systemd-nspawn`. Per-channel nspawn build roots under `/var/lib/camelot-build` replace the container builder in `omarchy-pkgs`; the same primitive hosts `mkarchiso` on the builder. x86_64-only scope deletes the foreign-architecture emulation requirement that Docker existed to satisfy. Release artifacts carry an Ed25519-sealed canonical manifest, pushed Tailscale-only to `/srv/camelot/distro/`, verified by a systemd path unit, and read by a native `hermes-agent.service`.

**Tech Stack:** Arch Linux packaging (`devtools`, `mkarchroot`, `arch-nspawn`, `makechrootpkg`, `mkarchiso`), Bash 5, Python 3.13, `cryptography` (Ed25519), `pytest`, systemd (units, slices, path units, cgroups v2), Rust/Go for hot-path binaries.

**Spec:** `docs/superpowers/specs/2026-09-15-camelot-os-omarchy-distro-design.md`

## Global Constraints

- **Zero Docker.** No `docker`, `podman`, `containerd`, `nerdctl`, or any container runtime may be required in the distro build path, the installed runtime, or the hub ingest path. `systemd-nspawn` is the only sanctioned isolation primitive for builds.
- **x86_64 only.** `PUBLISHED_ARCHES="x86_64"`. No aarch64, no QEMU emulation, no cross-architecture build roots.
- **Rule 7 holds.** 0% Python/Node in the runtime hot path. `npx` is an ephemeral bootstrap vehicle only. Native systemd, Rust, Go, WASM in the hot path.
- **No secrets in the tree.** `user_credentials.json`, `tailscale_authkey`, private signing keys, and device tokens are never committed. Public keys only.
- **Tailnet only.** Distro artifacts move over Tailscale. No public WAN fallback, no public listener on the hub, no inbound port added to the hub firewall.
- **Version floor is explicit.** Every release version is `"<upstream omarchy version>+camelot.<patch>"`, e.g. `4.0.2+camelot.1`.
- **HUMAN_GATE is never auto-approved.** Publish and hub-mutation steps require `CAMELOT_DASHBOARD_OPERATOR_TOKEN`.
- **No fabricated completion.** A task is done when its verification command prints the expected result. Build and measurement claims stay `planned` until a command output backs them.
- **Do not touch `PROVENANCE_LEDGER.md`.** The PostToolUse hook writes it.

---

## File structure

| File | Responsibility |
| --- | --- |
| `control_plane/distro/__init__.py` | Package boundary for distro tooling. |
| `control_plane/distro/docker_inventory.py` | Scans for container surfaces; classifies release-critical blockers. |
| `control_plane/distro/manifest.py` | Canonical bytes, Ed25519 seal, seal verification, key loading. |
| `control_plane/distro/release_gate.py` | Anya-gated release authorization, HITL tier enforcement. |
| `control_plane/distro/iso_build.py` | Host-capability gating and ISO build/acceptance invocation. |
| `control_plane/distro/hub_push.py` | Tailnet-only push, remote sha256 verification, receipt handling. |
| `control_plane/distro/hermes_contract.py` | Hermes-side manifest read, seal verification, fail-closed release description. |
| `05_INFRASTRUCTURE/distro/builder/provision-builder.sh` | Verifies builder capability; provisions per-channel nspawn roots. |
| `05_INFRASTRUCTURE/distro/builder/camelot-build@.service` | Creates and refreshes one channel build root. |
| `05_INFRASTRUCTURE/distro/builder/nspawn-build.sh` | Builds a PKGBUILD inside a channel root (`makechrootpkg`). |
| `05_INFRASTRUCTURE/distro/builder/sync-profile.sh` | Copies CAMELOT_OS profile sources into the `camelot-pkgs` fork. |
| `05_INFRASTRUCTURE/distro/profile/camelot-os-profile/PKGBUILD` | The node profile package: slices, tethers, bootstrap. |
| `05_INFRASTRUCTURE/distro/profile/camelot-os-profile/camelot-*.slice` | cgroups v2 memory ceilings from the spec budget table. |
| `05_INFRASTRUCTURE/distro/iso/cidata/user_configuration.json` | archinstall config for unattended install. |
| `05_INFRASTRUCTURE/distro/iso/cidata/authorized_keys.example` | Template; the real file is never committed. |
| `05_INFRASTRUCTURE/distro/iso/build-cidata.sh` | Builds the `cidata.iso` NoCloud drive. |
| `05_INFRASTRUCTURE/distro/iso/camelot-iso.env` | Pinned upstream refs and channel selection. |
| `05_INFRASTRUCTURE/distro/hub/camelot-distro-ingest.{path,service}` | Hub-side verified ingest. |
| `05_INFRASTRUCTURE/distro/hub/camelot-distro-ingest.sh` | sha256 + seal verification, atomic rename, rejection receipt. |
| `infra/systemd/hermes-agent.service` | Native Hermes unit, replacing the container path. |
| `scripts/ops/migrate-hermes-off-docker.sh` | One-way migration from the container deployment. |
| `control_plane/dispatch/omarchy_agent_matrix.py` | Modified: Hermes stub no longer shells into a container. |
| `tests/test_docker_inventory.py` | Container-surface detection. |
| `tests/test_distro_manifest.py` | Seal behaviour, including the key-mismatch discriminator. |
| `tests/test_distro_release_gate.py` | HITL tier enforcement. |
| `tests/test_distro_profile.py` | PKGBUILD and slice budget conformance. |
| `tests/test_cidata_profile.py` | Required cidata keys; secret non-commitment. |
| `tests/test_distro_iso_build.py` | Host-capability gating logic. |
| `tests/test_omarchy_agent_matrix_stub.py` | Hermes stub is container-free. |
| `tests/test_distro_hub_push.py` | Tailnet guard and remote verification. |
| `tests/test_hermes_contract.py` | Fail-closed manifest consumption. |
| `docs/operations/camelot-os-distro.md` | Build, provision, publish, recover runbook. |

All Python tests run as:

```bash
.venv/Scripts/python.exe -m pytest tests/<file>::<test> -v
```

---

## Task 1: Docker footprint inventory and hot-path guard

Establishes the factual baseline for the no-Docker claim. Without this, the
manifest's `hotpath` block would be an unchecked assertion, which is exactly the
failure mode the spec's F4 finding describes.

**Files:**
- Create: `control_plane/distro/__init__.py`
- Create: `control_plane/distro/docker_inventory.py`
- Test: `tests/test_docker_inventory.py`

**Interfaces:**
- Produces: `Finding`, `InventoryReport`, `scan_for_container_surfaces(root: Path, *, max_bytes: int = 2_000_000) -> InventoryReport`, `InventoryReport.release_path_blockers() -> list[Finding]`, `InventoryReport.to_json() -> str`, and the constants `RELEASE_CRITICAL_GLOBS` and `CONTAINER_PATTERNS`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_docker_inventory.py
from pathlib import Path

from control_plane.distro.docker_inventory import scan_for_container_surfaces


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_flags_docker_in_a_release_critical_path(tmp_path: Path) -> None:
    _write(tmp_path, "05_INFRASTRUCTURE/distro/builder/bad.sh",
           "docker run --rm archlinux pacman -Syu\n")
    report = scan_for_container_surfaces(tmp_path)
    assert len(report.release_path_blockers()) == 1
    assert report.release_path_blockers()[0].path.endswith("bad.sh")


def test_ignores_container_mention_outside_the_release_path(tmp_path: Path) -> None:
    _write(tmp_path, "docs/scratch.md", "docker is not used here\n")
    report = scan_for_container_surfaces(tmp_path)
    assert report.release_path_blockers() == []
    assert len(report.findings) == 1


def test_detects_a_dockerfile_from_instruction(tmp_path: Path) -> None:
    _write(tmp_path, "infra/systemd/Dockerfile", "FROM python:3.12-slim\n")
    report = scan_for_container_surfaces(tmp_path)
    assert any(f.pattern == r"^\s*FROM\s+\S+" for f in report.findings)


def test_skips_binary_and_vendor_paths(tmp_path: Path) -> None:
    _write(tmp_path, "node_modules/pkg/index.js", "docker podman\n")
    _write(tmp_path, "01_KERNEL/blob.png", "docker podman\n")
    report = scan_for_container_surfaces(tmp_path)
    assert report.findings == []


def test_report_serializes_sorted_and_stable(tmp_path: Path) -> None:
    _write(tmp_path, "infra/systemd/a.service", "Requires=docker.service\n")
    report = scan_for_container_surfaces(tmp_path)
    assert report.to_json() == scan_for_container_surfaces(tmp_path).to_json()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest tests/test_docker_inventory.py -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'control_plane.distro'`

- [ ] **Step 3: Write the minimal implementation**

```python
# control_plane/distro/__init__.py
# SPDX-License-Identifier: MIT
"""Camelot-OS distro build, seal, and hub-publish tooling."""
```

```python
# control_plane/distro/docker_inventory.py
# SPDX-License-Identifier: MIT
"""
Container-surface inventory for the Camelot-OS distro release path.

Rule 7 forbids a container runtime in the hot path. This module produces the
evidence for that claim instead of asserting it. Findings inside
RELEASE_CRITICAL_GLOBS block a release; findings elsewhere are reported as debt.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from fnmatch import fnmatch
from pathlib import Path
from typing import Iterable, List, Sequence

RELEASE_CRITICAL_GLOBS: Sequence[str] = (
    "05_INFRASTRUCTURE/distro/**",
    "infra/systemd/**",
    "control_plane/distro/**",
    "scripts/deploy_*vps*.sh",
    "scripts/ops/migrate-hermes-off-docker.sh",
)

CONTAINER_PATTERNS: Sequence[re.Pattern[str]] = (
    re.compile(r"\bdocker\b", re.IGNORECASE),
    re.compile(r"\bdocker-compose\b", re.IGNORECASE),
    re.compile(r"\bpodman\b", re.IGNORECASE),
    re.compile(r"\bcontainerd\b", re.IGNORECASE),
    re.compile(r"^\s*FROM\s+\S+"),
)

SKIP_DIRS = frozenset(
    {".git", "node_modules", "target", ".venv", "__pycache__", "dist", "build", ".next"}
)
SKIP_SUFFIXES = frozenset(
    {
        ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip",
        ".exe", ".dll", ".so", ".dylib", ".whl", ".iso", ".gz", ".br",
        ".zst", ".7z", ".mp4", ".woff", ".woff2",
    }
)


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    pattern: str
    excerpt: str
    release_critical: bool


@dataclass
class InventoryReport:
    root: str
    scanned_files: int = 0
    findings: List[Finding] = field(default_factory=list)

    def release_path_blockers(self) -> List[Finding]:
        """Findings that must be zero before a release may publish."""
        return [f for f in self.findings if f.release_critical]

    def to_json(self) -> str:
        return json.dumps(
            {
                "root": self.root,
                "scanned_files": self.scanned_files,
                "release_critical_blockers": [asdict(f) for f in self.release_path_blockers()],
                "all_findings": [asdict(f) for f in self.findings],
            },
            indent=2,
            sort_keys=True,
        )


def _iter_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in SKIP_SUFFIXES:
            continue
        yield path


def _is_release_critical(rel_posix: str) -> bool:
    return any(fnmatch(rel_posix, glob) for glob in RELEASE_CRITICAL_GLOBS)


def scan_for_container_surfaces(
    root: Path, *, max_bytes: int = 2_000_000
) -> InventoryReport:
    root = Path(root).resolve()
    report = InventoryReport(root=str(root))

    for path in _iter_files(root):
        try:
            if path.stat().st_size > max_bytes:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        report.scanned_files += 1
        rel = path.relative_to(root).as_posix()
        critical = _is_release_critical(rel)

        for line_no, line in enumerate(text.splitlines(), start=1):
            for pattern in CONTAINER_PATTERNS:
                if pattern.search(line):
                    report.findings.append(
                        Finding(
                            path=rel,
                            line=line_no,
                            pattern=pattern.pattern,
                            excerpt=line.strip()[:200],
                            release_critical=critical,
                        )
                    )
                    break

    return report


def _main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Camelot-OS container-surface inventory")
    parser.add_argument("--root", default=".", help="Repository root to scan")
    parser.add_argument("--json", action="store_true", help="Emit the full report as JSON")
    parser.add_argument(
        "--out",
        default="03_VAULT/runtime_state/distro/docker_inventory.json",
        help="Artifact path for the inventory report",
    )
    args = parser.parse_args(argv)

    report = scan_for_container_surfaces(Path(args.root))
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report.to_json(), encoding="utf-8")

    blockers = report.release_path_blockers()
    if args.json:
        print(report.to_json())

    print(f"scanned={report.scanned_files} findings={len(report.findings)} "
          f"blockers={len(blockers)} artifact={out_path}", file=sys.stderr)

    for blocker in blockers:
        print(f"BLOCKER {blocker.path}:{blocker.line}: {blocker.excerpt}", file=sys.stderr)

    return 1 if blockers else 0


if __name__ == "__main__":
    raise SystemExit(_main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/Scripts/python.exe -m pytest tests/test_docker_inventory.py -v`

Expected: PASS, 5 passed.

- [ ] **Step 5: Run the inventory against the real repository and record the baseline**

Run: `.venv/Scripts/python.exe -m control_plane.distro.docker_inventory --root . --out 03_VAULT/runtime_state/distro/docker_inventory.json`

Expected: prints `scanned=<n> findings=<n> blockers=<n>`. Record the actual
numbers in the task commit message. If `blockers` is non-zero, list every blocker
in the commit message; a non-zero baseline is a legitimate result and is the
input to Tasks 9 and 10, not a failure of this task.

- [ ] **Step 6: Commit**

```bash
git add control_plane/distro/__init__.py control_plane/distro/docker_inventory.py tests/test_docker_inventory.py
git commit -m "feat: add container-surface inventory for distro release path"
```

---

## Task 2: Ed25519-sealed canonical distro manifest

The seal is deliberately specified by test behaviour. Requirement 2 below —
verification fails under a different public key — is unsatisfiable by the keyless
digest pattern found in `control_plane/cartridges/qr_bridge.py`, so this test set
is what prevents that defect from being reproduced.

**Files:**
- Create: `control_plane/distro/manifest.py`
- Test: `tests/test_distro_manifest.py`

**Interfaces:**
- Consumes: nothing from Task 1.
- Produces: `SEAL_FIELD`, `canonical_bytes(payload: dict) -> bytes`, `key_id_for(private_key) -> str`, `seal_manifest(payload: dict, private_key, *, key_id: str) -> dict`, `verify_manifest(manifest: dict, public_key) -> bool`, `load_signing_key(path: Path | None) -> Ed25519PrivateKey`, `load_public_key(path: Path) -> Ed25519PublicKey`, `build_manifest(...) -> dict`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_distro_manifest.py
import json
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from control_plane.distro.manifest import (
    canonical_bytes,
    key_id_for,
    load_public_key,
    load_signing_key,
    seal_manifest,
    verify_manifest,
)


def _payload() -> dict:
    return {
        "schema_version": 1,
        "arch": "x86_64",
        "release": {"version": "4.0.2+camelot.1", "channel": "stable"},
    }


def test_canonical_bytes_exclude_the_seal() -> None:
    """The seal must never be inside the bytes it signs."""
    assert canonical_bytes(_payload()) == canonical_bytes(
        {**_payload(), "seal": {"signature": "anything", "algorithm": "ed25519"}}
    )


def test_canonical_bytes_are_key_order_independent() -> None:
    assert canonical_bytes({"b": 1, "a": 2}) == canonical_bytes({"a": 2, "b": 1})


def test_round_trip_verifies() -> None:
    key = Ed25519PrivateKey.generate()
    manifest = seal_manifest(_payload(), key, key_id=key_id_for(key))
    assert verify_manifest(manifest, key.public_key()) is True


def test_verification_fails_under_a_different_public_key() -> None:
    """The discriminator. A keyless digest cannot satisfy this test."""
    key = Ed25519PrivateKey.generate()
    other = Ed25519PrivateKey.generate()
    manifest = seal_manifest(_payload(), key, key_id=key_id_for(key))
    assert verify_manifest(manifest, other.public_key()) is False


def test_verification_fails_when_a_signed_byte_changes() -> None:
    key = Ed25519PrivateKey.generate()
    manifest = seal_manifest(_payload(), key, key_id=key_id_for(key))
    manifest["release"]["version"] = "4.0.2+camelot.99"
    assert verify_manifest(manifest, key.public_key()) is False


def test_verification_fails_when_the_signature_is_tampered() -> None:
    key = Ed25519PrivateKey.generate()
    manifest = seal_manifest(_payload(), key, key_id=key_id_for(key))
    manifest["seal"]["signature"] = manifest["seal"]["signature"][:-4] + "AAAA"
    assert verify_manifest(manifest, key.public_key()) is False


def test_verification_fails_on_a_missing_or_malformed_seal() -> None:
    key = Ed25519PrivateKey.generate()
    assert verify_manifest(_payload(), key.public_key()) is False
    assert verify_manifest({**_payload(), "seal": {"algorithm": "sha256"}},
                           key.public_key()) is False


def test_key_files_round_trip(tmp_path: Path) -> None:
    key = Ed25519PrivateKey.generate()
    from cryptography.hazmat.primitives import serialization

    priv_path = tmp_path / "distro_signing.pem"
    priv_path.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    pub_path = tmp_path / "distro_signing.pub"
    pub_path.write_bytes(
        key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )

    manifest = seal_manifest(_payload(), load_signing_key(priv_path),
                             key_id=key_id_for(key))
    assert verify_manifest(manifest, load_public_key(pub_path)) is True


def test_load_signing_key_refuses_a_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_signing_key(tmp_path / "absent.pem")


def test_manifest_is_json_serializable() -> None:
    key = Ed25519PrivateKey.generate()
    manifest = seal_manifest(_payload(), key, key_id=key_id_for(key))
    assert json.loads(json.dumps(manifest))["seal"]["algorithm"] == "ed25519"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest tests/test_distro_manifest.py -v`

Expected: FAIL with `ImportError: cannot import name 'canonical_bytes'`

- [ ] **Step 3: Write the minimal implementation**

```python
# control_plane/distro/manifest.py
# SPDX-License-Identifier: MIT
"""
Canonical, Ed25519-sealed Camelot-OS distro manifest.

The seal is a real detached signature over canonical bytes produced by a private
key that never enters the repository. It is deliberately NOT a hash of a field
concatenation: a digest carries no key, so it cannot fail under a different public
key and any party can forge one. See the spec's F4 finding.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Union

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

SEAL_FIELD = "seal"
SEAL_ALGORITHM = "ed25519"
CANONICAL_SEPARATORS = (",", ":")

DEFAULT_PRIVATE_KEY_ENV = "CAMELOT_DISTRO_SIGNING_KEY"
DEFAULT_PUBLIC_KEY_PATH = Path("/etc/camelot/distro-signing.pub")


def canonical_bytes(payload: Dict[str, Any]) -> bytes:
    """Canonical JSON over every field except the seal.

    Sorted keys, compact separators, UTF-8. Excluding the seal is mandatory:
    including a signature in the bytes it signs makes verification unreproducible.
    """
    body = {k: v for k, v in payload.items() if k != SEAL_FIELD}
    return json.dumps(
        body, sort_keys=True, separators=CANONICAL_SEPARATORS, ensure_ascii=False
    ).encode("utf-8")


def key_id_for(key: Ed25519PrivateKey) -> str:
    """Stable short identifier for the key pair, derived from the public key."""
    raw = key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return hashlib.sha256(raw).hexdigest()[:16]


def seal_manifest(
    payload: Dict[str, Any], private_key: Ed25519PrivateKey, *, key_id: str
) -> Dict[str, Any]:
    manifest = {k: v for k, v in payload.items() if k != SEAL_FIELD}
    signature = private_key.sign(canonical_bytes(manifest))
    public_raw = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    manifest[SEAL_FIELD] = {
        "algorithm": SEAL_ALGORITHM,
        "key_id": key_id,
        "public_key": base64.b64encode(public_raw).decode("ascii"),
        "signature": base64.b64encode(signature).decode("ascii"),
    }
    return manifest


def verify_manifest(manifest: Dict[str, Any], public_key: Ed25519PublicKey) -> bool:
    """True only when the seal is a valid Ed25519 signature by this public key."""
    seal = manifest.get(SEAL_FIELD)
    if not isinstance(seal, dict) or seal.get("algorithm") != SEAL_ALGORITHM:
        return False
    signature_b64 = seal.get("signature")
    if not isinstance(signature_b64, str):
        return False
    try:
        signature = base64.b64decode(signature_b64, validate=True)
    except (binascii.Error, ValueError):
        return False
    try:
        public_key.verify(signature, canonical_bytes(manifest))
    except InvalidSignature:
        return False
    return True


def load_signing_key(path: Optional[Union[Path, str]] = None,
                     password: Optional[bytes] = None) -> Ed25519PrivateKey:
    """Load the distro signing key from disk or from the environment path.

    Raises FileNotFoundError rather than generating a key. A silently generated
    key would produce a manifest the hub cannot verify, which fails at ingest
    instead of at build time.
    """
    resolved = Path(path or os.environ.get(DEFAULT_PRIVATE_KEY_ENV, ""))

    if not str(resolved) or not resolved.is_file():
        raise FileNotFoundError(
            f"distro signing key not found at {resolved!s}; "
            f"set {DEFAULT_PRIVATE_KEY_ENV} to a key outside the repository"
        )

    key = serialization.load_pem_private_key(
        resolved.read_bytes(), password=password
    )
    if not isinstance(key, Ed25519PrivateKey):
        raise TypeError(f"{resolved!s} is not an Ed25519 private key")
    return key


def load_public_key(path: Union[Path, str] = DEFAULT_PUBLIC_KEY_PATH) -> Ed25519PublicKey:
    resolved = Path(path)
    key = serialization.load_pem_public_key(resolved.read_bytes())
    if not isinstance(key, Ed25519PublicKey):
        raise TypeError(f"{resolved!s} is not an Ed25519 public key")
    return key


def build_manifest(
    *,
    version: str,
    channel: str,
    base_upstream: str,
    arch: str,
    artifacts: Sequence[Dict[str, Any]],
    packages: Sequence[Dict[str, Any]],
    sources: Sequence[Dict[str, Any]],
    builder: Dict[str, Any],
    hotpath: Dict[str, Any],
) -> Dict[str, Any]:
    """Assemble the unsigned manifest body. Sign it with seal_manifest."""
    return {
        "schema_version": 1,
        "release": {
            "version": version,
            "channel": channel,
            "base_upstream": base_upstream,
        },
        "arch": arch,
        "artifacts": list(artifacts),
        "packages": list(packages),
        "sources": list(sources),
        "builder": builder,
        "hotpath": hotpath,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/Scripts/python.exe -m pytest tests/test_distro_manifest.py -v`

Expected: PASS, 10 passed.

- [ ] **Step 5: Generate the development key pair outside the repository**

Run (from the repository root, writing into a directory the repo ignores):

```bash
.venv/Scripts/python.exe -c "
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
out = Path.home() / '.camelot'; out.mkdir(exist_ok=True)
k = Ed25519PrivateKey.generate()
(out / 'distro_signing.pem').write_bytes(k.private_bytes(
    serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
    serialization.NoEncryption()))
(out / 'distro_signing.pub').write_bytes(k.public_key().public_bytes(
    serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
print('wrote', out)
"
```

Expected: prints the directory. Verify the key is outside the repository and
unmentioned by `git status`. **Never commit it.** The public key is distributed to
the hub out of band in Task 10.

- [ ] **Step 6: Commit**

```bash
git add control_plane/distro/manifest.py tests/test_distro_manifest.py
git commit -m "feat: add Ed25519-sealed canonical distro manifest"
```

---

## Task 3: Anya release gate with HITL tier enforcement

Publishing a release mutates hub state and publishes signed artifacts, so it is
HUMAN_GATE. This task makes that structural rather than a convention.

**Files:**
- Create: `control_plane/distro/release_gate.py`
- Test: `tests/test_distro_release_gate.py`

**Interfaces:**
- Consumes: nothing from Tasks 1-2.
- Produces: `OPERATOR_TOKEN_ENV`, `ReleaseIntent`, `GateDecision`, `render_intent(intent: ReleaseIntent) -> str`, `gate_release(intent: ReleaseIntent, *, approved: bool = False, operator_token: str | None = None, gate: Any | None = None) -> GateDecision`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_distro_release_gate.py
from dataclasses import dataclass

from control_plane.distro.release_gate import (
    OPERATOR_TOKEN_ENV,
    ReleaseIntent,
    gate_release,
    render_intent,
)


@dataclass
class _StubTriage:
    hitl_tier: str
    assigned_knight: str = "sir_link"
    risk_entropy: float = 0.45


class _StubGate:
    def __init__(self, tier: str) -> None:
        self._tier = tier

    def triage(self, raw_intent: str) -> _StubTriage:
        return _StubTriage(hitl_tier=self._tier)


def _intent() -> ReleaseIntent:
    return ReleaseIntent(version="4.0.2+camelot.1", channel="stable", artifact_count=3)


def test_render_intent_names_version_channel_and_hub() -> None:
    text = render_intent(_intent())
    assert "4.0.2+camelot.1" in text and "stable" in text and "Hermes" in text


def test_auto_tier_is_allowed_without_approval() -> None:
    decision = gate_release(_intent(), gate=_StubGate("AUTO"))
    assert decision.allowed is True
    assert decision.tier == "AUTO"


def test_prompt_tier_requires_explicit_approval() -> None:
    blocked = gate_release(_intent(), gate=_StubGate("PROMPT"))
    assert blocked.allowed is False
    assert "approval" in blocked.reason.lower()

    allowed = gate_release(_intent(), approved=True, gate=_StubGate("PROMPT"))
    assert allowed.allowed is True


def test_human_gate_requires_both_approval_and_operator_token() -> None:
    no_token = gate_release(_intent(), approved=True, operator_token="",
                            gate=_StubGate("HUMAN_GATE"))
    assert no_token.allowed is False
    assert OPERATOR_TOKEN_ENV in no_token.reason

    no_approval = gate_release(_intent(), approved=False, operator_token="tok",
                               gate=_StubGate("HUMAN_GATE"))
    assert no_approval.allowed is False

    ok = gate_release(_intent(), approved=True, operator_token="tok",
                      gate=_StubGate("HUMAN_GATE"))
    assert ok.allowed is True


def test_operator_token_falls_back_to_the_environment(monkeypatch) -> None:
    monkeypatch.setenv(OPERATOR_TOKEN_ENV, "from-env")
    decision = gate_release(_intent(), approved=True, gate=_StubGate("HUMAN_GATE"))
    assert decision.allowed is True


def test_decision_carries_the_triage_context() -> None:
    decision = gate_release(_intent(), gate=_StubGate("PROMPT"))
    assert decision.assigned_knight == "sir_link"
    assert decision.risk_entropy == 0.45
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest tests/test_distro_release_gate.py -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'control_plane.distro.release_gate'`

- [ ] **Step 3: Write the minimal implementation**

```python
# control_plane/distro/release_gate.py
# SPDX-License-Identifier: MIT
"""
Anya-gated authorization for publishing a Camelot-OS distro release.

Publishing mutates hub state and emits signed artifacts, so it never
auto-approves. Failure to import the real gate is fail-closed, not fail-open.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Optional

OPERATOR_TOKEN_ENV = "CAMELOT_DASHBOARD_OPERATOR_TOKEN"


@dataclass(frozen=True)
class ReleaseIntent:
    version: str
    channel: str
    artifact_count: int


@dataclass(frozen=True)
class GateDecision:
    allowed: bool
    tier: str
    reason: str
    assigned_knight: str
    risk_entropy: float


def render_intent(intent: ReleaseIntent) -> str:
    return (
        f"publish Camelot-OS distro release {intent.version} to the {intent.channel} "
        f"channel on the VPS hub for the Hermes agent "
        f"({intent.artifact_count} sealed artifacts)"
    )


def _resolve_gate(gate: Any) -> Any:
    if gate is not None:
        return gate
    from control_plane.core.anya_gate import AnyaGate

    return AnyaGate()


def gate_release(
    intent: ReleaseIntent,
    *,
    approved: bool = False,
    operator_token: Optional[str] = None,
    gate: Any = None,
) -> GateDecision:
    triage = _resolve_gate(gate).triage(render_intent(intent))
    tier = triage.hitl_tier
    token = (
        operator_token
        if operator_token is not None
        else os.environ.get(OPERATOR_TOKEN_ENV, "")
    )

    def decision(allowed: bool, reason: str) -> GateDecision:
        return GateDecision(
            allowed=allowed,
            tier=tier,
            reason=reason,
            assigned_knight=triage.assigned_knight,
            risk_entropy=triage.risk_entropy,
        )

    if tier == "HUMAN_GATE":
        if not token:
            return decision(
                False,
                f"HUMAN_GATE blocked: {OPERATOR_TOKEN_ENV} is not set; suspend, do not publish",
            )
        if not approved:
            return decision(False, "HUMAN_GATE requires explicit operator approval")
        return decision(True, "HUMAN_GATE satisfied: token present and approved")

    if tier == "PROMPT":
        if not approved:
            return decision(False, "operator approval required before publish")
        return decision(True, "approval recorded")

    return decision(True, f"{tier} lane: no additional gate")


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Anya distro release gate")
    parser.add_argument("--version", required=True)
    parser.add_argument("--channel", default="stable")
    parser.add_argument("--artifacts", type=int, default=1)
    parser.add_argument("--approved", action="store_true")
    args = parser.parse_args()

    result = gate_release(
        ReleaseIntent(version=args.version, channel=args.channel,
                      artifact_count=args.artifacts),
        approved=args.approved,
    )
    print(f"allowed={result.allowed} tier={result.tier} knight={result.assigned_knight}")
    print(f"reason={result.reason}")
    raise SystemExit(0 if result.allowed else 1)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/Scripts/python.exe -m pytest tests/test_distro_release_gate.py -v`

Expected: PASS, 6 passed.

- [ ] **Step 5: Verify the real gate reports the tier for a publish intent**

Run: `.venv/Scripts/python.exe -m control_plane.distro.release_gate --version 4.0.2+camelot.1 --channel stable --artifacts 3`

Expected: prints `allowed=False ... tier=<tier>` and exits 1. Record the reported
tier in the commit message. If the tier is not `HUMAN_GATE`, the release lane needs
an explicit `HUMAN_GATE` override before Task 10 may run — resolve that with the
operator rather than proceeding.

- [ ] **Step 6: Commit**

```bash
git add control_plane/distro/release_gate.py tests/test_distro_release_gate.py
git commit -m "feat: add Anya release gate with HITL tier enforcement"
```

---

## Task 4: Builder host provisioning and per-channel nspawn roots

**This task is the schedule gate.** The spec's F2 finding established that no
Arch-capable builder exists in the inventory and that `mkarchiso` cannot run on
Windows or on the Ubuntu hub. Tasks 5-8 cannot start until this task reports a
capable builder.

**Files:**
- Create: `05_INFRASTRUCTURE/distro/builder/provision-builder.sh`
- Create: `05_INFRASTRUCTURE/distro/builder/camelot-build@.service`
- Create: `05_INFRASTRUCTURE/distro/builder/README.md`

**Interfaces:**
- Consumes: nothing from Tasks 1-3.
- Produces: the build roots `/var/lib/camelot-build/{edge,rc,stable}-x86_64`, and a zero exit from `provision-builder.sh --self-test` that Tasks 5-8 treat as a precondition.

- [ ] **Step 1: Write the capability self-test**

```bash
#!/usr/bin/env bash
# 05_INFRASTRUCTURE/distro/builder/provision-builder.sh
#
# Provisions systemd-nspawn build roots for Camelot-OS packages and ISO builds.
#
# Isolation primitive: systemd-nspawn via Arch devtools. There is deliberately no
# container runtime in this path. x86_64 only, so no foreign-architecture
# emulation is required and the Docker dependency that existed for that purpose
# does not need a replacement.

set -euo pipefail

BUILD_ROOT="${CAMELOT_BUILD_ROOT:-/var/lib/camelot-build}"
CHANNELS=(edge rc stable)
ARCH="x86_64"

log()  { printf '=> %s\n' "$*"; }
fail() { printf 'FAIL: %s\n' "$*" >&2; exit 1; }

self_test() {
    local rc=0

    for bin in systemd-nspawn mkarchroot arch-nspawn makechrootpkg mkarchiso; do
        if command -v "$bin" >/dev/null 2>&1; then
            log "ok    $bin -> $(command -v "$bin")"
        else
            printf 'MISSING %s\n' "$bin" >&2
            rc=1
        fi
    done

    if command -v docker >/dev/null 2>&1; then
        printf 'FORBIDDEN docker present at %s\n' "$(command -v docker)" >&2
        printf 'Camelot-OS builds must not depend on a container runtime.\n' >&2
        rc=1
    else
        log "ok    no container runtime on PATH"
    fi

    for channel in "${CHANNELS[@]}"; do
        local conf="/etc/camelot-build/pacman-${channel}.conf"
        if [[ -f "$conf" ]]; then
            log "ok    channel conf $conf"
        else
            printf 'MISSING channel conf %s\n' "$conf" >&2
            rc=1
        fi
    done

    if [[ "$(uname -m)" != "$ARCH" ]]; then
        printf 'REFUSED host arch %s, %s required\n' "$(uname -m)" "$ARCH" >&2
        rc=1
    else
        log "ok    host arch $ARCH"
    fi

    return "$rc"
}

provision() {
    self_test || fail "builder host is not capable; see the MISSING lines above"

    if [[ "$(id -u)" -ne 0 ]]; then
        fail "provision must run as root (nspawn roots are root-owned)"
    fi

    install -d -m 0755 "$BUILD_ROOT"

    for channel in "${CHANNELS[@]}"; do
        local root="$BUILD_ROOT/${channel}-${ARCH}"
        install -d -m 0755 "$root"
        log "root $root"
        # Root creation is performed by the systemd unit so that it is
        # observable and restartable: systemctl start camelot-build@${channel}
    done

    log "starting per-channel build roots"
    for channel in "${CHANNELS[@]}"; do
        systemctl start "camelot-build@${channel}.service"
    done

    log "provisioned $BUILD_ROOT for channels: ${CHANNELS[*]}"
}

case "${1:-}" in
    --self-test) self_test ;;
    --provision) provision ;;
    *)
        printf 'usage: %s [--self-test|--provision]\n' "$0" >&2
        exit 2
        ;;
esac
```

- [ ] **Step 2: Add the per-channel root unit**

```ini
# 05_INFRASTRUCTURE/distro/builder/camelot-build@.service
#
# Creates and refreshes one Camelot-OS package build root for channel %i.
# Isolation is systemd-nspawn via devtools. No container runtime is involved.

[Unit]
Description=Camelot-OS build root (%i, x86_64)
Documentation=file:/usr/share/doc/devtools
After=network-online.target
Wants=network-online.target
ConditionArchitecture=x86-64
ConditionPathIsDirectory=/var/lib/camelot-build

[Service]
Type=oneshot
RemainAfterExit=yes
# Create the root against the channel's pinned mirror configuration.
ExecStart=/usr/bin/mkarchroot -C /etc/camelot-build/pacman-%i.conf \
    /var/lib/camelot-build/%i-x86_64/root base base-devel devtools
# Refresh to the channel snapshot.
ExecStart=/usr/bin/arch-nspawn /var/lib/camelot-build/%i-x86_64/root \
    pacman -Syuu --noconfirm
TimeoutStartSec=1800
MemoryMax=3G
TasksMax=infinity

[Install]
WantedBy=multi-user.target
```

- [ ] **Step 3: Document the channel mirror configuration**

```markdown
# Camelot-OS Builder

Isolation primitive: **systemd-nspawn** (Arch `devtools`). No container runtime
is used or permitted in this path.

## Why there is no Docker here

Upstream `omarchy-pkgs` uses Docker or Podman for two jobs: per-channel base
isolation, and QEMU emulation of foreign architectures. Camelot-OS is x86_64-only,
which removes the second job entirely. The first is served by one nspawn root per
channel under `/var/lib/camelot-build/<channel>-x86_64`, using `mkarchroot`,
`arch-nspawn`, and `makechrootpkg` from `devtools` — the Arch project's own
packaging toolchain, nspawn-based by construction.

One primitive, already present on every target host, with no daemon, no registry,
and no image store, replaces the container runtime in both build paths.

## Host prerequisites

Install on the builder host (Arch):

```bash
sudo pacman -S --needed devtools arch-install-scripts systemd pacman-contrib
```

`mkarchiso` comes from `archiso`.

## Channel mirror configuration

The channel is defined by its pacman configuration, not by an image tag. Provide
one file per channel:

```
/etc/camelot-build/pacman-edge.conf
/etc/camelot-build/pacman-rc.conf
/etc/camelot-build/pacman-stable.conf
```

Each pins the Arch mirror snapshot and the Omarchy package mirror for that
channel. **The operator supplies the mirror URLs.** They are intentionally not
hardcoded here, because inventing a mirror would produce builds that silently
resolve against the wrong snapshot.

## Provision

```bash
sudo ./provision-builder.sh --self-test    # capability gate, safe, read-only
sudo ./provision-builder.sh --provision    # create and refresh the roots
```

`--self-test` fails if any of `systemd-nspawn`, `mkarchroot`, `arch-nspawn`,
`makechrootpkg`, `mkarchiso` is missing, if `docker` is present, if a channel
configuration is missing, or if the host is not x86_64.
```

- [ ] **Step 4: Verify the self-test on the intended builder host**

Run (on the Arch builder host selected by the operator, not on Windows):

```bash
sudo 05_INFRASTRUCTURE/distro/builder/provision-builder.sh --self-test; echo "exit=$?"
```

Expected: every line `ok`, no `MISSING`, no `FORBIDDEN`, `exit=0`.

On a non-Arch host the expected result is a `MISSING mkarchiso` failure. That is
a valid outcome that identifies the builder decision as still open.

- [ ] **Step 5: Provision and confirm the roots**

```bash
sudo 05_INFRASTRUCTURE/distro/builder/provision-builder.sh --provision
systemctl is-active camelot-build@edge.service camelot-build@rc.service camelot-build@stable.service
ls -d /var/lib/camelot-build/*-x86_64/root
```

Expected: three `active` units and three existing root directories.

- [ ] **Step 6: Commit**

```bash
git add 05_INFRASTRUCTURE/distro/builder/
git commit -m "feat: add nspawn builder host provisioning for x86_64 channels"
```

---

## Task 5: Native package builder and profile sync

Replaces the container build invocation in the `camelot-pkgs` fork and keeps
profile sources authoritative in this repository.

**Files:**
- Create: `05_INFRASTRUCTURE/distro/builder/nspawn-build.sh`
- Create: `05_INFRASTRUCTURE/distro/builder/sync-profile.sh`

**Interfaces:**
- Consumes: `/var/lib/camelot-build/<channel>-x86_64` from Task 4; `05_INFRASTRUCTURE/distro/profile/` sources from Task 6.
- Produces: `nspawn-build.sh <channel> <pkgname> [pkgbuild-dir]` exiting 0 with an artifact in `./release/`; `sync-profile.sh [--check]` exiting non-zero when the fork has drifted.

- [ ] **Step 1: Write the build driver**

```bash
#!/usr/bin/env bash
# 05_INFRASTRUCTURE/distro/builder/nspawn-build.sh
#
# Build one Camelot-OS PKGBUILD inside a channel nspawn root.
#
# Replaces the container invocation upstream omarchy-pkgs uses for per-channel
# base isolation. makechrootpkg creates a disposable working copy of the root, so
# a failed build cannot poison the channel root.

set -euo pipefail

BUILD_ROOT="${CAMELOT_BUILD_ROOT:-/var/lib/camelot-build}"
ARCH="x86_64"
CHANNEL="${1:-}"
PKGNAME="${2:-}"
PKGBUILD_DIR="${3:-pkgbuilds/${PKGNAME}}"

usage() { printf 'usage: %s <edge|rc|stable> <pkgname> [pkgbuild-dir]\n' "$0" >&2; exit 2; }
log()   { printf '=> %s\n' "$*"; }
fail()  { printf 'FAIL: %s\n' "$*" >&2; exit 1; }

[[ -n "$CHANNEL" && -n "$PKGNAME" ]] || usage
case "$CHANNEL" in edge|rc|stable) ;; *) fail "unknown channel '$CHANNEL'" ;; esac

CHROOT="$BUILD_ROOT/${CHANNEL}-${ARCH}"
ROOT="$CHROOT/root"
CONF="/etc/camelot-build/pacman-${CHANNEL}.conf"

[[ -d "$ROOT" ]] || fail "missing build root $ROOT; run provision-builder.sh --provision"
[[ -f "$CONF" ]] || fail "missing channel config $CONF"
[[ -f "$PKGBUILD_DIR/PKGBUILD" ]] || fail "missing $PKGBUILD_DIR/PKGBUILD"

command -v docker >/dev/null 2>&1 && fail "container runtime present; this path must not use one"

log "channel=$CHANNEL arch=$ARCH pkg=$PKGNAME root=$ROOT"

mkdir -p release

# makechrootpkg reads the PKGBUILD from the working directory, so change into it
# rather than guessing at a flag. -c refreshes the working copy and -l names it;
# the channel root itself is never modified. Remaining args go to makepkg after --.
cd "$PKGBUILD_DIR"

makechrootpkg \
    -r "$CHROOT" \
    -l "camelot-${CHANNEL}-${PKGNAME}" \
    -- --config "$CONF" --noconfirm

log "artifacts:"
ls -1 ./*.pkg.tar.* 2>/dev/null || printf '  (no package produced)\n'
```

- [ ] **Step 2: Write the profile sync tool**

```bash
#!/usr/bin/env bash
# 05_INFRASTRUCTURE/distro/builder/sync-profile.sh
#
# Copies Camelot-OS profile sources from this repository into the camelot-pkgs
# fork. This repository is the source of truth; the fork is a build surface.

set -euo pipefail

SRC="${CAMELOT_PROFILE_SRC:-05_INFRASTRUCTURE/distro/profile}"
DEST="${CAMELOT_PKGS_PKGBUILDS:-}"
MODE="${1:-}"

fail() { printf 'FAIL: %s\n' "$*" >&2; exit 1; }

[[ -d "$SRC" ]] || fail "missing profile source directory $SRC"
[[ -n "$DEST" ]] || fail "set CAMELOT_PKGS_PKGBUILDS to the camelot-pkgs pkgbuilds directory"
[[ -d "$DEST" ]] || fail "missing destination directory $DEST"

if ! command -v docker >/dev/null 2>&1; then
    printf 'ok: no container runtime on PATH\n'
fi

if [[ "$MODE" == "--check" ]]; then
    if diff -r --brief "$SRC" "$DEST"; then
        printf 'ok: profile in sync with %s\n' "$DEST"
        exit 0
    fi
    printf 'DRIFT: profile sources differ from %s\n' "$DEST" >&2
    exit 1
fi

for pkg in "$SRC"/*/; do
    name="$(basename "$pkg")"
    printf '=> syncing %s\n' "$name"
    install -d -m 0755 "$DEST/$name"
    cp -r "$pkg"/. "$DEST/$name/"
done

printf 'synced %s -> %s\n' "$SRC" "$DEST"
```

- [ ] **Step 3: Verify the drivers refuse unsafe conditions**

Run each and confirm the expected failure. This is the verification for this task;
an actual package build requires Task 6's PKGBUILD and a provisioned Task 4 host.

```bash
bash 05_INFRASTRUCTURE/distro/builder/nspawn-build.sh
# Expected: usage on stderr, exit 2

bash 05_INFRASTRUCTURE/distro/builder/nspawn-build.sh edge camelot-os-profile
# Expected on a non-provisioned host: FAIL missing build root ...; exit 1

CAMELOT_PKGS_PKGBUILDS= bash 05_INFRASTRUCTURE/distro/builder/sync-profile.sh
# Expected: FAIL set CAMELOT_PKGS_PKGBUILDS ...; exit 1
```

- [ ] **Step 4: Commit**

```bash
git add 05_INFRASTRUCTURE/distro/builder/nspawn-build.sh 05_INFRASTRUCTURE/distro/builder/sync-profile.sh
git commit -m "feat: add nspawn package builder and profile sync"
```

---

## Task 6: `camelot-os-profile` package with slices and tethers

This is the package that makes an installed machine a Camelot node. The slice
values are the spec's memory budget, and the test asserts the shipped units match
the spec table.

**Files:**
- Create: `05_INFRASTRUCTURE/distro/profile/camelot-os-profile/PKGBUILD`
- Create: `05_INFRASTRUCTURE/distro/profile/camelot-os-profile/.omarchy/package.json`
- Create: `05_INFRASTRUCTURE/distro/profile/camelot-os-profile/camelot-critical.slice`
- Create: `05_INFRASTRUCTURE/distro/profile/camelot-os-profile/camelot-control.slice`
- Create: `05_INFRASTRUCTURE/distro/profile/camelot-os-profile/camelot-data.slice`
- Create: `05_INFRASTRUCTURE/distro/profile/camelot-os-profile/camelot-workers.slice`
- Create: `05_INFRASTRUCTURE/distro/profile/camelot-os-profile/camelot-os-profile.install`
- Create: `05_INFRASTRUCTURE/distro/profile/camelot-os-profile/camelot-slice-budget.conf`
- Test: `tests/test_distro_profile.py`

**Interfaces:**
- Consumes: nothing from earlier tasks at the Python level.
- Produces: `camelot-os-profile` package; the four `camelot-*.slice` units; `camelot-slice-budget.conf` declaring the 8 GB and 4 GB ceilings that Task 7's acceptance run validates.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_distro_profile.py
"""The shipped profile must match the spec's budget table and stay Docker-free."""
import re
from pathlib import Path

import pytest

PROFILE = Path("05_INFRASTRUCTURE/distro/profile/camelot-os-profile")

# From the spec's hardware floor and memory budget table.
BUDGET_8GB = {
    "camelot-critical.slice": "512M",
    "camelot-control.slice": "512M",
    "camelot-data.slice": "1G",
    "camelot-workers.slice": "2G",
}
BUDGET_4GB = {
    "camelot-critical.slice": "384M",
    "camelot-control.slice": "384M",
    "camelot-data.slice": "512M",
    "camelot-workers.slice": "1G",
}


def _pkgbuild() -> str:
    return (PROFILE / "PKGBUILD").read_text(encoding="utf-8")


def _depends_block(pkgbuild: str) -> str:
    match = re.search(r"^depends=\((.*?)\)", pkgbuild, re.M | re.S)
    assert match, "PKGBUILD declares no depends array"
    return match.group(1)


@pytest.mark.parametrize("unit,expected", BUDGET_8GB.items())
def test_slice_memory_max_matches_the_8gb_budget(unit: str, expected: str) -> None:
    text = (PROFILE / unit).read_text(encoding="utf-8")
    assert f"MemoryMax={expected}" in text


def test_slice_budget_conf_records_both_profiles() -> None:
    text = (PROFILE / "camelot-slice-budget.conf").read_text(encoding="utf-8")
    for unit, value in BUDGET_8GB.items():
        assert f"{unit} {value}" in text
    for unit, value in BUDGET_4GB.items():
        assert f"{unit}_profile4gb {value}" in text


def test_pkgbuild_never_depends_on_a_container_runtime() -> None:
    depends = _depends_block(_pkgbuild())
    for forbidden in ("docker", "podman", "containerd"):
        assert forbidden not in depends


def test_pkgbuild_is_x86_64_only() -> None:
    assert "arch=('x86_64')" in _pkgbuild()


def test_pkgbuild_installs_every_slice() -> None:
    pkgbuild = _pkgbuild()
    for unit in BUDGET_8GB:
        assert unit in pkgbuild


def test_omarchy_package_metadata_pins_the_edge_channel() -> None:
    import json

    meta = json.loads((PROFILE / ".omarchy" / "package.json").read_text(encoding="utf-8"))
    assert meta["name"] == "camelot-os-profile"
    assert "channels" in meta


def test_install_scriptlet_reloads_systemd() -> None:
    text = (PROFILE / "camelot-os-profile.install").read_text(encoding="utf-8")
    assert "systemctl daemon-reload" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/Scripts/python.exe -m pytest tests/test_distro_profile.py -v`

Expected: FAIL with `FileNotFoundError` for the profile directory.

- [ ] **Step 3: Write the PKGBUILD**

```bash
# Maintainer: Sir Codex <codex@camelot.invalid>
# Camelot-OS node profile: cgroups v2 agent slices and systemd tethers.
# x86_64 only. Requires no container runtime.

pkgname=camelot-os-profile
pkgver=1.0.0
pkgrel=1
pkgdesc="Camelot-OS node profile: agent systemd slices and tethers"
arch=('x86_64')
url="https://github.com/Cyberdad247/camelot-iso"
license=('MIT')
depends=('systemd' 'tailscale' 'ufw')
optdepends=('hermes-agent: autonomous recursive execution layer')
install=camelot-os-profile.install
source=(
    'camelot-critical.slice'
    'camelot-control.slice'
    'camelot-data.slice'
    'camelot-workers.slice'
    'camelot-slice-budget.conf'
)
sha256sums=('SKIP' 'SKIP' 'SKIP' 'SKIP' 'SKIP')

package() {
    install -Dm644 camelot-critical.slice \
        "$pkgdir/usr/lib/systemd/system/camelot-critical.slice"
    install -Dm644 camelot-control.slice \
        "$pkgdir/usr/lib/systemd/system/camelot-control.slice"
    install -Dm644 camelot-data.slice \
        "$pkgdir/usr/lib/systemd/system/camelot-data.slice"
    install -Dm644 camelot-workers.slice \
        "$pkgdir/usr/lib/systemd/system/camelot-workers.slice"
    install -Dm644 camelot-slice-budget.conf \
        "$pkgdir/etc/camelot/slice-budget.conf"
}
```

- [ ] **Step 4: Write the slice units and budget declaration**

```ini
# camelot-critical.slice — Bifrost gateway, Heimdall perimeter.
[Unit]
Description=Camelot-OS critical slice
Before=slices.target

[Slice]
MemoryAccounting=yes
MemoryMax=512M
```

```ini
# camelot-control.slice — runic router, Anya gate.
[Unit]
Description=Camelot-OS control slice
Before=slices.target

[Slice]
MemoryAccounting=yes
MemoryMax=512M
```

```ini
# camelot-data.slice — SQLite, Graphiti, VFS.
[Unit]
Description=Camelot-OS data slice
Before=slices.target

[Slice]
MemoryAccounting=yes
MemoryMax=1G
```

```ini
# camelot-workers.slice — agent workers, Hermes.
# MemoryHigh sits below MemoryMax so PSI reclaim degrades the desktop smoothly
# instead of letting the hard cap OOM-kill a worker.
[Unit]
Description=Camelot-OS workers slice
Before=slices.target

[Slice]
MemoryAccounting=yes
MemoryHigh=1536M
MemoryMax=2G
```

```
# camelot-slice-budget.conf
# Design ceilings from the distro spec. Measured values arrive from the Task 7
# acceptance run; update both this file and the units together.
camelot-critical.slice 512M
camelot-control.slice 512M
camelot-data.slice 1G
camelot-workers.slice 2G
camelot-critical.slice_profile4gb 384M
camelot-control.slice_profile4gb 384M
camelot-data.slice_profile4gb 512M
camelot-workers.slice_profile4gb 1G
```

- [ ] **Step 5: Write the install scriptlet and fork metadata**

```bash
# camelot-os-profile.install
post_install() {
    systemctl daemon-reload
    printf 'Camelot-OS profile installed. Slices available:\n'
    printf '  camelot-critical.slice camelot-control.slice\n'
    printf '  camelot-data.slice camelot-workers.slice\n'
}

post_upgrade() {
    post_install
}

pre_remove() {
    systemctl daemon-reload
}
```

```json
{
  "name": "camelot-os-profile",
  "version": "1.0.0",
  "description": "Camelot-OS node profile: agent systemd slices and tethers",
  "channels": ["edge"],
  "release_ring": "fast",
  "arch": ["x86_64"],
  "skip_build": false
}
```

- [ ] **Step 6: Run test to verify it passes**

Run: `.venv/Scripts/python.exe -m pytest tests/test_distro_profile.py -v`

Expected: PASS, 12 passed.

- [ ] **Step 7: Commit**

```bash
git add 05_INFRASTRUCTURE/distro/profile/ tests/test_distro_profile.py
git commit -m "feat: add camelot-os-profile package with agent slices"
```

---

## Task 7: Unattended cidata install profile

Produces the NoCloud drive that makes an install unattended. The schema comes from
the upstream `omarchy-iso` README; the authoritative copy is whatever the
configurator writes, so Step 4 diffs against a real interactive install.

**Files:**
- Create: `05_INFRASTRUCTURE/distro/iso/cidata/user_configuration.json`
- Create: `05_INFRASTRUCTURE/distro/iso/cidata/authorized_keys.example`
- Create: `05_INFRASTRUCTURE/distro/iso/build-cidata.sh`
- Create: `05_INFRASTRUCTURE/distro/iso/cidata/.gitignore`
- Test: `tests/test_cidata_profile.py`

**Interfaces:**
- Consumes: nothing from earlier tasks at the Python level.
- Produces: `cidata.iso` via `build-cidata.sh`, and `user_configuration.json` with hostname `camelot-node`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_cidata_profile.py
"""cidata profile conformance and secret non-commitment."""
import json
from pathlib import Path

import pytest

CIDATA = Path("05_INFRASTRUCTURE/distro/iso/cidata")
FORBIDDEN_TRACKED = ("user_credentials.json", "tailscale_authkey", "authorized_keys")


def _config() -> dict:
    return json.loads((CIDATA / "user_configuration.json").read_text(encoding="utf-8"))


def test_user_configuration_is_valid_json() -> None:
    assert isinstance(_config(), dict)


def test_required_upstream_keys_are_present() -> None:
    config = _config()
    for key in ("hostname", "timezone", "kernels", "disk_config", "bootloader"):
        assert key in config, f"missing required key {key}"


def test_hostname_is_camelot_node() -> None:
    assert _config()["hostname"] == "camelot-node"


def test_tailscale_is_installed_for_the_autoinstall() -> None:
    assert "tailscale" in _config()["packages"]


def test_no_container_runtime_is_requested() -> None:
    packages = " ".join(_config()["packages"]).lower()
    for forbidden in ("docker", "podman", "containerd"):
        assert forbidden not in packages


@pytest.mark.parametrize("name", FORBIDDEN_TRACKED)
def test_secret_bearing_cidata_files_are_not_committed(name: str) -> None:
    """The upstream README states user_credentials.json carries a password hash
    and tailscale_authkey carries a join key. Neither may enter the tree."""
    assert not (CIDATA / name).exists(), f"{name} must never be committed"


def test_gitignore_excludes_every_secret_bearing_file() -> None:
    text = (CIDATA / ".gitignore").read_text(encoding="utf-8")
    for name in FORBIDDEN_TRACKED:
        assert name in text


def test_authorized_keys_example_contains_no_real_key() -> None:
    text = (CIDATA / "authorized_keys.example").read_text(encoding="utf-8")
    assert "ssh-ed25519" not in text
    assert "AAAA" not in text


def test_build_script_is_executable_and_generates_a_cidata_iso() -> None:
    path = Path("05_INFRASTRUCTURE/distro/iso/build-cidata.sh")
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "genisoimage" in text
    assert "-volid cidata" in text
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest tests/test_cidata_profile.py -v`

Expected: FAIL with `FileNotFoundError` for `user_configuration.json`.

- [ ] **Step 3: Write the config, templates, and gitignore**

```json
{
  "archinstall-language": "English",
  "audio": "pipewire",
  "bootloader": "systemd-boot",
  "kernels": ["linux"],
  "hostname": "camelot-node",
  "timezone": "UTC",
  "keyboard_layout": "us",
  "profile": {"main": "Minimal"},
  "packages": ["tailscale", "ufw", "git", "sudo", "vim", "networkmanager"],
  "nic": {"type": "NetworkManager"},
  "disk_config": {"config_type": "default_layout", "device_modifications": []},
  "ntp": true,
  "swap": true
}
```

```
# authorized_keys.example
# sshd's own format, one public key per line.
# Copy this file to authorized_keys (untracked) and add real keys.
#   ssh-ed25519 <base64 public key> you@host
```

```gitignore
# This directory is the cidata source. Secret-bearing files are generated
# locally and attached to a cidata volume; they are never committed.
user_credentials.json
tailscale_authkey
authorized_keys
user_full_name.txt
user_email_address.txt
user_encrypt_installation.txt
cidata.iso
```

- [ ] **Step 4: Write the cidata build script**

```bash
#!/usr/bin/env bash
# 05_INFRASTRUCTURE/distro/iso/build-cidata.sh
#
# Builds the NoCloud cidata ISO the Omarchy installer reads to skip its
# configurator. Autoinstall triggers only when a drive labelled `cidata` is
# attached alongside the install ISO.

set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/cidata" && pwd)"
OUT="${1:-cidata.iso}"

fail() { printf 'FAIL: %s\n' "$*" >&2; exit 1; }

command -v genisoimage >/dev/null 2>&1 || fail "genisoimage not found (Arch: cdrtools)"

[[ -f "$SRC/user_configuration.json" ]] || fail "missing user_configuration.json"
[[ -f "$SRC/user_credentials.json" ]] || \
    fail "missing user_credentials.json (generate locally; do not commit). \
Create it with: openssl passwd -6 \"yourpassword\""

command -v docker >/dev/null 2>&1 && printf 'note: container runtime present but unused\n'

genisoimage -output "$OUT" -volid cidata -joliet -rock "$SRC"

printf '=> wrote %s\n' "$OUT"
if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$OUT"
fi
```

```bash
chmod +x 05_INFRASTRUCTURE/distro/iso/build-cidata.sh
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `.venv/Scripts/python.exe -m pytest tests/test_cidata_profile.py -v`

Expected: PASS, 11 passed.

- [ ] **Step 6: Reconcile this profile against a real interactive install**

Per the upstream README, the configurator's own output files are authoritative.
On the builder host, run one interactive Omarchy install, then:

```bash
sudo cp /root/user_configuration.json /tmp/generated_user_configuration.json
diff -u 05_INFRASTRUCTURE/distro/iso/cidata/user_configuration.json \
        /tmp/generated_user_configuration.json
```

Expected: a diff. Reconcile our file toward the generator's schema and commit the
reconciled file. Do not commit the generated credentials file.

- [ ] **Step 7: Commit**

```bash
git add 05_INFRASTRUCTURE/distro/iso/
git commit -m "feat: add unattended cidata install profile for x86_64"
```

---

## Task 8: ISO build driver with host-capability gating

`mkarchiso` needs privilege and loop devices. This driver refuses to attempt a
build on a host that cannot do it, so a Windows or Ubuntu run fails with a clear
reason instead of a half-built ISO.

**Files:**
- Create: `control_plane/distro/iso_build.py`
- Create: `05_INFRASTRUCTURE/distro/iso/camelot-iso.env`
- Test: `tests/test_distro_iso_build.py`

**Interfaces:**
- Consumes: `05_INFRASTRUCTURE/distro/iso/camelot-iso.env`, the builder from Task 4.
- Produces: `HostCapability`, `detect_host_capability() -> HostCapability`, `HostCapability.blockers() -> list[str]`, `build_iso_command(env: dict, release_dir: Path) -> list[str]`, `acceptance_command(iso: Path) -> list[str]`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_distro_iso_build.py
from pathlib import Path

from control_plane.distro.iso_build import (
    HostCapability,
    acceptance_command,
    build_iso_command,
)


def _cap(**kw) -> HostCapability:
    base = dict(is_linux=True, is_arch=True, has_mkarchiso=True,
                has_nspawn=True, container_runtime_present=False,
                arch="x86_64")
    base.update(kw)
    return HostCapability(**base)


def test_a_windows_host_cannot_build() -> None:
    blockers = _cap(is_linux=False, is_arch=False, has_mkarchiso=False).blockers()
    assert any("linux" in b.lower() for b in blockers)


def test_an_ubuntu_host_cannot_build() -> None:
    blockers = _cap(is_arch=False).blockers()
    assert any("arch" in b.lower() for b in blockers)


def test_a_missing_mkarchiso_blocks_the_build() -> None:
    assert any("mkarchiso" in b for b in _cap(has_mkarchiso=False).blockers())


def test_a_present_container_runtime_blocks_the_build() -> None:
    blockers = _cap(container_runtime_present=True).blockers()
    assert any("container runtime" in b for b in blockers)


def test_an_aarch64_host_blocks_the_build() -> None:
    assert any("x86_64" in b for b in _cap(arch="aarch64").blockers())


def test_a_capable_host_has_no_blockers() -> None:
    assert _cap().blockers() == []


def test_build_command_uses_local_source_and_no_container() -> None:
    env = {"CAMELOT_ISO_VERSION": "4.0.2+camelot.1", "OMARCHY_SRC": "../omarchy",
           "CAMELOT_PKGS": "../camelot-pkgs"}
    cmd = build_iso_command(env, Path("release"))
    assert cmd[:1] == ["./bin/omarchy-iso-make"] or "omarchy-iso-make" in cmd[0]
    assert "--local-source" in cmd
    assert "../omarchy" in cmd and "../camelot-pkgs" in cmd
    assert not any("docker" in part for part in cmd)


def test_build_command_requests_a_channel_when_pinned() -> None:
    cmd = build_iso_command({"CAMELOT_ISO_CHANNEL": "rc"}, Path("release"))
    assert "--rc" in cmd


def test_acceptance_command_targets_the_iso() -> None:
    cmd = acceptance_command(Path("release/camelot.iso"))
    assert "omarchy-iso-test" in cmd[0]
    assert "release/camelot.iso" in cmd


def test_build_command_is_idempotent_for_the_same_inputs() -> None:
    env = {"CAMELOT_ISO_VERSION": "4.0.2+camelot.1"}
    assert build_iso_command(env, Path("release")) == build_iso_command(env, Path("release"))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest tests/test_distro_iso_build.py -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'control_plane.distro.iso_build'`

- [ ] **Step 3: Write the implementation**

```python
# control_plane/distro/iso_build.py
# SPDX-License-Identifier: MIT
"""
Camelot-OS ISO build driver.

mkarchiso requires an Arch host with loop-device access. This module refuses to
attempt a build on a host that cannot perform one, and refuses any build path that
would reach for a container runtime.
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Mapping, Sequence

FORBIDDEN_BINARIES = ("docker", "podman", "containerd", "nerdctl")
OMARCHY_ISO_MAKE = "./bin/omarchy-iso-make"
OMARCHY_ISO_TEST = "./bin/omarchy-iso-test"
ARCH_RELEASE_FILE = Path("/etc/arch-release")


@dataclass(frozen=True)
class HostCapability:
    is_linux: bool
    is_arch: bool
    has_mkarchiso: bool
    has_nspawn: bool
    container_runtime_present: bool
    arch: str

    def blockers(self) -> List[str]:
        problems: List[str] = []
        if not self.is_linux:
            problems.append("host is not linux; mkarchiso cannot run here")
        if not self.is_arch:
            problems.append(f"host is not Arch Linux (no {ARCH_RELEASE_FILE})")
        if not self.has_mkarchiso:
            problems.append("mkarchiso not found; install archiso")
        if not self.has_nspawn:
            problems.append("systemd-nspawn not found; devtools builds need it")
        if self.container_runtime_present:
            problems.append(
                "container runtime present on PATH; Camelot-OS builds must not "
                "depend on one"
            )
        if self.arch != "x86_64":
            problems.append(f"host arch is {self.arch}; x86_64 required")
        return problems


def detect_host_capability(
    *, which=shutil.which, system: str | None = None,
    machine: str | None = None, arch_release: Path = ARCH_RELEASE_FILE,
) -> HostCapability:
    system = system or platform.system()
    machine = machine or platform.machine()
    return HostCapability(
        is_linux=system.lower() == "linux",
        is_arch=arch_release.is_file(),
        has_mkarchiso=which("mkarchiso") is not None,
        has_nspawn=which("systemd-nspawn") is not None,
        container_runtime_present=any(which(b) for b in FORBIDDEN_BINARIES),
        arch=machine,
    )


def build_iso_command(env: Mapping[str, str], release_dir: Path) -> List[str]:
    cmd: List[str] = [OMARCHY_ISO_MAKE]

    omarchy_src = env.get("OMARCHY_SRC")
    camelot_pkgs = env.get("CAMELOT_PKGS")
    if omarchy_src and camelot_pkgs:
        cmd += ["--local-source", omarchy_src, camelot_pkgs]

    channel = env.get("CAMELOT_ISO_CHANNEL", "").strip()
    if channel in {"dev", "rc", "edge"}:
        cmd.append(f"--{channel}")

    if env.get("CAMELOT_ISO_VERSION"):
        os.environ.setdefault("CAMELOT_ISO_VERSION", env["CAMELOT_ISO_VERSION"])

    # as_posix() so generated commands are identical on Windows and Linux.
    cmd += ["--release-dir", release_dir.as_posix()]
    return cmd


def acceptance_command(iso: Path) -> List[str]:
    return [OMARCHY_ISO_TEST, iso.as_posix()]


def _main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Camelot-OS ISO build driver")
    parser.add_argument("--check", action="store_true", help="Report host capability only")
    parser.add_argument("--iso", help="Run the acceptance harness against this ISO")
    parser.add_argument("--release-dir", default="release")
    args = parser.parse_args(argv)

    if args.iso:
        cmd = acceptance_command(Path(args.iso))
        print(" ".join(cmd))
        return 0

    capability = detect_host_capability()
    blockers = capability.blockers()
    print(f"host={capability.arch} linux={capability.is_linux} arch={capability.is_arch} "
          f"mkarchiso={capability.has_mkarchiso} nspawn={capability.has_nspawn} "
          f"container_runtime={capability.container_runtime_present}")

    if blockers:
        for blocker in blockers:
            print(f"BLOCKER: {blocker}", file=sys.stderr)
        return 1

    if args.check:
        print("host is capable of building a Camelot-OS ISO")
        return 0

    env = {**os.environ}
    print(" ".join(build_iso_command(env, Path(args.release_dir))))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
```

- [ ] **Step 4: Add the pinned release environment**

```bash
# 05_INFRASTRUCTURE/distro/iso/camelot-iso.env
# Pinned inputs for a Camelot-OS release build.
# Source this file on the builder host before building.

# Version is "<upstream omarchy version>+camelot.<patch>".
export CAMELOT_ISO_VERSION="4.0.2+camelot.1"

# Channel: dev | rc | edge. Empty means the upstream default (stable mirror).
export CAMELOT_ISO_CHANNEL=""

# Sibling checkouts on the builder host.
export OMARCHY_SRC="../omarchy"
export CAMELOT_PKGS="../camelot-pkgs"

# Build roots provisioned by Task 4.
export CAMELOT_BUILD_ROOT="/var/lib/camelot-build"

# Signing key lives outside the repository.
export CAMELOT_DISTRO_SIGNING_KEY="$HOME/.camelot/distro_signing.pem"
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `.venv/Scripts/python.exe -m pytest tests/test_distro_iso_build.py -v`

Expected: PASS, 10 passed.

- [ ] **Step 6: Confirm this host is correctly refused**

Run: `.venv/Scripts/python.exe -m control_plane.distro.iso_build --check; echo "exit=$?"`

Expected on Windows: prints a `host=` line containing `linux=False` and
`arch=False`, then `BLOCKER:` lines and `exit=1`. That refusal is the correct
behaviour and the evidence that the gate works.

- [ ] **Step 7: Commit**

```bash
git add control_plane/distro/iso_build.py tests/test_distro_iso_build.py 05_INFRASTRUCTURE/distro/iso/camelot-iso.env
git commit -m "feat: add ISO build driver with host capability gating"
```

---

## Task 9: De-Dockerize Hermes on the hub

Removes the container dependency from the Hermes path. This is `HUMAN_GATE`
because it mutates VPS unit state.

**Files:**
- Create: `infra/systemd/hermes-agent.service`
- Create: `scripts/ops/migrate-hermes-off-docker.sh`
- Modify: `control_plane/dispatch/omarchy_agent_matrix.py` (`generate_omarchy_mise_stub`)
- Test: `tests/test_omarchy_agent_matrix_stub.py`

**Interfaces:**
- Consumes: nothing from earlier tasks at the Python level.
- Produces: `hermes-agent.service`; a `generate_omarchy_mise_stub("hermes")` result containing no container reference.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_omarchy_agent_matrix_stub.py
"""The Hermes launcher stub must not shell into a container."""
from control_plane.dispatch.omarchy_agent_matrix import generate_omarchy_mise_stub


def test_hermes_stub_has_no_container_reference() -> None:
    stub = generate_omarchy_mise_stub("hermes")
    for forbidden in ("docker", "podman", "containerd"):
        assert forbidden not in stub.lower()


def test_hermes_stub_targets_the_native_binary() -> None:
    stub = generate_omarchy_mise_stub("hermes")
    assert "/usr/local/bin/hermes" in stub


def test_hermes_stub_remains_a_valid_script() -> None:
    stub = generate_omarchy_mise_stub("hermes")
    assert stub.startswith("#!/bin/bash")
    assert "set -euo pipefail" in stub


def test_hermes_stub_quotes_arguments_for_the_remote_shell() -> None:
    """ssh joins argv into one remote command string, so bare "$@" would split
    on spaces. printf '%q ' is what keeps arguments intact."""
    stub = generate_omarchy_mise_stub("hermes")
    assert "printf '%q '" in stub


def test_other_agent_stubs_are_unaffected() -> None:
    codex_stub = generate_omarchy_mise_stub("codex")
    assert "sir_codex" in codex_stub.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/Scripts/python.exe -m pytest tests/test_omarchy_agent_matrix_stub.py -v`

Expected: FAIL, `test_hermes_stub_has_no_container_reference` — the current stub
contains `docker exec -i hermes hermes`.

- [ ] **Step 3: Replace the container stub**

In `control_plane/dispatch/omarchy_agent_matrix.py`, replace the `hermes` branch of
`generate_omarchy_mise_stub`:

```python
    if mapping.omarchy_cmd == "hermes":
        # The hub runs Hermes as a native systemd unit (hermes-agent.service).
        # This path must not invoke a container runtime.
        #
        # ssh joins its remaining arguments into a single string that the remote
        # shell then splits, so arguments are quoted locally with printf '%q '
        # rather than forwarded as bare "$@" (which would break on spaces).
        return "\n".join(
            [
                "#!/bin/bash",
                "# Omarchy <-> Camelot Hermes proxy stub.",
                "# The hub runs Hermes natively via hermes-agent.service.",
                "# No container runtime is involved in this path.",
                "set -euo pipefail",
                "HUB=root@162.35.107.134",
                "ARGS=$(printf '%q ' \"$@\")",
                "exec ssh -o BatchMode=yes \"$HUB\" \"/usr/local/bin/hermes $ARGS\"",
                "",
            ]
        )
```

- [ ] **Step 4: Add the native unit**

```ini
# infra/systemd/hermes-agent.service
#
# Native Hermes agent on the VPS hub. Replaces the container deployment.
# No container runtime is required by or referenced from this unit.

[Unit]
Description=Camelot Hermes Agent (native)
Documentation=https://github.com/Cyberdad247/camelot-iso
After=network-online.target tailscaled.service
Wants=network-online.target
ConditionPathExists=/usr/local/bin/hermes

[Service]
Type=simple
Slice=camelot-workers.slice
User=camelot
Group=camelot
WorkingDirectory=/srv/camelot/hermes
Environment=HERMES_HOME=/srv/camelot/hermes
EnvironmentFile=-/etc/camelot/hermes.env
ExecStart=/usr/local/bin/hermes serve --host 127.0.0.1 --port 8642
Restart=on-failure
RestartSec=5s
StateDirectory=camelot/hermes
RuntimeDirectory=camelot/hermes
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/srv/camelot/hermes
MemoryHigh=1536M
MemoryMax=2G
TasksMax=512
StandardOutput=journal
StandardError=journal
SyslogIdentifier=hermes-agent

# The listener is loopback-only; the mesh bridge fronts it.
IPAddressDeny=any
IPAddressAllow=localhost
IPAddressAllow=100.64.0.0/10

[Install]
WantedBy=multi-user.target
```

- [ ] **Step 5: Write the migration script**

```bash
#!/usr/bin/env bash
# scripts/ops/migrate-hermes-off-docker.sh
#
# One-way migration of the Hermes agent on the VPS hub from a container to the
# native hermes-agent.service unit.
#
# HUMAN_GATE: this mutates hub unit state. It refuses to run without operator
# acknowledgement and an explicit confirmation flag.

set -euo pipefail

CONFIRM="${1:-}"
TOKEN="${CAMELOT_DASHBOARD_OPERATOR_TOKEN:-}"

HUB="${CAMELOT_HUB_HOST:-162.35.107.134}"
UNIT_SRC="infra/systemd/hermes-agent.service"
UNIT_DEST="/etc/systemd/system/hermes-agent.service"

fail() { printf 'FAIL: %s\n' "$*" >&2; exit 1; }

[[ "$CONFIRM" == "--confirm" ]] || \
    fail "refusing to mutate hub unit state without --confirm"
[[ -n "$TOKEN" ]] || \
    fail "CAMELOT_DASHBOARD_OPERATOR_TOKEN is not set; HUMAN_GATE not satisfied"
[[ -f "$UNIT_SRC" ]] || fail "missing $UNIT_SRC"

printf '=> target hub: %s\n' "$HUB"

# 1. Confirm the native binary is present before removing anything.
ssh -o BatchMode=yes "root@${HUB}" \
    'test -x /usr/local/bin/hermes && echo "ok: /usr/local/bin/hermes" || { echo "MISSING hermes binary"; exit 1; }'

# 2. Confirm the unit carries no container dependency.
if grep -qiE '\b(docker|podman|containerd)\b' "$UNIT_SRC"; then
    fail "$UNIT_SRC references a container runtime"
fi
printf 'ok: unit is container-free\n'

# 3. Install the unit.
scp -o BatchMode=yes "$UNIT_SRC" "root@${HUB}:${UNIT_DEST}"

# 4. Install the slices the unit binds to, then start.
ssh -o BatchMode=yes "root@${HUB}" bash -s <<'REMOTE'
set -euo pipefail
systemctl daemon-reload
systemctl enable --now hermes-agent.service
systemctl is-active hermes-agent.service
REMOTE

# 5. Report any surviving container deployment. Removal is a separate, explicit
#    operator decision so the previous deployment stays available for rollback.
ssh -o BatchMode=yes "root@${HUB}" \
    'command -v docker >/dev/null 2>&1 && docker ps --format "{{.Names}}" 2>/dev/null | grep -x hermes || echo "no hermes container running"'

printf '=> migration complete. Rollback: systemctl disable --now hermes-agent.service\n'
```

```bash
chmod +x scripts/ops/migrate-hermes-off-docker.sh
```

- [ ] **Step 6: Run test to verify it passes**

Run: `.venv/Scripts/python.exe -m pytest tests/test_omarchy_agent_matrix_stub.py -v`

Expected: PASS, 5 passed.

- [ ] **Step 7: Verify the migration script refuses an unapproved run**

Run: `bash scripts/ops/migrate-hermes-off-docker.sh`

Expected: `FAIL: refusing to mutate hub unit state without --confirm`, exit 1.

Run: `bash scripts/ops/migrate-hermes-off-docker.sh --confirm`

Expected: `FAIL: CAMELOT_DASHBOARD_OPERATOR_TOKEN is not set; HUMAN_GATE not satisfied`, exit 1.

- [ ] **Step 8: Commit**

```bash
git add infra/systemd/hermes-agent.service scripts/ops/migrate-hermes-off-docker.sh control_plane/dispatch/omarchy_agent_matrix.py tests/test_omarchy_agent_matrix_stub.py
git commit -m "feat: migrate Hermes off containers onto a native systemd unit"
```

---

## Task 10: Verified hub ingest and Tailscale-only push

**Files:**
- Create: `control_plane/distro/hub_push.py`
- Create: `05_INFRASTRUCTURE/distro/hub/camelot-distro-ingest.sh`
- Create: `05_INFRASTRUCTURE/distro/hub/camelot-distro-ingest.service`
- Create: `05_INFRASTRUCTURE/distro/hub/camelot-distro-ingest.path`
- Test: `tests/test_distro_hub_push.py`

**Interfaces:**
- Consumes: `seal_manifest`, `verify_manifest`, `load_signing_key` from Task 2; the ISO from Task 8; `gate_release` from Task 3.
- Produces: `TAILNET_ALLOWED_HOSTS`, `assert_tailnet_only(host: str) -> None`, `ingest_path(version: str) -> str`, `remote_verify_command(version: str, sha256: str) -> list[str]`, `push_release(...) -> dict`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_distro_hub_push.py
import pytest

from control_plane.distro.hub_push import (
    TAILNET_ALLOWED_HOSTS,
    assert_tailnet_only,
    ingest_path,
    remote_verify_command,
)


def test_refuses_a_public_host() -> None:
    with pytest.raises(ValueError, match="non-tailnet"):
        assert_tailnet_only("example.com")


def test_refuses_the_public_vps_address() -> None:
    """162.35.107.134 is the hub's public address. Only tailnet addresses are
    permitted so that a misconfigured push cannot traverse the public WAN."""
    with pytest.raises(ValueError, match="non-tailnet"):
        assert_tailnet_only("162.35.107.134")


@pytest.mark.parametrize("host", sorted(TAILNET_ALLOWED_HOSTS))
def test_allows_every_configured_tailnet_host(host: str) -> None:
    assert_tailnet_only(host) is None


def test_refuses_an_empty_host() -> None:
    with pytest.raises(ValueError):
        assert_tailnet_only("")


def test_ingest_path_is_versioned_under_inbox() -> None:
    assert ingest_path("4.0.2+camelot.1") == "/srv/camelot/distro/inbox/4.0.2+camelot.1"


def test_remote_verify_command_checks_sha256() -> None:
    cmd = remote_verify_command("4.0.2+camelot.1", "a" * 64)
    joined = " ".join(cmd)
    assert "sha256sum" in joined
    assert "a" * 64 in joined
    assert "inbox/4.0.2+camelot.1" in joined


def test_remote_verify_command_uses_no_container_runtime() -> None:
    joined = " ".join(remote_verify_command("v", "b" * 64))
    for forbidden in ("docker", "podman", "containerd"):
        assert forbidden not in joined
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest tests/test_distro_hub_push.py -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'control_plane.distro.hub_push'`

- [ ] **Step 3: Write the push client**

```python
# control_plane/distro/hub_push.py
# SPDX-License-Identifier: MIT
"""
Publish a sealed Camelot-OS release to the VPS hub.

Transport is Tailscale-only and fails closed. `assert_tailnet_only` deliberately
rejects the hub's public address: the hub is reachable both ways, and a push that
silently used the public path would move release artifacts across the open
internet and defeat the perimeter.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence

HUB_ROOT = "/srv/camelot/distro"
INBOX = f"{HUB_ROOT}/inbox"
RELEASES = f"{HUB_ROOT}/releases"

# Tailnet addresses for the hub only. The public address 162.35.107.134 is
# intentionally absent.
TAILNET_ALLOWED_HOSTS = frozenset(
    {
        "100.71.218.75",   # kba-services, Linux remote services node
        "100.110.180.18",  # hub tailnet interface
        "kba-services",
    }
)

PUBLIC_HUB_ADDRESS = "162.35.107.134"


def assert_tailnet_only(host: str) -> None:
    if not host:
        raise ValueError("empty host is not a permitted distro push target")
    if host == PUBLIC_HUB_ADDRESS or host not in TAILNET_ALLOWED_HOSTS:
        raise ValueError(
            f"refusing to push distro artifacts to non-tailnet host {host!r}; "
            f"permitted: {sorted(TAILNET_ALLOWED_HOSTS)}"
        )


def ingest_path(version: str) -> str:
    return f"{INBOX}/{version}"


def release_path(version: str) -> str:
    return f"{RELEASES}/{version}"


def remote_verify_command(version: str, sha256: str) -> List[str]:
    return [
        "bash",
        "-c",
        f"set -euo pipefail; cd {ingest_path(version)}; "
        f'echo "{sha256}  *" | sha256sum -c -',
    ]


def local_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True)
class PushResult:
    version: str
    host: str
    ingest_path: str
    artifacts: List[str]
    sha256: Dict[str, str]
    verified: bool


def push_release(
    *,
    host: str,
    version: str,
    artifacts: Sequence[Path],
    dry_run: bool = False,
) -> PushResult:
    assert_tailnet_only(host)

    digests = {a.name: local_sha256(a) for a in artifacts}
    target = ingest_path(version)

    if not dry_run:
        subprocess.run(
            ["ssh", "-o", "BatchMode=yes", f"root@{host}",
             f"install -d -m 0755 {target}"],
            check=True,
        )
        subprocess.run(
            ["scp", "-o", "BatchMode=yes",
             *[str(a) for a in artifacts], f"root@{host}:{target}/"],
            check=True,
        )

    return PushResult(
        version=version,
        host=host,
        ingest_path=target,
        artifacts=[a.name for a in artifacts],
        sha256=digests,
        verified=False,
    )


def _main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Push a sealed distro release to the hub")
    parser.add_argument("--host", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--artifact", action="append", default=[])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    try:
        assert_tailnet_only(args.host)
    except ValueError as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 1

    result = push_release(
        host=args.host,
        version=args.version,
        artifacts=[Path(a) for a in args.artifact],
        dry_run=args.dry_run,
    )
    print(json.dumps(asdict(result), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
```

- [ ] **Step 4: Write the hub-side ingest**

```bash
#!/usr/bin/env bash
# 05_INFRASTRUCTURE/distro/hub/camelot-distro-ingest.sh
#
# Hub-side ingest for pushed Camelot-OS releases.
#
# Verifies sha256 and the Ed25519 seal against the pinned public key before the
# artifact becomes visible. Failure leaves the artifact in inbox/ and writes a
# rejection receipt. No container runtime is involved.

set -euo pipefail

HUB_ROOT="/srv/camelot/distro"
INBOX="${HUB_ROOT}/inbox"
RELEASES="${HUB_ROOT}/releases"
RECEIPTS="${HUB_ROOT}/receipts"
CURRENT="${HUB_ROOT}/current"
PUBKEY="${CAMELOT_DISTRO_PUBKEY:-/etc/camelot/distro-signing.pub}"

log()  { printf '=> %s\n' "$*"; }
fail() { printf 'FAIL: %s\n' "$*" >&2; exit 1; }

command -v docker >/dev/null 2>&1 && \
    log "note: container runtime present on hub but unused by this path"

install -d -m 0755 "$RELEASES" "$RECEIPTS"
[[ -f "$PUBKEY" ]] || fail "missing pinned public key $PUBKEY"

processed=0
for staging in "$INBOX"/*/; do
    [[ -d "$staging" ]] || continue
    version="$(basename "$staging")"
    manifest="${staging}manifest.json"

    if [[ ! -f "$manifest" ]]; then
        log "skip ${version}: no manifest.json"
        continue
    fi

    # 1. Verify every listed artifact digest.
    if ! python3 - "$manifest" "$staging" <<'PY'
import hashlib, json, sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
staging = Path(sys.argv[2])

for artifact in manifest.get("artifacts", []):
    target = staging / artifact["name"]
    if not target.is_file():
        raise SystemExit(f"missing artifact {artifact['name']}")
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    if digest != artifact["sha256"]:
        raise SystemExit(f"sha256 mismatch for {artifact['name']}")
print("digests ok")
PY
    then
        printf '{"version":"%s","result":"rejected","reason":"digest"}\n' "$version" \
            >> "$RECEIPTS/rejections.jsonl"
        fail "digest verification failed for $version"
    fi

    # 2. Verify the Ed25519 seal against the pinned public key.
    if ! python3 - "$manifest" "$PUBKEY" <<'PY'
import json, sys
from pathlib import Path
sys.path.insert(0, "/opt/camelot")
from control_plane.distro.manifest import load_public_key, verify_manifest

manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
if not verify_manifest(manifest, load_public_key(sys.argv[2])):
    raise SystemExit("seal verification failed")
print("seal ok")
PY
    then
        printf '{"version":"%s","result":"rejected","reason":"seal"}\n' "$version" \
            >> "$RECEIPTS/rejections.jsonl"
        fail "seal verification failed for $version"
    fi

    # 3. Atomic promote, then repoint current.
    mv "$staging" "$RELEASES/$version"
    ln -sfn "$RELEASES/$version" "$CURRENT"
    printf '{"version":"%s","result":"accepted"}\n' "$version" \
        >> "$RECEIPTS/accepted.jsonl"
    log "accepted $version"
    processed=$((processed + 1))
done

log "processed ${processed} release(s)"
```

```bash
chmod +x 05_INFRASTRUCTURE/distro/hub/camelot-distro-ingest.sh
```

- [ ] **Step 5: Write the path and service units**

```ini
# 05_INFRASTRUCTURE/distro/hub/camelot-distro-ingest.path
[Unit]
Description=Watch for pushed Camelot-OS distro releases
Documentation=file:/srv/camelot/distro

[Path]
PathExistsGlob=/srv/camelot/distro/inbox/*
Unit=camelot-distro-ingest.service
MakeDirectory=yes
DirectoryMode=0755

[Install]
WantedBy=multi-user.target
```

```ini
# 05_INFRASTRUCTURE/distro/hub/camelot-distro-ingest.service
[Unit]
Description=Verify and promote a pushed Camelot-OS distro release
After=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/libexec/camelot-distro-ingest.sh
User=root
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ReadWritePaths=/srv/camelot/distro
MemoryMax=512M
StandardOutput=journal
StandardError=journal
SyslogIdentifier=camelot-distro-ingest
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `.venv/Scripts/python.exe -m pytest tests/test_distro_hub_push.py -v`

Expected: PASS, 8 passed.

- [ ] **Step 7: Verify the tailnet guard blocks the public address**

Run: `.venv/Scripts/python.exe -m control_plane.distro.hub_push --host 162.35.107.134 --version 4.0.2+camelot.1 --dry-run; echo "exit=$?"`

Expected: `BLOCKED: refusing to push distro artifacts to non-tailnet host ...`, `exit=1`.

- [ ] **Step 8: Distribute the public key to the hub, out of band**

The public key generated in Task 2 Step 5 goes to `/etc/camelot/distro-signing.pub`
on the hub. Verify it arrived and that the private key never left the machine that
built the release:

```bash
ssh -o BatchMode=yes root@100.110.180.18 'ls -l /etc/camelot/distro-signing.pub'
grep -rl "BEGIN PRIVATE KEY" . --include=* 2>/dev/null | grep -v node_modules || echo "ok: no private key in the tree"
```

Expected: the public key exists on the hub; the grep prints `ok`.

- [ ] **Step 9: Commit**

```bash
git add control_plane/distro/hub_push.py tests/test_distro_hub_push.py 05_INFRASTRUCTURE/distro/hub/
git commit -m "feat: add verified hub ingest and tailnet-only release push"
```

---

## Task 11: Hermes consumption contract, runbook, and northstar rule

Closing task: makes the manifest consumable, documents the whole path, and records
the durable no-Docker preference so it survives this conversation.

**Files:**
- Create: `control_plane/distro/hermes_contract.py`
- Modify: `AGENTS.md` (append `Rule 10` under `## Learned Rules`)
- Create: `docs/operations/camelot-os-distro.md`
- Test: `tests/test_hermes_contract.py`

**Interfaces:**
- Consumes: `load_public_key`, `verify_manifest` from Task 2; the layout from Task 10.
- Produces: `DistroRelease`, `read_current_release(hub_root: Path, pubkey_path: Path) -> DistroRelease`, raising `ManifestRejected` on any failure.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_hermes_contract.py
import json
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from control_plane.distro.hermes_contract import ManifestRejected, read_current_release
from control_plane.distro.manifest import seal_manifest


def _hub(tmp_path: Path, *, channel: str = "stable"):
    """Returns (hub_root, pubkey_path, release_dir, signing_key). The key is
    returned so tests that must reach a post-seal check can reseal with the hub's
    own key rather than a throwaway one."""
    key = Ed25519PrivateKey.generate()
    pub = tmp_path / "distro-signing.pub"
    pub.write_bytes(key.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))

    release_dir = tmp_path / "releases" / "4.0.2+camelot.1"
    release_dir.mkdir(parents=True)
    manifest = seal_manifest(
        {"schema_version": 1, "arch": "x86_64",
         "release": {"version": "4.0.2+camelot.1", "channel": channel},
         "artifacts": [], "hotpath": {"container_runtime_required": False}},
        key, key_id="test")
    (release_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    current = tmp_path / "current"
    current.symlink_to(release_dir, target_is_directory=True)
    return tmp_path, pub, release_dir, key


def test_reads_a_valid_release(tmp_path: Path) -> None:
    hub, pub, _, _ = _hub(tmp_path)
    release = read_current_release(hub, pub)
    assert release.version == "4.0.2+camelot.1"
    assert release.channel == "stable"
    assert release.container_runtime_required is False


def test_rejects_a_tampered_manifest(tmp_path: Path) -> None:
    hub, pub, release_dir, _ = _hub(tmp_path)
    manifest = json.loads((release_dir / "manifest.json").read_text(encoding="utf-8"))
    manifest["release"]["channel"] = "edge"
    (release_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ManifestRejected, match="seal"):
        read_current_release(hub, pub)


def test_rejects_a_manifest_signed_by_another_key(tmp_path: Path) -> None:
    hub, pub, release_dir, _ = _hub(tmp_path)
    other = Ed25519PrivateKey.generate()
    manifest = seal_manifest(
        {"schema_version": 1, "arch": "x86_64",
         "release": {"version": "4.0.2+camelot.1", "channel": "stable"},
         "artifacts": [], "hotpath": {"container_runtime_required": False}},
        other, key_id="impostor")
    (release_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ManifestRejected, match="seal"):
        read_current_release(hub, pub)


def test_rejects_an_unsupported_schema_version(tmp_path: Path) -> None:
    """The schema check runs before the seal, so any key reaches it."""
    hub, pub, release_dir, _ = _hub(tmp_path)
    key = Ed25519PrivateKey.generate()
    manifest = seal_manifest(
        {"schema_version": 99, "arch": "x86_64",
         "release": {"version": "x", "channel": "stable"}, "artifacts": [],
         "hotpath": {"container_runtime_required": False}}, key, key_id="t")
    (release_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ManifestRejected, match="schema"):
        read_current_release(hub, pub)


def test_rejects_a_manifest_requiring_a_container_runtime(tmp_path: Path) -> None:
    """Must be sealed with the hub's own key, otherwise the seal check rejects
    first and the container assertion is never reached."""
    hub, pub, release_dir, key = _hub(tmp_path)
    manifest = seal_manifest(
        {"schema_version": 1, "arch": "x86_64",
         "release": {"version": "4.0.2+camelot.1", "channel": "stable"},
         "artifacts": [], "hotpath": {"container_runtime_required": True}},
        key, key_id="test")
    (release_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ManifestRejected, match="container"):
        read_current_release(hub, pub)


def test_rejects_a_missing_current_symlink(tmp_path: Path) -> None:
    hub, pub, _, _ = _hub(tmp_path)
    (hub / "current").unlink()
    with pytest.raises(ManifestRejected, match="current"):
        read_current_release(hub, pub)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest tests/test_hermes_contract.py -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'control_plane.distro.hermes_contract'`

- [ ] **Step 3: Write the implementation**

```python
# control_plane/distro/hermes_contract.py
# SPDX-License-Identifier: MIT
"""
Hermes-side consumption of the sealed Camelot-OS distro manifest.

Fail-closed by design. Every rejection path raises rather than returning a
partially-trusted release, because Hermes acting on an unverified artifact is
worse than Hermes acting on nothing.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Union

from control_plane.distro.manifest import load_public_key, verify_manifest

SUPPORTED_SCHEMA_VERSIONS = frozenset({1})
CURRENT_LINK = "current"
MANIFEST_NAME = "manifest.json"


class ManifestRejected(Exception):
    """Raised when the current release cannot be trusted."""


@dataclass(frozen=True)
class DistroRelease:
    version: str
    channel: str
    arch: str
    container_runtime_required: bool
    manifest_path: str


def read_current_release(
    hub_root: Union[Path, str], pubkey_path: Union[Path, str]
) -> DistroRelease:
    hub_root = Path(hub_root)
    current = hub_root / CURRENT_LINK

    if not current.exists():
        raise ManifestRejected(f"no {CURRENT_LINK} release present under {hub_root}")

    manifest_path = (current / MANIFEST_NAME) if current.is_dir() else current.resolve()

    try:
        manifest: Dict[str, Any] = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestRejected(f"unreadable manifest at {manifest_path}: {exc}") from exc

    schema_version = manifest.get("schema_version")
    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        raise ManifestRejected(
            f"unsupported schema_version {schema_version!r}; "
            f"supported: {sorted(SUPPORTED_SCHEMA_VERSIONS)}"
        )

    try:
        public_key = load_public_key(pubkey_path)
    except (OSError, TypeError) as exc:
        raise ManifestRejected(f"cannot load pinned public key {pubkey_path}: {exc}") from exc

    if not verify_manifest(manifest, public_key):
        raise ManifestRejected(
            f"seal verification failed for {manifest_path}; refusing to trust it"
        )

    hotpath = manifest.get("hotpath") or {}
    if hotpath.get("container_runtime_required"):
        raise ManifestRejected(
            "manifest declares container_runtime_required=true; "
            "this violates the Camelot-OS no-runtime constraint"
        )

    release = manifest.get("release") or {}
    return DistroRelease(
        version=release.get("version", "unknown"),
        channel=release.get("channel", "unknown"),
        arch=manifest.get("arch", "unknown"),
        container_runtime_required=bool(hotpath.get("container_runtime_required")),
        manifest_path=str(manifest_path),
    )


def _main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Read the current sealed distro release")
    parser.add_argument("--hub-root", default="/srv/camelot/distro")
    parser.add_argument("--pubkey", default="/etc/camelot/distro-signing.pub")
    args = parser.parse_args(argv)

    try:
        release = read_current_release(args.hub_root, args.pubkey)
    except ManifestRejected as exc:
        print(f"REJECTED: {exc}", file=sys.stderr)
        return 1

    print(f"version={release.version} channel={release.channel} arch={release.arch}")
    print(f"manifest={release.manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/Scripts/python.exe -m pytest tests/test_hermes_contract.py -v`

Expected: PASS, 6 passed.

- [ ] **Step 5: Append the northstar rule**

Under `## Learned Rules` in `AGENTS.md`, after `Rule 9`, append:

```markdown
Rule 10: [Architecture/Distro] - ALWAYS treat `systemd-nspawn` (Arch `devtools`)
as the only sanctioned build-isolation primitive in Camelot-OS, and NEVER require
Docker, Podman, containerd, or any container runtime in the distro build path,
the installed runtime, or the VPS hub ingest path, because the northstar is
enterprise-level agentic operation on low-end consumer hardware, where a
container runtime is pure overhead and an additional supply-chain surface.
`omarchy-pkgs` used Docker for per-channel base isolation and foreign-architecture
emulation; the x86_64-only scope removes the second need, and per-channel nspawn
roots under `/var/lib/camelot-build` remove the first.
```

Per the Genome Evolution Protocol this appends a rule and rewrites none.

- [ ] **Step 6: Write the operations runbook**

```markdown
# Camelot-OS Distro Runbook

Derived from `docs/superpowers/specs/2026-09-15-camelot-os-omarchy-distro-design.md`.

## What this is

A bootable x86_64 Camelot-OS ISO built from the Omarchy stack, installing
unattended, booting a native systemd agent stack, and publishing a sealed manifest
the VPS hub verifies before Hermes reads it.

## Layout on the hub

```
/srv/camelot/distro/
  inbox/<version>/       pushed here, not yet trusted
  releases/<version>/    verified, promoted
  receipts/accepted.jsonl
  receipts/rejections.jsonl
  current -> releases/<version>
```

## Build sequence

```bash
# 1. On the Arch builder host
sudo 05_INFRASTRUCTURE/distro/builder/provision-builder.sh --self-test
sudo 05_INFRASTRUCTURE/distro/builder/provision-builder.sh --provision

# 2. Sync the profile into the fork
CAMELOT_PKGS_PKGBUILDS=../camelot-pkgs/pkgbuilds \
  bash 05_INFRASTRUCTURE/distro/builder/sync-profile.sh

# 3. Build the profile package into each channel
bash 05_INFRASTRUCTURE/distro/builder/nspawn-build.sh edge camelot-os-profile

# 4. Build the ISO
source 05_INFRASTRUCTURE/distro/iso/camelot-iso.env
../camelot-iso/bin/omarchy-iso-make --local-source ../omarchy ../camelot-pkgs
../camelot-iso/bin/omarchy-iso-test release/camelot-<version>.iso
```

## Publish sequence

Publishing is HUMAN_GATE. Both the approval and the operator token are required.

```bash
.venv/Scripts/python.exe -m control_plane.distro.release_gate \
  --version 4.0.2+camelot.1 --channel stable --artifacts 3 --approved
# Expect: allowed=True tier=HUMAN_GATE

.venv/Scripts/python.exe -m control_plane.distro.hub_push \
  --host 100.110.180.18 --version 4.0.2+camelot.1 \
  --artifact release/camelot-4.0.2+camelot.1.iso

ssh root@100.110.180.18 systemctl start camelot-distro-ingest.service
ssh root@100.110.180.18 cat /srv/camelot/distro/receipts/accepted.jsonl
```

## Verification, in order

```bash
.venv/Scripts/python.exe -m control_plane.distro.docker_inventory --root .
# Expect: blockers=0

.venv/Scripts/python.exe -m control_plane.distro.hermes_contract
# Expect: version=... channel=... arch=x86_64
```

## Failure handling

| Symptom | Meaning | Action |
| --- | --- | --- |
| `BLOCKER` lines from the inventory | A container surface reached the release path | Fix the surface; do not publish |
| `host is not linux` / `not Arch Linux` | Wrong build host | Move to the Task 4 builder |
| `MISSING mkarchiso` | archiso absent on the builder | `pacman -S archiso` |
| `FORBIDDEN docker present` | Container runtime on the builder | Remove it; the build must not need it |
| `digest verification failed` | Transport corruption | Re-push; the artifact stays in `inbox/` |
| `seal verification failed` | Wrong key or tampered manifest | Do not promote; re-sign with the correct key |
| `refusing to push ... non-tailnet host` | Misconfigured push target | Use a tailnet address |

Rejection receipts are append-only and are the audit trail for refused artifacts.

## Rollback

```bash
# Revert to the previous release
ln -sfn /srv/camelot/distro/releases/<previous-version> /srv/camelot/distro/current

# Revert Hermes to the previous deployment
ssh root@100.110.180.18 'systemctl disable --now hermes-agent.service'
```

## Known debt

- `control_plane/cartridges/qr_bridge.py` advertises Ed25519 signing but produces
  a keyless SHA-256 digest, so its "signature" is forgeable and its verification
  cannot fail under a different key. It is out of scope here and needs its own
  task.
- Anya Gate routes a distro-build intent to `sir_link` rather than `SIR_KAY`.
  Either the root `AGENTS.md` roster gains `sir_link` or the lane is repointed.
  Operator's call.
```

- [ ] **Step 7: Run the full distro test suite**

Run: `.venv/Scripts/python.exe -m pytest tests/test_docker_inventory.py tests/test_distro_manifest.py tests/test_distro_release_gate.py tests/test_distro_profile.py tests/test_cidata_profile.py tests/test_distro_iso_build.py tests/test_omarchy_agent_matrix_stub.py tests/test_distro_hub_push.py tests/test_hermes_contract.py -v`

Expected: all pass. Record the counts.

- [ ] **Step 8: Commit**

```bash
git add control_plane/distro/hermes_contract.py tests/test_hermes_contract.py docs/operations/camelot-os-distro.md AGENTS.md
git commit -m "feat: add Hermes distro consumption contract, runbook, and no-container rule"
```

---

## Self-review

**Spec coverage.** Every spec section maps to a task:

| Spec section | Task |
| --- | --- |
| Findings F1-F7 | Task 1 (F1-F3, F5-F7 baseline), Task 11 Step 5/Step 6 (F4, F7 recorded as debt) |
| Topology | Tasks 4, 8, 9, 10 |
| One primitive replaces Docker | Task 4 (roots), Task 5 (package builds), Task 8 (ISO) |
| Upstream fork map | Tasks 5 (`sync-profile.sh`), 8 (`camelot-iso.env`), 10 |
| Versioning and channels | Task 6 (`.omarchy/package.json`), Task 8 (`CAMELOT_ISO_VERSION`) |
| Hardware floor and memory budget | Task 6 (slice units + budget conf), Task 7 (4 GB profile values) |
| Seal requirements 1-4 | Task 2, with requirement 2 as the explicit discriminator test |
| Hub contract | Task 10 (ingest + path unit), Task 11 (Hermes consumption) |
| Governance map | Task 3 (release gate), Task 4 (builder PROMPT), Task 9 (HUMAN_GATE migration) |
| Open question 1 (builder host) | Task 4, with Step 4 accepting a negative result as a valid outcome |
| Open questions 2-5 | Recorded in the runbook's debt section, not silently resolved |

**Placeholder scan.** No `TBD`, no "implement later", no "add appropriate error
handling". Every code step carries runnable code. Two steps intentionally defer to
the operator rather than inventing values: Task 4 Step 3 (channel mirror URLs) and
Task 7 Step 6 (configurator schema reconciliation). Both name exactly what the
operator must supply. Neither is a placeholder in the "figure it out" sense.

**Type and name consistency.** Verified across tasks:

- `canonical_bytes`, `seal_manifest`, `verify_manifest`, `key_id_for`,
  `load_signing_key`, `load_public_key` — Task 2 definitions, used identically in
  Tasks 10 and 11.
- `InventoryReport.release_path_blockers()` — Task 1 definition, used in the
  runbook's verification section.
- `HostCapability.blockers()` — Task 8 definition; the test helper `_cap` passes
  `arch="x86_64"` and every test asserts against that same signature.
- `ReleaseIntent(version, channel, artifact_count)` — Task 3; the CLI in Step 5 and
  the runbook pass exactly these.
- `ManifestRejected` — Task 11; raised on all five rejection paths, each asserted
  by a distinct test.
- `TAILNET_ALLOWED_HOSTS`, `assert_tailnet_only`, `ingest_path`,
  `remote_verify_command` — Task 10 definitions; all four used in the runbook.
- Slice names and `MemoryMax` values — Task 6 units and `camelot-slice-budget.conf`
  carry identical values to the spec table; the parametrized test enforces it.
- `hermes-agent.service` binds `Slice=camelot-workers.slice`, which Task 6 installs.

**Three defects found and fixed during this self-review**, all of which would
have shipped as failures or as a false security claim:

1. **Task 10 permitted the public WAN.** An earlier draft listed `162.35.107.134`
   in `TAILNET_ALLOWED_HOSTS`. The hub is reachable at both that public address
   and on the tailnet, so this would have let release artifacts cross the open
   internet while the spec claimed Tailscale-only transport. The address is now
   `PUBLIC_HUB_ADDRESS` and explicitly rejected, with a test asserting the
   rejection.
2. **Task 11's container-runtime test could never pass.** It resealed the manifest
   with a throwaway key, so `verify_manifest` rejected it and the container check
   was never reached — the test would have errored on the wrong assertion
   message. `_hub()` now returns the signing key so that test reseals with the
   hub's own key and actually exercises the constraint it names.
3. **Task 8's acceptance test was platform-dependent.** `str(Path(...))` yields
   backslashes on Windows, so `"release/camelot.iso" in cmd` would have failed
   here and passed on Linux. `build_iso_command` and `acceptance_command` now emit
   `.as_posix()`.

Defect 1 is the one worth dwelling on: it was a *silent* weakening of a security
property, in the task that moves release artifacts. Defects 2 and 3 were ordinary
test bugs. This is the argument for writing the verification step adjacent to the
code step rather than deferring it.
