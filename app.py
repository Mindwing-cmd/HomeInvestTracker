
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import json
import os
from calculator import (
    calculate_mortgage_payment,
    calculate_amortization_schedule,
    calculate_investment_metrics,
    calculate_loan_term
)

# Translation dictionaries
translations = {
    "en": {
        "title": "German Real Estate Investment Calculator",
        "subtitle": "Analyze your potential real estate investment with this buy and hold calculator, including German tax benefits (AFA).",
        "investment_details": "Investment Details",
        "purchase_price": "Purchase Price (€)",
        "down_payment": "Down Payment (€)",
        "interest_rate": "Interest Rate (%)",
        "repayment_rate": "Initial Repayment Rate (%)",
        "monthly_expenses": "Monthly Expenses (€)",
        "rental_income": "Monthly Rental Income (€)",
        "appreciation_rate": "Annual Appreciation Rate (%)",
        "tax_settings": "Tax Settings",
        "income_tax": "Income Tax Rate (%)",
        "afa_rate": "AFA Rate (%)",
        "investment_analysis": "Investment Analysis",
        "monthly_mortgage": "Monthly Mortgage Payment",
        "loan_term": "Loan Term",
        "monthly_cash_flow": "Monthly Cash Flow",
        "monthly_tax_benefit": "Monthly Tax Benefit",
        "cash_on_cash": "Cash on Cash Return",
        "annual_tax_benefit": "Annual Tax Benefit",
        "visualizations": "Visualizations",
        "total_payments": "Total Monthly Payments",
        "rental_income_only": "Rental Income Only",
        "rent_tax": "Rent + Tax Benefits",
        "property_value": "Property Value",
        "total_return": "Total Return (incl. Appreciation)",
        "etf_investment": "ETF Investment (7% annual)",
        "investment_returns": "Investment Returns Comparison",
        "year": "Year",
        "total_return_euro": "Total Return (€)",
        "monthly_breakdown": "Monthly Cash Flow Breakdown",
        "rent_increase_rate": "Annual Rent Increase Rate (%)",
        "mortgage_payment": "Mortgage Payment",
        "other_expenses": "Other Expenses",
        "tax_benefits": "Tax Benefits",
        "net_cash_flow": "Net Cash Flow",
        "monthly_interest": "Monthly Interest",
        "monthly_principal": "Monthly Principal",
        "amount_euro": "Amount (€)",
        "language": "Language",
        "theme": "Theme",
        "light": "Light",
        "dark": "Dark",
        "rent_increase_simulation": "Rent Increase Simulation",
        "add_rent_increase": "Add Rent Increase",
        "increase_year": "Year",
        "increase_amount": "Amount (€)",
        "add_increase": "Add",
        "clear_increases": "Clear All Increases"
    },
    "de": {
        "title": "Deutscher Immobilieninvestitionsrechner",
        "subtitle": "Analysieren Sie Ihre potenzielle Immobilieninvestition mit diesem Kauf-und-Halte-Rechner, einschließlich deutscher Steuervorteile (AfA).",
        "investment_details": "Investitionsdetails",
        "purchase_price": "Kaufpreis (€)",
        "down_payment": "Anzahlung (€)",
        "interest_rate": "Zinssatz (%)",
        "repayment_rate": "Anfängliche Tilgungsrate (%)",
        "monthly_expenses": "Monatliche Ausgaben (€)",
        "rental_income": "Monatliche Mieteinnahmen (€)",
        "appreciation_rate": "Jährliche Wertsteigerungsrate (%)",
        "tax_settings": "Steuereinstellungen",
        "income_tax": "Einkommensteuersatz (%)",
        "afa_rate": "AfA-Satz (%)",
        "investment_analysis": "Investitionsanalyse",
        "monthly_mortgage": "Monatliche Hypothekenzahlung",
        "loan_term": "Kreditlaufzeit",
        "monthly_cash_flow": "Monatlicher Cashflow",
        "monthly_tax_benefit": "Monatlicher Steuervorteil",
        "cash_on_cash": "Cash-on-Cash-Rendite",
        "annual_tax_benefit": "Jährlicher Steuervorteil",
        "visualizations": "Visualisierungen",
        "total_payments": "Gesamte monatliche Zahlungen",
        "rental_income_only": "Nur Mieteinnahmen",
        "rent_tax": "Miete + Steuervorteile",
        "property_value": "Immobilienwert",
        "total_return": "Gesamtrendite (inkl. Wertsteigerung)",
        "etf_investment": "ETF-Investition (7% jährlich)",
        "investment_returns": "Vergleich der Investitionsrenditen",
        "year": "Jahr",
        "total_return_euro": "Gesamtrendite (€)",
        "monthly_breakdown": "Aufschlüsselung des monatlichen Cashflows",
        "rent_increase_rate": "Jährliche Mieterhöhungsrate (%)",
        "mortgage_payment": "Hypothekenzahlung",
        "other_expenses": "Andere Ausgaben",
        "tax_benefits": "Steuervorteile",
        "net_cash_flow": "Netto-Cashflow",
        "monthly_interest": "Monatliche Zinsen",
        "monthly_principal": "Monatliche Tilgung",
        "amount_euro": "Betrag (€)",
        "language": "Sprache",
        "theme": "Thema",
        "light": "Hell",
        "dark": "Dunkel",
        "rent_increase_simulation": "Mieterhöhungssimulation",
        "add_rent_increase": "Mieterhöhung hinzufügen",
        "increase_year": "Jahr",
        "increase_amount": "Betrag (€)",
        "add_increase": "Hinzufügen",
        "clear_increases": "Alle Erhöhungen löschen"
    }
}

