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
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injeksi CSS Custom — Design System Overhaul
st.markdown("""
    <style>
    /* ============================================
       CSS VARIABLES — DESIGN TOKENS
       ============================================ */
    :root {
        --color-primary: #2d6a4f;
        --color-primary-light: #40916c;
        --color-background: #f8f6f2;
        --color-sidebar: #1a2e1a;
        --color-sidebar-text: #ffffff;
        --color-text-primary: #1a1a2e;
        --color-text-secondary: #6b7280;
        --color-danger: #dc2626;
        --color-warning: #d97706;
        --color-success: #2d6a4f;
        --color-card-border: #e5e1d8;
    }

    /* ============================================
       GLOBAL / HIDE STREAMLIT DEFAULTS
       ============================================ */
    #MainMenu {visibility: hidden;}
    .stAppDeployButton {display: none;}
    footer {visibility: hidden;}
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        padding-left: 32px !important;
        padding-right: 32px !important;
    }

    /* ============================================
       SIDEBAR — DARK GREEN
       ============================================ */
    [data-testid="stSidebar"] {
        background-color: #1a2e1a !important;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] label {
        color: rgba(255, 255, 255, 0.8) !important;
        font-size: 0.85rem !important;
    }
    [data-testid="stSidebar"] .stTextInput > div > div > input,
    [data-testid="stSidebar"] .stNumberInput > div > div > input,
    [data-testid="stSidebar"] .stSelectbox > div > div,
    [data-testid="stSidebar"] .stDateInput > div > div > input {
        border: 1px solid #40916c !important;
        background-color: rgba(255, 255, 255, 0.08) !important;
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] [data-testid="stHeadingWithActionElements"] {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* ============================================
       BUTTON SYSTEM — GREEN PRIMARY
       ============================================ */
    .stButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primary"],
    .stButton > button[data-testid="stBaseButton-primary"],
    .stFormSubmitButton > button[data-testid="stBaseButton-primary"] {
        background-color: #2d6a4f !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        transition: background-color 0.2s ease !important;
    }
    .stButton > button[kind="primary"]:hover,
    .stFormSubmitButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="stBaseButton-primary"]:hover,
    .stFormSubmitButton > button[data-testid="stBaseButton-primary"]:hover {
        background-color: #40916c !important;
        color: #ffffff !important;
    }
    /* Secondary button */
    .stButton > button[kind="secondary"],
    .stButton > button[data-testid="stBaseButton-secondary"] {
        background-color: transparent !important;
        color: #2d6a4f !important;
        border: 1px solid #2d6a4f !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: background-color 0.2s ease !important;
    }
    .stButton > button[kind="secondary"]:hover,
    .stButton > button[data-testid="stBaseButton-secondary"]:hover {
        background-color: #f0fdf4 !important;
    }

    /* ============================================
       CARD & SHADOW SYSTEM — UNIFORM
       ============================================ */
    [data-testid="stExpander"],
    div[data-testid="stVerticalBlockBorderWrapper"]:has(> div[data-testid="stVerticalBlock"] > div.stContainer) {
        border: 1px solid #e5e1d8 !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
    }
    /* st.container(border=True) styling */
    [data-testid="stVerticalBlockBorderWrapper"][data-testid] {
        border-color: #e5e1d8 !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
        padding: 20px !important;
    }

    /* ============================================
       TYPOGRAPHY SYSTEM
       ============================================ */
    /* Section heading utama (h2 / st.subheader) */
    h2, .stSubheader {
        font-size: 24px !important;
        font-weight: 700 !important;
        color: #1a1a2e !important;
    }
    /* Sub-section heading (h3) */
    h3 {
        font-size: 18px !important;
        font-weight: 600 !important;
        color: #1a1a2e !important;
    }
    /* Angka finansial (metric values) — 32px bold */
    [data-testid="stMetricValue"] {
        font-size: 32px !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em !important;
        color: #1a1a2e !important;
    }
    /* Label metric */
    [data-testid="stMetricLabel"] {
        font-size: 12px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        color: #6b7280 !important;
    }
    /* Caption / st.caption */
    .stCaption, [data-testid="stCaptionContainer"] {
        font-size: 12px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        color: #6b7280 !important;
    }
    /* Body text */
    .stMarkdown p {
        font-size: 14px;
        color: #6b7280;
    }
    /* Bold text inside markdown */
    .stMarkdown strong {
        color: #1a1a2e;
    }

    /* ============================================
       SPACING SYSTEM — 8px grid
       ============================================ */
    /* Jarak antar section utama */
    [data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        margin-bottom: 16px;
    }
    /* Jarak dalam form elements */
    .stForm [data-testid="stVerticalBlock"] > div {
        margin-bottom: 16px;
    }

    /* ============================================
       DATAFRAME & TABLE
       ============================================ */
    [data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
    }

    /* ============================================
       RESPONSIVE — MOBILE 375px
       ============================================ */
    @media (max-width: 480px) {
        .block-container {
            padding-left: 16px !important;
            padding-right: 16px !important;
        }
        [data-testid="stMetricValue"] {
            font-size: 24px !important;
        }
        h2, .stSubheader {
            font-size: 20px !important;
        }
        .stMarkdown p {
            font-size: 14px !important;
        }
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
    '<div style="background:linear-gradient(135deg, #1a2e1a, #2d6a4f); '
    'padding:32px 36px; border-radius:12px; margin-bottom:48px; '
    'box-shadow:0 4px 12px rgba(0,0,0,0.12);">'
    '<h1 style="color:#FFFFFF; margin:0; font-size:24px; font-weight:700; letter-spacing:-0.025em;">'
    'Arsitek Finansial Pribadi</h1>'
    '<p style="color:#A7F3D0; margin:8px 0 0 0; font-size:14px; line-height:1.5;">'
    'Dasbor manajemen arus kas khusus freelancer &mdash; pantau runway, kelola amplop, dan cairkan piutang dalam satu layar.</p>'
    '</div>',
    unsafe_allow_html=True
)

# ==========================================
# HERO SECTION: RUNWAY HEALTH (Full Width)
# ==========================================
render_runway_health(transactions)

st.markdown('<div style="margin-top:48px;"></div>', unsafe_allow_html=True)

# ==========================================
# TWO-COLUMN LAYOUT: ENVELOPES + PENDING
# ==========================================
col_left, col_right = st.columns(2, gap="large")

with col_left:
    current_balance, _, _ = calculate_runway(transactions)
    render_virtual_envelopes(current_balance, envelopes)

with col_right:
    render_pending_incomes(pending_incomes)

st.markdown('<div style="margin-top:48px;"></div>', unsafe_allow_html=True)

# ==========================================
# PURCHASE SIMULATOR (Full Width)
# ==========================================
render_purchase_simulator(transactions, envelopes)

st.markdown('<div style="margin-top:48px;"></div>', unsafe_allow_html=True)

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
        st.markdown(
            '<div style="background:#f8f6f2; border-radius:8px; padding:24px; text-align:center;">'
            '<div style="font-size:2rem; margin-bottom:8px;">📭</div>'
            '<div style="color:#1a1a2e; font-weight:700; font-size:16px; margin-bottom:4px;">Belum ada transaksi.</div>'
            '<div style="color:#6b7280; font-size:14px;">Yuk catat pengeluaran pertamamu lewat sidebar!</div>'
            '</div>',
            unsafe_allow_html=True
        )
