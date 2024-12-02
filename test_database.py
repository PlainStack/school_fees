import sqlite3

def test_database():
    try:
        # Connect to the database
        conn = sqlite3.connect('school_fees.db')
        cursor = conn.cursor()

        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("Tables in database:")
        for table in tables:
            print(f"- {table[0]}")
            # Show structure of each table
            cursor.execute(f"PRAGMA table_info({table[0]})")
            columns = cursor.fetchall()
            for column in columns:
                print(f"  * {column[1]} ({column[2]})")
        
        conn.close()
        print("\nDatabase test completed successfully!")
        
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_database() 