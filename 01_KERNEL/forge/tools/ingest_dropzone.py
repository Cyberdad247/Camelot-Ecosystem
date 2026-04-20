# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os
import shutil
from pathlib import Path

from appwrite.client import Client
from appwrite.id import ID
from appwrite.services.databases import Databases

# 🛡️ SETTINGS
VAULT_ROOT = Path(r"C:\Users\vizio\CAMELOT_OS\03_VAULT")
SOURCE_FOLDER = VAULT_ROOT / "SENSES"
HISTORY_FOLDER = VAULT_ROOT / "99_HISTORY"


def ingest_new_wisdom():
    print(f"👂 [LUKAS] Listening to the Drop-Zone: {SOURCE_FOLDER}")

    # Verify Credentials
    if not os.environ.get("APPWRITE_ENDPOINT"):
        print("❌ [ERR] APPWRITE_ENDPOINT not set. Cannot ingest.")
        return

    try:
        client = Client()
        client.set_endpoint(os.environ["APPWRITE_ENDPOINT"])
        client.set_project(os.environ["APPWRITE_PROJECT_ID"])
        client.set_key(os.environ["APPWRITE_API_KEY"])
        db = Databases(client)
    except Exception as e:
        print(f"❌ [ERR] Failed to connect to Appwrite: {e}")
        return

    # Check for files
    if not SOURCE_FOLDER.exists():
        print(f"⚠️ Drop-Zone not found: {SOURCE_FOLDER}")
        return

    files = [f for f in SOURCE_FOLDER.iterdir() if f.is_file() and f.suffix in [".md", ".txt", ".pdf", ".json"]]

    if not files:
        print("💤 [LUKAS] No new senses detected.")
        return

    for file_path in files:
        print(f"🚀 [KINETIC] Ingesting {file_path.name} to Cloud Vault...")
        try:
            # Read Content (Simple read for text/md, placeholder for PDF)
            if file_path.suffix == ".pdf":
                content = f"[PDF BINARY PLACEHOLDER] - {file_path.name}"
            else:
                content = file_path.read_text(encoding="utf-8", errors="ignore")

            # Anchor to Appwrite
            db.create_document(
                database_id="Memory",
                collection_id="Sovereign_Logs",
                document_id=ID.unique(),
                data={"task_name": f"SOURCE: {file_path.name}", "result_data": content[:9000]},  # Appwrite limit safety
            )

            # Archive
            shutil.move(str(file_path), str(HISTORY_FOLDER / file_path.name))
            print(f"✅ {file_path.name} anchored and archived.")

        except Exception as e:
            print(f"❌ [ERR] Failed to ingest {file_path.name}: {e}")


if __name__ == "__main__":
    ingest_new_wisdom()