import sentry_sdk
import streamlit as st
from utils.logger import get_logger

logger = get_logger("monitor")

def init_sentry():
    """
    Inisialisasi Sentry error monitoring.
    DSN diambil dari secrets.toml agar tidak hardcoded.
    """
    try:
        dsn = st.secrets.get("SENTRY_DSN", None)
        if not dsn:
            logger.info("SENTRY_DSN tidak ditemukan di secrets. Sentry dinonaktifkan.")
            return

        sentry_sdk.init(
            dsn=dsn,
            traces_sample_rate=0.2,  # Rekam 20% transaksi untuk performance monitoring
            send_default_pii=False   # Jangan kirim data pribadi ke Sentry
        )
        logger.info("Sentry berhasil diinisialisasi.")
    except Exception as e:
        logger.error(f"Gagal menginisialisasi Sentry: {e}")