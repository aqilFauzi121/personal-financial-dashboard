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

    st.title("Arsitek Finansial Pribadi")
    st.markdown("Silakan masukkan PIN Anda untuk mengakses dasbor keuangan.")
    
    st.text_input(
        "PIN Akses", type="password", on_change=password_entered, key="password"
    )
    
    if "password" in st.session_state and not st.session_state["password_correct"]:
        if st.session_state["password"] != "":  # Hindari pesan error sebelum diisi
            st.error("PIN salah. Silakan coba lagi.")
    
    return False
