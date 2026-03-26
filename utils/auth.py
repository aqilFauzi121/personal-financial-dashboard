import streamlit as st

def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["APP_PIN"]:
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    # Login page — centered card layout
    st.markdown(
        '<div style="max-width:480px; margin:60px auto 0 auto;">'
        
        # Card wrapper
        '<div style="background:#ffffff; border:1px solid #e5e1d8; border-radius:16px; '
        'padding:40px; box-shadow:0 4px 16px rgba(0,0,0,0.08); text-align:center;">'
        
        # Icon + Title + Tagline
        '<div style="font-size:4rem; margin-bottom:8px;">💼</div>'
        '<h1 style="margin:0; font-size:24px; font-weight:800; color:#1a1a2e; letter-spacing:-0.03em;">'
        'Arsitek Finansial Pribadi</h1>'
        '<p style="color:#6b7280; font-size:14px; margin:8px 0 24px 0; font-weight:400;">'
        'Kelola arus kas freelancer — lebih tenang, lebih terarah.</p>'
        
        # Divider
        '<hr style="border:none; border-top:1px solid #e5e1d8; margin:0 0 24px 0;">'
        
        # Subtitle
        '<p style="color:#6b7280; font-size:14px; margin-bottom:16px;">'
        'Silakan masukkan PIN untuk mengakses dasbor keuangan Anda.</p>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    # PIN input — placed below the card for Streamlit widget rendering
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.text_input(
            "PIN Akses", type="password", on_change=password_entered, key="password",
            label_visibility="collapsed", placeholder="Masukkan PIN..."
        )
    
        if "password" in st.session_state and not st.session_state["password_correct"]:
            if st.session_state["password"] != "":
                st.error("PIN salah. Silakan coba lagi.")
    
    return False
