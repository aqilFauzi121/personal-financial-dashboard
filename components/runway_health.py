import streamlit as st
from utils.calculations import calculate_runway

def render_runway_health(transactions_data):
    st.subheader("🏥 Runway Health Calculator")
    
    current_balance, avg_daily_expense, runway_days = calculate_runway(transactions_data)
    
    # Gunakan st.columns untuk responsivitas Mobile-First
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Saldo Aktif", f"Rp {current_balance:,.0f}")
    with col2:
        st.metric("Rata-rata Pengeluaran/Hari", f"Rp {avg_daily_expense:,.0f}")
    
    # Indikator warna kesehatan runway
    if runway_days > 90:
        runway_color = "🟢"
    elif runway_days >= 30:
        runway_color = "🟡"
    else:
        runway_color = "🔴"
        
    if runway_days >= 999:
        days_display = "Aman (Tak Terhingga)"
    else:
        days_display = f"{runway_days:.0f} Hari"
        
    with col3:
        st.metric("Estimasi Bertahan", f"{runway_color} {days_display}")
    
    # Logic peringatan
    if runway_days < 30 and current_balance > 0:
        st.warning(f"⚠️ Peringatan: Runway Anda tersisa kurang dari sebulan ({days_display}). Segera cairkan piutang atau kurangi pengeluaran!")
    elif current_balance <= 0 and len(transactions_data) > 0:
        st.error("🚨 Saldo Anda kosong atau minus!")
