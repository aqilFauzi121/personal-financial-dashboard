import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.tokens import COLOR, CHART_PALETTE_EXPENSE, CHART_PALETTE_INCOME


def _prepare_df(transactions_data: list, period: str) -> pd.DataFrame:
    """
    Filter dan kelompokkan transaksi berdasarkan periode (minggu/bulan).
    Mengembalikan DataFrame dengan kolom: type, category, amount.
    """
    if not transactions_data:
        return pd.DataFrame(columns=["type", "category", "amount"])

    df = pd.DataFrame(transactions_data)
    df["amount"] = pd.to_numeric(df["amount"])
    df["date"] = pd.to_datetime(df["date"])

    cutoff = (
        datetime.now() - timedelta(weeks=1)
        if period == "Minggu ini"
        else datetime.now() - timedelta(days=30)
    )
    df = df[df["date"] >= cutoff]
    return df


def _pie(df: pd.DataFrame, tx_type: str, palette: list) -> go.Figure:
    """
    Buat satu Plotly pie chart untuk tipe transaksi tertentu.
    Mengembalikan Figure kosong dengan pesan jika tidak ada data.
    """
    subset = df[df["type"] == tx_type].groupby("category")["amount"].sum().reset_index()
    subset = subset.sort_values("amount", ascending=False)

    fig = go.Figure()

    if subset.empty:
        fig.add_annotation(
            text="Belum ada data",
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=14, color=COLOR["text_secondary"]),
        )
        fig.update_layout(
            height=320,
            margin=dict(t=8, b=8, l=8, r=8),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return fig

    fig.add_trace(go.Pie(
        labels=subset["category"],
        values=subset["amount"],
        hole=0.48,
        marker=dict(
            colors=palette[: len(subset)],
            line=dict(color=COLOR["text_white"], width=2),
        ),
        textinfo="percent",
        hovertemplate="<b>%{label}</b><br>Rp %{value:,.0f}<br>%{percent}<extra></extra>",
        insidetextfont=dict(size=12),
    ))

    fig.update_layout(
        height=320,
        margin=dict(t=8, b=8, l=8, r=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(
            orientation="v",
            x=1.02, y=0.5,
            xanchor="left",
            font=dict(size=12, color=COLOR["text_primary"]),
        ),
    )
    return fig


def _summary_metrics(df: pd.DataFrame, tx_type: str) -> tuple[float, str]:
    """Hitung total dan kategori terbesar untuk suatu tipe transaksi."""
    subset = df[df["type"] == tx_type]
    if subset.empty:
        return 0.0, "-"
    total = subset["amount"].sum()
    top_cat = subset.groupby("category")["amount"].sum().idxmax()
    return total, top_cat


def render_spending_chart(transactions_data: list) -> None:
    """
    Render section Analisis Transaksi — dua pie chart berdampingan
    (Pengeluaran & Pemasukan) dengan toggle periode mingguan/bulanan.

    Dipanggil dari app.py setelah Riwayat Transaksi.
    """
    st.subheader("Analisis Transaksi")

    if not transactions_data:
        from utils.ui import empty_state
        st.markdown(
            empty_state(
                icon="📊",
                title="Belum ada data untuk ditampilkan.",
                body="Tambahkan beberapa transaksi dulu lewat sidebar.",
                variant="info",
            ),
            unsafe_allow_html=True,
        )
        return

    # ── Toggle periode ──────────────────────────────────────────
    period = st.radio(
        "Periode",
        options=["Minggu ini", "30 Hari Terakhir"],
        horizontal=True,
        label_visibility="collapsed",
    )

    df = _prepare_df(transactions_data, period)

    # ── Summary metrics ─────────────────────────────────────────
    total_expense, top_expense_cat = _summary_metrics(df, "Pengeluaran")
    total_income,  top_income_cat  = _summary_metrics(df, "Pemasukan")

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Total Pengeluaran", f"Rp {total_expense:,.0f}")
    col_m2.metric("Kategori Terbesar", top_expense_cat)
    col_m3.metric("Total Pemasukan",   f"Rp {total_income:,.0f}")
    col_m4.metric("Sumber Terbesar",   top_income_cat)

    st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)

    # ── Dua pie chart berdampingan ───────────────────────────────
    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        with st.container(border=True):
            st.caption("Komposisi Pengeluaran")
            fig_expense = _pie(df, "Pengeluaran", CHART_PALETTE_EXPENSE)
            st.plotly_chart(fig_expense, use_container_width=True, config={"displayModeBar": False}, key="chart_expense")

    with col_right:
        with st.container(border=True):
            st.caption("Komposisi Pemasukan")
            fig_income = _pie(df, "Pemasukan", CHART_PALETTE_INCOME)
            st.plotly_chart(fig_income, use_container_width=True, config={"displayModeBar": False}, key="chart_income")