import streamlit as st
from utils.calculations import calculate_runway

def render_runway_health(transactions_data):
    st.subheader("Runway Health Calculator")

    try:
        current_balance, avg_daily_expense, runway_days = calculate_runway(transactions_data)
    except Exception as e:
        st.error(f"❌ Gagal menghitung Runway Health. ({e})")
        return

    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Saldo Aktif", f"Rp {current_balance:,.0f}")
        with col2:
            st.metric("Pengeluaran/Hari (Rata-rata)", f"Rp {avg_daily_expense:,.0f}")

    if runway_days >= 999:
        days_display = "Tak Terhingga"
    else:
        days_display = f"{runway_days:.0f} Hari"

    if current_balance <= 0 and len(transactions_data) > 0:
        st.markdown(
            f'<div style="background:#fef2f2; border-left:4px solid #dc2626; padding:16px 20px; border-radius:8px; margin-top:8px;">'
            f'<span style="color:#dc2626; font-weight:700; font-size:12px; text-transform:uppercase; letter-spacing:0.05em;">⚠️ KRITIS</span>'
            f'<br><span style="color:#1a1a2e; font-size:32px; font-weight:800;">Saldo Minus</span>'
            f'<br><span style="color:#6b7280; font-size:14px;">Saldo utama Anda saat ini kosong atau minus.</span></div>',
            unsafe_allow_html=True
        )
    elif runway_days < 15:
        st.markdown(
            f'<div style="background:#fef2f2; border-left:4px solid #dc2626; padding:16px 20px; border-radius:8px; margin-top:8px;">'
            f'<span style="color:#dc2626; font-weight:700; font-size:12px; text-transform:uppercase; letter-spacing:0.05em;">⚠️ KRITIS</span>'
            f'<br><span style="color:#1a1a2e; font-size:32px; font-weight:800;">{days_display}</span>'
            f'<br><span style="color:#6b7280; font-size:14px;">Dana Anda sangat menipis. Segera cairkan piutang atau kurangi pengeluaran.</span></div>',
            unsafe_allow_html=True
        )
    elif runway_days <= 30:
        st.markdown(
            f'<div style="background:#fffbeb; border-left:4px solid #d97706; padding:16px 20px; border-radius:8px; margin-top:8px;">'
            f'<span style="color:#d97706; font-weight:700; font-size:12px; text-transform:uppercase; letter-spacing:0.05em;">⚠️ HATI-HATI</span>'
            f'<br><span style="color:#1a1a2e; font-size:32px; font-weight:800;">{days_display}</span>'
            f'<br><span style="color:#6b7280; font-size:14px;">Runway mulai menipis. Pertimbangkan untuk mengevaluasi pengeluaran Anda.</span></div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div style="background:#f0fdf4; border-left:4px solid #2d6a4f; padding:16px 20px; border-radius:8px; margin-top:8px;">'
            f'<span style="color:#2d6a4f; font-weight:700; font-size:12px; text-transform:uppercase; letter-spacing:0.05em;">✅ AMAN</span>'
            f'<br><span style="color:#1a1a2e; font-size:32px; font-weight:800;">{days_display}</span>'
            f'<br><span style="color:#6b7280; font-size:14px;">Keuangan Anda dalam kondisi sehat.</span></div>',
            unsafe_allow_html=True
        )