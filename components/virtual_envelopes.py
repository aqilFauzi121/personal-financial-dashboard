import streamlit as st

def render_virtual_envelopes(current_balance, envelopes_data):
    st.subheader("Virtual Envelopes")
    
    if current_balance <= 0:
        st.info("Saldo utama sedang kosong atau minus. Tidak dapat mengalokasikan dana ke amplop.")
        return
        
    if not envelopes_data:
        st.info("Belum ada konfigurasi persentase amplop di tabel envelopes Supabase.")
        return
        
    st.caption("Visualisasi ini membantu memecah sisa Runway Balance (Rp {0:,.0f}) ke pos-pos penting agar tidak terpakai sembarangan.".format(current_balance))
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.container(border=True):
        for env in envelopes_data:
            per = float(env['allocation_percentage'])
            allocated_amount = current_balance * (per / 100.0)
            
            # Kolom text dan nilai alokasi
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{env['name']}** ({per}%)")
            with col2:
                st.markdown(f"**Rp {allocated_amount:,.0f}**")
                
            st.progress(int(per), text=f"Alokasi {per}%")
