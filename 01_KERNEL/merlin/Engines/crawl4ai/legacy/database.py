# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os
import sqlite3
from pathlib import Path
from typing import Optional, Tuple

DB_PATH = os.path.join(os.getenv("CRAWL4_AI_BASE_DIRECTORY", Path.home()), ".crawl4ai")
os.makedirs(DB_PATH, exist_ok=True)
DB_PATH = os.path.join(DB_PATH, "crawl4ai.db")


def init_db():
    global DB_PATH
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS crawled_data (
            url TEXT PRIMARY KEY,
            html TEXT,
            cleaned_html TEXT,
            markdown TEXT,
            extracted_content TEXT,
            success BOOLEAN,
            media TEXT DEFAULT "{}",
            links TEXT DEFAULT "{}",
            metadata TEXT DEFAULT "{}",
            screenshot TEXT DEFAULT ""
        )
    """
    )
    conn.commit()
    conn.close()


_ALLOWED_COLUMNS = frozenset({"media", "links", "metadata", "screenshot", "response_headers"})


def alter_db_add_screenshot(new_column: str = "media"):
    if new_column not in _ALLOWED_COLUMNS:
        raise ValueError(f"Column '{new_column}' is not in the allowed column list")
    check_db_path()
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        queries = {
            "media": 'ALTER TABLE crawled_data ADD COLUMN media TEXT DEFAULT ""',
            "links": 'ALTER TABLE crawled_data ADD COLUMN links TEXT DEFAULT ""',
            "metadata": 'ALTER TABLE crawled_data ADD COLUMN metadata TEXT DEFAULT ""',
            "screenshot": 'ALTER TABLE crawled_data ADD COLUMN screenshot TEXT DEFAULT ""',
            "response_headers": 'ALTER TABLE crawled_data ADD COLUMN response_headers TEXT DEFAULT ""'
        }
        cursor.execute(queries[new_column])

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error altering database to add screenshot column: {e}")


def check_db_path():
    if not DB_PATH:
        raise ValueError("Database path is not set or is empty.")


def get_cached_url(
    url: str,
) -> Optional[Tuple[str, str, str, str, str, str, str, bool, str]]:
    check_db_path()
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT url, html, cleaned_html, markdown, extracted_content, success, media, links, metadata, screenshot FROM crawled_data WHERE url = ?",
            (url,),
        )
        result = cursor.fetchone()
        conn.close()
        return result
    except Exception as e:
        print(f"Error retrieving cached URL: {e}")
        return None


def cache_url(
    url: str,
    html: str,
    cleaned_html: str,
    markdown: str,
    extracted_content: str,
    success: bool,
    media: str = "{}",
    links: str = "{}",
    metadata: str = "{}",
    screenshot: str = "",
):
    check_db_path()
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO crawled_data (url, html, cleaned_html, markdown, extracted_content, success, media, links, metadata, screenshot)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
                html = excluded.html,
                cleaned_html = excluded.cleaned_html,
                markdown = excluded.markdown,
                extracted_content = excluded.extracted_content,
                success = excluded.success,
                media = excluded.media,      
                links = excluded.links,    
                metadata = excluded.metadata,      
                screenshot = excluded.screenshot
        """,
            (
                url,
                html,
                cleaned_html,
                markdown,
                extracted_content,
                success,
                media,
                links,
                metadata,
                screenshot,
            ),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error caching URL: {e}")


def get_total_count() -> int:
    check_db_path()
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM crawled_data")
        result = cursor.fetchone()
        conn.close()
        return result[0]
    except Exception as e:
        print(f"Error getting total count: {e}")
        return 0


def clear_db():
    check_db_path()
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM crawled_data")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error clearing database: {e}")


def flush_db():
    check_db_path()
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE crawled_data")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error flushing database: {e}")


def update_existing_records(new_column: str = "media", default_value: str = "{}"):
    if new_column not in _ALLOWED_COLUMNS:
        raise ValueError(f"Column '{new_column}' is not in the allowed column list")
    check_db_path()
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        queries = {
            "media": "UPDATE crawled_data SET media = ? WHERE screenshot IS NULL",
            "links": "UPDATE crawled_data SET links = ? WHERE screenshot IS NULL",
            "metadata": "UPDATE crawled_data SET metadata = ? WHERE screenshot IS NULL",
            "screenshot": "UPDATE crawled_data SET screenshot = ? WHERE screenshot IS NULL",
            "response_headers": "UPDATE crawled_data SET response_headers = ? WHERE screenshot IS NULL"
        }
        cursor.execute(queries[new_column], (default_value,))

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error updating existing records: {e}")


if __name__ == "__main__":
    # Delete the existing database file
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()
    # alter_db_add_screenshot("COL_NAME")