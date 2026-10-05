"""
db_manager.py  –  All SQLite CRUD operations for Fazian Tailor Shop
"""
import sqlite3
import os
import shutil
from datetime import datetime

# ── Locate the database file next to this package ──────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, "tailor_shop.db")


# ═══════════════════════════════════════════════════════════════════════════
#  Connection helper
# ═══════════════════════════════════════════════════════════════════════════
def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row          # access columns by name
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


# ═══════════════════════════════════════════════════════════════════════════
#  Database Initialisation  (called once on startup)
# ═══════════════════════════════════════════════════════════════════════════
def init_db():
    """Create all tables if they don't exist yet."""
    conn = get_connection()
    c = conn.cursor()

    # CUSTOMERS
    c.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            phone      TEXT    NOT NULL UNIQUE,
            name       TEXT    NOT NULL,
            address    TEXT,
            created_at TEXT    DEFAULT (datetime('now','localtime')),
            updated_at TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_cust_phone ON customers(phone)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_cust_name  ON customers(name)")

    # MEASUREMENTS
    c.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id    INTEGER NOT NULL UNIQUE,
            length         REAL,
            shoulder       REAL,
            neck           REAL,
            chest          REAL,
            waist          REAL,
            sleeves        REAL,
            armhole        REAL,
            bottom_ghera   REAL,
            trouser_length REAL,
            trouser_poncha REAL,
            collar_type    TEXT,
            front_pocket   TEXT,
            side_pocket    TEXT,
            cuffs          TEXT,
            shalwar_pocket TEXT,
            special_notes  TEXT,
            updated_at     TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
        )
    """)

    # ORDERS
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id   INTEGER NOT NULL,
            order_date    TEXT    NOT NULL DEFAULT (date('now','localtime')),
            delivery_date TEXT,
            suit_type     TEXT    NOT NULL,
            quantity      INTEGER DEFAULT 1,
            status        TEXT    NOT NULL DEFAULT 'Pending',
            color         TEXT,
            cuff_type     TEXT,
            shalwar_bottom TEXT,
            kameez_bottom TEXT,
            collar_type   TEXT,
            front_pocket  TEXT,
            side_pocket   TEXT,
            shalwar_pocket TEXT,
            total_amount  REAL    DEFAULT 0,
            advance_paid  REAL    DEFAULT 0,
            remaining     REAL    DEFAULT 0,
            remarks       TEXT,
            worker_name   TEXT,
            is_urgent     INTEGER DEFAULT 0,
            fabric_details TEXT,
            created_at    TEXT    DEFAULT (datetime('now','localtime')),
            updated_at    TEXT    DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_ord_cust   ON orders(customer_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_ord_status ON orders(status)")

    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════════════════
#  CUSTOMER CRUD
# ═══════════════════════════════════════════════════════════════════════════
def add_customer(phone: str, name: str, address: str = "") -> int | None:
    """Insert a new customer. Returns new row id, or None if phone exists."""
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            "INSERT INTO customers (phone, name, address) VALUES (?,?,?)",
            (phone.strip(), name.strip(), address.strip())
        )
        conn.commit()
        return c.lastrowid
    except sqlite3.IntegrityError:
        return None          # duplicate phone
    finally:
        conn.close()


def get_customer_by_phone(phone: str) -> sqlite3.Row | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM customers WHERE phone = ?", (phone.strip(),)
    ).fetchone()
    conn.close()
    return row


def get_customer_by_id(customer_id: int) -> sqlite3.Row | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM customers WHERE id = ?", (customer_id,)
    ).fetchone()
    conn.close()
    return row


def search_customers(query: str) -> list[sqlite3.Row]:
    """Search by phone OR name (partial, case-insensitive)."""
    conn = get_connection()
    like = f"%{query.strip()}%"
    rows = conn.execute(
        "SELECT * FROM customers WHERE phone LIKE ? OR name LIKE ? ORDER BY name",
        (like, like)
    ).fetchall()
    conn.close()
    return rows


def update_customer(customer_id: int, name: str, address: str) -> bool:
    conn = get_connection()
    conn.execute(
        "UPDATE customers SET name=?, address=?, updated_at=datetime('now','localtime') WHERE id=?",
        (name.strip(), address.strip(), customer_id)
    )
    conn.commit()
    conn.close()
    return True


def delete_customer(customer_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM customers WHERE id=?", (customer_id,))
    conn.commit()
    conn.close()


def get_all_customers() -> list[sqlite3.Row]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM customers ORDER BY name").fetchall()
    conn.close()
    return rows


# ═══════════════════════════════════════════════════════════════════════════
#  MEASUREMENTS CRUD
# ═══════════════════════════════════════════════════════════════════════════
def save_measurements(customer_id: int, data: dict) -> bool:
    """Insert or update measurements for a customer."""
    conn = get_connection()
    existing = conn.execute(
        "SELECT id FROM measurements WHERE customer_id=?", (customer_id,)
    ).fetchone()

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if existing:
        conn.execute("""
            UPDATE measurements SET
                length=?, shoulder=?, neck=?, chest=?, waist=?,
                sleeves=?, armhole=?, bottom_ghera=?,
                trouser_length=?, trouser_poncha=?,
                collar_type=?, front_pocket=?, side_pocket=?, cuffs=?, shalwar_pocket=?,
                special_notes=?, updated_at=?
            WHERE customer_id=?
        """, (
            data.get("length"), data.get("shoulder"), data.get("neck"),
            data.get("chest"), data.get("waist"), data.get("sleeves"),
            data.get("armhole"), data.get("bottom_ghera"),
            data.get("trouser_length"), data.get("trouser_poncha"),
            data.get("collar_type"), data.get("front_pocket"), data.get("side_pocket"),
            data.get("cuffs"), data.get("shalwar_pocket"),
            data.get("special_notes"), ts, customer_id
        ))
    else:
        conn.execute("""
            INSERT INTO measurements
                (customer_id, length, shoulder, neck, chest, waist,
                 sleeves, armhole, bottom_ghera, trouser_length,
                 trouser_poncha, collar_type, front_pocket, side_pocket, cuffs, shalwar_pocket, special_notes, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            customer_id,
            data.get("length"), data.get("shoulder"), data.get("neck"),
            data.get("chest"), data.get("waist"), data.get("sleeves"),
            data.get("armhole"), data.get("bottom_ghera"),
            data.get("trouser_length"), data.get("trouser_poncha"),
            data.get("collar_type"), data.get("front_pocket"), data.get("side_pocket"),
            data.get("cuffs"), data.get("shalwar_pocket"),
            data.get("special_notes"), ts
        ))
    conn.commit()
    conn.close()
    return True


