import streamlit as st
import datetime
from utils.db import insert_pending_income, mark_income_as_paid

def render_pending_incomes(pending_data):
    st.subheader("Pending Income Tracker")
    
    with st.container(border=True):
        st.markdown("**Tambah Faktur / Piutang Baru**")
        with st.form("new_invoice_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                client = st.text_input("Nama Klien / Proyek")
                amount = st.number_input("Nominal Tagihan (Rp)", min_value=0.0, step=100000.0)
            with col2:
                due_date = st.date_input("Tenggat Waktu", datetime.date.today() + datetime.timedelta(days=14))
            
            submitted_invoice = st.form_submit_button("Tambah Tagihan", use_container_width=True, type="primary")
            if submitted_invoice:
                if client and amount > 0:
                    insert_pending_income(client, amount, due_date)
                    st.success("Faktur berhasil ditambahkan.")
                    st.rerun()
                else:
                    st.error("Mohon lengkapi Nama Klien dan Nominal.")

    # List faktur yang statusnya 'Pending'
    pending_items = [item for item in pending_data if item['status'] == 'Pending']
    
    if not pending_items:
        st.markdown(
            '<div style="background:#ECFDF5; border-left:4px solid #10B981; padding:16px 20px; border-radius:8px;">'
            '<span style="font-size:1.3rem;">🎉</span> '
            '<span style="color:#065F46; font-weight:600;">Semua piutang sudah cair!</span><br>'
            '<span style="color:#064E3B; font-size:0.9rem;">Tidak ada tagihan tertunda. Kerja bagus!</span>'
            '</div>',
            unsafe_allow_html=True
        )
        return

    st.markdown("**Daftar Menunggu Pembayaran:**")
    
    for item in pending_items:
        with st.container(border=True):
            # Baris informasi faktur
            st.markdown(f"**{item['client_name']}** — Rp {float(item['amount']):,.0f}")
            st.caption(f"Tenggat: {item['due_date']} | ID: {item['id']}")
            
            # Tombol pencairan (logic pop-over persentase pajak)
            cair_key = f"cair_btn_{item['id']}"
            if st.button("Tandai Cair", key=cair_key, use_container_width=True):
                st.session_state[f"show_tax_{item['id']}"] = True

            # Jika state show_tax diaktifkan, munculkan pengaturan potongan
            if st.session_state.get(f"show_tax_{item['id']}", False):
                st.markdown("---")
                tax_pct = st.slider(f"Potong Persentase ke Pajak/Biaya Admin (%) untuk {item['client_name']}", 
                                    min_value=0.0, max_value=30.0, value=0.0, step=1.0, key=f"tax_slider_{item['id']}")
                
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    if st.button("Konfirmasi Cairkan Saldo", key=f"confirm_{item['id']}", type="primary", use_container_width=True):
                        mark_income_as_paid(
                            income_id=item['id'], 
                            client_name=item['client_name'], 
                            amount=float(item['amount']), 
                            due_date=datetime.date.today(), # Set tanggal cair hari ini
                            tax_percentage=tax_pct
                        )
                        st.success(f"Faktur {item['client_name']} berhasil dicairkan.")
                        st.session_state[f"show_tax_{item['id']}"] = False
                        st.rerun()
                with col_c2:
                    if st.button("Batal", key=f"cancel_{item['id']}", use_container_width=True):
                        st.session_state[f"show_tax_{item['id']}"] = False
                        st.rerun()
