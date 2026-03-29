import streamlit as st
import pandas as pd
import datetime
from utils.db import update_transaction, delete_transaction, fetch_envelopes, fetch_wallets, refresh_data
from utils.ui import empty_state

CATEGORIES_PEMASUKAN = [
    'Freelance / Project Fee', 'Gaji / Retainer', 'Bonus',
    'Passive Income (Royalti, Afiliasi)', 'Investasi / Dividen',
    'Pencairan Faktur', 'Pengembalian Dana / Refund',
    'Transfer Masuk', 'Lainnya',
]

CATEGORIES_PENGELUARAN_EXTRA = [
    'Transportasi & BBM', 'Makan & Minum', 'Langganan (Software, Streaming)',
    'Kesehatan & Medis', 'Pendidikan & Kursus',
    'Transfer Keluar', 'Lainnya',
]

PAGE_SIZE = 10


def _build_categories_pengeluaran() -> list[str]:
    try:
        envelopes = fetch_envelopes()
        env_cats  = [e['name'] for e in envelopes]
    except Exception:
        env_cats  = ['Dana Darurat', 'Operasional', 'Self-Reward', 'Pajak & Biaya Admin']
    seen, result = set(), []
    for cat in env_cats + CATEGORIES_PENGELUARAN_EXTRA:
        if cat not in seen:
            seen.add(cat)
            result.append(cat)
    return result


def _apply_filters(
    df: pd.DataFrame,
    filter_jenis: str,
    filter_kategori: str,
    filter_wallet: str,
    date_from: datetime.date,
    date_to: datetime.date,
) -> pd.DataFrame:
    if filter_jenis != "Semua":
        df = df[df['type'] == filter_jenis]
    if filter_kategori != "Semua":
        df = df[df['category'] == filter_kategori]
    if filter_wallet != "Semua":
        df = df[df['_wallet_name'] == filter_wallet]
    df = df[(df['date'] >= pd.Timestamp(date_from)) & (df['date'] <= pd.Timestamp(date_to))]
    return df