def calculate_etf_returns(initial_investment, monthly_investment, monthly_income, years, annual_return=0.07, rent_increase_rate=0.0):
    """Calculate ETF investment returns over time with monthly cash flows and rent increases."""
    months = int(years * 12)
    monthly_return = (1 + annual_return) ** (1/12) - 1

    balance = [initial_investment]
    for month in range(1, months + 1):
        prev_balance = balance[-1]
        
        # Calculate rent with increases
        year = month / 12
        increased_rent = monthly_income * (1 + rent_increase_rate/100) ** year
        
        # Add monthly rental income and subtract monthly expenses/mortgage
        monthly_cash_flow = increased_rent - monthly_investment
        new_balance = (prev_balance + monthly_cash_flow) * (1 + monthly_return)
        balance.append(new_balance)

    return balance

def main():
    # App configuration using session state to persist settings
    if 'language' not in st.session_state:
        st.session_state.language = "de"
    
    # Add language selector to the top right corner
    language = st.sidebar.selectbox(
        "Language/Sprache", 
        options=["de", "en"],
        format_func=lambda x: "Deutsch" if x == "de" else "English",
        key="language",
        help="Sprache wählen/Select language"
    )
    
    # Translate text based on selected language
    t = translations[language]
    
    st.title(t["title"])
    st.write(t["subtitle"])

    # Input Section
    st.header(t["investment_details"])

    col1, col2 = st.columns(2)

    with col1:
        purchase_price = st.number_input(
            t["purchase_price"], 
            min_value=0, 
            value=300000,
            help="The total purchase price of the property"
        )

        down_payment = st.number_input(
            t["down_payment"], 
            min_value=0, 
            max_value=purchase_price,
            value=int(purchase_price * 0.1),
            help="The amount you plan to pay upfront"
        )

        interest_rate = st.number_input(
            t["interest_rate"], 
            min_value=0.0, 
            max_value=20.0, 
            value=4.0,
            step=0.1,
            help="Annual interest rate for the mortgage"
        )

        repayment_rate = st.number_input(
            t["repayment_rate"], 
            min_value=0.1, 
            max_value=20.0, 
            value=2.0,
            step=0.1,
            help="Annual repayment rate (affects loan term)"
        )

    with col2:
        monthly_expenses = st.number_input(
            t["monthly_expenses"], 
            min_value=0, 
            value=500,
            help="Total monthly expenses including taxes, insurance, and maintenance"
        )

        rental_income = st.number_input(
            t["rental_income"], 
            min_value=0, 
            value=2500,
            help="Expected monthly rental income"
        )

        appreciation_rate = st.number_input(
            t["appreciation_rate"], 
            min_value=-10.0, 
            max_value=20.0, 
            value=3.0,
            step=0.1,
            help="Expected annual property value appreciation rate"
        )
        
        rent_increase_rate = st.number_input(
            t["rent_increase_rate"], 
            min_value=0.0, 
            max_value=10.0, 
            value=1.5,
            step=0.1,
            help="Expected annual rent increase rate"
        )
        
        # Rent increase simulation
        st.write(t["rent_increase_simulation"])
        
        # Initialize session state for rent increases if not exists
        if 'rent_increases' not in st.session_state:
            st.session_state.rent_increases = []
            
        # Display the current rent increases in a table
        if st.session_state.rent_increases:
            increase_df = pd.DataFrame(st.session_state.rent_increases)
            st.dataframe(increase_df)
            
        # Add new rent increase
        with st.expander(t["add_rent_increase"]):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                new_year = st.number_input(t["increase_year"], min_value=1, max_value=50, value=5)
            with col2:
                new_amount = st.number_input(t["increase_amount"], min_value=0, value=100)
            with col3:
                if st.button(t["add_increase"]):
                    # Add new increase to the list
                    st.session_state.rent_increases.append({
                        "Year": new_year,
                        "Amount": new_amount
                    })
                    st.rerun()
        
        # Clear all increases
        if st.button(t["clear_increases"]):
            st.session_state.rent_increases = []
            st.rerun()

    # Tax Settings
    st.header(t["tax_settings"])
    col1, col2 = st.columns(2)

    with col1:
        tax_rate = st.number_input(
            t["income_tax"],
            min_value=0.0,
            max_value=45.0,
            value=42.0,
            step=1.0,
            help="Your marginal tax rate"
        )

    with col2:
        afa_rate = st.number_input(
            t["afa_rate"],
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
            tax_rate,
            rent_increase_rate
        )

        # Results Section
        st.header(t["investment_analysis"])

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                t["monthly_mortgage"],
                f"€{metrics['monthly_mortgage']:,.2f}"
            )
            st.metric(
                t["loan_term"],
                f"{metrics['loan_term']:.1f} {'years' if language == 'en' else 'Jahre'}"
            )

        with col2:
            st.metric(
                t["monthly_cash_flow"],
                f"€{metrics['monthly_cash_flow']:,.2f}"
            )
            st.metric(
                t["monthly_tax_benefit"],
                f"€{metrics['monthly_tax_benefit']:,.2f}"
            )

        with col3:
            st.metric(
                t["cash_on_cash"],
                f"{metrics['cash_on_cash_return']:.2f}%"
            )
            st.metric(
                t["annual_tax_benefit"],
                f"€{metrics['annual_tax_benefit']:,.2f}"
            )

        # Visualization Section
        st.header(t["visualizations"])

        # Investment Returns Comparison
        years = np.linspace(0, loan_term, int(loan_term * 12) + 1)
        months = list(range(int(loan_term * 12) + 1))

        # Calculate rent with increases over time
        rent_values = []
        
        # Get custom rent increases from session state
        custom_increases = {}
        if st.session_state.rent_increases:
            for item in st.session_state.rent_increases:
                custom_increases[item["Year"]] = item["Amount"]
        
        for month in months:
            year = month / 12
            current_year = int(year)
            
            # Start with base rent and apply general increase rate
            current_rent = rental_income * (1 + rent_increase_rate/100) ** year
            
            # Apply custom increases for years before or at the current year
            for inc_year, inc_amount in custom_increases.items():
                if inc_year <= current_year:
                    current_rent += inc_amount
                    
            rent_values.append(current_rent)
        
        rent_only = [rent_values[month] * month for month in months]
        rent_tax = [(rent_values[month] + metrics['monthly_tax_benefit']) * month for month in months]
        monthly_payments = [month * (metrics['monthly_mortgage'] + monthly_expenses) for month in months]
        property_values = [purchase_price * (1 + appreciation_rate/100) ** year for year in years]
        total_returns = [r + t + (v - purchase_price) for r, t, v in zip(rent_only, rent_tax, property_values)]

        fig_returns = go.Figure()
        fig_returns.add_trace(go.Scatter(
            x=years,
            y=monthly_payments,
            name=t["total_payments"],
            line=dict(dash='dot', color='#ff4d4d')
        ))
        fig_returns.add_trace(go.Scatter(
            x=years,
            y=rent_only,
            name=t["rental_income_only"],
            line=dict(dash='dot', color='#2E86C1')
        ))
        fig_returns.add_trace(go.Scatter(
            x=years,
            y=rent_tax,
            name=t["rent_tax"],
            line=dict(dash='dash', color='#27AE60')
        ))
        fig_returns.add_trace(go.Scatter(
            x=years,
            y=property_values,
            name=t["property_value"],
            line=dict(dash='dashdot', color='#3498DB')
        ))
        fig_returns.add_trace(go.Scatter(
            x=years,
            y=total_returns,
            name=t["total_return"],
            line=dict(dash='solid', color='#2ECC71')
        ))

        # Add ETF comparison with monthly cash flows
        etf_returns = calculate_etf_returns(
            down_payment,
            metrics['monthly_mortgage'] + monthly_expenses,
            rental_income,
            loan_term,
            0.07,  # 7% annual return
            rent_increase_rate
        )
        fig_returns.add_trace(go.Scatter(
            x=years[:len(etf_returns)],
            y=etf_returns,
            name=t["etf_investment"],
            line=dict(dash='longdash', color='#E74C3C')
        ))

        fig_returns.update_layout(
            title=t["investment_returns"],
            xaxis_title=t["year"],
            yaxis_title=t["total_return_euro"],
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        st.plotly_chart(fig_returns, use_container_width=True)

        # Monthly Payment Breakdown
        monthly_breakdown = go.Figure(data=[
            go.Pie(
                labels=[t["mortgage_payment"], t["other_expenses"], t["tax_benefits"], t["net_cash_flow"]],
                values=[
                    metrics['monthly_mortgage'],
                    monthly_expenses,
                    metrics['monthly_tax_benefit'],
                    metrics['monthly_cash_flow']
                ],
                hole=0.4,
                marker_colors=['#ff4d4d', '#ff6666', '#27AE60', '#2ECC71']
            )
        ])
        monthly_breakdown.update_layout(title=t["monthly_breakdown"])
        st.plotly_chart(monthly_breakdown, use_container_width=True)

        # Monthly Interest vs Principal Payments
        amort_schedule = calculate_amortization_schedule(
            purchase_price, down_payment, interest_rate, repayment_rate, afa_rate, tax_rate)

        fig_monthly = go.Figure()
        fig_monthly.add_trace(go.Scatter(
            x=amort_schedule['Month'] / 12,  # Convert to years
            y=amort_schedule['Interest'],
            name=t["monthly_interest"],
            line=dict(dash='solid', color='#ff4d4d')
        ))
        fig_monthly.add_trace(go.Scatter(
            x=amort_schedule['Month'] / 12,  # Convert to years
            y=amort_schedule['Principal'],
            name=t["monthly_principal"],
            line=dict(dash='solid', color='#2E86C1')
        ))
        fig_monthly.update_layout(
            title=t["monthly_interest"] + " vs " + t["monthly_principal"],
            xaxis_title=t["year"],
            yaxis_title=t["amount_euro"]
        )
        st.plotly_chart(fig_monthly, use_container_width=True)

    except Exception as e:
        st.error(f"An error occurred in calculations: {str(e)}")

if __name__ == "__main__":
    main()
