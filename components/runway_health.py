import streamlit as st
from utils.calculations import calculate_runway

def render_runway_health(transactions_data):
    st.subheader("Runway Health Calculator")
    
    current_balance, avg_daily_expense, runway_days = calculate_runway(transactions_data)
    
    with st.container(border=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Saldo Aktif", f"Rp {current_balance:,.0f}")
        with col2:
            st.metric("Pengeluaran/Hari (Rata-rata)", f"Rp {avg_daily_expense:,.0f}")
            
    # Indikator Runway berwarna dinamis
    if runway_days >= 999:
        days_display = "Tak Terhingga"
    else:
        days_display = f"{runway_days:.0f} Hari"
        
    if current_balance <= 0 and len(transactions_data) > 0:
        st.markdown(
            f'<div style="background:#FEE2E2; border-left:4px solid #EF4444; padding:12px 16px; border-radius:6px; margin-top:8px;">'
            f'<span style="color:#991B1B; font-weight:600;">KRITIS</span>'
            f'<br><span style="color:#7F1D1D; font-size:1.4rem; font-weight:700;">Saldo Minus</span>'
            f'<br><span style="color:#991B1B;">Saldo utama Anda saat ini kosong atau minus.</span></div>',
            unsafe_allow_html=True
        )
    elif runway_days < 15:
        st.markdown(
            f'<div style="background:#FEE2E2; border-left:4px solid #EF4444; padding:12px 16px; border-radius:6px; margin-top:8px;">'
            f'<span style="color:#991B1B; font-weight:600;">KRITIS</span>'
            f'<br><span style="color:#7F1D1D; font-size:1.4rem; font-weight:700;">{days_display}</span>'
            f'<br><span style="color:#991B1B;">Dana Anda sangat menipis. Segera cairkan piutang atau kurangi pengeluaran.</span></div>',
            unsafe_allow_html=True
        )
    elif runway_days <= 30:
        st.markdown(
            f'<div style="background:#FEF9C3; border-left:4px solid #EAB308; padding:12px 16px; border-radius:6px; margin-top:8px;">'
            f'<span style="color:#854D0E; font-weight:600;">HATI-HATI</span>'
            f'<br><span style="color:#713F12; font-size:1.4rem; font-weight:700;">{days_display}</span>'
            f'<br><span style="color:#854D0E;">Runway mulai menipis. Pertimbangkan untuk mengevaluasi pengeluaran Anda.</span></div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div style="background:#D1FAE5; border-left:4px solid #10B981; padding:12px 16px; border-radius:6px; margin-top:8px;">'
            f'<span style="color:#065F46; font-weight:600;">AMAN</span>'
            f'<br><span style="color:#064E3B; font-size:1.4rem; font-weight:700;">{days_display}</span>'
            f'<br><span style="color:#065F46;">Keuangan Anda dalam kondisi sehat.</span></div>',
            unsafe_allow_html=True
        )
