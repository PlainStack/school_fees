import sqlite3

def create_database():
    # Connect to SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect('school_fees.db')
    cursor = conn.cursor()

    # Create projections table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS projections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        projection_date DATE NOT NULL,
        seed_capital DECIMAL NOT NULL,
        investment_rate DECIMAL NOT NULL,
        contribution_escalation DECIMAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create projected_values table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS projected_values (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        projection_id INTEGER,
        year INTEGER NOT NULL,
        school_fees DECIMAL,
        monthly_contribution DECIMAL,
        annual_bonus DECIMAL,
        projected_balance DECIMAL,
        FOREIGN KEY (projection_id) REFERENCES projections(id)
    )
    ''')

    # Create actual_values table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS actual_values (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        year INTEGER UNIQUE NOT NULL,
        school_fees DECIMAL,
        monthly_contribution DECIMAL,
        annual_bonus DECIMAL,
        actual_balance DECIMAL,
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print("Database created successfully!")

if __name__ == "__main__":
    create_database() 