def get_measurements(customer_id: int) -> sqlite3.Row | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM measurements WHERE customer_id=?", (customer_id,)
    ).fetchone()
    conn.close()
    return row


# ═══════════════════════════════════════════════════════════════════════════
#  ORDER CRUD
# ═══════════════════════════════════════════════════════════════════════════
SUIT_TYPES  = ["Shalwar Kameez", "Pant Coat", "Kurta", "Waistcoat", "Sherwani", "Other"]
ORDER_STATUSES = ["Pending", "In Progress", "Ready", "Delivered"]


def add_order(customer_id: int, data: dict) -> int:
    remaining = float(data.get("total_amount") or 0) - float(data.get("advance_paid") or 0)
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO orders
            (customer_id, order_date, delivery_date, suit_type, quantity, status,
             color, cuff_type, shalwar_bottom, kameez_bottom,
             collar_type, front_pocket, side_pocket, shalwar_pocket,
             total_amount, advance_paid, remaining, remarks, worker_name, is_urgent, fabric_details)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        customer_id,
        data.get("order_date", datetime.now().strftime("%Y-%m-%d")),
        data.get("delivery_date"),
        data.get("suit_type"),
        int(data.get("quantity") or 1),
        data.get("status", "Pending"),
        data.get("color"),
        data.get("cuff_type"),
        data.get("shalwar_bottom"),
        data.get("kameez_bottom"),
        data.get("collar_type"),
        data.get("front_pocket"),
        data.get("side_pocket"),
        data.get("shalwar_pocket"),
        float(data.get("total_amount") or 0),
        float(data.get("advance_paid") or 0),
        remaining,
        data.get("remarks", ""),
        data.get("worker_name"),
        int(data.get("is_urgent", 0) if data.get("is_urgent") is not None else 0),
        data.get("fabric_details")
    ))
    conn.commit()
    new_id = c.lastrowid
    conn.close()
    return new_id


