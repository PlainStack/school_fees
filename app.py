import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Initialize connection to database
@st.cache_resource
def init_connection():
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    
    conn = sqlite3.connect('school_fees.db', check_same_thread=False)
    conn.row_factory = dict_factory
    return conn

def save_projection(conn, inputs, yearly_results):
    cursor = conn.cursor()
    
    # Save main projection
    cursor.execute("""
        INSERT INTO projections (projection_date, seed_capital, investment_rate, contribution_escalation)
        VALUES (?, ?, ?, ?)
    """, (datetime.now().date(), inputs['seed_capital'], 
          inputs['investment_rate'], inputs['contribution_escalation']))
    
    projection_id = cursor.lastrowid
    
    # Save yearly projections
    for year, values in yearly_results.items():
        cursor.execute("""
            INSERT INTO projected_values 
            (projection_id, year, school_fees, monthly_contribution, annual_bonus, projected_balance)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (projection_id, year, values['school_fees'], 
              values['monthly_contribution'], values['annual_bonus'], 
              values['balance']))
    
    conn.commit()

def save_actual_values(conn, year, values):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO actual_values 
        (year, school_fees, monthly_contribution, annual_bonus, actual_balance)
        VALUES (?, ?, ?, ?, ?)
    """, (year, values['school_fees'], values['monthly_contribution'],
          values['annual_bonus'], values['balance']))
    conn.commit()

def calculate_monthly_contribution(inputs, fees_data, bonus_data):
    def calculate_future_value(monthly_payment):
        balance = float(inputs['seed_capital'])
        monthly_payment_current = monthly_payment
        MONTHLY_RATE = (1 + float(inputs['investment_rate'])) ** (1/12) - 1
        
        # Only simulate up to 2039
        for year in range(2025, 2040):  # Changed end year to 2040 (exclusive)
            # Get annual values for this year
            school_fees = float(fees_data[fees_data['Year'] == year]['Fees'].iloc[0])
            annual_bonus = float(bonus_data[bonus_data['Year'] == year]['Bonus'].iloc[0])
            
            # Deduct school fees at start of year (except first year)
            if year > 2025:
                if balance < school_fees:
                    return float('-inf')
                balance -= school_fees
            
            # Monthly contributions and growth
            for _ in range(12):
                balance += monthly_payment_current
                balance *= (1 + MONTHLY_RATE)
            
            # Add bonus at end of year
            balance += annual_bonus
            monthly_payment_current *= (1 + float(inputs['contribution_escalation']))
        
        return balance

    # Binary search to find optimal monthly payment
    payment_low = 0
    payment_high = max(fees_data['Fees']) / 12 * 3
    
    while payment_high - payment_low > 0.01:
        payment_mid = (payment_low + payment_high) / 2
        final_balance = calculate_future_value(payment_mid)
        
        if final_balance == float('-inf'):
            payment_low = payment_mid
        elif abs(final_balance) < 1:
            return payment_mid
        elif final_balance < 0:
            payment_low = payment_mid
        else:
            payment_high = payment_mid
    
    return payment_low

def calculate_projection(inputs, fees_data, bonus_data):
    # Calculate initial monthly payment
    initial_monthly_payment = calculate_monthly_contribution(inputs, fees_data, bonus_data)
    
    balance = float(inputs['seed_capital'])
    monthly_payment = initial_monthly_payment
    MONTHLY_RATE = (1 + float(inputs['investment_rate'])) ** (1/12) - 1
    
    yearly_results = {}
    
    # Only project up to 2039
    for year in range(2025, 2040):  # Changed end year to 2040 (exclusive)
        starting_balance = balance
        
        # Get annual values
        school_fees = float(fees_data[fees_data['Year'] == year]['Fees'].iloc[0])
        annual_bonus = float(bonus_data[bonus_data['Year'] == year]['Bonus'].iloc[0])
        
        # Deduct school fees at start of year (except first year)
        if year > 2025:
            balance -= school_fees
            print(f"Year {year} - Deducted school fees: R{school_fees:,.2f}")
            print(f"Balance after fees: R{balance:,.2f}")
        
        # Monthly contributions and growth
        annual_contributions = 0
        for _ in range(12):
            balance += monthly_payment
            annual_contributions += monthly_payment
            balance *= (1 + MONTHLY_RATE)
        
        # Add annual bonus at end of year
        balance += annual_bonus
        
        yearly_results[year] = {
            'school_fees': float(school_fees),
            'monthly_contribution': float(monthly_payment),
            'annual_contributions': float(annual_contributions),
            'annual_bonus': float(annual_bonus),
            'balance': float(balance),
            'investment_return': float(balance - starting_balance - annual_contributions - annual_bonus + 
                                    (school_fees if year > 2025 else 0))
        }
        
        # Increase monthly payment for next year
        monthly_payment *= (1 + float(inputs['contribution_escalation']))
    
    return yearly_results

def create_projection_chart(yearly_results):
    df = pd.DataFrame.from_dict(yearly_results, orient='index')
    df = df.astype(float)
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'Year'}, inplace=True)
    
    fig = go.Figure()
    
    # Add balance line
    fig.add_trace(go.Scatter(
        x=df['Year'].astype(int),
        y=df['balance'].astype(float),
        name='Projected Balance',
        line=dict(color='blue')
    ))
    
    # Add school fees bars
    fig.add_trace(go.Bar(
        x=df['Year'].astype(int),
        y=df['school_fees'].astype(float),
        name='School Fees',
        marker_color='red',
        opacity=0.6
    ))
    
    fig.update_layout(
        title='Projected Balance vs School Fees',
        xaxis_title='Year',
        yaxis_title='Amount',
        hovermode='x unified',
        showlegend=True
    )
    
    return fig

