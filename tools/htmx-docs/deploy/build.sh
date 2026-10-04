#!/usr/bin/env bash
# N080: Build script for HTMX Documentation Site
set -e

echo "[+] Compiling static Go binary..."
# Go binaries are statically linked, meaning no Docker or external runtime is required.
GOOS=linux GOARCH=amd64 go build -o htmx-docs-server .

echo "[+] Creating release bundle (N081)..."
mkdir -p release/static release/templates release/docs
cp htmx-docs-server release/
cp -r static/* release/static/
cp -r templates/* release/templates/
cp -r docs/* release/docs/

echo "[+] Packaging tarball..."
tar -czvf htmx-docs-release.tar.gz -C release .
rm -rf release

echo "[+] Build complete: htmx-docs-release.tar.gz ready for deployment."
