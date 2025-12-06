
import sqlite3

try:
    conn = sqlite3.connect('instance/pragati.db')
    cursor = conn.cursor()
    
    # Reset ALL users to mentee so they can re-apply
    cursor.execute("UPDATE users SET role='mentee', is_verified_mentor=0")
    conn.commit()
    
    print(f"Reset {cursor.rowcount} users to 'mentee' role.")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
