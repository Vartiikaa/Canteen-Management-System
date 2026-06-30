"""
database.py
-----------
Handles SQLite database connection and table creation.
Uses sqlite3 from Python's standard library — no extra installs needed.
"""

import sqlite3
import os

# Database file path — stored inside 'database/' folder
DB_DIR = os.path.join(os.path.dirname(__file__), "database")
DB_PATH = os.path.join(DB_DIR, "canteen.db")


def get_connection():
    """Return a new database connection.
    detect_types enables date-time parsing if needed.
    """
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row  # so we can access columns by name
    return conn


def init_db():
    """Create the tables if they don't already exist."""
    # Ensure the database folder exists
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)

    conn = get_connection()
    cursor = conn.cursor()

    # ---------- Menu Table ----------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu (
            item_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name   TEXT    NOT NULL,
            category    TEXT    NOT NULL,
            price       REAL    NOT NULL
        )
    """)

    # ---------- Orders Table ----------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT    NOT NULL,
            item_name     TEXT    NOT NULL,
            quantity      INTEGER NOT NULL,
            total_price   REAL    NOT NULL,
            order_date    TEXT    NOT NULL
        )
    """)

    # ---------- Cart Table (temporary cart) ----------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            cart_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id   INTEGER NOT NULL,
            item_name TEXT    NOT NULL,
            price     REAL    NOT NULL,
            quantity  INTEGER NOT NULL,
            total     REAL    NOT NULL,
            FOREIGN KEY (item_id) REFERENCES menu(item_id)
        )
    """)

    # ---------- Populate menu with starter data (only if empty) ----------
    cursor.execute("SELECT COUNT(*) FROM menu")
    count = cursor.fetchone()[0]

    if count == 0:
        default_items = [
            # Snacks
            ("Samosa",        "Snacks",  15.00),
            ("Vada Pav",      "Snacks",  20.00),
            ("French Fries",  "Snacks",  50.00),
            ("Sandwich",      "Snacks",  40.00),
            ("Pav Bhaji",     "Snacks",  70.00),
            # Drinks
            ("Tea",           "Drinks",  10.00),
            ("Coffee",        "Drinks",  20.00),
            ("Cold Drink",    "Drinks",  30.00),
            ("Lassi",         "Drinks",  35.00),
            ("Milkshake",     "Drinks",  60.00),
            # Meals
            ("Rajma Chawal",  "Meals",   80.00),
            ("Chole Bhature", "Meals",   90.00),
            ("Dal Makhani",   "Meals",   100.00),
            ("Biryani",       "Meals",   120.00),
            ("Thali",         "Meals",   150.00),
        ]
        cursor.executemany(
            "INSERT INTO menu (item_name, category, price) VALUES (?, ?, ?)",
            default_items
        )

    conn.commit()
    conn.close()
