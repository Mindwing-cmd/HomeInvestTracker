import numpy as np
import pandas as pd

def calculate_mortgage_payment(principal, down_payment, interest_rate, loan_term):
    """Calculate monthly mortgage payment using the PMT formula."""
    loan_amount = principal - down_payment
    monthly_rate = interest_rate / 12 / 100
    num_payments = loan_term * 12
    
    if monthly_rate == 0:
        return loan_amount / num_payments
    
    return -np.pmt(monthly_rate, num_payments, loan_amount)

def calculate_amortization_schedule(principal, down_payment, interest_rate, loan_term):
    """Generate amortization schedule."""
    loan_amount = principal - down_payment
    monthly_rate = interest_rate / 12 / 100
    num_payments = loan_term * 12
    monthly_payment = calculate_mortgage_payment(principal, down_payment, interest_rate, loan_term)
    
    schedule = []
    remaining_balance = loan_amount
    
    for month in range(1, num_payments + 1):
        interest_payment = remaining_balance * monthly_rate
        principal_payment = monthly_payment - interest_payment
        remaining_balance -= principal_payment
        
        schedule.append({
            'Month': month,
            'Payment': monthly_payment,
            'Principal': principal_payment,
            'Interest': interest_payment,
            'Remaining Balance': max(0, remaining_balance)
        })
    
    return pd.DataFrame(schedule)

def calculate_investment_metrics(purchase_price, down_payment, interest_rate, loan_term,
                              monthly_expenses, rental_income, appreciation_rate):
    """Calculate various investment metrics."""
    # Monthly mortgage payment
    monthly_mortgage = calculate_mortgage_payment(
        purchase_price, down_payment, interest_rate, loan_term)
    
    # Monthly cash flow
    monthly_cash_flow = rental_income - (monthly_mortgage + monthly_expenses)
    
    # Annual cash flow
    annual_cash_flow = monthly_cash_flow * 12
    
    # Cash on cash return
    initial_investment = down_payment  # Simplified, normally would include closing costs
    cash_on_cash_return = (annual_cash_flow / initial_investment) * 100
    
    # Future value after loan term
    future_value = purchase_price * (1 + appreciation_rate/100) ** loan_term
    
    # Total equity (future value - remaining loan balance)
    loan_amount = purchase_price - down_payment
    remaining_balance = -np.fv(
        interest_rate/12/100, 
        loan_term * 12, 
        monthly_mortgage, 
        -loan_amount
    )
    total_equity = future_value - remaining_balance
    
    return {
        'monthly_mortgage': monthly_mortgage,
        'monthly_cash_flow': monthly_cash_flow,
        'annual_cash_flow': annual_cash_flow,
        'cash_on_cash_return': cash_on_cash_return,
        'future_value': future_value,
        'total_equity': total_equity
    }
