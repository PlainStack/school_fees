CREATE TABLE IF NOT EXISTS projections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projection_date DATE NOT NULL,
    seed_capital DECIMAL NOT NULL,
    investment_rate DECIMAL NOT NULL,
    contribution_escalation DECIMAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS projected_values (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projection_id INTEGER,
    year INTEGER NOT NULL,
    school_fees DECIMAL,
    monthly_contribution DECIMAL,
    annual_bonus DECIMAL,
    projected_balance DECIMAL,
    FOREIGN KEY (projection_id) REFERENCES projections(id)
);

CREATE TABLE IF NOT EXISTS actual_values (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER UNIQUE NOT NULL,
    school_fees DECIMAL,
    monthly_contribution DECIMAL,
    annual_bonus DECIMAL,
    actual_balance DECIMAL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);