def update_order(order_id: int, data: dict) -> bool:
    remaining = float(data.get("total_amount") or 0) - float(data.get("advance_paid") or 0)
    conn = get_connection()
    conn.execute("""
        UPDATE orders SET
            order_date=?, delivery_date=?, suit_type=?, quantity=?, status=?,
            color=?, cuff_type=?, shalwar_bottom=?, kameez_bottom=?,
            collar_type=?, front_pocket=?, side_pocket=?, shalwar_pocket=?,
            total_amount=?, advance_paid=?, remaining=?, remarks=?,
            worker_name=?, is_urgent=?, fabric_details=?,
            updated_at=datetime('now','localtime')
        WHERE id=?
    """, (
        data.get("order_date"),
        data.get("delivery_date"),
        data.get("suit_type"),
        int(data.get("quantity") or 1),
        data.get("status"),
        data.get("color"),
        data.get("cuff_type"),
        data.get("shalwar_bottom"),
        data.get("kameez_bottom"),
        data.get("collar_type"),
        data.get("front_pocket"),
        data.get("side_pocket"),
        data.get("shalwar_pocket"),
        float(data.get("total_amount") or 0),
        float(data.get("advance_paid") or 0),
        remaining,
        data.get("remarks", ""),
        data.get("worker_name"),
        int(data.get("is_urgent", 0) if data.get("is_urgent") is not None else 0),
        data.get("fabric_details"),
        order_id
    ))
    conn.commit()
    conn.close()
    return True


def delete_order(order_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM orders WHERE id=?", (order_id,))
    conn.commit()
    conn.close()


def get_orders_for_customer(customer_id: int) -> list[sqlite3.Row]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM orders WHERE customer_id=? ORDER BY order_date DESC",
        (customer_id,)
    ).fetchall()
    conn.close()
    return rows


def get_order_by_id(order_id: int) -> sqlite3.Row | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    conn.close()
    return row


def get_all_orders(status_filter: str = None) -> list[sqlite3.Row]:
    conn = get_connection()
    if status_filter and status_filter != "All":
        rows = conn.execute(
            """SELECT o.*, c.name as customer_name, c.phone as customer_phone
               FROM orders o JOIN customers c ON o.customer_id = c.id
               WHERE o.status=? ORDER BY o.delivery_date ASC""",
            (status_filter,)
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT o.*, c.name as customer_name, c.phone as customer_phone
               FROM orders o JOIN customers c ON o.customer_id = c.id
               ORDER BY o.delivery_date ASC"""
        ).fetchall()
    conn.close()
    return rows


# ═══════════════════════════════════════════════════════════════════════════
#  DASHBOARD STATS
# ═══════════════════════════════════════════════════════════════════════════
def get_dashboard_stats() -> dict:
    conn = get_connection()
    stats = {}
    stats["total_customers"]  = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    stats["total_orders"]     = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    stats["pending_orders"]   = conn.execute("SELECT COUNT(*) FROM orders WHERE status='Pending'").fetchone()[0]
    stats["inprogress_orders"]= conn.execute("SELECT COUNT(*) FROM orders WHERE status='In Progress'").fetchone()[0]
    stats["ready_orders"]     = conn.execute("SELECT COUNT(*) FROM orders WHERE status='Ready'").fetchone()[0]
    stats["delivered_orders"] = conn.execute("SELECT COUNT(*) FROM orders WHERE status='Delivered'").fetchone()[0]
    today_str = datetime.now().strftime("%Y-%m-%d")
    stats["due_today"] = conn.execute("SELECT COUNT(*) FROM orders WHERE delivery_date=? AND status!='Delivered'", (today_str,)).fetchone()[0]
    row = conn.execute("SELECT SUM(total_amount), SUM(advance_paid), SUM(remaining) FROM orders").fetchone()
    stats["total_revenue"]    = row[0] or 0
    stats["total_advance"]    = row[1] or 0
    stats["total_remaining"]  = row[2] or 0
    conn.close()
    return stats


# ═══════════════════════════════════════════════════════════════════════════
#  BACKUP / EXPORT
# ═══════════════════════════════════════════════════════════════════════════
def backup_database(destination_folder: str) -> str:
    """Copy the .db file to destination_folder and return the new path."""
    ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = os.path.join(destination_folder, f"tailor_backup_{ts}.db")
    shutil.copy2(DB_PATH, dst)
    return dst
