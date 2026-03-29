import streamlit as st
from utils.tokens import ENVELOPE_PALETTE
from utils.ui import empty_state, envelope_card


def render_virtual_envelopes(current_balance, envelopes_data):
    st.subheader("Virtual Envelopes")

    if current_balance <= 0:
        st.markdown(
            empty_state(
                icon="💰",
                title="Saldo masih kosong.",
                body="Tambahkan pemasukan dulu ya agar alokasi amplop bisa aktif!",
                variant="warning",
            ),
            unsafe_allow_html=True,
        )
        return

    if not envelopes_data:
        st.markdown(
            empty_state(
                icon="📁",
                title="Belum ada amplop terkonfigurasi.",
                body="Atur persentase alokasi di tabel envelopes Supabase untuk mulai.",
                variant="info",
            ),
            unsafe_allow_html=True,
        )
        return

    st.caption("Alokasi sisa Runway Balance (Rp {0:,.0f}) ke pos-pos penting.".format(current_balance))

    for idx, env in enumerate(envelopes_data):
        per = float(env["allocation_percentage"])
        allocated_amount = current_balance * (per / 100.0)
        color = ENVELOPE_PALETTE[idx % len(ENVELOPE_PALETTE)]

        st.markdown(
            envelope_card(
                name=env["name"],
                allocated_amount=allocated_amount,
                percentage=per,
                color=color,
            ),
            unsafe_allow_html=True,
        )