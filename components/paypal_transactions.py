import streamlit as st
import datetime
from utils.db import get_supabase, refresh_data
from utils.fx import get_usd_to_idr, get_paypal_effective_rate, get_all_fx_settings
from utils.tokens import COLOR, FONT, SPACE
from utils.ui import empty_state


def _get_paypal_wallets(wallets_data: list) -> list:
    """Filter hanya wallet dengan currency USD."""
    return [w for w in wallets_data if w.get('currency') == 'USD']


def _get_idr_wallets(wallets_data: list) -> list:
    """Filter wallet IDR (non-investment) untuk tujuan transfer."""
    return [w for w in wallets_data if w.get('currency', 'IDR') == 'IDR' and not w.get('is_investment')]


def _fx_info_bar(fx_data: dict, paypal_data: dict) -> str:
    """HTML bar info kurs aktif."""
    c = COLOR
    f = FONT
    source_label = "Live" if fx_data["source"] == "live" else "Cache"
    updated_str  = fx_data["updated_at"].strftime("%d %b %Y %H:%M") if fx_data.get("updated_at") else "—"

    return (
        f'<div style="'
        f'background:{c["info_bg"]}; '
        f'border-left:4px solid {c["info_border"]}; '
        f'border-radius:8px; border-top-left-radius:0; border-bottom-left-radius:0; '
        f'padding:{SPACE["sm"]} {SPACE["xl"]}; '
        f'margin-bottom:{SPACE["md"]}; '
        f'display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">'

        f'<div style="display:flex; gap:24px; flex-wrap:wrap;">'
        f'<span style="color:{c["info_text"]}; font-size:{f["size_sm"]};">'
        f'Kurs USD/IDR &nbsp;<strong>Rp {fx_data["rate"]:,.0f}</strong>'
        f'</span>'
        f'<span style="color:{c["info_text"]}; font-size:{f["size_sm"]};">'
        f'Kurs efektif PayPal &nbsp;<strong>Rp {paypal_data["paypal_rate"]:,.0f}</strong>'
        f'&nbsp;(spread −Rp {paypal_data["spread"]:,.0f}/USD)'
        f'</span>'
        f'</div>'

        f'<span style="color:{c["text_secondary"]}; font-size:{f["size_sm"]};">'
        f'{source_label} · {updated_str}'
        f'</span>'
        f'</div>'
    )


