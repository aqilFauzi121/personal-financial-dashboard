import streamlit as st
import pandas as pd
from utils.auth import check_password
from utils.db import fetch_transactions, fetch_envelopes, fetch_pending_incomes
from utils.calculations import calculate_runway

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="Arsitek Finansial Pribadi",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injeksi CSS Custom
st.markdown("""
    <style>
    /* Sembunyikan Header Deploy dan Hamburger Menu */
    header {visibility: hidden;}
    /* Sembunyikan Footer Streamlit */
    footer {visibility: hidden;}
    /* Kurangi Padding Atas */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. PIN GATE
# ==========================================
if not check_password():
    st.stop()

# ==========================================
# IMPORT KOMPONEN MODULAR
# ==========================================
from components.quick_add import render_quick_add_sidebar
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
# SIDEBAR: QUICK ADD FORM
# ==========================================
render_quick_add_sidebar()

# ==========================================
# HERO BANNER
# ==========================================
st.markdown(
    '<div style="background:linear-gradient(135deg, #0D9488 0%, #065F46 100%); '
    'padding:28px 32px; border-radius:12px; margin-bottom:24px;">'
    '<h1 style="color:#FFFFFF; margin:0; font-size:1.75rem; font-weight:700; letter-spacing:-0.025em;">'
    'Arsitek Finansial Pribadi</h1>'
    '<p style="color:#CCFBF1; margin:6px 0 0 0; font-size:0.95rem;">'
    'Dasbor manajemen arus kas khusus freelancer &mdash; pantau runway, kelola amplop, dan cairkan piutang dalam satu layar.</p>'
    '</div>',
    unsafe_allow_html=True
)

# ==========================================
# HERO SECTION: RUNWAY HEALTH (Full Width)
# ==========================================
render_runway_health(transactions)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# TWO-COLUMN LAYOUT: ENVELOPES + PENDING
# ==========================================
col_left, col_right = st.columns(2, gap="large")

with col_left:
    current_balance, _, _ = calculate_runway(transactions)
    render_virtual_envelopes(current_balance, envelopes)

with col_right:
    render_pending_incomes(pending_incomes)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# PURCHASE SIMULATOR (Full Width)
# ==========================================
render_purchase_simulator(transactions, envelopes)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# RIWAYAT TRANSAKSI
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
            st.dataframe(df_display, use_container_width=True)
    else:
        st.info("Belum ada transaksi tercatat.")