def render_transaction_history(transactions_data: list, wallets_data: list) -> None:
    st.subheader("Riwayat Transaksi")

    if not transactions_data:
        st.markdown(
            empty_state(
                icon="📭",
                title="Belum ada transaksi.",
                body="Yuk catat pengeluaran pertamamu lewat sidebar!",
                variant="warning",
            ),
            unsafe_allow_html=True,
        )
        return

    # ── Bangun DataFrame ─────────────────────────────────────
    df = pd.DataFrame(transactions_data)
    df['date']   = pd.to_datetime(df['date'])
    df['amount'] = pd.to_numeric(df['amount'])

    wallet_map = {w['id']: w['name'] for w in wallets_data} if wallets_data else {}
    df['_wallet_name'] = df['wallet_id'].apply(lambda x: wallet_map.get(str(x), '—') if x else '—')

    # ── Panel filter ─────────────────────────────────────────
    with st.container(border=True):
        fc1, fc2, fc3, fc4 = st.columns([1, 1, 1, 2])

        with fc1:
            filter_jenis = st.selectbox(
                "Jenis", ["Semua", "Pemasukan", "Pengeluaran"],
                key="th_filter_jenis",
            )
        with fc2:
            all_cats = sorted(df['category'].dropna().unique().tolist())
            filter_kategori = st.selectbox(
                "Kategori", ["Semua"] + all_cats,
                key="th_filter_kategori",
            )
        with fc3:
            wallet_names = sorted(df['_wallet_name'].unique().tolist())
            filter_wallet = st.selectbox(
                "Wallet", ["Semua"] + wallet_names,
                key="th_filter_wallet",
            )
        with fc4:
            min_date = df['date'].min().date()
            max_date = df['date'].max().date()
            date_range = st.date_input(
                "Rentang Tanggal",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key="th_filter_date",
            )
            if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
                date_from, date_to = date_range
            else:
                date_from, date_to = min_date, max_date

    # ── Terapkan filter ──────────────────────────────────────
    df_filtered = _apply_filters(df, filter_jenis, filter_kategori, filter_wallet, date_from, date_to)
    df_filtered = df_filtered.sort_values('date', ascending=False).reset_index(drop=True)

    total = len(df_filtered)
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)

    if "th_page" not in st.session_state:
        st.session_state["th_page"] = 1
    # Reset ke hal 1 setiap kali filter berubah
    st.session_state["th_page"] = min(st.session_state["th_page"], total_pages)

    # ── Summary row ──────────────────────────────────────────
    total_masuk  = df_filtered[df_filtered['type'] == 'Pemasukan']['amount'].sum()
    total_keluar = df_filtered[df_filtered['type'] == 'Pengeluaran']['amount'].sum()
    sm1, sm2, sm3 = st.columns(3)
    sm1.metric("Total Transaksi", f"{total}")
    sm2.metric("Total Pemasukan",   f"Rp {total_masuk:,.0f}")
    sm3.metric("Total Pengeluaran", f"Rp {total_keluar:,.0f}")

    if total == 0:
        st.markdown(
            empty_state(
                icon="🔍",
                title="Tidak ada transaksi yang cocok.",
                body="Coba ubah filter di atas.",
                variant="info",
            ),
            unsafe_allow_html=True,
        )
        return

    # ── Slice halaman ────────────────────────────────────────
    page     = st.session_state["th_page"]
    start    = (page - 1) * PAGE_SIZE
    end      = start + PAGE_SIZE
    df_page  = df_filtered.iloc[start:end]

    # ── Render baris transaksi ───────────────────────────────
    categories_pengeluaran = _build_categories_pengeluaran()

    for _, row in df_page.iterrows():
        tx_id  = str(row['id'])
        is_out = row['type'] == 'Pengeluaran'
        amount_color = "#dc2626" if is_out else "#2d6a4f"
        amount_prefix = "−" if is_out else "+"

        with st.container(border=True):
            col_info, col_amount, col_actions = st.columns([4, 2, 1])

            with col_info:
                st.markdown(
                    f"**{row['category']}**  \n"
                    f"<span style='font-size:12px; color:#6b7280;'>"
                    f"{row['date'].strftime('%d %b %Y')} · {row['_wallet_name']}"
                    f"{'  · ' + str(row['notes']) if row['notes'] else ''}"
                    f"</span>",
                    unsafe_allow_html=True,
                )

            with col_amount:
                st.markdown(
                    f"<div style='text-align:right; font-size:18px; font-weight:800; "
                    f"color:{amount_color}; padding-top:6px;'>"
                    f"{amount_prefix} Rp {float(row['amount']):,.0f}"
                    f"</div>",
                    unsafe_allow_html=True,
                )

            with col_actions:
                if st.button("✏️", key=f"edit_{tx_id}", help="Edit transaksi"):
                    st.session_state[f"editing_{tx_id}"] = True
                if st.button("🗑️", key=f"del_{tx_id}", help="Hapus transaksi"):
                    st.session_state[f"confirm_del_{tx_id}"] = True

            # ── Konfirmasi hapus ─────────────────────────────
            if st.session_state.get(f"confirm_del_{tx_id}", False):
                st.warning(f"Yakin hapus transaksi **{row['category']}** Rp {float(row['amount']):,.0f}?")
                cc1, cc2 = st.columns(2)
                with cc1:
                    if st.button("Ya, Hapus", key=f"confirm_yes_{tx_id}", type="primary"):
                        try:
                            delete_transaction(tx_id)
                            refresh_data()
                            st.session_state.pop(f"confirm_del_{tx_id}", None)
                            st.success("✅ Transaksi berhasil dihapus.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Gagal menghapus. ({e})")
                with cc2:
                    if st.button("Batal", key=f"confirm_no_{tx_id}"):
                        st.session_state.pop(f"confirm_del_{tx_id}", None)
                        st.rerun()

            # ── Form edit ────────────────────────────────────
            if st.session_state.get(f"editing_{tx_id}", False):
                with st.form(key=f"edit_form_{tx_id}"):
                    st.markdown("**Edit Transaksi**")
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        new_date = st.date_input(
                            "Tanggal",
                            value=row['date'].date(),
                            key=f"ef_date_{tx_id}",
                        )
                        new_type = st.selectbox(
                            "Jenis",
                            ["Pemasukan", "Pengeluaran"],
                            index=0 if row['type'] == "Pemasukan" else 1,
                            key=f"ef_type_{tx_id}",
                        )
                        new_amount = st.number_input(
                            "Nominal (Rp)",
                            value=float(row['amount']),
                            min_value=0.01,
                            step=1000.0,
                            format="%.0f",
                            key=f"ef_amount_{tx_id}",
                        )
                    with ec2:
                        cats = CATEGORIES_PEMASUKAN if new_type == "Pemasukan" else categories_pengeluaran
                        cur_cat = row['category'] if row['category'] in cats else cats[0]
                        new_cat = st.selectbox(
                            "Kategori", cats,
                            index=cats.index(cur_cat),
                            key=f"ef_cat_{tx_id}",
                        )
                        wallet_options = {"(Tidak ada)": None}
                        if wallets_data:
                            wallet_options.update({w['name']: w['id'] for w in wallets_data})
                        cur_wallet_name = row['_wallet_name'] if row['_wallet_name'] in wallet_options else "(Tidak ada)"
                        new_wallet_name = st.selectbox(
                            "Wallet",
                            list(wallet_options.keys()),
                            index=list(wallet_options.keys()).index(cur_wallet_name),
                            key=f"ef_wallet_{tx_id}",
                        )
                        new_notes = st.text_input(
                            "Catatan",
                            value=str(row['notes']) if row['notes'] else "",
                            key=f"ef_notes_{tx_id}",
                        )

                    es1, es2 = st.columns(2)
                    with es1:
                        save = st.form_submit_button("Simpan Perubahan", type="primary", use_container_width=True)
                    with es2:
                        cancel = st.form_submit_button("Batal", use_container_width=True)

                    if save:
                        try:
                            update_transaction(
                                tx_id=tx_id,
                                date=new_date,
                                type_=new_type,
                                amount=new_amount,
                                category=new_cat,
                                notes=new_notes,
                                wallet_id=wallet_options[new_wallet_name],
                            )
                            refresh_data()
                            st.session_state.pop(f"editing_{tx_id}", None)
                            st.success("✅ Transaksi berhasil diperbarui.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Gagal menyimpan. ({e})")
                    if cancel:
                        st.session_state.pop(f"editing_{tx_id}", None)
                        st.rerun()

    # ── Pagination ───────────────────────────────────────────
    if total_pages > 1:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        pc1, pc2, pc3 = st.columns([1, 3, 1])
        with pc1:
            if st.button("← Sebelumnya", disabled=(page <= 1), key="th_prev"):
                st.session_state["th_page"] -= 1
                st.rerun()
        with pc2:
            st.markdown(
                f"<div style='text-align:center; padding-top:6px; font-size:13px; color:#6b7280;'>"
                f"Halaman {page} dari {total_pages} &nbsp;·&nbsp; {total} transaksi"
                f"</div>",
                unsafe_allow_html=True,
            )
        with pc3:
            if st.button("Selanjutnya →", disabled=(page >= total_pages), key="th_next"):
                st.session_state["th_page"] += 1
                st.rerun()