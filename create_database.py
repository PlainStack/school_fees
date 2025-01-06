import sqlite3
import os

def create_database():
    """Create the database and all required tables"""
    try:
        # Connect to SQLite database (creates it if it doesn't exist)
        conn = sqlite3.connect('school_fees.db')
        cursor = conn.cursor()

        # Read schema from file
        with open('schema.sql', 'r') as schema_file:
            schema_script = schema_file.read()
            
        # Execute schema script
        cursor.executescript(schema_script)
        
        # Commit the changes and close the connection
        conn.commit()
        conn.close()
        
        return True

    except Exception as e:
        print(f"Error creating database: {str(e)}")
        # If something went wrong and the file was created, remove it
        if os.path.exists('school_fees.db'):
            try:
                os.remove('school_fees.db')
            except:
                pass
        return False

if __name__ == "__main__":
    success = create_database()
    if success:
        print("Database created successfully!")
    else:
        print("Failed to create database.") 