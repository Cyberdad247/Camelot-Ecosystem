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
    tables = cursor.fetchall()
    print(f"Tables: {tables}")

    for table in tables:
        table_name = table[0]
        print(f"\n--- Content of {table_name} ---")
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 10;")
        rows = cursor.fetchall()
        for row in rows:
            print(row)

    conn.close()
except Exception as e:
    print(f"Error reading database: {e}")