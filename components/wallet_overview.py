import streamlit as st
import datetime
from utils.db import (
    insert_wallet, deactivate_wallet,
    transfer_wallets, calculate_wallet_balance, refresh_data,
)
from utils.tokens import COLOR, FONT, SPACE, RADIUS, BORDER
from utils.ui import empty_state

WALLET_TYPE_META = {
    "cash":       {"label": "Cash / Tunai", "icon": "💵"},
    "bank":       {"label": "Bank",         "icon": "🏦"},
    "ewallet":    {"label": "E-Wallet",     "icon": "📱"},
    "investment": {"label": "Investasi",    "icon": "📈"},
}

WALLET_COLORS = {
    "cash":       {"bg": "#f0fdf4", "bar": "#2d6a4f", "text": "#1a2e1a"},
    "bank":       {"bg": "#EFF6FF", "bar": "#3B82F6", "text": "#1E3A5F"},
    "ewallet":    {"bg": "#FAF5FF", "bar": "#9333EA", "text": "#581C87"},
    "investment": {"bg": "#FFF7ED", "bar": "#EA580C", "text": "#9A3412"},
}


def _wallet_card(
    name: str,
    wallet_type: str,
    balance_idr: float,
    wallet_id: str,
    currency: str = "IDR",
    balance_usd: float | None = None,
    idr_rate: float | None = None,
) -> str:
    """
    HTML card untuk satu wallet.
    Jika currency='USD', tampilkan dua baris: saldo USD + estimasi IDR.
    """
    meta   = WALLET_TYPE_META.get(wallet_type, {"label": wallet_type, "icon": "💼"})
    colors = WALLET_COLORS.get(wallet_type, WALLET_COLORS["cash"])
    c  = COLOR
    f  = FONT
    r  = RADIUS
    bw = BORDER["accent_width"]

    is_usd = (currency == "USD")
    balance_color = c["danger_text"] if balance_idr < 0 else colors["text"]

    if is_usd and balance_usd is not None:
        primary_amount = (
            f'<div style="text-align:right;">'
            f'<span style="color:{balance_color}; font-weight:{f["weight_black"]}; font-size:{f["size_lg"]};">'
            f'$ {balance_usd:,.2f}</span>'
            f'<div style="color:{c["text_secondary"]}; font-size:{f["size_sm"]}; margin-top:2px;">'
            f'≈ Rp {balance_idr:,.0f}'
            f'{(" @ " + f"{idr_rate:,.0f}") if idr_rate else ""}'
            f'</div>'
            f'</div>'
        )
    else:
        primary_amount = (
            f'<span style="color:{balance_color}; font-weight:{f["weight_black"]}; font-size:{f["size_lg"]};">'
            f'Rp {balance_idr:,.0f}'
            f'</span>'
        )

    return (
        f'<div style="'
        f'background:{colors["bg"]}; '
        f'border-left:{bw} solid {colors["bar"]}; '
        f'border-radius:{r["md"]}; '
        f'border-top-left-radius:0; border-bottom-left-radius:0; '
        f'padding:{SPACE["md"]} {SPACE["xl"]}; '
        f'margin-bottom:{SPACE["sm"]};">'
        f'<div style="display:flex; justify-content:space-between; align-items:center;">'
        f'<div>'
        f'<span style="font-size:1.2rem;">{meta["icon"]}</span> '
        f'<span style="color:{colors["text"]}; font-weight:{f["weight_bold"]}; font-size:{f["size_body"]};">'
        f'{name}'
        f'</span>'
        f'<div style="color:{c["text_secondary"]}; font-size:{f["size_sm"]}; margin-top:2px;">'
        f'{meta["label"]}'
        f'{" · USD" if is_usd else ""}'
        f'</div>'
        f'</div>'
        f'{primary_amount}'
        f'</div>'
        f'</div>'
    )


