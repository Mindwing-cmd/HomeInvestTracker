import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from calculator import (
    calculate_mortgage_payment,
    calculate_amortization_schedule,
    calculate_investment_metrics
)

def main():
    st.title("Real Estate Investment Calculator")
    st.write("Analyze your potential real estate investment with this buy and hold calculator.")

    # Input Section
    st.header("Investment Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        purchase_price = st.number_input(
            "Purchase Price ($)", 
            min_value=0, 
            value=300000,
            help="The total purchase price of the property"
        )
        
        down_payment = st.number_input(
            "Down Payment ($)", 
            min_value=0, 
            max_value=purchase_price,
            value=int(purchase_price * 0.2),
            help="The amount you plan to pay upfront"
        )
        
        interest_rate = st.number_input(
            "Interest Rate (%)", 
            min_value=0.0, 
            max_value=20.0, 
            value=4.5,
            step=0.1,
            help="Annual interest rate for the mortgage"
        )
        
        loan_term = st.number_input(
            "Loan Term (years)", 
            min_value=1, 
            max_value=40, 
            value=30,
            help="The length of the mortgage in years"
        )

    with col2:
        monthly_expenses = st.number_input(
            "Monthly Expenses ($)", 
            min_value=0, 
            value=500,
            help="Total monthly expenses including taxes, insurance, and maintenance"
        )
        
        rental_income = st.number_input(
            "Monthly Rental Income ($)", 
            min_value=0, 
            value=2500,
            help="Expected monthly rental income"
        )
        
        appreciation_rate = st.number_input(
            "Annual Appreciation Rate (%)", 
            min_value=-10.0, 
            max_value=20.0, 
            value=3.0,
            step=0.1,
            help="Expected annual property value appreciation rate"
        )

    # Calculate metrics
    try:
        metrics = calculate_investment_metrics(
            purchase_price,
            down_payment,
            interest_rate,
            loan_term,
            monthly_expenses,
            rental_income,
            appreciation_rate
        )
        
        # Results Section
        st.header("Investment Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Monthly Mortgage Payment",
                f"${metrics['monthly_mortgage']:,.2f}"
            )
            
        with col2:
            st.metric(
                "Monthly Cash Flow",
                f"${metrics['monthly_cash_flow']:,.2f}"
            )
            
        with col3:
            st.metric(
                "Cash on Cash Return",
                f"{metrics['cash_on_cash_return']:.2f}%"
            )

        # Visualization Section
        st.header("Visualizations")
        
        # Monthly Payment Breakdown
        monthly_breakdown = go.Figure(data=[
            go.Pie(
                labels=['Mortgage Payment', 'Other Expenses', 'Net Cash Flow'],
                values=[
                    metrics['monthly_mortgage'],
                    monthly_expenses,
                    metrics['monthly_cash_flow']
                ],
                hole=0.4
            )
        ])
        monthly_breakdown.update_layout(title="Monthly Payment Breakdown")
        st.plotly_chart(monthly_breakdown, use_container_width=True)

        # Amortization Schedule
        amort_schedule = calculate_amortization_schedule(
            purchase_price, down_payment, interest_rate, loan_term)
        
        cumulative_equity = go.Figure()
        cumulative_equity.add_trace(go.Scatter(
            x=amort_schedule['Month'],
            y=amort_schedule['Principal'].cumsum(),
            name='Principal Paid',
            fill='tozeroy'
        ))
        cumulative_equity.update_layout(
            title="Cumulative Principal Paid Over Time",
            xaxis_title="Month",
            yaxis_title="Cumulative Principal ($)"
        )
        st.plotly_chart(cumulative_equity, use_container_width=True)

        # Property Value Projection
        years = list(range(loan_term + 1))
        property_values = [purchase_price * (1 + appreciation_rate/100) ** year for year in years]
        
        value_projection = px.line(
            x=years,
            y=property_values,
            title="Projected Property Value Over Time",
            labels={"x": "Year", "y": "Property Value ($)"}
        )
        st.plotly_chart(value_projection, use_container_width=True)

    except Exception as e:
        st.error(f"An error occurred in calculations: {str(e)}")

if __name__ == "__main__":
    main()
