import streamlit as st

def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["APP_PIN"]:
            st.session_state["password_correct"] = True
            # Jangan hapus session state agar tidak terus-menerus minta PIN jika reload page (opsional)
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    # Branding visual pada halaman login
    st.markdown(
        '<div style="text-align:center; padding:40px 20px 10px 20px;">'
        '<div style="font-size:4rem; margin-bottom:8px;">💼</div>'
        '<h1 style="margin:0; font-size:2rem; font-weight:800; color:#1E293B; letter-spacing:-0.03em;">'
        'Arsitek Finansial Pribadi</h1>'
        '<p style="color:#64748B; font-size:1rem; margin:8px 0 0 0; font-weight:400;">'
        'Kelola arus kas freelancer — lebih tenang, lebih terarah.</p>'
        '</div>',
        unsafe_allow_html=True
    )
    st.markdown("---")
    st.markdown(
        '<p style="text-align:center; color:#64748B; font-size:0.9rem; margin-bottom:-10px;">'
        'Silakan masukkan PIN untuk mengakses dasbor keuangan Anda.</p>',
        unsafe_allow_html=True
    )

    st.text_input(
        "PIN Akses", type="password", on_change=password_entered, key="password"
    )
    
    if "password" in st.session_state and not st.session_state["password_correct"]:
        if st.session_state["password"] != "":  # Hindari pesan error sebelum diisi
            st.error("PIN salah. Silakan coba lagi.")
    
    return False
