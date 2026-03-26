import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def init_connection() -> Client:
    """Menginisialisasi dan menyimpan koneksi Supabase agar tidak berulang kali dibuat."""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def get_supabase() -> Client:
    return init_connection()

# ==========================================
# TRANSACTIONS
# ==========================================
def fetch_transactions():
    supabase = get_supabase()
    response = supabase.table('transactions').select("*").order('date', desc=True).execute()
    return response.data

def insert_transaction(date, type_, amount, category, notes):
    supabase = get_supabase()
    data = {
        "date": str(date),
        "type": type_,
        "amount": amount,
        "category": category,
        "notes": notes
    }
    supabase.table('transactions').insert(data).execute()

# ==========================================
# ENVELOPES
# ==========================================
def fetch_envelopes():
    supabase = get_supabase()
    response = supabase.table('envelopes').select("*").execute()
    return response.data

# ==========================================
# PENDING INCOMES
# ==========================================
def fetch_pending_incomes():
    supabase = get_supabase()
    response = supabase.table('pending_incomes').select("*").order('due_date', desc=False).execute()
    return response.data

def insert_pending_income(client_name, amount, due_date):
    supabase = get_supabase()
    data = {"client_name": client_name, "amount": amount, "due_date": str(due_date), "status": "Pending"}
    supabase.table('pending_incomes').insert(data).execute()

def mark_income_as_paid(income_id, client_name, amount, due_date, tax_percentage=0):
    """
    Logika otomatisasi:
    1. Update status faktur menjadi 'Cair'.
    2. Tambahkan ke tabel transactions (Pemasukan).
    3. Jika tax_percentage > 0, potong langsung sebagai 'Pengeluaran' ke kategori Pajak.
    """
    supabase = get_supabase()
    
    # 1. Update status
    supabase.table('pending_incomes').update({"status": "Cair"}).eq("id", income_id).execute()
    
    # 2. Catat Transaksi Pemasukan (Gross)
    insert_transaction(
        date=due_date, 
        type_='Pemasukan', 
        amount=amount, 
        category='Pencairan Faktur', 
        notes=f"Dari: {client_name}"
    )
    
    # 3. Catat Pemotongan Pajak jika ada
    if tax_percentage > 0:
        tax_amount = amount * (tax_percentage / 100)
        insert_transaction(
            date=due_date, 
            type_='Pengeluaran', 
            amount=tax_amount, 
            category='Pajak & Biaya Admin', 
            notes=f"Pemotongan pajak {tax_percentage}% faktur {client_name}"
        )
