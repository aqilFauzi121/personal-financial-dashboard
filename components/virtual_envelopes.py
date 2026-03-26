import streamlit as st

# Palet warna untuk setiap amplop — diselaraskan dengan tema Teal
ENVELOPE_COLORS = [
    {"bg": "#F0FDFA", "bar": "#0D9488", "text": "#134E4A"},  # Teal (Primary)
    {"bg": "#ECFDF5", "bar": "#059669", "text": "#064E3B"},  # Emerald
    {"bg": "#EFF6FF", "bar": "#3B82F6", "text": "#1E3A5F"},  # Blue
    {"bg": "#FFF7ED", "bar": "#EA580C", "text": "#9A3412"},  # Orange
    {"bg": "#FAF5FF", "bar": "#9333EA", "text": "#581C87"},  # Purple
    {"bg": "#FDF2F8", "bar": "#DB2777", "text": "#9D174D"},  # Pink
]

def render_virtual_envelopes(current_balance, envelopes_data):
    st.subheader("Virtual Envelopes")
    
    if current_balance <= 0:
        st.info("Saldo utama sedang kosong atau minus. Tidak dapat mengalokasikan dana ke amplop.")
        return
        
    if not envelopes_data:
        st.info("Belum ada konfigurasi persentase amplop di tabel envelopes Supabase.")
        return
        
    st.caption("Alokasi sisa Runway Balance (Rp {0:,.0f}) ke pos-pos penting.".format(current_balance))
    
    for idx, env in enumerate(envelopes_data):
        per = float(env['allocation_percentage'])
        allocated_amount = current_balance * (per / 100.0)
        color = ENVELOPE_COLORS[idx % len(ENVELOPE_COLORS)]
        
        st.markdown(
            f'<div style="background:{color["bg"]}; border-left:4px solid {color["bar"]}; '
            f'padding:12px 16px; border-radius:6px; margin-bottom:10px;">'
            f'<div style="display:flex; justify-content:space-between; align-items:center;">'
            f'<span style="color:{color["text"]}; font-weight:600;">{env["name"]}</span>'
            f'<span style="color:{color["text"]}; font-weight:700; font-size:1.1rem;">Rp {allocated_amount:,.0f}</span>'
            f'</div>'
            f'<div style="background:#E2E8F0; border-radius:4px; height:8px; margin-top:8px; overflow:hidden;">'
            f'<div style="background:{color["bar"]}; width:{int(per)}%; height:100%; border-radius:4px;"></div>'
            f'</div>'
            f'<span style="color:{color["text"]}; font-size:0.75rem;">Alokasi {per}%</span>'
            f'</div>',
            unsafe_allow_html=True
        )
