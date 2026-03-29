import os
import json
import sqlite3
import subprocess
from pathlib import Path

# ─────────────────────────────────────────────
# STEP 1 — Clone the PhonePe Pulse GitHub repo
# ─────────────────────────────────────────────

REPO_URL = "https://github.com/PhonePe/pulse.git"
CLONE_DIR = "pulse-master"

# ─────────────────────────────────────────────
# STEP 2 — Set up SQLite Database & Tables
# ─────────────────────────────────────────────

DB_NAME = "phonepe.db"

def create_tables(conn):
    cursor = conn.cursor()

    cursor.executescript("""
        -- AGGREGATED TABLES
        CREATE TABLE IF NOT EXISTS aggregated_transaction (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            state           TEXT,
            year            INTEGER,
            quarter         INTEGER,
            transaction_type TEXT,
            transaction_count INTEGER,
            transaction_amount REAL
        );

        CREATE TABLE IF NOT EXISTS aggregated_user (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            state           TEXT,
            year            INTEGER,
            quarter         INTEGER,
            registered_users INTEGER,
            app_opens       INTEGER
        );

        CREATE TABLE IF NOT EXISTS aggregated_insurance (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            state           TEXT,
            year            INTEGER,
            quarter         INTEGER,
            insurance_type  TEXT,
            insurance_count INTEGER,
            insurance_amount REAL
        );

        -- MAP TABLES
        CREATE TABLE IF NOT EXISTS map_transaction (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            state           TEXT,
            year            INTEGER,
            quarter         INTEGER,
            district        TEXT,
            transaction_count INTEGER,
            transaction_amount REAL
        );

        CREATE TABLE IF NOT EXISTS map_user (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            state           TEXT,
            year            INTEGER,
            quarter         INTEGER,
            district        TEXT,
            registered_users INTEGER,
            app_opens       INTEGER
        );

        CREATE TABLE IF NOT EXISTS map_insurance (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            state           TEXT,
            year            INTEGER,
            quarter         INTEGER,
            district        TEXT,
            insurance_count INTEGER,
            insurance_amount REAL
        );

        -- TOP TABLES
        CREATE TABLE IF NOT EXISTS top_transaction (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            state           TEXT,
            year            INTEGER,
            quarter         INTEGER,
            entity_type     TEXT,  -- district / pincode
            entity_name     TEXT,
            transaction_count INTEGER,
            transaction_amount REAL
        );

        CREATE TABLE IF NOT EXISTS top_user (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            state           TEXT,
            year            INTEGER,
            quarter         INTEGER,
            entity_type     TEXT,
            entity_name     TEXT,
            registered_users INTEGER
        );

        CREATE TABLE IF NOT EXISTS top_insurance (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            state           TEXT,
            year            INTEGER,
            quarter         INTEGER,
            entity_type     TEXT,
            entity_name     TEXT,
            insurance_count INTEGER,
            insurance_amount REAL
        );
    """)

    conn.commit()
    print("All tables created!")

# ─────────────────────────────────────────────
# STEP 3 — Parse & Load JSON Files
# ─────────────────────────────────────────────

DATA_PATH = Path(CLONE_DIR) / "data"

# ── Aggregated Transaction ──
def load_aggregated_transaction(conn):
    cursor = conn.cursor()
    base = DATA_PATH / "aggregated" / "transaction" / "country" / "india" / "state"
    rows = []
    for state_dir in base.iterdir():
        state = state_dir.name
        for year_dir in state_dir.iterdir():
            year = int(year_dir.name)
            for file in year_dir.glob("*.json"):
                quarter = int(file.stem)
                data = json.loads(file.read_text())
                for item in data.get("data", {}).get("transactionData", []):
                    rows.append((
                        state, year, quarter,
                        item["name"],
                        item["paymentInstruments"][0]["count"],
                        item["paymentInstruments"][0]["amount"]
                    ))
    cursor.executemany(
        "INSERT INTO aggregated_transaction (state,year,quarter,transaction_type,transaction_count,transaction_amount) VALUES (?,?,?,?,?,?)",
        rows
    )
    conn.commit()
    print(f" aggregated_transaction — {len(rows)} rows inserted")

