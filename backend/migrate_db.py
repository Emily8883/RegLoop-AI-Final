"""
Safe database migration script - adds new fields to Obligation table
Run this BEFORE restarting the backend
"""

import sqlite3
import os

DB_PATH = "regloop.db"

def migrate_database():
    """Add missing columns to existing Obligation table"""
    
    if not os.path.exists(DB_PATH):
        print(f"✓ {DB_PATH} doesn't exist - will be created fresh on startup")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if columns exist
        cursor.execute("PRAGMA table_info(obligations)")
        columns = [col[1] for col in cursor.fetchall()]
        
        print(f"Current columns in obligations table: {columns}")
        
        # Add missing columns if they don't exist
        if "confidence_score" not in columns:
            print("Adding confidence_score column...")
            cursor.execute("""
                ALTER TABLE obligations ADD COLUMN confidence_score REAL DEFAULT 0.75
            """)
            print("✓ Added confidence_score")
        
        if "source_citation" not in columns:
            print("Adding source_citation column...")
            cursor.execute("""
                ALTER TABLE obligations ADD COLUMN source_citation TEXT DEFAULT ''
            """)
            print("✓ Added source_citation")
        
        conn.commit()
        print("\n✓ Database migration successful!")
        print("✓ New fields added: confidence_score, source_citation")
        print("\nNow restart the backend with: uvicorn main:app --reload")
        
    except sqlite3.OperationalError as e:
        if "already exists" in str(e):
            print(f"✓ Columns already exist: {e}")
        else:
            print(f"✗ Migration error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_database()
