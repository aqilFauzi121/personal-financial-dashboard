import streamlit as st

# Palet warna berbeda untuk setiap amplop agar tampilan lebih kaya visual
ENVELOPE_COLORS = [
    {"bg": "#EEF2FF", "bar": "#6366F1", "text": "#3730A3"},  # Indigo
    {"bg": "#ECFDF5", "bar": "#10B981", "text": "#065F46"},  # Emerald
    {"bg": "#FFF7ED", "bar": "#F97316", "text": "#9A3412"},  # Orange
    {"bg": "#FDF2F8", "bar": "#EC4899", "text": "#9D174D"},  # Pink
    {"bg": "#F0F9FF", "bar": "#0EA5E9", "text": "#0C4A6E"},  # Sky
    {"bg": "#FEFCE8", "bar": "#EAB308", "text": "#854D0E"},  # Yellow
]

def render_virtual_envelopes(current_balance, envelopes_data):
    st.subheader("Virtual Envelopes")
    
    if current_balance <= 0:
        st.info("Saldo utama sedang kosong atau minus. Tidak dapat mengalokasikan dana ke amplop.")
        return
        
    if not envelopes_data:
        st.info("Belum ada konfigurasi persentase amplop di tabel envelopes Supabase.")
        return
        
    st.caption("Visualisasi ini membantu memecah sisa Runway Balance (Rp {0:,.0f}) ke pos-pos penting agar tidak terpakai sembarangan.".format(current_balance))
    
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
            f'<div style="background:#E5E7EB; border-radius:4px; height:8px; margin-top:8px; overflow:hidden;">'
            f'<div style="background:{color["bar"]}; width:{int(per)}%; height:100%; border-radius:4px;"></div>'
            f'</div>'
            f'<span style="color:{color["text"]}; font-size:0.75rem;">Alokasi {per}%</span>'
            f'</div>',
            unsafe_allow_html=True
        )
