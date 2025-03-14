import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from calculator import (
    calculate_mortgage_payment,
    calculate_amortization_schedule,
    calculate_investment_metrics,
    calculate_loan_term
)

def calculate_etf_returns(initial_investment, monthly_investment, monthly_income, years, annual_return=0.07):
    """Calculate ETF investment returns over time with monthly cash flows."""
    months = int(years * 12)
    monthly_return = (1 + annual_return) ** (1/12) - 1

    balance = [initial_investment]
    for month in range(1, months + 1):
        prev_balance = balance[-1]
        # Add monthly rental income and subtract monthly expenses/mortgage
        monthly_cash_flow = monthly_income - monthly_investment
        new_balance = (prev_balance + monthly_cash_flow) * (1 + monthly_return)
        balance.append(new_balance)

    return balance

def main():
    st.title("German Real Estate Investment Calculator")
    st.write("Analyze your potential real estate investment with this buy and hold calculator, including German tax benefits (AFA).")

    # Input Section
    st.header("Investment Details")

    col1, col2 = st.columns(2)

    with col1:
        purchase_price = st.number_input(
            "Purchase Price (€)", 
            min_value=0, 
            value=300000,
            help="The total purchase price of the property"
        )

        down_payment = st.number_input(
            "Down Payment (€)", 
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

        repayment_rate = st.number_input(
            "Initial Repayment Rate (%)", 
            min_value=0.1, 
            max_value=20.0, 
            value=2.0,
            step=0.1,
            help="Annual repayment rate (affects loan term)"
        )

    with col2:
        monthly_expenses = st.number_input(
            "Monthly Expenses (€)", 
            min_value=0, 
            value=500,
            help="Total monthly expenses including taxes, insurance, and maintenance"
        )

        rental_income = st.number_input(
            "Monthly Rental Income (€)", 
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

    # Tax Settings
    st.header("Tax Settings")
    col1, col2 = st.columns(2)

    with col1:
        tax_rate = st.number_input(
            "Income Tax Rate (%)",
            min_value=0.0,
            max_value=45.0,
            value=42.0,
            step=1.0,
            help="Your marginal tax rate"
        )

    with col2:
        afa_rate = st.number_input(
            "AFA Rate (%)",
            min_value=0.0,
            max_value=5.0,
            value=2.0,
            step=0.1,
            help="Depreciation rate (typically 2% for residential properties)"
        )

    # Calculate metrics
    try:
        loan_term = calculate_loan_term(
            purchase_price, down_payment, interest_rate, repayment_rate)

        metrics = calculate_investment_metrics(
            purchase_price,
            down_payment,
            interest_rate,
            repayment_rate,
            monthly_expenses,
            rental_income,
            appreciation_rate,
            afa_rate,
            tax_rate
        )

        # Results Section
        st.header("Investment Analysis")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Monthly Mortgage Payment",
                f"€{metrics['monthly_mortgage']:,.2f}"
            )
            st.metric(
                "Loan Term",
                f"{metrics['loan_term']:.1f} years"
            )

        with col2:
            st.metric(
                "Monthly Cash Flow",
                f"€{metrics['monthly_cash_flow']:,.2f}"
            )
            st.metric(
                "Monthly Tax Benefit",
                f"€{metrics['monthly_tax_benefit']:,.2f}"
            )

        with col3:
            st.metric(
                "Cash on Cash Return",
                f"{metrics['cash_on_cash_return']:.2f}%"
            )
            st.metric(
                "Annual Tax Benefit",
                f"€{metrics['annual_tax_benefit']:,.2f}"
            )

        # Visualization Section
        st.header("Visualizations")

        # Monthly Payment Breakdown
        monthly_breakdown = go.Figure(data=[
            go.Pie(
                labels=['Mortgage Payment', 'Other Expenses', 'Tax Benefits', 'Net Cash Flow'],
                values=[
                    metrics['monthly_mortgage'],
                    monthly_expenses,
                    metrics['monthly_tax_benefit'],
                    metrics['monthly_cash_flow']
                ],
                hole=0.4
            )
        ])
        monthly_breakdown.update_layout(title="Monthly Cash Flow Breakdown")
        st.plotly_chart(monthly_breakdown, use_container_width=True)

        # Monthly Interest vs Principal Payments
        amort_schedule = calculate_amortization_schedule(
            purchase_price, down_payment, interest_rate, repayment_rate, afa_rate, tax_rate)

        fig_monthly = go.Figure()
        fig_monthly.add_trace(go.Scatter(
            x=amort_schedule['Month'] / 12,  # Convert to years
            y=amort_schedule['Interest'],
            name='Monthly Interest',
            line=dict(dash='solid')
        ))
        fig_monthly.add_trace(go.Scatter(
            x=amort_schedule['Month'] / 12,  # Convert to years
            y=amort_schedule['Principal'],
            name='Monthly Principal',
            line=dict(dash='solid')
        ))
        fig_monthly.update_layout(
            title="Monthly Interest vs Principal Payments",
            xaxis_title="Year",
            yaxis_title="Amount (€)"
        )
        st.plotly_chart(fig_monthly, use_container_width=True)

        # Investment Returns Comparison
        years = np.linspace(0, loan_term, int(loan_term * 12) + 1)
        months = list(range(int(loan_term * 12) + 1))

        rent_only = [month * rental_income for month in months]
        rent_tax = [month * (rental_income + metrics['monthly_tax_benefit']) for month in months]
        monthly_payments = [month * (metrics['monthly_mortgage'] + monthly_expenses) for month in months]
        property_values = [purchase_price * (1 + appreciation_rate/100) ** (year) for year in years]
        total_returns = [r + t + (v - purchase_price) for r, t, v in zip(rent_only, rent_tax, property_values)]

        fig_returns = go.Figure()
        fig_returns.add_trace(go.Scatter(
            x=years,
            y=monthly_payments,
            name='Total Monthly Payments',
            line=dict(dash='dot', color='red')
        ))
        fig_returns.add_trace(go.Scatter(
            x=years,
            y=rent_only,
            name='Rental Income Only',
            line=dict(dash='dot')
        ))
        fig_returns.add_trace(go.Scatter(
            x=years,
            y=rent_tax,
            name='Rent + Tax Benefits',
            line=dict(dash='dash')
        ))
        fig_returns.add_trace(go.Scatter(
            x=years,
            y=property_values,
            name='Property Value',
            line=dict(dash='dashdot')
        ))
        fig_returns.add_trace(go.Scatter(
            x=years,
            y=total_returns,
            name='Total Return (incl. Appreciation)',
            line=dict(dash='solid')
        ))

        # Add ETF comparison with monthly cash flows
        etf_returns = calculate_etf_returns(
            down_payment,
            metrics['monthly_mortgage'] + monthly_expenses,
            rental_income,
            loan_term
        )
        fig_returns.add_trace(go.Scatter(
            x=years[:len(etf_returns)],
            y=etf_returns,
            name='ETF Investment (7% annual)',
            line=dict(dash='longdash')
        ))

        fig_returns.update_layout(
            title="Investment Returns Comparison",
            xaxis_title="Year",
            yaxis_title="Total Return (€)",
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        st.plotly_chart(fig_returns, use_container_width=True)

        # Property Value Projection
        years = list(range(int(loan_term) + 1))
        property_values = [purchase_price * (1 + appreciation_rate/100) ** year for year in years]

        value_projection = px.line(
            x=years,
            y=property_values,
            title="Projected Property Value Over Time",
            labels={"x": "Year", "y": "Property Value (€)"}
        )
        st.plotly_chart(value_projection, use_container_width=True)

    except Exception as e:
        st.error(f"An error occurred in calculations: {str(e)}")

if __name__ == "__main__":
    main()