# ── Aggregated User ──
def load_aggregated_user(conn):
    cursor = conn.cursor()
    base = DATA_PATH / "aggregated" / "user" / "country" / "india" / "state"
    rows = []
    for state_dir in base.iterdir():
        state = state_dir.name
        for year_dir in state_dir.iterdir():
            year = int(year_dir.name)
            for file in year_dir.glob("*.json"):
                quarter = int(file.stem)
                data = json.loads(file.read_text())
                summary = data.get("data", {}).get("aggregated", {})
                rows.append((
                    state, year, quarter,
                    summary.get("registeredUsers", 0),
                    summary.get("appOpens", 0)
                ))
    cursor.executemany(
        "INSERT INTO aggregated_user (state,year,quarter,registered_users,app_opens) VALUES (?,?,?,?,?)",
        rows
    )
    conn.commit()
    print(f"aggregated_user — {len(rows)} rows inserted")

# ── Aggregated Insurance ──
def load_aggregated_insurance(conn):
    cursor = conn.cursor()
    base = DATA_PATH / "aggregated" / "insurance" / "country" / "india" / "state"
    if not base.exists():
        print("aggregated_insurance folder not found — skipping")
        return
    rows = []
    for state_dir in base.iterdir():
        state = state_dir.name
        for year_dir in state_dir.iterdir():
            year = int(year_dir.name)
            for file in year_dir.glob("*.json"):
                quarter = int(file.stem)
                data = json.loads(file.read_text())
                for item in data.get("data", {}).get("transactionData", []):
                    rows.append((
                        state, year, quarter,
                        item["name"],
                        item["paymentInstruments"][0]["count"],
                        item["paymentInstruments"][0]["amount"]
                    ))
    cursor.executemany(
        "INSERT INTO aggregated_insurance (state,year,quarter,insurance_type,insurance_count,insurance_amount) VALUES (?,?,?,?,?,?)",
        rows
    )
    conn.commit()
    print(f"aggregated_insurance — {len(rows)} rows inserted")

# ── Map Transaction ──
def load_map_transaction(conn):
    cursor = conn.cursor()
    base = DATA_PATH / "map" / "transaction" / "hover" / "country" / "india" / "state"
    rows = []
    for state_dir in base.iterdir():
        state = state_dir.name
        for year_dir in state_dir.iterdir():
            year = int(year_dir.name)
            for file in year_dir.glob("*.json"):
                quarter = int(file.stem)
                data = json.loads(file.read_text())
                for item in data.get("data", {}).get("hoverDataList", []):
                    metric = item.get("metric", [{}])
                    rows.append((
                        state, year, quarter,
                        item["name"],
                        metric[0].get("count", 0),
                        metric[0].get("amount", 0)
                    ))
    cursor.executemany(
        "INSERT INTO map_transaction (state,year,quarter,district,transaction_count,transaction_amount) VALUES (?,?,?,?,?,?)",
        rows
    )
    conn.commit()
    print(f" map_transaction — {len(rows)} rows inserted")

# ── Map User ──
def load_map_user(conn):
    cursor = conn.cursor()
    base = DATA_PATH / "map" / "user" / "hover" / "country" / "india" / "state"
    rows = []
    for state_dir in base.iterdir():
        state = state_dir.name
        for year_dir in state_dir.iterdir():
            year = int(year_dir.name)
            for file in year_dir.glob("*.json"):
                quarter = int(file.stem)
                data = json.loads(file.read_text())
                for district, info in data.get("data", {}).get("hoverData", {}).items():
                    rows.append((
                        state, year, quarter,
                        district,
                        info.get("registeredUsers", 0),
                        info.get("appOpens", 0)
                    ))
    cursor.executemany(
        "INSERT INTO map_user (state,year,quarter,district,registered_users,app_opens) VALUES (?,?,?,?,?,?)",
        rows
    )
    conn.commit()
    print(f" map_user — {len(rows)} rows inserted")

# ── Map Insurance ──
def load_map_insurance(conn):
    cursor = conn.cursor()
    base = DATA_PATH / "map" / "insurance" / "hover" / "country" / "india" / "state"
    if not base.exists():
        print("map_insurance folder not found — skipping")
        return
    rows = []
    for state_dir in base.iterdir():
        state = state_dir.name
        for year_dir in state_dir.iterdir():
            year = int(year_dir.name)
            for file in year_dir.glob("*.json"):
                quarter = int(file.stem)
                data = json.loads(file.read_text())
                for item in data.get("data", {}).get("hoverDataList", []):
                    metric = item.get("metric", [{}])
                    rows.append((
                        state, year, quarter,
                        item["name"],
                        metric[0].get("count", 0),
                        metric[0].get("amount", 0)
                    ))
    cursor.executemany(
        "INSERT INTO map_insurance (state,year,quarter,district,insurance_count,insurance_amount) VALUES (?,?,?,?,?,?)",
        rows
    )
    conn.commit()
    print(f"map_insurance — {len(rows)} rows inserted")

