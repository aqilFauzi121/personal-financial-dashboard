import streamlit as st

def render_virtual_envelopes(current_balance, envelopes_data):
    st.subheader("✉️ Virtual Envelopes (Visualisasi Alokasi Sisa Saldo)")
    
    if current_balance <= 0:
        st.info("Saldo utama sedang kosong atau minus. Tidak dapat mengalokasikan dana ke amplop.")
        return
        
    if not envelopes_data:
        st.info("Belum ada konfigurasi persentase amplop di tabel `envelopes` Supabase.")
        return
        
    st.markdown("Visualisasi ini membantu memecah sisa *Runway Balance* (Rp {0:,.0f}) ke pos-pos penting agar tidak terpakai sembarangan.".format(current_balance))
    
    for env in envelopes_data:
        per = float(env['allocation_percentage'])
        allocated_amount = current_balance * (per / 100.0)
        
        # Kolom text dan nilai alokasi
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{env['name']}** ({per}%)")
        with col2:
            st.markdown(f"**Rp {allocated_amount:,.0f}**")
            
        # progress selalu 100 dari kapasitas alokasi, untuk visual progress bar gunakan nilai max per
        # Untuk Streamlit, max value adalah 100 jika di dalam int, atau float antar 0.0 - 1.0
        # Kita pakaikan bar warna biru untuk merepresentasikan amplop penuh
        st.progress(int(per), text=f"Alokasi {per}%")
