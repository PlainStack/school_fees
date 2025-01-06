# School Fees Projection Calculator

A Streamlit-based application for calculating and visualizing school fees projections, tracking actual values, and maintaining historical projections.

## Features

- Calculate required monthly contributions based on:
  - Initial seed capital
  - Investment rate
  - Contribution escalation rate
- Project school fees and investment balance up to 2039
- Visualize projections with interactive charts
- Store and view historical projections
- Track actual values against projections
- Editable school fees and bonus tables

## Installation

1. Clone this repository:

```bash
git clone https://github.com/your-username/school-fees-projection-calculator.git
cd school-fees-projection-calculator
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Access the application in your web browser at `http://localhost:8501`

## Database Structure

The application uses SQLite with three main tables:
- `projections`: Stores projection parameters and metadata
- `projected_values`: Stores yearly projected values
- `actual_values`: Stores actual recorded values

## Testing

To verify the database setup:

```bash
python test_db.py
```

This script will create the necessary tables and populate them with example data.

## Usage

- Create the database: `python create_database.py`
- Run the application: `streamlit run app.py`
- Access the application in your web browser at `http://localhost:8501`
- Use the sidebar to navigate through different sections and features
- Edit projections, actual values, and bonus tables as needed
- View and interact with the projections and historical data