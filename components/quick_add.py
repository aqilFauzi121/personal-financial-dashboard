import streamlit as st
import datetime
from utils.db import insert_transaction, fetch_envelopes, refresh_data

def render_quick_add_sidebar():
    """Render Quick Add form inside the sidebar."""
    st.sidebar.header("Quick Add Transaction")

    try:
        envelopes = fetch_envelopes()
        categories = [env['name'] for env in envelopes]
    except Exception:
        categories = []

    categories_pemasukan = ['Gaji/Proyek', 'Bonus', 'Pencairan Faktur', 'Lainnya']
    categories_pengeluaran = categories if categories else ['Dana Darurat', 'Operasional', 'Self-Reward', 'Pajak & Biaya Admin', 'Lainnya']

    with st.sidebar.form("quick_add_form", clear_on_submit=True):
        date_input = st.date_input("Tanggal", datetime.date.today())
        type_input = st.selectbox("Jenis", ["Pengeluaran", "Pemasukan"])
        amount_input = st.number_input("Nominal (Rp)", min_value=0.0, step=10000.0, format="%.0f")

        if type_input == "Pemasukan":
            category_input = st.selectbox("Kategori", categories_pemasukan)
        else:
            category_input = st.selectbox("Kategori", categories_pengeluaran)

        notes_input = st.text_input("Catatan (Opsional)")

        submitted = st.form_submit_button("Simpan Transaksi", use_container_width=True, type="primary")

        if submitted:
            if amount_input > 0:
                    try:
                        insert_transaction(date_input, type_input, amount_input, category_input, notes_input)
                        refresh_data()
                        st.success("✅ Transaksi berhasil disimpan!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Gagal menyimpan transaksi. Silakan coba lagi. ({e})")
            else:
                st.error("Nominal harus lebih dari 0.")