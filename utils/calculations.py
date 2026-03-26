import pandas as pd
from datetime import datetime, timedelta

def calculate_runway(transactions_data):
    """
    Menghitung current_balance, rata-rata pengeluaran 30 hari terakhir, dan sisa hari bertahan.
    """
    if not transactions_data:
        return 0.0, 0.0, 0.0
        
    df = pd.DataFrame(transactions_data)
    df['amount'] = pd.to_numeric(df['amount'])
    df['date'] = pd.to_datetime(df['date']).dt.date
    
    # Hitung total balance saat ini
    total_income = df[df['type'] == 'Pemasukan']['amount'].sum()
    total_expense = df[df['type'] == 'Pengeluaran']['amount'].sum()
    current_balance = total_income - total_expense
    
    # Rata-rata pengeluaran 30 hari terakhir
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    recent_expenses = df[(df['type'] == 'Pengeluaran') & (df['date'] >= thirty_days_ago)]
    
    if not recent_expenses.empty:
        total_recent_expense = recent_expenses['amount'].sum()
        avg_daily_expense = total_recent_expense / 30.0
    else:
        avg_daily_expense = 0.0
        
    # Runway Days
    if avg_daily_expense > 0:
        runway_days = current_balance / avg_daily_expense
    else:
        # Jika tidak ada pengeluaran, runway diasumsikan tak terhingga (kita batasi 999 untuk UI)
        runway_days = 999.0 if current_balance > 0 else 0.0
        
    return current_balance, avg_daily_expense, runway_days
