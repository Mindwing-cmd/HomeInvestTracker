import numpy as np
import pandas as pd
import streamlit as st

def calculate_loan_term(principal, down_payment, interest_rate, repayment_rate):
    """Calculate loan term based on repayment rate."""
    loan_amount = principal - down_payment
    # Monthly rate calculations
    monthly_interest_rate = interest_rate / 12 / 100
    monthly_repayment_rate = repayment_rate / 12 / 100

    # Total monthly rate (interest + repayment)
    total_monthly_rate = monthly_interest_rate + monthly_repayment_rate

    # Calculate years until full repayment
    # Using the formula: n = -log(1 - (P*r)/(PMT)) / log(1 + r)
    # where P is principal, r is interest rate, PMT is total payment
    monthly_payment = loan_amount * total_monthly_rate
    if monthly_interest_rate == 0:
        return loan_amount / (monthly_payment)

    term_months = -np.log(1 - (loan_amount * monthly_interest_rate) / monthly_payment) / np.log(1 + monthly_interest_rate)
    return round(term_months / 12, 1)

def calculate_mortgage_payment(principal, down_payment, interest_rate, repayment_rate):
    """Calculate monthly mortgage payment including repayment."""
    loan_amount = principal - down_payment
    monthly_total_rate = (interest_rate + repayment_rate) / 12 / 100
    return loan_amount * monthly_total_rate

def calculate_tax_benefits(purchase_price, loan_amount, interest_rate, afa_rate, tax_rate, month, repayment_rate):
    """Calculate monthly tax benefits from interest and depreciation."""
    # Calculate remaining loan and interest payment
    years_passed = month / 12
    # Simplified remaining loan calculation
    remaining_loan = loan_amount * (1 - years_passed * repayment_rate/100)
    remaining_loan = max(0, remaining_loan)

    # Monthly interest payment
    monthly_interest = remaining_loan * (interest_rate / 12 / 100)

    # Monthly depreciation (AFA)
    monthly_afa = (purchase_price * (afa_rate / 100)) / 12

    # Total deductible amount
    total_deductible = monthly_interest + monthly_afa

    # Tax benefit
    tax_benefit = total_deductible * (tax_rate / 100)

    return {
        'interest_deduction': monthly_interest,
        'afa_deduction': monthly_afa,
        'tax_benefit': tax_benefit
    }

def calculate_amortization_schedule(principal, down_payment, interest_rate, repayment_rate, afa_rate, tax_rate):
    """Generate amortization schedule with tax benefits."""
    loan_amount = principal - down_payment
    loan_term = calculate_loan_term(principal, down_payment, interest_rate, repayment_rate)
    num_payments = int(loan_term * 12)
    monthly_payment = calculate_mortgage_payment(principal, down_payment, interest_rate, repayment_rate)

    schedule = []
    remaining_balance = loan_amount

    for month in range(1, num_payments + 1):
        # Calculate tax benefits
        tax_benefits = calculate_tax_benefits(
            principal, loan_amount, interest_rate, afa_rate, tax_rate, month, repayment_rate)

        # Calculate interest and principal portions
        interest_payment = remaining_balance * (interest_rate / 12 / 100)
        principal_payment = monthly_payment - interest_payment
        remaining_balance -= principal_payment

        schedule.append({
            'Month': month,
            'Payment': monthly_payment,
            'Principal': principal_payment,
            'Interest': interest_payment,
            'Remaining Balance': max(0, remaining_balance),
            'Interest Deduction': tax_benefits['interest_deduction'],
            'AFA Deduction': tax_benefits['afa_deduction'],
            'Tax Benefit': tax_benefits['tax_benefit']
        })

    return pd.DataFrame(schedule)

def calculate_investment_metrics(purchase_price, down_payment, interest_rate, repayment_rate,
                              monthly_expenses, rental_income, appreciation_rate,
                              afa_rate, tax_rate, rent_increase_rate=0.0):
    """Calculate various investment metrics including tax benefits and rent increases."""
    # Calculate loan term based on repayment rate
    loan_term = calculate_loan_term(purchase_price, down_payment, interest_rate, repayment_rate)

    # Monthly mortgage payment
    monthly_mortgage = calculate_mortgage_payment(
        purchase_price, down_payment, interest_rate, repayment_rate)

    # Calculate first month's tax benefits
    loan_amount = purchase_price - down_payment
    initial_tax_benefits = calculate_tax_benefits(
        purchase_price, loan_amount, interest_rate, afa_rate, tax_rate, 1, repayment_rate)

    # Calculate average rental income over the loan term (with rent increases)
    avg_rental_income = 0
    total_rent = 0
    
    # Setup for custom rent increases
    custom_increases = {}
    if 'rent_increases' in st.session_state:
        for item in st.session_state.rent_increases:
            custom_increases[item["Year"]] = item["Amount"]
    
    for month in range(1, int(loan_term * 12) + 1):
        year = month / 12
        current_year = int(year)
        
        # Start with base rent
        current_rent = rental_income
        
        # Apply general increase rate
        current_rent = rental_income * (1 + rent_increase_rate/100) ** year
        
        # Apply custom increases for years before or at the current year
        for inc_year, inc_amount in custom_increases.items():
            if inc_year <= current_year:
                current_rent += inc_amount
        
        total_rent += current_rent
    
    if loan_term > 0:
        avg_rental_income = total_rent / (loan_term * 12)
    else:
        avg_rental_income = rental_income

    # We still use rental_income for initial cash flow (first month)
    monthly_cash_flow = (rental_income 
                        - (monthly_mortgage + monthly_expenses) 
                        + initial_tax_benefits['tax_benefit'])

    # Annual cash flow (using initial rental income)
    annual_cash_flow = monthly_cash_flow * 12

    # Cash on cash return (based on initial investment and initial cash flow)
    initial_investment = down_payment  # Simplified, normally would include closing costs
    cash_on_cash_return = (annual_cash_flow / initial_investment) * 100

    # Future value after loan term
    future_value = purchase_price * (1 + appreciation_rate/100) ** loan_term

    # Calculate remaining balance using amortization schedule
    amort_schedule = calculate_amortization_schedule(
        purchase_price, down_payment, interest_rate, repayment_rate, afa_rate, tax_rate)
    remaining_balance = amort_schedule.iloc[-1]['Remaining Balance']

    total_equity = future_value - remaining_balance

    # Calculate average annual tax benefits
    avg_annual_tax_benefit = amort_schedule['Tax Benefit'].mean() * 12

    return {
        'loan_term': loan_term,
        'monthly_mortgage': monthly_mortgage,
        'monthly_cash_flow': monthly_cash_flow,
        'annual_cash_flow': annual_cash_flow,
        'cash_on_cash_return': cash_on_cash_return,
        'future_value': future_value,
        'total_equity': total_equity,
        'monthly_tax_benefit': initial_tax_benefits['tax_benefit'],
        'annual_tax_benefit': avg_annual_tax_benefit,
        'avg_rental_income': avg_rental_income
    }