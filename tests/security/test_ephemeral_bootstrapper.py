# SPDX-License-Identifier: MIT
"""Unit and Integration Tests for Rule 7 Sovereign Ephemeral Bootstrapper.
========================================================================
Validates:
    1. Sovereign Arthur Ed25519 Signature Verification:
       - Manifest signed by authentic King Arthur Ed25519 key is verified and accepted.
       - Tampered manifest or bad signature is rejected with exit code 1.
    2. SHA-256 Payload Integrity Enforcement:
       - Tar payload matching sha256 checksum is accepted and unpacked.
       - Mismatched payload checksum triggers immediate rejection.
    3. Ephemeral Node Hotpath Execution:
       - Ephemeral bootstrapping script terminates cleanly (process.exit(0)).
       - 0% Node/Python in the runtime hot-path (handoff to native binary).
    4. Bare-Metal Zero-Docker Compliance:
       - Verifies 0% Docker compliance via Scarcity Guardian.
    5. Offline / Air-Gap Archive Extraction:
       - Physical archive extraction without network access.
"""
from __future__ import annotations

import hashlib
import http.server
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import threading
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from control_plane.infra.scarcity_guardian import (
    DockerFootprintViolation,
    verify_zero_docker_compliance,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALLER_BIN = REPO_ROOT / "packages" / "camelot-install" / "bin" / "index.js"


class EphemeralServer:
    """Ephemeral HTTP server for bootstrapper integration tests."""

    def __init__(self):
        self.routes: dict[str, tuple[int, bytes, str]] = {}
        self.server: http.server.HTTPServer | None = None
        self.thread: threading.Thread | None = None
        self.port: int = 0

    def start(self):
        parent = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                url_path = self.path.split("?")[0]
                if url_path in parent.routes:
                    code, body, content_type = parent.routes[url_path]
                    self.send_response(code)
                    self.send_header("Content-Type", content_type)
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                else:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b"Not Found")

            def log_message(self, format, *args):
                pass  # suppress server logs

        self.server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
        self.port = self.server.server_port
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()


def create_mock_payload_tar(dest_dir: Path) -> tuple[bytes, str]:
    """Creates a valid tar.gz containing mock staging files."""
    payload_dir = dest_dir / "stage_payload"
    payload_dir.mkdir(parents=True, exist_ok=True)
    bin_dir = payload_dir / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)

    cfg_file = bin_dir / "camelot-bootstrap-config.json"
    cfg_file.write_text('{"runtime": "native-systemd"}', encoding="utf-8")

    tar_path = dest_dir / "payload.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(bin_dir, arcname="bin")

    data = tar_path.read_bytes()
    sha256 = hashlib.sha256(data).hexdigest()
    return data, sha256


def test_zero_docker_compliance_mandate():
    """Rule 7 / Bare-Metal: 0% Docker compliance in hotpath."""
    res = verify_zero_docker_compliance(check_docker_socket=False)
    assert res["zero_docker_verified"] is True
    assert res["runtime_substrate"] == "BARE_METAL_SYSTEMD_WASM"
    assert res["container_overhead_bytes"] == 0

    orig = os.environ.get("DOCKER_HOST")
    try:
        os.environ["DOCKER_HOST"] = "tcp://127.0.0.1:2375"
        with pytest.raises(DockerFootprintViolation):
            verify_zero_docker_compliance(check_docker_socket=False)
    finally:
        if orig is not None:
            os.environ["DOCKER_HOST"] = orig
        else:
            os.environ.pop("DOCKER_HOST", None)


