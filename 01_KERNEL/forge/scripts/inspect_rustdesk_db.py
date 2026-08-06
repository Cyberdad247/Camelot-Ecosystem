# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os
import sqlite3

db_path = r"c:\Users\vizio\rustdesk-server\data\db_v2.sqlite3"

if not os.path.exists(db_path):
    print(f"Error: Database not found at {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # List tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

    # Store table names in a list first, as we'll reuse the cursor for fetching rows
    tables = [row[0] for row in cursor]
    print(f"Tables: {tables}")

    for table_name in tables:
        print(f"\n--- Content of {table_name} ---")
        # Securely quote the table name to prevent SQL injection
        escaped_name = table_name.replace('"', '""')
        safe_table_name = f'"{escaped_name}"'
        cursor.execute(f"SELECT * FROM {safe_table_name} LIMIT 10;")
        for row in cursor:
            print(row)

    conn.close()
except Exception as e:
    print(f"Error reading database: {e}")
