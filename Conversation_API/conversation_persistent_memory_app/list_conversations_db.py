import sqlite3
import os

# Define the absolute path to the database based on the script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(SCRIPT_DIR, "conversations.db")

def list_conversations():
    if not os.path.exists(DB_FILE):
        print(f"Database file '{DB_FILE}' not found.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM conversations")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        if not rows:
            print("No conversations found in the database.")
        else:
            print(f"Found {len(rows)} conversation(s) in the database:")
            print("-" * 50)
            # Print column headers dynamically
            header = " | ".join(f"{col:<20}" for col in columns)
            print(header)
            print("-" * 50)
            
            # Print each row
            for row in rows:
                row_str = " | ".join(f"{str(val):<20}" for val in row)
                print(row_str)
                
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    list_conversations()
