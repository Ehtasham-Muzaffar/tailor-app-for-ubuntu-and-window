import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "tailor_shop.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check existing columns in orders table
    c.execute("PRAGMA table_info(orders)")
    columns = [row[1] for row in c.fetchall()]
    
    if "worker_name" not in columns:
        print("Adding worker_name to orders...")
        c.execute("ALTER TABLE orders ADD COLUMN worker_name TEXT")
        
    if "is_urgent" not in columns:
        print("Adding is_urgent to orders...")
        c.execute("ALTER TABLE orders ADD COLUMN is_urgent INTEGER DEFAULT 0")
        
    if "fabric_details" not in columns:
        print("Adding fabric_details to orders...")
        c.execute("ALTER TABLE orders ADD COLUMN fabric_details TEXT")
        
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
