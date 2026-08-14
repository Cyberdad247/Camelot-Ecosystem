# SPDX-License-Identifier: MIT

"""One-shot compression script — dedup saltare, gzip archival text, archive assimilation_7."""
import gzip
import hashlib
import os
import shutil
import tarfile
from pathlib import Path

os.chdir(Path(__file__).resolve().parent.parent)

saved_total = 0

# ── 1. Deduplicate identical saltare pair (hard link) ──────────────────────
print("=== 1. SALTARE DEDUP ===")
canon = Path("bin/saltare.exe")
dupe = Path("kinetic_edge/saltare/saltare.exe")

if canon.exists() and dupe.exists():
    canon_size = canon.stat().st_size
    dupe_size = dupe.stat().st_size
    print(f"  Canon: {canon} ({canon_size/(1024*1024):.1f}MB)")
    print(f"  Dupe:  {dupe} ({dupe_size/(1024*1024):.1f}MB)")

    ch = hashlib.sha256(canon.read_bytes()).hexdigest()
    dh = hashlib.sha256(dupe.read_bytes()).hexdigest()
    match = ch == dh
    print(f"  Hashes match: {match}")

    if match:
        dupe.unlink()
        try:
            os.link(str(canon), str(dupe))
        except OSError:
            # Restore from canon if hard link fails
            shutil.copy2(str(canon), str(dupe))
            print("  WARNING: hard link failed, restored via copy")
        saved_total += dupe_size
        print(f"  HARDLINK created: {dupe} -> {canon}")
        print(f"  SAVED: {dupe_size/(1024*1024):.1f}MB (double-counting eliminated)")
    else:
        print("  SKIPPED: hashes differ")
else:
    print(f"  SKIPPED: one or both missing (canon={canon.exists()}, dupe={dupe.exists()})")

# ── 2. Gzip archival text files ────────────────────────────────────────────
print()
print("=== 2. ARCHIVAL TEXT GZIP ===")

text_targets = [
    "99_HISTORY/harness_queue_archive/harness_queue.20260520-100450.jsonl",
    "03_VAULT/runtime_state/sir_codex_directory_purge/user_home_audit/sir_codex_directory_purge_report.json",
    "03_VAULT/training/configs/memory/lt_local/memories.jsonl",
    "03_VAULT/Missions/verification_ledger.jsonl",
    "03_VAULT/runtime_state/squire_index_scan.json",
]

for fp in text_targets:
    p = Path(fp)
    if not p.exists():
        print(f"  MISSING: {fp}")
        continue
    orig = p.stat().st_size
    compressed = gzip.compress(p.read_bytes(), compresslevel=6)
    gz_path = p.with_suffix(p.suffix + ".gz")
    gz_path.write_bytes(compressed)
    # Delete original to actually free disk space
    p.unlink()
    new_size = gz_path.stat().st_size
    saved = orig - new_size
    saved_total += saved
    print(f"  {orig/(1024*1024):5.1f}MB -> {new_size/(1024*1024):5.1f}MB "
          f"(saved {saved/(1024*1024):.1f}MB)  {fp}")

# ── 3. Tar.gz assimilation_7 ───────────────────────────────────────────────
print()
print("=== 3. ASSIMILATION_7 ARCHIVE ===")

assim_dir = Path("03_VAULT/runtime_state/assimilation_7")
if assim_dir.exists():
    # Measure total size
    total = 0
    for root, _dirs, files in os.walk(assim_dir):
        for f in files:
            try:
                total += (Path(root) / f).stat().st_size
            except OSError:
                pass

    print(f"  Original: {total/(1024*1024):.1f} MB ({assim_dir})")

    # Create tar.gz
    archive_path = Path("03_VAULT/runtime_state/assimilation_7.tar.gz")
    print("  Compressing...")
    with tarfile.open(archive_path, "w:gz", compresslevel=6) as tar:
        tar.add(assim_dir, arcname="assimilation_7")

    # Verify archive integrity before deleting original
    print("  Verifying...")
    try:
        with tarfile.open(archive_path, "r:gz") as tf:
            member_count = len(tf.getmembers())
        print(f"  Verified: {member_count} members")
    except Exception as e:
        print(f"  Archive VERIFICATION FAILED: {e} — NOT deleting original")
        print(f"  Original kept: {assim_dir}")
        archive_path.unlink()
        continue_flag = False
        # Can't use 'continue' here, use a flag

    archive_size = archive_path.stat().st_size

    print(f"  Archive:  {archive_size/(1024*1024):.1f} MB")
    saved = total - archive_size
    saved_total += saved
    print(f"  SAVED: {saved/(1024*1024):.1f} MB ({(1-archive_size/total)*100:.0f}%)")

    # Remove original directory
    shutil.rmtree(assim_dir)
    print(f"  REMOVED: {assim_dir}")
    print(f"  KEPT:    {archive_path}")
else:
    print(f"  Directory not found: {assim_dir}")

print()
print(f"===== TOTAL SAVED: {saved_total/(1024*1024):.1f} MB =====")
