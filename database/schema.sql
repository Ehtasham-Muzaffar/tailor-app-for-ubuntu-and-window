-- ============================================================
-- FAZIAN TAILOR SHOP - SQLite Database Schema
-- ============================================================

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys = ON;

-- -------------------------------------------------------
-- TABLE: customers
-- Primary identifier: phone number (unique)
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS customers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    phone           TEXT    NOT NULL UNIQUE,          -- Unique phone, used as lookup key
    name            TEXT    NOT NULL,
    address         TEXT,
    created_at      TEXT    DEFAULT (datetime('now','localtime')),
    updated_at      TEXT    DEFAULT (datetime('now','localtime'))
);

CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);
CREATE INDEX IF NOT EXISTS idx_customers_name  ON customers(name);

-- -------------------------------------------------------
-- TABLE: measurements
-- One row per customer (upsert on update)
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS measurements (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id     INTEGER NOT NULL UNIQUE,
    -- Kameez / Shirt
    length          REAL,
    shoulder        REAL,
    neck            REAL,
    chest           REAL,
    waist           REAL,
    sleeves         REAL,
    armhole         REAL,
    bottom_ghera    REAL,
    -- Trouser / Shalwar
    trouser_length  REAL,
    trouser_poncha  REAL,
    -- Style / Preferences
    collar_type     TEXT,
    front_pocket    TEXT,
    side_pocket     TEXT,
    cuffs           TEXT,
    shalwar_pocket  TEXT,
    -- Extra
    special_notes   TEXT,
    updated_at      TEXT DEFAULT (datetime('now','localtime')),
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

-- -------------------------------------------------------
-- TABLE: orders
-- Each customer can have multiple orders
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS orders (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id     INTEGER NOT NULL,
    order_date      TEXT    NOT NULL DEFAULT (date('now','localtime')),
    delivery_date   TEXT,
    suit_type       TEXT    NOT NULL,   -- Shalwar Kameez / Pant Coat / Kurta / etc.
    quantity        INTEGER DEFAULT 1,
    status          TEXT    NOT NULL DEFAULT 'Pending',  -- Pending / In Progress / Ready / Delivered
    -- Order Specific Styles
    color           TEXT,
    cuff_type       TEXT,
    shalwar_bottom  TEXT,
    kameez_bottom   TEXT,
    collar_type     TEXT,
    front_pocket    TEXT,
    side_pocket     TEXT,
    shalwar_pocket  TEXT,
    -- Financial
    total_amount    REAL    DEFAULT 0,
    advance_paid    REAL    DEFAULT 0,
    remaining       REAL    GENERATED ALWAYS AS (total_amount - advance_paid) STORED,
    -- Notes
    remarks         TEXT,
    worker_name     TEXT,
    is_urgent       INTEGER DEFAULT 0,
    fabric_details  TEXT,
    created_at      TEXT    DEFAULT (datetime('now','localtime')),
    updated_at      TEXT    DEFAULT (datetime('now','localtime')),
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_orders_customer  ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status    ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_delivery  ON orders(delivery_date);
