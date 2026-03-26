import streamlit as st
import datetime
from utils.db import insert_transaction, fetch_envelopes

def render_quick_add():
    st.subheader("⚡ Quick Add Transaction")
    
    # Ambil data envelopes untuk dropdown kategori (Opsional)
    try:
        envelopes = fetch_envelopes()
        categories = [env['name'] for env in envelopes]
    except Exception as e:
        categories = []
        
    categories_pemasukan = ['Gaji/Proyek', 'Bonus', 'Pencairan Faktur', 'Lainnya']
    categories_pengeluaran = categories if categories else ['Dana Darurat', 'Operasional', 'Self-Reward', 'Pajak & Biaya Admin', 'Lainnya']
    
    with st.expander("➕ Tambah Pemasukan / Pengeluaran", expanded=True):
        with st.form("quick_add_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                date_input = st.date_input("Tanggal", datetime.date.today())
                type_input = st.selectbox("Jenis", ["Pengeluaran", "Pemasukan"])
            
            with col2:
                amount_input = st.number_input("Nominal (Rp)", min_value=0.0, step=10000.0, format="%.2f")
                if type_input == "Pemasukan":
                    category_input = st.selectbox("Kategori", categories_pemasukan)
                else:
                    category_input = st.selectbox("Kategori", categories_pengeluaran)
                    
            notes_input = st.text_input("Catatan (Opsional)")
            
            submitted = st.form_submit_button("Simpan Transaksi", use_container_width=True)
            
            if submitted:
                if amount_input > 0:
                    insert_transaction(date_input, type_input, amount_input, category_input, notes_input)
                    st.success("✅ Transaksi berhasil disimpan!")
                    st.rerun()
                else:
                    st.error("Nominal harus lebih dari 0!")
