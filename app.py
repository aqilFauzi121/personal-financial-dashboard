import streamlit as st
import pandas as pd
from utils.auth import check_password
from utils.db import fetch_transactions, fetch_envelopes, fetch_pending_incomes

# ==========================================
# KONFIGURASI HALAMAN (Mobile-First UI)
# ==========================================
st.set_page_config(
    page_title="Arsitek Finansial Pribadi",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Injeksi CSS Custom untuk Tampilan Clean SaaS
st.markdown("""
    <style>
    /* Sembunyikan Header Deploy dan Hamburger Menu */
    header {visibility: hidden;}
    /* Sembunyikan Footer Streamlit */
    footer {visibility: hidden;}
    /* Kurangi Padding Atas */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    /* Kustomisasi font untuk judul utama */
    h1 {
        font-weight: 700;
        letter-spacing: -0.025em;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. PIN GATE (Sistem Login)
# ==========================================
if not check_password():
    st.stop()  # Hentikan eksekusi script jika PIN belum dimasukkan/salah

# ==========================================
# IMPORT KOMPONEN MODULAR
# ==========================================
from components.quick_add import render_quick_add
from components.runway_health import render_runway_health
from components.pending_income import render_pending_incomes
from components.virtual_envelopes import render_virtual_envelopes
from components.purchase_simulator import render_purchase_simulator

# ==========================================
# PULL DATA DARI SUPABASE
# ==========================================
try:
    transactions = fetch_transactions()
    envelopes = fetch_envelopes()
    pending_incomes = fetch_pending_incomes()
except Exception as e:
    st.error(f"Gagal memuat data dari Supabase. Pastikan URL dan API Key benar. Error: {e}")
    st.stop()

# ==========================================
# HEADER HALAMAN
# ==========================================
st.title("Arsitek Finansial Pribadi")
st.markdown("Dasbor manajemen arus kas khusus freelancer.")
st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# BAGIAN 1: QUICK ADD FORM
# ==========================================
render_quick_add()

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# BAGIAN 2: RUNWAY HEALTH & ENVELOPES 
# (Menggunakan Tabs agar hemat ruang layar HP)
# ==========================================
tab1, tab2 = st.tabs(["Runway Health", "Virtual Envelopes"])

with tab1:
    render_runway_health(transactions)

with tab2:
    from utils.calculations import calculate_runway
    current_balance, _, _ = calculate_runway(transactions)
    render_virtual_envelopes(current_balance, envelopes)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# BAGIAN 3: PENDING INCOME TRACKER
# ==========================================
render_pending_incomes(pending_incomes)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# BAGIAN 4: PURCHASE SIMULATOR 
# ==========================================
render_purchase_simulator(transactions, envelopes)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# BAGIAN 5: TABEL RIWAYAT TRANSAKSI 
# (Diubah menjadi style border component)
# ==========================================
with st.container(border=True):
    st.markdown("**Riwayat Transaksi (5 Terakhir)**")
    if transactions:
        df = pd.DataFrame(transactions)
        df_display = df.head(5).copy()
        try:
            df_display = df_display[['date', 'type', 'amount', 'category', 'notes']]
            df_display.columns = ['Tanggal', 'Jenis', 'Nominal (Rp)', 'Kategori', 'Catatan']
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        except KeyError:
            st.dataframe(df_display, use_container_width=True) # Fallback jika kolom tidak sama
    else:
        st.info("Belum ada transaksi tercatat.")