def render_wallet_overview(transactions_data: list, wallets_data: list) -> None:
    """
    Section Wallet Overview — tampilkan saldo per wallet,
    form tambah wallet baru, dan form transfer antar wallet.
    """
    st.subheader("Wallet & Rekening")

    # Ambil kurs untuk konversi USD wallet
    idr_rate = None
    try:
        from utils.fx import get_usd_to_idr
        fx = get_usd_to_idr()
        idr_rate = fx["rate"]
    except Exception:
        idr_rate = 16200.0

    if not wallets_data:
        st.markdown(
            empty_state(
                icon="💳",
                title="Belum ada wallet terkonfigurasi.",
                body="Tambahkan wallet pertama Anda di bawah.",
                variant="info",
            ),
            unsafe_allow_html=True,
        )
    else:
        total_operational = 0.0
        total_investment   = 0.0

        for wallet in wallets_data:
            currency = wallet.get('currency', 'IDR')
            balance_idr = calculate_wallet_balance(
                wallet['id'], transactions_data, float(wallet.get('initial_balance', 0))
            )

            # Untuk wallet USD, hitung saldo USD asli
            if currency == 'USD' and idr_rate:
                balance_usd = balance_idr / idr_rate
                st.markdown(
                    _wallet_card(
                        name=wallet['name'],
                        wallet_type=wallet['type'],
                        balance_idr=balance_idr,
                        wallet_id=wallet['id'],
                        currency='USD',
                        balance_usd=balance_usd,
                        idr_rate=idr_rate,
                    ),
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    _wallet_card(
                        name=wallet['name'],
                        wallet_type=wallet['type'],
                        balance_idr=balance_idr,
                        wallet_id=wallet['id'],
                    ),
                    unsafe_allow_html=True,
                )

            if wallet.get('is_investment'):
                total_investment += balance_idr
            else:
                total_operational += balance_idr

        with st.container(border=True):
            col1, col2 = st.columns(2)
            col1.metric(
                "Total Saldo Operasional",
                f"Rp {total_operational:,.0f}",
                help="Cash + Bank + E-Wallet. Masuk ke perhitungan runway.",
            )
            col2.metric(
                "Total Investasi",
                f"Rp {total_investment:,.0f}",
                help="Tidak masuk perhitungan runway.",
            )

    st.markdown("---")

    # ── Dua kolom: Tambah Wallet | Transfer ──────────────────
    col_add, col_transfer = st.columns(2, gap="large")

    with col_add:
        with st.container(border=True):
            st.markdown("**Tambah Wallet Baru**")
            with st.form("add_wallet_form", clear_on_submit=True):
                w_name    = st.text_input("Nama Wallet", placeholder="cth: Bank Mandiri")
                w_type    = st.selectbox(
                    "Tipe",
                    options=["cash", "bank", "ewallet", "investment"],
                    format_func=lambda x: WALLET_TYPE_META[x]["label"],
                )
                w_balance = st.number_input(
                    "Saldo Awal (Rp)", min_value=0.0, step=100000.0, format="%.0f"
                )
                submitted_add = st.form_submit_button(
                    "Tambah Wallet", use_container_width=True, type="primary"
                )
                if submitted_add:
                    if w_name.strip():
                        try:
                            insert_wallet(
                                name=w_name.strip(),
                                type_=w_type,
                                initial_balance=w_balance,
                                is_investment=(w_type == "investment"),
                            )
                            refresh_data()
                            st.success(f"✅ Wallet {w_name} berhasil ditambahkan!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Gagal menambahkan wallet. ({e})")
                    else:
                        st.error("Nama wallet tidak boleh kosong.")

    with col_transfer:
        with st.container(border=True):
            st.markdown("**Transfer Antar Wallet**")
            if len(wallets_data) < 2:
                st.caption("Minimal 2 wallet untuk melakukan transfer.")
            else:
                wallet_map = {w['name']: w['id'] for w in wallets_data}
                wallet_names = list(wallet_map.keys())

                with st.form("transfer_wallet_form", clear_on_submit=True):
                    from_name = st.selectbox("Dari Wallet", wallet_names, key="tf_from")
                    to_name   = st.selectbox(
                        "Ke Wallet",
                        [n for n in wallet_names if n != from_name],
                        key="tf_to",
                    )
                    tf_amount = st.number_input(
                        "Nominal Transfer (Rp)", min_value=0.0, step=100000.0, format="%.0f"
                    )
                    tf_date   = st.date_input("Tanggal Transfer", datetime.date.today())
                    tf_notes  = st.text_input("Catatan (Opsional)")

                    submitted_tf = st.form_submit_button(
                        "Konfirmasi Transfer", use_container_width=True, type="primary"
                    )
                    if submitted_tf:
                        if tf_amount > 0 and from_name != to_name:
                            try:
                                transfer_wallets(
                                    from_wallet_id=wallet_map[from_name],
                                    to_wallet_id=wallet_map[to_name],
                                    amount=tf_amount,
                                    date=tf_date,
                                    notes=tf_notes,
                                )
                                refresh_data()
                                st.success(
                                    f"✅ Transfer Rp {tf_amount:,.0f} dari {from_name} ke {to_name} berhasil!"
                                )
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Transfer gagal. ({e})")
                        elif from_name == to_name:
                            st.error("Wallet asal dan tujuan tidak boleh sama.")
                        else:
                            st.error("Nominal transfer harus lebih dari 0.")