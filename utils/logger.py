import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """
    Mengembalikan logger terstandarisasi untuk dipakai di seluruh modul.
    Format: [LEVEL] YYYY-MM-DD HH:MM:SS — nama_modul: pesan
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="[%(levelname)s] %(asctime)s — %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger