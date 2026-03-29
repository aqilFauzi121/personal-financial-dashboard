import streamlit as st
import pandas as pd
from utils.auth import check_password
from utils.monitor import init_sentry
from utils.db import fetch_transactions, fetch_envelopes, fetch_pending_incomes, fetch_wallets
from utils.calculations import calculate_runway
from utils.tokens import inject_css
from utils.ui import hero_banner, section_gap

init_sentry()

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="Arsitek Finansial Pribadi",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injeksi CSS dari token system terpusat
inject_css()

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
from components.spending_chart import render_spending_chart
from components.wallet_overview import render_wallet_overview
from components.transaction_history import render_transaction_history
from components.paypal_transactions import render_paypal_transactions

# ==========================================
# PULL DATA DARI SUPABASE (dengan session_state caching)
# ==========================================
def load_all_data():
    """Fetch semua data dari Supabase dan simpan ke session_state."""
    try:
        st.session_state["transactions"]    = fetch_transactions()
        st.session_state["envelopes"]       = fetch_envelopes()
        st.session_state["pending_incomes"] = fetch_pending_incomes()
        st.session_state["wallets"]         = fetch_wallets()
    except Exception as e:
        st.error(f"Gagal memuat data dari Supabase. Pastikan URL dan API Key benar. Error: {e}")
        st.stop()

# Hanya fetch jika session_state belum ada (pertama kali load)
if "transactions" not in st.session_state:
    load_all_data()

transactions    = st.session_state["transactions"]
envelopes       = st.session_state["envelopes"]
pending_incomes = st.session_state["pending_incomes"]
wallets         = st.session_state["wallets"]

# ==========================================
# SIDEBAR: QUICK ADD FORM
# ==========================================
render_quick_add_sidebar()

# ==========================================
# HERO BANNER
# ==========================================
st.markdown(
    hero_banner(
        title="Arsitek Finansial Pribadi",
        subtitle="Dasbor manajemen arus kas khusus freelancer \u2014 pantau runway, kelola amplop, dan cairkan piutang dalam satu layar.",
    ),
    unsafe_allow_html=True,
)

# ==========================================
# HERO SECTION: RUNWAY HEALTH (Full Width)
# ==========================================
render_runway_health(transactions)

st.markdown(section_gap(), unsafe_allow_html=True)

# ==========================================
# WALLET OVERVIEW
# ==========================================
render_wallet_overview(transactions, wallets)

st.markdown(section_gap(), unsafe_allow_html=True)

# ==========================================
# TRANSAKSI PAYPAL & ADOBE STOCK
# ==========================================
render_paypal_transactions(wallets)

st.markdown(section_gap(), unsafe_allow_html=True)

# ==========================================
# TWO-COLUMN LAYOUT: ENVELOPES + PENDING
# ==========================================
col_left, col_right = st.columns(2, gap="large")

with col_left:
    current_balance, _, _ = calculate_runway(transactions)
    render_virtual_envelopes(current_balance, envelopes)

with col_right:
    render_pending_incomes(pending_incomes)

st.markdown(section_gap(), unsafe_allow_html=True)

# ==========================================
# PURCHASE SIMULATOR (Full Width)
# ==========================================
render_purchase_simulator(transactions, envelopes)

st.markdown(section_gap(), unsafe_allow_html=True)

# ==========================================
# RIWAYAT TRANSAKSI
# ==========================================
render_transaction_history(transactions, wallets)

st.markdown(section_gap(), unsafe_allow_html=True)

# ==========================================
# ANALISIS TRANSAKSI — PIE CHART
# ==========================================
render_spending_chart(transactions)