def main():
    st.title("School Fees Projection Calculator")
    
    conn = init_connection()
    
    # Load initial data
    fees_df = pd.DataFrame({
        'Year': range(2025, 2040),  # Changed to 2040 (exclusive)
        'Fees': [
            0,      # 2025
            181413, # 2026
            203907, # 2027
            259330, # 2028
            287039, # 2029
            311901, # 2030
            323677, # 2031
            359029, # 2032
            384372, # 2033
            411551, # 2034
            465033, # 2035
            497920, # 2036
            524159, # 2037
            554905, # 2038
            627957  # 2039
        ]
    })
    
    bonus_df = pd.DataFrame({
        'Year': range(2025, 2040),  # Changed to 2040 (exclusive)
        'Bonus': [
            50000,  # 2025
            75000,  # 2026
            78750,  # 2027
            82688,  # 2028
            86822,  # 2029
            91163,  # 2030
            95721,  # 2031
            100507, # 2032
            105533, # 2033
            110809, # 2034
            116350, # 2035
            122167, # 2036
            128256, # 2037
            134629, # 2038
            0       # 2039
        ]
    })
    
    tab1, tab2, tab3 = st.tabs(["Calculator", "Historical Projections", "Actual Values"])
    
    with tab1:
        st.header("Calculator")
        
        # Input parameters
        seed_capital = st.number_input("Seed Capital", value=119000.0, min_value=0.0)
        investment_rate = st.number_input("Investment Rate", value=0.0878, format="%.4f")
        contribution_escalation = st.number_input("Contribution Escalation", value=0.05, format="%.4f")
        
        # Editable tables for fees and bonus
        with st.expander("Edit School Fees"):
            edited_fees = st.data_editor(fees_df, num_rows="fixed")
        
        with st.expander("Edit Annual Bonus"):
            edited_bonus = st.data_editor(bonus_df, num_rows="fixed")
        
        if st.button("Calculate Projection"):
            inputs = {
                'seed_capital': seed_capital,
                'investment_rate': investment_rate,
                'contribution_escalation': contribution_escalation
            }
            
            yearly_results = calculate_projection(inputs, edited_fees, edited_bonus)
            
            # Save projection to database
            save_projection(conn, inputs, yearly_results)
            
            # Display results
            fig = create_projection_chart(yearly_results)
            st.plotly_chart(fig)
            
            # Create and display detailed results table
            results_df = pd.DataFrame.from_dict(yearly_results, orient='index')
            results_df.reset_index(inplace=True)
            results_df.rename(columns={'index': 'Year'}, inplace=True)
            st.dataframe(results_df)
    
    with tab2:
        st.header("Historical Projections")
        
        # Query historical projections
        cursor = conn.cursor()
        projections = pd.read_sql_query("""
            SELECT id, projection_date, seed_capital, investment_rate, contribution_escalation
            FROM projections
            ORDER BY projection_date DESC
        """, conn)
        
        if not projections.empty:
            st.write("Select a projection to view:")
            selected_projection = st.selectbox(
                "Historical Projections",
                projections['id'].tolist(),
                format_func=lambda x: f"Projection {x} - {projections[projections['id']==x]['projection_date'].iloc[0]}"
            )
            
            if selected_projection:
                projection_data = pd.read_sql_query("""
                    SELECT year, school_fees, monthly_contribution, annual_bonus, projected_balance
                    FROM projected_values
                    WHERE projection_id = ?
                    ORDER BY year
                """, conn, params=(selected_projection,))
                
                st.dataframe(projection_data)
                
                # Create visualization
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=projection_data['year'],
                    y=projection_data['projected_balance'],
                    name='Projected Balance'
                ))
                fig.add_trace(go.Bar(
                    x=projection_data['year'],
                    y=projection_data['school_fees'],
                    name='School Fees',
                    opacity=0.6
                ))
                st.plotly_chart(fig)
    
    with tab3:
        st.header("Actual Values")
        
        # Form for adding actual values
        year = st.number_input("Year", min_value=2025, max_value=2039, step=1)
        actual_fees = st.number_input("Actual School Fees", min_value=0.0)
        actual_monthly = st.number_input("Actual Monthly Contribution", min_value=0.0)
        actual_bonus = st.number_input("Actual Annual Bonus", min_value=0.0)
        actual_balance = st.number_input("Actual Balance", min_value=0.0)
        
        if st.button("Save Actual Values"):
            values = {
                'school_fees': actual_fees,
                'monthly_contribution': actual_monthly,
                'annual_bonus': actual_bonus,
                'balance': actual_balance
            }
            save_actual_values(conn, year, values)
            st.success(f"Actual values for {year} saved successfully!")
        
        # Display actual values
        actual_data = pd.read_sql_query("""
            SELECT * FROM actual_values ORDER BY year
        """, conn)
        
        if not actual_data.empty:
            st.subheader("Recorded Actual Values")
            st.dataframe(actual_data)

if __name__ == "__main__":
    main()