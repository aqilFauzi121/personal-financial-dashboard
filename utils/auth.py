import bcrypt
import streamlit as st
from datetime import datetime, timedelta
from utils.ui import login_card

MAX_ATTEMPTS = 5
LOCKOUT_MINUTES = 5

def check_password():
    """Returns True if the user had a correct password."""

    # Inisialisasi session state
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if "failed_attempts" not in st.session_state:
        st.session_state["failed_attempts"] = 0
    if "lockout_until" not in st.session_state:
        st.session_state["lockout_until"] = None

    # Jika sudah login, langsung return True
    if st.session_state["password_correct"]:
        return True

    # ── UI Card ──────────────────────────────────────────
    st.markdown(
        login_card(
            title="Arsitek Finansial Pribadi",
            subtitle="Kelola arus kas freelancer — lebih tenang, lebih terarah.",
            prompt="Silakan masukkan PIN untuk mengakses dasbor keuangan Anda.",
        ),
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:

        # ── Cek apakah sedang dalam masa lockout ─────────
        if st.session_state["lockout_until"]:
            remaining = st.session_state["lockout_until"] - datetime.now()
            if remaining.total_seconds() > 0:
                minutes_left = int(remaining.total_seconds() // 60) + 1
                st.error(f"🔒 Terlalu banyak percobaan gagal. Coba lagi dalam {minutes_left} menit.")
                return False
            else:
                # Lockout sudah selesai, reset
                st.session_state["lockout_until"] = None
                st.session_state["failed_attempts"] = 0

        # ── Input PIN ────────────────────────────────────
        pin_input = st.text_input(
            "PIN Akses", type="password",
            label_visibility="collapsed",
            placeholder="Masukkan PIN...",
            key="password"
        )

        if pin_input:
            if bcrypt.checkpw(pin_input.encode(), st.secrets["APP_PIN"].encode()):
                st.session_state["password_correct"] = True
                st.session_state["failed_attempts"] = 0
                st.session_state["lockout_until"] = None
                st.rerun()
            else:
                st.session_state["failed_attempts"] += 1
                attempts_left = MAX_ATTEMPTS - st.session_state["failed_attempts"]

                if st.session_state["failed_attempts"] >= MAX_ATTEMPTS:
                    st.session_state["lockout_until"] = datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)
                    st.error(f"🔒 Akun dikunci selama {LOCKOUT_MINUTES} menit karena terlalu banyak percobaan.")
                else:
                    st.error(f"PIN salah. Sisa percobaan: {attempts_left}")

    return False