import sqlite3
import os

# Define path to your existing database
db_path = os.path.join(os.getcwd(), 'safesurf.db')

def update_database():
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # SQL to create the reports table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            comment TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """

        # Execute and Commit
        cursor.execute(create_table_query)
        conn.commit()
        
        print("✅ Success: 'reports' table created in safesurf.db")
        
    except sqlite3.Error as e:
        print(f"❌ Database Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    update_database()