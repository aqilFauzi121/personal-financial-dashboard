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

def insert_transaction(date, type_, amount, category, notes, wallet_id=None):
    try:
        supabase = get_supabase()
        data = {
            "date":     str(date),
            "type":     type_,
            "amount":   amount,
            "category": category,
            "notes":    notes,
        }
        if wallet_id:
            data["wallet_id"] = str(wallet_id)
        supabase.table('transactions').insert(data).execute()
        logger.info(f"insert_transaction: {type_} Rp {amount:,.0f} — {category}.")
    except Exception as e:
        logger.error(f"insert_transaction gagal: {e}")
        raise

def update_transaction(tx_id: str, date, type_: str, amount: float, category: str, notes: str, wallet_id=None):
    try:
        supabase = get_supabase()
        data = {
            "date":     str(date),
            "type":     type_,
            "amount":   amount,
            "category": category,
            "notes":    notes or "",
            "wallet_id": str(wallet_id) if wallet_id else None,
        }
        supabase.table('transactions').update(data).eq('id', str(tx_id)).execute()
        logger.info(f"update_transaction: {tx_id} diperbarui.")
    except Exception as e:
        logger.error(f"update_transaction gagal: {e}")
        raise

def delete_transaction(tx_id: str):
    try:
        supabase = get_supabase()
        supabase.table('transactions').delete().eq('id', str(tx_id)).execute()
        logger.info(f"delete_transaction: {tx_id} dihapus.")
    except Exception as e:
        logger.error(f"delete_transaction gagal: {e}")
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
    for key in ["transactions", "envelopes", "pending_incomes", "wallets"]:
        if key in st.session_state:
            del st.session_state[key]


# ==========================================
# WALLETS
# ==========================================
def fetch_wallets():
    try:
        supabase = get_supabase()
        response = supabase.table('wallets').select("*").eq('is_active', True).order('created_at').execute()
        logger.info(f"fetch_wallets: {len(response.data)} wallet diterima.")
        return response.data
    except Exception as e:
        logger.error(f"fetch_wallets gagal: {e}")
        raise

def insert_wallet(name: str, type_: str, initial_balance: float, is_investment: bool):
    try:
        supabase = get_supabase()
        data = {
            "name":            name,
            "type":            type_,
            "initial_balance": initial_balance,
            "is_investment":   is_investment,
            "is_active":       True,
        }
        supabase.table('wallets').insert(data).execute()
        logger.info(f"insert_wallet: {name} ({type_}) saldo awal Rp {initial_balance:,.0f}.")
    except Exception as e:
        logger.error(f"insert_wallet gagal: {e}")
        raise

def deactivate_wallet(wallet_id: str):
    """Soft delete — set is_active=False, data histori tetap utuh."""
    try:
        supabase = get_supabase()
        supabase.table('wallets').update({"is_active": False}).eq('id', wallet_id).execute()
        logger.info(f"deactivate_wallet: {wallet_id} dinonaktifkan.")
    except Exception as e:
        logger.error(f"deactivate_wallet gagal: {e}")
        raise

def transfer_wallets(from_wallet_id: str, to_wallet_id: str, amount: float, date, notes: str = ""):
    """Memanggil function atomik transfer_between_wallets() di Supabase."""
    try:
        supabase = get_supabase()
        supabase.rpc("transfer_between_wallets", {
            "p_from_wallet_id": str(from_wallet_id),
            "p_to_wallet_id":   str(to_wallet_id),
            "p_amount":         amount,
            "p_date":           str(date),
            "p_notes":          notes,
        }).execute()
        logger.info(f"transfer_wallets: Rp {amount:,.0f} dari {from_wallet_id} ke {to_wallet_id}.")
    except Exception as e:
        logger.error(f"transfer_wallets gagal: {e}")
        raise

def calculate_wallet_balance(wallet_id: str, transactions_data: list, initial_balance: float) -> float:
    """Hitung saldo wallet dari initial_balance + semua transaksi yang terkait."""
    balance = initial_balance
    for tx in transactions_data:
        if str(tx.get('wallet_id')) == str(wallet_id):
            if tx['type'] == 'Pemasukan':
                balance += float(tx['amount'])
            else:
                balance -= float(tx['amount'])
    return balance