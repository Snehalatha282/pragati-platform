
import sqlite3
import os

def add_columns():
    db_path = 'instance/pragati.db'
    if not os.path.exists(db_path):
        db_path = 'pragati.db'
        
    print(f"Connecting to {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # List of columns to add
    columns = [
        ("company", "TEXT"),
        ("job_title", "TEXT"),
        ("experience_years", "INTEGER"),
        ("is_verified_mentor", "BOOLEAN DEFAULT 0")
    ]
    
    for col_name, col_type in columns:
        try:
            print(f"Adding column {col_name}...")
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
            print(f"Success.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"Column {col_name} already exists.")
            else:
                print(f"Error adding {col_name}: {e}")
                
    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_columns()
