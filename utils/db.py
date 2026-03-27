import streamlit as st
from supabase import create_client, Client
from utils.logger import get_logger

logger = get_logger("db")

@st.cache_resource
def init_connection() -> Client:
    """Menginisialisasi dan menyimpan koneksi Supabase."""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    logger.info("Inisialisasi koneksi Supabase.")
    return create_client(url, key)

def get_supabase() -> Client:
    return init_connection()


# ==========================================
# TRANSACTIONS
# ==========================================
def fetch_transactions():
    try:
        supabase = get_supabase()
        response = supabase.table('transactions').select("*").order('date', desc=True).execute()
        logger.info(f"fetch_transactions: {len(response.data)} baris diterima.")
        return response.data
    except Exception as e:
        logger.error(f"fetch_transactions gagal: {e}")
        raise

def insert_transaction(date, type_, amount, category, notes):
    try:
        supabase = get_supabase()
        data = {
            "date": str(date),
            "type": type_,
            "amount": amount,
            "category": category,
            "notes": notes
        }
        supabase.table('transactions').insert(data).execute()
        logger.info(f"insert_transaction: {type_} Rp {amount:,.0f} — {category}.")
    except Exception as e:
        logger.error(f"insert_transaction gagal: {e}")
        raise


# ==========================================
# ENVELOPES
# ==========================================
def fetch_envelopes():
    try:
        supabase = get_supabase()
        response = supabase.table('envelopes').select("*").execute()
        logger.info(f"fetch_envelopes: {len(response.data)} amplop diterima.")
        return response.data
    except Exception as e:
        logger.error(f"fetch_envelopes gagal: {e}")
        raise


# ==========================================
# PENDING INCOMES
# ==========================================
def fetch_pending_incomes():
    try:
        supabase = get_supabase()
        response = supabase.table('pending_incomes').select("*").order('due_date', desc=False).execute()
        logger.info(f"fetch_pending_incomes: {len(response.data)} faktur diterima.")
        return response.data
    except Exception as e:
        logger.error(f"fetch_pending_incomes gagal: {e}")
        raise

def insert_pending_income(client_name, amount, due_date):
    try:
        supabase = get_supabase()
        data = {
            "client_name": client_name,
            "amount": amount,
            "due_date": str(due_date),
            "status": "Pending"
        }
        supabase.table('pending_incomes').insert(data).execute()
        logger.info(f"insert_pending_income: {client_name} Rp {amount:,.0f}.")
    except Exception as e:
        logger.error(f"insert_pending_income gagal: {e}")
        raise

def mark_income_as_paid(income_id, client_name, amount, due_date, tax_percentage=0):
    """
    Memanggil database function mark_income_paid() di Supabase.
    Seluruh operasi berjalan dalam satu transaksi atomik di sisi PostgreSQL.
    """
    try:
        supabase = get_supabase()
        supabase.rpc("mark_income_paid", {
            "p_income_id":      str(income_id),
            "p_client_name":    client_name,
            "p_amount":         amount,
            "p_due_date":       str(due_date),
            "p_tax_percentage": tax_percentage
        }).execute()
        logger.info(f"mark_income_as_paid: {client_name} Rp {amount:,.0f} berhasil dicairkan (pajak {tax_percentage}%).")
    except Exception as e:
        logger.error(f"mark_income_as_paid gagal: {e}")
        raise

def refresh_data():
    """
    Invalidate session_state agar data di-fetch ulang dari Supabase
    pada rerun berikutnya. Dipanggil setelah operasi write berhasil.
    """
    import streamlit as st
    for key in ["transactions", "envelopes", "pending_incomes"]:
        if key in st.session_state:
            del st.session_state[key]