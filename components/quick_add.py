import streamlit as st
import datetime
from utils.db import insert_transaction, fetch_envelopes, fetch_wallets, refresh_data

# ── Kategori pemasukan ────────────────────────────────────────
CATEGORIES_PEMASUKAN = [
    'Freelance / Project Fee',
    'Gaji / Retainer',
    'Bonus',
    'Passive Income (Royalti, Afiliasi)',
    'Investasi / Dividen',
    'Pencairan Faktur',
    'Pengembalian Dana / Refund',
    'THR',
    'Lainnya',
]

# ── Kategori pengeluaran tambahan (di luar envelope names) ────
CATEGORIES_PENGELUARAN_EXTRA = [
    'Transportasi & BBM',
    'Makan & Minum',
    'Langganan (Software, Streaming)',
    'Kesehatan & Medis',
    'Pendidikan & Kursus',
    'Belanja',
    'Kebutuhan Rumah Tangga',
    'Kebutuhan Pribadi',
    'Kebutuhan Keluarga',
    'Kebutuhan Hewan Peliharaan',
    'Kebutuhan Kendaraan',
    'Kebutuhan Liburan',
    'Kebutuhan Hobi',
    'Lainnya',
]


def render_quick_add_sidebar():
    """Render Quick Add form inside the sidebar."""
    st.sidebar.header("Quick Add Transaction")

    try:
        envelopes = fetch_envelopes()
        envelope_categories = [env['name'] for env in envelopes]
    except Exception:
        envelope_categories = ['Dana Darurat', 'Operasional', 'Self-Reward', 'Pajak & Biaya Admin']

    try:
        wallets = fetch_wallets()
        wallet_options = {w['name']: w['id'] for w in wallets if w.get('is_active', True)}
    except Exception:
        wallet_options = {}

    # Gabung envelope categories + extra, buang duplikat, pertahankan urutan
    seen = set()
    categories_pengeluaran = []
    for cat in envelope_categories + CATEGORIES_PENGELUARAN_EXTRA:
        if cat not in seen:
            seen.add(cat)
            categories_pengeluaran.append(cat)

    # ── type_input di LUAR form agar kategori reaktif ─────────
    # Ini fix untuk bug Streamlit: selectbox di dalam form tidak
    # bisa mempengaruhi selectbox lain dalam form yang sama.
    type_input = st.sidebar.selectbox(
        "Jenis",
        ["Pengeluaran", "Pemasukan"],
        key="sidebar_type_input",
    )

    categories = CATEGORIES_PEMASUKAN if type_input == "Pemasukan" else categories_pengeluaran

    with st.sidebar.form("quick_add_form", clear_on_submit=True):
        date_input     = st.date_input("Tanggal", datetime.date.today())
        amount_input   = st.number_input("Nominal (Rp)", min_value=0.0, step=10000.0, format="%.0f")
        category_input = st.selectbox("Kategori", categories)

        if wallet_options:
            wallet_name   = st.selectbox("Wallet", list(wallet_options.keys()))
            wallet_id_val = wallet_options[wallet_name]
        else:
            wallet_name   = None
            wallet_id_val = None

        notes_input = st.text_input("Catatan (Opsional)")

        submitted = st.form_submit_button("Simpan Transaksi", use_container_width=True, type="primary")

        if submitted:
            if amount_input > 0:
                try:
                    insert_transaction(
                        date_input, type_input, amount_input,
                        category_input, notes_input, wallet_id_val,
                    )
                    refresh_data()
                    st.success("✅ Transaksi berhasil disimpan!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Gagal menyimpan transaksi. Silakan coba lagi. ({e})")
            else:
                st.error("Nominal harus lebih dari 0.")