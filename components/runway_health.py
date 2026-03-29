import streamlit as st
from utils.calculations import calculate_runway
from utils.ui import status_danger, status_warning, status_success, empty_state


def render_runway_health(transactions_data):
    st.subheader("Runway Health Calculator")

    # State khusus: database kosong — belum ada transaksi sama sekali
    if not transactions_data:
        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Saldo Aktif", "Rp 0")
            with col2:
                st.metric("Pengeluaran/Hari (Rata-rata)", "Rp 0")
        st.markdown(
            empty_state(
                icon="📋",
                title="Belum ada data transaksi.",
                body="Tambahkan pemasukan pertama Anda lewat sidebar untuk mulai memantau runway.",
                variant="info",
            ),
            unsafe_allow_html=True,
        )
        return

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

    if current_balance <= 0:
        html = status_danger(
            value_text="Saldo Minus",
            body_text="Saldo utama Anda saat ini kosong atau minus.",
        )
    elif runway_days < 15:
        html = status_danger(
            value_text=days_display,
            body_text="Dana Anda sangat menipis. Segera cairkan piutang atau kurangi pengeluaran.",
        )
    elif runway_days <= 30:
        html = status_warning(
            value_text=days_display,
            body_text="Runway mulai menipis. Pertimbangkan untuk mengevaluasi pengeluaran Anda.",
        )
    else:
        html = status_success(
            value_text=days_display,
            body_text="Keuangan Anda dalam kondisi sehat.",
        )

    st.markdown(html, unsafe_allow_html=True)