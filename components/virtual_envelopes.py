import streamlit as st

# Palet warna untuk setiap amplop — diselaraskan dengan tema brand hijau
ENVELOPE_COLORS = [
    {"bg": "#f0fdf4", "bar": "#2d6a4f", "text": "#1a1a2e"},  # Green (Primary)
    {"bg": "#ECFDF5", "bar": "#059669", "text": "#064E3B"},  # Emerald
    {"bg": "#EFF6FF", "bar": "#3B82F6", "text": "#1E3A5F"},  # Blue
    {"bg": "#FFF7ED", "bar": "#EA580C", "text": "#9A3412"},  # Orange
    {"bg": "#FAF5FF", "bar": "#9333EA", "text": "#581C87"},  # Purple
    {"bg": "#FDF2F8", "bar": "#DB2777", "text": "#9D174D"},  # Pink
]

def render_virtual_envelopes(current_balance, envelopes_data):
    st.subheader("Virtual Envelopes")
    
    if current_balance <= 0:
        st.markdown(
            '<div style="background:#fffbeb; border-left:4px solid #d97706; padding:24px; border-radius:8px; text-align:center;">'
            '<div style="font-size:2rem; margin-bottom:8px;">💰</div>'
            '<div style="color:#1a1a2e; font-weight:700; font-size:16px; margin-bottom:4px;">Saldo masih kosong.</div>'
            '<div style="color:#6b7280; font-size:14px;">Tambahkan pemasukan dulu ya agar alokasi amplop bisa aktif!</div>'
            '</div>',
            unsafe_allow_html=True
        )
        return
        
    if not envelopes_data:
        st.markdown(
            '<div style="background:#f0f9ff; border-left:4px solid #0284c7; padding:24px; border-radius:8px; text-align:center;">'
            '<div style="font-size:2rem; margin-bottom:8px;">📁</div>'
            '<div style="color:#1a1a2e; font-weight:700; font-size:16px; margin-bottom:4px;">Belum ada amplop terkonfigurasi.</div>'
            '<div style="color:#6b7280; font-size:14px;">Atur persentase alokasi di tabel envelopes Supabase untuk mulai.</div>'
            '</div>',
            unsafe_allow_html=True
        )
        return
        
    st.caption("Alokasi sisa Runway Balance (Rp {0:,.0f}) ke pos-pos penting.".format(current_balance))
    
    for idx, env in enumerate(envelopes_data):
        per = float(env['allocation_percentage'])
        allocated_amount = current_balance * (per / 100.0)
        color = ENVELOPE_COLORS[idx % len(ENVELOPE_COLORS)]
        
        st.markdown(
            f'<div style="background:{color["bg"]}; border-left:4px solid {color["bar"]}; '
            f'padding:16px 20px; border-radius:8px; margin-bottom:16px;">'
            f'<div style="display:flex; justify-content:space-between; align-items:center;">'
            f'<span style="color:{color["text"]}; font-weight:600; font-size:14px;">{env["name"]}</span>'
            f'<span style="color:{color["text"]}; font-weight:800; font-size:18px;">Rp {allocated_amount:,.0f}</span>'
            f'</div>'
            f'<div style="background:#e5e1d8; border-radius:4px; height:8px; margin-top:8px; overflow:hidden;">'
            f'<div style="background:{color["bar"]}; width:{int(per)}%; height:100%; border-radius:4px;"></div>'
            f'</div>'
            f'<span style="color:#6b7280; font-size:12px; text-transform:uppercase; letter-spacing:0.05em;">Alokasi {per}%</span>'
            f'</div>',
            unsafe_allow_html=True
        )
