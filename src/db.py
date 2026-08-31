import re
import sqlite3
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "sales.db"


def init_demo_db(force=False):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if force and DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            city TEXT,
            region TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            product_id INTEGER,
            order_date TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            amount REAL NOT NULL,
            FOREIGN KEY(customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY(product_id) REFERENCES products(product_id)
        )
    """)

    if cur.execute("SELECT COUNT(*) FROM customers").fetchone()[0] == 0:

        cur.executemany(
            "INSERT INTO customers VALUES (?,?,?,?)",
            [
                (1, "Amit", "Kolkata", "East"),
                (2, "Priya", "Delhi", "North"),
                (3, "Rahul", "Mumbai", "West"),
                (4, "Sneha", "Bengaluru", "South"),
                (5, "Arjun", "Kolkata", "East"),
                (6, "Neha", "Pune", "West"),
            ],
        )

        cur.executemany(
            "INSERT INTO products VALUES (?,?,?,?)",
            [
                (1, "Laptop Pro", "Electronics", 75000),
                (2, "Wireless Headphones", "Electronics", 7000),
                (3, "Office Chair", "Furniture", 12000),
                (4, "Mechanical Keyboard", "Electronics", 5500),
                (5, "Standing Desk", "Furniture", 25000),
                (6, "Monitor 27", "Electronics", 22000),
            ],
        )

        cur.executemany(
            "INSERT INTO orders VALUES (?,?,?,?,?,?)",
            [
                (1, 1, 1, "2026-01-10", 1, 75000),
                (2, 2, 2, "2026-01-15", 2, 14000),
                (3, 3, 3, "2026-02-03", 2, 24000),
                (4, 4, 6, "2026-02-11", 2, 44000),
                (5, 5, 5, "2026-02-18", 1, 25000),
                (6, 6, 4, "2026-03-01", 3, 16500),
                (7, 1, 6, "2026-03-12", 1, 22000),
                (8, 2, 1, "2026-03-20", 1, 75000),
                (9, 3, 5, "2026-04-04", 2, 50000),
                (10, 4, 2, "2026-04-10", 3, 21000),
                (11, 5, 4, "2026-05-07", 2, 11000),
                (12, 6, 3, "2026-05-19", 2, 24000),
                (13, 1, 1, "2026-06-02", 1, 75000),
                (14, 2, 6, "2026-06-14", 2, 44000),
                (15, 3, 2, "2026-07-05", 4, 28000),
                (16, 4, 5, "2026-07-17", 1, 25000),
                (17, 5, 1, "2026-08-01", 1, 75000),
                (18, 6, 6, "2026-08-12", 2, 44000),
            ],
        )

    conn.commit()
    conn.close()


def get_schema():
    conn = sqlite3.connect(DB_PATH)

    out = []

    for table in ("customers", "products", "orders"):
        cols = conn.execute(
            f"PRAGMA table_info({table})"
        ).fetchall()

        out.append(
            f"TABLE {table}:\n"
            + "\n".join(f"- {c[1]} ({c[2]})" for c in cols)
        )

    conn.close()

    return "\n\n".join(out)


def run_readonly_sql(sql):
    sql = sql.strip().rstrip(";")

    if not re.match(r"^(SELECT|WITH)\b", sql, re.I):
        raise ValueError("Only SELECT/WITH queries are allowed.")

    if re.search(
        r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|ATTACH|DETACH|PRAGMA|REPLACE|VACUUM)\b",
        sql,
        re.I,
    ):
        raise ValueError("Unsafe SQL detected.")

    if ";" in sql:
        raise ValueError("Multiple SQL statements are not allowed.")

    conn = sqlite3.connect(
        f"file:{DB_PATH}?mode=ro",
        uri=True,
    )

    try:
        return pd.read_sql_query(sql, conn)
    finally:
        conn.close()