# ── Top Transaction ──
def load_top_transaction(conn):
    cursor = conn.cursor()
    base = DATA_PATH / "top" / "transaction" / "country" / "india" / "state"
    rows = []
    for state_dir in base.iterdir():
        state = state_dir.name
        for year_dir in state_dir.iterdir():
            year = int(year_dir.name)
            for file in year_dir.glob("*.json"):
                quarter = int(file.stem)
                data = json.loads(file.read_text())
                top_data = data.get("data", {})
                for entity_type, items in [("district", top_data.get("districts", [])),
                                            ("pincode",  top_data.get("pincodes",  []))]:
                    for item in (items or []):
                        rows.append((
                            state, year, quarter,
                            entity_type,
                            item["entityName"],
                            item["metric"]["count"],
                            item["metric"]["amount"]
                        ))
    cursor.executemany(
        "INSERT INTO top_transaction (state,year,quarter,entity_type,entity_name,transaction_count,transaction_amount) VALUES (?,?,?,?,?,?,?)",
        rows
    )
    conn.commit()
    print(f"top_transaction — {len(rows)} rows inserted")

# ── Top User ──
def load_top_user(conn):
    cursor = conn.cursor()
    base = DATA_PATH / "top" / "user" / "country" / "india" / "state"
    rows = []
    for state_dir in base.iterdir():
        state = state_dir.name
        for year_dir in state_dir.iterdir():
            year = int(year_dir.name)
            for file in year_dir.glob("*.json"):
                quarter = int(file.stem)
                data = json.loads(file.read_text())
                top_data = data.get("data", {})
                for entity_type, items in [("district", top_data.get("districts", [])),
                                            ("pincode",  top_data.get("pincodes",  []))]:
                    for item in (items or []):
                        rows.append((
                            state, year, quarter,
                            entity_type,
                            item["name"],
                            item["registeredUsers"]
                        ))
    cursor.executemany(
        "INSERT INTO top_user (state,year,quarter,entity_type,entity_name,registered_users) VALUES (?,?,?,?,?,?)",
        rows
    )
    conn.commit()
    print(f"top_user — {len(rows)} rows inserted")

# ── Top Insurance ──
def load_top_insurance(conn):
    cursor = conn.cursor()
    base = DATA_PATH / "top" / "insurance" / "country" / "india" / "state"
    if not base.exists():
        print("top_insurance folder not found — skipping")
        return
    rows = []
    for state_dir in base.iterdir():
        state = state_dir.name
        for year_dir in state_dir.iterdir():
            year = int(year_dir.name)
            for file in year_dir.glob("*.json"):
                quarter = int(file.stem)
                data = json.loads(file.read_text())
                top_data = data.get("data", {})
                for entity_type, items in [("district", top_data.get("districts", [])),
                                            ("pincode",  top_data.get("pincodes",  []))]:
                    for item in (items or []):
                        rows.append((
                            state, year, quarter,
                            entity_type,
                            item["entityName"],
                            item["metric"]["count"],
                            item["metric"]["amount"]
                        ))
    cursor.executemany(
        "INSERT INTO top_insurance (state,year,quarter,entity_type,entity_name,insurance_count,insurance_amount) VALUES (?,?,?,?,?,?,?)",
        rows
    )
    conn.commit()
    print(f"top_insurance — {len(rows)} rows inserted")

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    # Step 1: Skipping clone — folder already downloaded
    print("Using existing pulse-master folder...")

    # Step 2: Connect to SQLite and create tables
    conn = sqlite3.connect(DB_NAME)
    print(f"\n Connected to SQLite database: {DB_NAME}")
    create_tables(conn)

    # Step 3: Load all data
    print("\n Loading data into tables...\n")
    load_aggregated_transaction(conn)
    load_aggregated_user(conn)
    load_aggregated_insurance(conn)
    load_map_transaction(conn)
    load_map_user(conn)
    load_map_insurance(conn)
    load_top_transaction(conn)
    load_top_user(conn)
    load_top_insurance(conn)

    conn.close()
    print(f"\n Done! Database saved as '{DB_NAME}'")