def render_paypal_transactions(wallets_data: list) -> None:
    """
    Section Transaksi PayPal & Adobe Stock.
    Menangani dua alur:
      1. Terima pembayaran Adobe Stock → PayPal (dengan potongan pajak W-8BEN)
      2. Withdraw PayPal → Bank lokal (dengan konversi kurs + fee otomatis)
    """
    st.subheader("Transaksi PayPal & Adobe Stock")

    paypal_wallets = _get_paypal_wallets(wallets_data)
    idr_wallets    = _get_idr_wallets(wallets_data)

    if not paypal_wallets:
        st.markdown(
            empty_state(
                icon="💸",
                title="Belum ada wallet PayPal (USD).",
                body="Tambahkan wallet baru dengan currency USD di section Wallet & Rekening di atas.",
                variant="info",
            ),
            unsafe_allow_html=True,
        )
        return

    # ── Fetch kurs otomatis ───────────────────────────────────
    with st.spinner("Mengambil kurs terkini..."):
        try:
            fx_data     = get_usd_to_idr()
            paypal_data = get_paypal_effective_rate()
            fx_settings = get_all_fx_settings()
        except Exception as e:
            st.error(f"❌ Gagal mengambil kurs: {e}")
            return

    # ── Info bar kurs + tombol refresh manual ────────────────
    col_bar, col_refresh = st.columns([5, 1])
    with col_bar:
        st.markdown(_fx_info_bar(fx_data, paypal_data), unsafe_allow_html=True)
    with col_refresh:
        if st.button("🔄 Refresh Kurs", key="refresh_fx", help="Paksa fetch kurs terbaru dari API"):
            with st.spinner("Fetching..."):
                try:
                    fx_data     = get_usd_to_idr(force_refresh=True)
                    paypal_data = get_paypal_effective_rate()
                    st.success(f"✅ Kurs diperbarui: Rp {fx_data['rate']:,.0f}/USD")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Gagal refresh: {e}")

    # ── Dua kolom: Adobe Stock | PayPal Withdraw ─────────────
    col_adobe, col_withdraw = st.columns(2, gap="large")

    # ─────────────────────────────────────────────────────────
    # KOLOM KIRI — Terima Pembayaran Adobe Stock
    # ─────────────────────────────────────────────────────────
    with col_adobe:
        with st.container(border=True):
            st.markdown("**Terima Pembayaran Adobe Stock**")
            st.caption("Hitung otomatis potongan pajak W-8BEN 10% sebelum masuk ke PayPal.")

            paypal_names = {w['name']: w['id'] for w in paypal_wallets}

            with st.form("adobe_stock_form", clear_on_submit=True):
                gross_usd = st.number_input(
                    "Nominal Kotor Adobe Stock (USD)",
                    min_value=0.01,
                    step=0.01,
                    format="%.2f",
                    key="adobe_gross",
                )
                paypal_wallet_name = st.selectbox(
                    "Masuk ke Wallet PayPal",
                    list(paypal_names.keys()),
                )
                adobe_date = st.date_input(
                    "Tanggal Diterima",
                    datetime.date.today(),
                )
                adobe_notes = st.text_input("Catatan (Opsional)")

                # Preview kalkulasi
                if gross_usd > 0:
                    tax_pct     = float(fx_settings.get('adobe_tax_w8ben_pct', {}).get('value', 10))
                    tax_usd     = round(gross_usd * tax_pct / 100, 2)
                    net_usd     = round(gross_usd - tax_usd, 2)
                    net_idr     = round(net_usd * fx_data["rate"], 0)

                    st.markdown(
                        f'<div style="background:#f0fdf4; border-radius:8px; padding:12px 16px; margin:8px 0;">'
                        f'<div style="font-size:12px; color:#6b7280; margin-bottom:4px;">Ringkasan kalkulasi</div>'
                        f'<div style="font-size:13px; color:#1a1a2e;">'
                        f'Kotor: <strong>${gross_usd:.2f}</strong>'
                        f' − Pajak W-8BEN {tax_pct:.0f}% (<strong>${tax_usd:.2f}</strong>)'
                        f' = <strong>${net_usd:.2f}</strong>'
                        f'</div>'
                        f'<div style="font-size:12px; color:#6b7280; margin-top:2px;">'
                        f'≈ Rp {net_idr:,.0f} (kurs Rp {fx_data["rate"]:,.0f}/USD)'
                        f'</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                submitted_adobe = st.form_submit_button(
                    "Catat Pemasukan Adobe Stock",
                    use_container_width=True,
                    type="primary",
                )

                if submitted_adobe:
                    if gross_usd > 0:
                        try:
                            supabase = get_supabase()
                            result   = supabase.rpc("receive_adobe_stock_payment", {
                                "p_gross_usd":        gross_usd,
                                "p_paypal_wallet_id": str(paypal_names[paypal_wallet_name]),
                                "p_date":             str(adobe_date),
                                "p_notes":            adobe_notes or "",
                                "p_use_w8ben":        True,
                            }).execute()
                            refresh_data()
                            row = result.data[0] if result.data else {}
                            st.success(
                                f"✅ Dicatat! ${row.get('gross_usd', gross_usd):.2f} "
                                f"→ pajak ${row.get('tax_usd', 0):.2f} "
                                f"→ neto ${row.get('net_usd', 0):.2f} masuk ke {paypal_wallet_name}"
                            )
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Gagal mencatat. ({e})")
                    else:
                        st.error("Nominal harus lebih dari 0.")

    # ─────────────────────────────────────────────────────────
    # KOLOM KANAN — Withdraw PayPal ke Bank
    # ─────────────────────────────────────────────────────────
    with col_withdraw:
        with st.container(border=True):
            st.markdown("**Withdraw PayPal ke Bank**")
            st.caption("Konversi USD → IDR otomatis dengan kurs efektif PayPal dan fee transfer.")

            if not idr_wallets:
                st.markdown(
                    empty_state(
                        icon="🏦",
                        title="Belum ada wallet bank IDR.",
                        body="Tambahkan wallet Bank terlebih dahulu.",
                        variant="warning",
                    ),
                    unsafe_allow_html=True,
                )
            else:
                paypal_names_wd = {w['name']: w['id'] for w in paypal_wallets}
                bank_names      = {w['name']: w['id'] for w in idr_wallets}

                with st.form("paypal_withdraw_form", clear_on_submit=True):
                    wd_from = st.selectbox("Dari Wallet PayPal", list(paypal_names_wd.keys()))
                    wd_to   = st.selectbox("Ke Wallet Bank", list(bank_names.keys()))
                    wd_usd  = st.number_input(
                        "Nominal Withdraw (USD)",
                        min_value=0.01,
                        step=0.01,
                        format="%.2f",
                    )
                    wd_date  = st.date_input("Tanggal Withdraw", datetime.date.today())
                    wd_notes = st.text_input("Catatan (Opsional)")

                    # Preview kalkulasi withdrawal
                    if wd_usd > 0:
                        threshold = float(fx_settings.get('paypal_fee_threshold_idr', {}).get('value', 1500000))
                        fee_below = float(fx_settings.get('paypal_fee_bank_below_threshold', {}).get('value', 16000))
                        gross_idr = round(wd_usd * paypal_data["paypal_rate"], 0)
                        fee_idr   = fee_below if gross_idr < threshold else 0
                        net_idr   = gross_idr - fee_idr

                        st.markdown(
                            f'<div style="background:#EFF6FF; border-radius:8px; padding:12px 16px; margin:8px 0;">'
                            f'<div style="font-size:12px; color:#6b7280; margin-bottom:4px;">Ringkasan kalkulasi</div>'
                            f'<div style="font-size:13px; color:#1a1a2e;">'
                            f'${wd_usd:.2f} × Rp {paypal_data["paypal_rate"]:,.0f}'
                            f' = <strong>Rp {gross_idr:,.0f}</strong>'
                            f'</div>'
                            f'<div style="font-size:12px; color:#6b7280; margin-top:2px;">'
                            f'Fee transfer: Rp {fee_idr:,.0f}'
                            f' · <strong>Diterima: Rp {net_idr:,.0f}</strong>'
                            f'</div>'
                            f'<div style="font-size:11px; color:#9ca3af; margin-top:2px;">'
                            f'Kurs PayPal = Rp {paypal_data["bank_rate"]:,.0f} − spread Rp {paypal_data["spread"]:,.0f}/USD'
                            f'</div>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

                    submitted_wd = st.form_submit_button(
                        "Konfirmasi Withdraw",
                        use_container_width=True,
                        type="primary",
                    )

                    if submitted_wd:
                        if wd_usd > 0:
                            try:
                                supabase = get_supabase()
                                result   = supabase.rpc("withdraw_paypal_to_bank", {
                                    "p_amount_usd":       wd_usd,
                                    "p_paypal_wallet_id": str(paypal_names_wd[wd_from]),
                                    "p_bank_wallet_id":   str(bank_names[wd_to]),
                                    "p_date":             str(wd_date),
                                    "p_notes":            wd_notes or "",
                                }).execute()
                                refresh_data()
                                row = result.data[0] if result.data else {}
                                st.success(
                                    f"✅ Withdraw ${row.get('amount_usd', wd_usd):.2f} "
                                    f"→ Rp {row.get('net_idr', 0):,.0f} "
                                    f"masuk ke {wd_to}"
                                )
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Gagal withdraw. ({e})")
                        else:
                            st.error("Nominal harus lebih dari 0.")