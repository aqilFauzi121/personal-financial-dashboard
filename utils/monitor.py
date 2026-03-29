import sys
import streamlit as st
from utils.logger import get_logger

logger = get_logger("monitor")

def init_sentry():
    # Hanya aktifkan Sentry di Linux (production)
    # Windows lokal skip — bug arsitektural sentry-sdk 2.x + supabase di Windows
    if sys.platform == "win32":
        logger.info("Platform Windows terdeteksi. Sentry dinonaktifkan untuk development lokal.")
        return

    try:
        import sentry_sdk
        dsn = st.secrets.get("SENTRY_DSN", None)
        if not dsn:
            logger.info("SENTRY_DSN tidak ditemukan. Sentry dinonaktifkan.")
            return

        sentry_sdk.init(
            dsn=dsn,
            traces_sample_rate=0.2,
            send_default_pii=False
        )
        logger.info("Sentry berhasil diinisialisasi.")
    except Exception as e:
        logger.error(f"Gagal menginisialisasi Sentry: {e}")