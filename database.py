import sqlite3
import json
import os

DB_PATH = os.environ.get("DB_PATH", "invoicegen.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            name TEXT,
            picture TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS store_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            profile_name TEXT NOT NULL,
            from_store TEXT NOT NULL,
            to_store TEXT NOT NULL,
            cgst_rate REAL DEFAULT 9.0,
            sgst_rate REAL DEFAULT 9.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_email) REFERENCES users(email),
            UNIQUE(user_email, profile_name)
        )
    """)
    conn.commit()
    conn.close()


def upsert_user(email: str, name: str, picture: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO users (email, name, picture) VALUES (?, ?, ?) "
        "ON CONFLICT(email) DO UPDATE SET name=excluded.name, picture=excluded.picture",
        (email, name, picture),
    )
    conn.commit()
    conn.close()


def get_store_profiles(user_email: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM store_profiles WHERE user_email = ? ORDER BY profile_name",
        (user_email,),
    ).fetchall()
    conn.close()
    return [
        {
            "profile_name": r["profile_name"],
            "from_store": json.loads(r["from_store"]),
            "to_store": json.loads(r["to_store"]),
            "cgst_rate": r["cgst_rate"],
            "sgst_rate": r["sgst_rate"],
        }
        for r in rows
    ]


def save_store_profile(
    user_email: str,
    profile_name: str,
    from_store: dict,
    to_store: dict,
    cgst_rate: float,
    sgst_rate: float,
):
    conn = get_connection()
    conn.execute(
        "INSERT INTO store_profiles (user_email, profile_name, from_store, to_store, cgst_rate, sgst_rate) "
        "VALUES (?, ?, ?, ?, ?, ?) "
        "ON CONFLICT(user_email, profile_name) DO UPDATE SET "
        "from_store=excluded.from_store, to_store=excluded.to_store, "
        "cgst_rate=excluded.cgst_rate, sgst_rate=excluded.sgst_rate",
        (user_email, profile_name, json.dumps(from_store), json.dumps(to_store), cgst_rate, sgst_rate),
    )
    conn.commit()
    conn.close()


def delete_store_profile(user_email: str, profile_name: str):
    conn = get_connection()
    conn.execute(
        "DELETE FROM store_profiles WHERE user_email = ? AND profile_name = ?",
        (user_email, profile_name),
    )
    conn.commit()
    conn.close()