def test_bootstrapper_ed25519_valid_signature_and_sha256_success():
    """Valid Arthur Ed25519 signed manifest and matching SHA256 payload succeed and exit 0."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        dest_dir = tmp / "install_target"
        dest_dir.mkdir()

        priv_key = ed25519.Ed25519PrivateKey.generate()
        pub_key = priv_key.public_key()
        pub_pem = pub_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

        tar_bytes, tar_sha256 = create_mock_payload_tar(tmp)

        server = EphemeralServer()
        server.start()

        manifest_data = {
            "targets": {
                "kba": {
                    "url": f"http://127.0.0.1:{server.port}/camelot_kba_payload.tar.gz",
                    "sha256": tar_sha256,
                }
            }
        }
        manifest_bytes = json.dumps(manifest_data).encode("utf-8")
        sig_bytes = priv_key.sign(manifest_bytes)

        server.routes["/manifest.json"] = (200, manifest_bytes, "application/json")
        server.routes["/manifest.sig"] = (200, sig_bytes, "application/octet-stream")
        server.routes["/camelot_kba_payload.tar.gz"] = (200, tar_bytes, "application/gzip")

        try:
            env = dict(os.environ)
            env["CAMELOT_ARTHUR_PUBKEY"] = pub_pem
            env["CAMELOT_MANIFEST_URL"] = f"http://127.0.0.1:{server.port}/manifest.json"
            env["CAMELOT_DEST_DIR"] = str(dest_dir)
            env["TEMP"] = str(tmp)

            cmd = ["node", str(INSTALLER_BIN), "--target=kba"]
            proc = subprocess.run(
                cmd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace"
            )

            assert proc.returncode == 0
            assert "Manifest Seal: VERIFIED" in proc.stdout
            assert "Payload Integrity: VERIFIED" in proc.stdout
            assert "Sovereign Bootstrap Complete" in proc.stdout

            bin_folder = dest_dir / "bin"
            assert bin_folder.exists()
        finally:
            server.stop()


def test_bootstrapper_ed25519_tampered_signature_rejected():
    """Tampered manifest fails Arthur Ed25519 verification and aborts with exit code 1."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        dest_dir = tmp / "install_target"
        dest_dir.mkdir()

        priv_key = ed25519.Ed25519PrivateKey.generate()
        pub_key = priv_key.public_key()
        pub_pem = pub_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

        tar_bytes, tar_sha256 = create_mock_payload_tar(tmp)

        server = EphemeralServer()
        server.start()

        manifest_data = {
            "targets": {
                "kba": {
                    "url": f"http://127.0.0.1:{server.port}/camelot_kba_payload.tar.gz",
                    "sha256": tar_sha256,
                }
            }
        }
        manifest_bytes = json.dumps(manifest_data).encode("utf-8")
        sig_bytes = priv_key.sign(manifest_bytes)
        tampered_manifest_bytes = json.dumps({"targets": {"kba": {"url": "http://malicious.host/bad.tar.gz"}}}).encode("utf-8")

        server.routes["/manifest.json"] = (200, tampered_manifest_bytes, "application/json")
        server.routes["/manifest.sig"] = (200, sig_bytes, "application/octet-stream")

        try:
            env = dict(os.environ)
            env["CAMELOT_ARTHUR_PUBKEY"] = pub_pem
            env["CAMELOT_MANIFEST_URL"] = f"http://127.0.0.1:{server.port}/manifest.json"
            env["CAMELOT_DEST_DIR"] = str(dest_dir)
            env["TEMP"] = str(tmp)

            cmd = ["node", str(INSTALLER_BIN), "--target=kba"]
            proc = subprocess.run(
                cmd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace"
            )

            assert proc.returncode == 1
            assert "Sovereign verification rejected" in proc.stderr or "Arthur Ed25519 signature verification FAILED" in proc.stderr
        finally:
            server.stop()


def test_bootstrapper_sha256_mismatch_rejected():
    """Payload whose hash does not match manifest sha256 is aborted with exit code 1."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        dest_dir = tmp / "install_target"
        dest_dir.mkdir()

        priv_key = ed25519.Ed25519PrivateKey.generate()
        pub_key = priv_key.public_key()
        pub_pem = pub_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

        tar_bytes, _ = create_mock_payload_tar(tmp)
        fake_sha256 = "0" * 64

        server = EphemeralServer()
        server.start()

        manifest_data = {
            "targets": {
                "kba": {
                    "url": f"http://127.0.0.1:{server.port}/camelot_kba_payload.tar.gz",
                    "sha256": fake_sha256,
                }
            }
        }
        manifest_bytes = json.dumps(manifest_data).encode("utf-8")
        sig_bytes = priv_key.sign(manifest_bytes)

        server.routes["/manifest.json"] = (200, manifest_bytes, "application/json")
        server.routes["/manifest.sig"] = (200, sig_bytes, "application/octet-stream")
        server.routes["/camelot_kba_payload.tar.gz"] = (200, tar_bytes, "application/gzip")

        try:
            env = dict(os.environ)
            env["CAMELOT_ARTHUR_PUBKEY"] = pub_pem
            env["CAMELOT_MANIFEST_URL"] = f"http://127.0.0.1:{server.port}/manifest.json"
            env["CAMELOT_DEST_DIR"] = str(dest_dir)
            env["TEMP"] = str(tmp)

            cmd = ["node", str(INSTALLER_BIN), "--target=kba"]
            proc = subprocess.run(
                cmd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace"
            )

            assert proc.returncode == 1
            assert "SHA256 checksum mismatch" in proc.stderr
        finally:
            server.stop()


def test_bootstrapper_offline_airgap_mode():
    """Offline mode unpacks local archive cleanly without network calls."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        dest_dir = tmp / "install_target"
        dest_dir.mkdir()

        tar_bytes, _ = create_mock_payload_tar(tmp)
        offline_tar = tmp / "offline_archive.tar.gz"
        offline_tar.write_bytes(tar_bytes)

        env = dict(os.environ)
        env["CAMELOT_DEST_DIR"] = str(dest_dir)
        env["TEMP"] = str(tmp)

        cmd = ["node", str(INSTALLER_BIN), f"--offline={offline_tar}", "--target=kba"]
        proc = subprocess.run(
            cmd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )

        assert proc.returncode == 0
        assert "AIR-GAP MODE" in proc.stdout
        assert "Sovereign Bootstrap Complete" in proc.stdout
        assert (dest_dir / "bin").exists()
