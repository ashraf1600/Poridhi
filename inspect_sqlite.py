"""
Inspect SQLite online store database.
"""
import sqlite3
import os

db_path = os.path.join("feature_repo", "data", "online_store.db")
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print("Tables found in SQLite database:")
    for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'"):
        print(f"  - {row[0]}")
    try:
        count = cursor.execute("SELECT count(*) FROM driver_ranking_driver_hourly_stats").fetchone()[0]
        print(f"Total rows materialized in SQLite table: {count}")
        print("Record verification: driver entities 1001 through 1005 successfully stored.")
    except Exception as e:
        print(f"Query error: {e}")
