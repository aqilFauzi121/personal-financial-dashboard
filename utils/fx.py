    # ============================================================
# FX — Foreign Exchange Rate Manager
# Arsitek Finansial Pribadi
# ============================================================
# Fetch kurs USD/IDR otomatis dari ExchangeRate-API
# (https://open.er-api.com) — gratis, tanpa API key.
#
# Strategi cache harian:
#   1. Cek apakah rate_updated_at di fx_settings adalah hari ini
#   2. Kalau ya  → pakai nilai dari database (tidak fetch ulang)
#   3. Kalau tidak → fetch dari API, simpan ke database, return
#
# Dengan ini maksimal 1 API call per hari, tidak ada rate limit.
# ============================================================

import datetime
import streamlit as st
from utils.logger import get_logger

logger = get_logger("fx")

FX_API_URL = "https://open.er-api.com/v6/latest/USD"
RATE_KEY   = "usd_to_idr_rate"


def _fetch_live_rate() -> float | None:
    """
    Fetch kurs USD→IDR langsung dari ExchangeRate-API.
    Return None jika gagal (network error, API down, dll).
    """
    try:
        import urllib.request
        import json

        with urllib.request.urlopen(FX_API_URL, timeout=5) as resp:
            data = json.loads(resp.read().decode())

        if data.get("result") == "success":
            rate = float(data["rates"]["IDR"])
            logger.info(f"fx: Kurs live USD→IDR = {rate:,.0f}")
            return rate
        else:
            logger.warning(f"fx: API response tidak sukses: {data.get('result')}")
            return None

    except Exception as e:
        logger.warning(f"fx: Gagal fetch live rate: {e}")
        return None


def _get_cached_rate() -> tuple[float, datetime.datetime | None]:
    """
    Baca kurs dan timestamp terakhir update dari database.
    Return (rate, updated_at) — updated_at bisa None jika belum pernah di-set.
    """
    try:
        from utils.db import get_supabase
        supabase = get_supabase()
        resp = supabase.table("fx_settings") \
            .select("value, rate_updated_at") \
            .eq("key", RATE_KEY) \
            .single() \
            .execute()

        row = resp.data
        rate = float(row["value"])
        updated_at = None

        if row.get("rate_updated_at"):
            updated_at = datetime.datetime.fromisoformat(
                row["rate_updated_at"].replace("Z", "+00:00")
            )

        return rate, updated_at

    except Exception as e:
        logger.error(f"fx: Gagal baca cached rate: {e}")
        return 16200.0, None  # fallback default


def _save_rate_to_db(rate: float) -> None:
    """Simpan kurs baru dan timestamp ke database."""
    try:
        from utils.db import get_supabase
        supabase = get_supabase()
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        supabase.table("fx_settings").update({
            "value":           rate,
            "rate_updated_at": now,
            "updated_at":      now,
        }).eq("key", RATE_KEY).execute()
        logger.info(f"fx: Kurs USD→IDR disimpan ke database: {rate:,.0f}")
    except Exception as e:
        logger.error(f"fx: Gagal simpan rate ke database: {e}")


def get_usd_to_idr(force_refresh: bool = False) -> dict:
    """
    Entry point utama — dapatkan kurs USD→IDR dengan cache harian.

    Args:
        force_refresh: kalau True, selalu fetch dari API meski sudah update hari ini

    Returns dict:
        {
            "rate":       float,   # kurs USD→IDR
            "source":     str,     # "live" atau "cached"
            "updated_at": datetime | None,
            "is_fresh":   bool,    # True jika diupdate hari ini
        }
    """
    cached_rate, updated_at = _get_cached_rate()
    today = datetime.date.today()

    # Cek apakah cache masih fresh (hari ini)
    is_fresh = (
        updated_at is not None
        and updated_at.date() == today
    )

    if is_fresh and not force_refresh:
        logger.info(f"fx: Pakai kurs cache ({cached_rate:,.0f}), diupdate {updated_at.strftime('%H:%M')} WIB")
        return {
            "rate":       cached_rate,
            "source":     "cached",
            "updated_at": updated_at,
            "is_fresh":   True,
        }

    # Cache sudah stale atau force refresh — fetch live
    live_rate = _fetch_live_rate()

    if live_rate is not None:
        _save_rate_to_db(live_rate)
        # Invalidate fx cache di session state
        if "fx_rate" in st.session_state:
            del st.session_state["fx_rate"]
        return {
            "rate":       live_rate,
            "source":     "live",
            "updated_at": datetime.datetime.now(datetime.timezone.utc),
            "is_fresh":   True,
        }
    else:
        # API gagal — fallback ke cache lama, tampilkan warning
        logger.warning(f"fx: API gagal, fallback ke cache lama: {cached_rate:,.0f}")
        return {
            "rate":       cached_rate,
            "source":     "cached_fallback",
            "updated_at": updated_at,
            "is_fresh":   False,
        }


def get_paypal_effective_rate() -> dict:
    """
    Hitung kurs efektif PayPal = kurs bank - spread PayPal.

    PayPal memotong sekitar Rp400/USD dari kurs mid-market
    sebagai keuntungan konversi mereka.

    Returns dict:
        {
            "bank_rate":    float,  # kurs mid-market
            "spread":       float,  # potongan PayPal per USD
            "paypal_rate":  float,  # kurs efektif setelah spread
            "source":       str,
            "updated_at":   datetime | None,
        }
    """
    fx_data = get_usd_to_idr()

    try:
        from utils.db import get_supabase
        supabase = get_supabase()
        resp = supabase.table("fx_settings") \
            .select("key, value") \
            .eq("key", "paypal_fx_spread_per_usd") \
            .single() \
            .execute()
        spread = float(resp.data["value"])
    except Exception:
        spread = 400.0  # default fallback

    paypal_rate = fx_data["rate"] - spread

    return {
        "bank_rate":   fx_data["rate"],
        "spread":      spread,
        "paypal_rate": paypal_rate,
        "source":      fx_data["source"],
        "updated_at":  fx_data["updated_at"],
    }


def get_all_fx_settings() -> dict:
    """
    Ambil semua konfigurasi FX dari database sebagai dict {key: value}.
    Dipakai oleh form PayPal untuk menampilkan semua parameter.
    """
    try:
        from utils.db import get_supabase
        supabase = get_supabase()
        resp = supabase.table("fx_settings").select("key, value, description, rate_updated_at").execute()
        return {row["key"]: row for row in resp.data}
    except Exception as e:
        logger.error(f"fx: Gagal ambil fx_settings: {e}")
        return {}


def update_fx_setting(key: str, value: float) -> bool:
    """
    Update satu konfigurasi FX dari dashboard settings.
    Return True jika berhasil.
    """
    try:
        from utils.db import get_supabase
        supabase = get_supabase()
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        supabase.table("fx_settings").update({
            "value":      value,
            "updated_at": now,
        }).eq("key", key).execute()
        logger.info(f"fx: Setting '{key}' diupdate ke {value}")
        return True
    except Exception as e:
        logger.error(f"fx: Gagal update setting '{key}': {e}")
        return False