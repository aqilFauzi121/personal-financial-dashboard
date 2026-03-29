# ============================================================
# UI HELPERS — ARSITEK FINANSIAL PRIBADI
# Komponen HTML reusable yang dibangun di atas design tokens.
# Import fungsi ini di komponen, bukan nulis HTML inline.
# ============================================================

from utils.tokens import COLOR, FONT, SPACE, RADIUS, BORDER


def _status_card(
    bg: str,
    border_color: str,
    label_color: str,
    label_text: str,
    value_text: str,
    body_text: str,
    margin_top: str = SPACE["sm"],
    css_class: str = "",
) -> str:
    """
    Kartu status dengan accent border di kiri.
    Dipakai untuk runway health states (aman / hati-hati / kritis).

    css_class — class tambahan untuk dark mode override (afp-status-*)
    Returns HTML string — render dengan st.markdown(..., unsafe_allow_html=True).
    """
    c = COLOR
    f = FONT
    r = RADIUS
    bw = BORDER["accent_width"]
    extra_class = f" {css_class}" if css_class else ""

    return (
        f'<div class="afp-status-card{extra_class}" style="'
        f'background:{bg}; '
        f'border-left:{bw} solid {border_color}; '
        f'padding:{SPACE["lg"]} {SPACE["xl"]}; '
        f'border-radius:{r["md"]}; '
        f'border-top-left-radius:0; '
        f'border-bottom-left-radius:0; '
        f'margin-top:{margin_top};">'
        f'<span style="'
        f'color:{label_color}; '
        f'font-weight:{f["weight_bold"]}; '
        f'font-size:{f["size_sm"]}; '
        f'text-transform:{f["transform_upper"]}; '
        f'letter-spacing:{f["tracking_wide"]};">'
        f'{label_text}'
        f'</span>'
        f'<br><span style="'
        f'color:{c["text_primary"]}; '
        f'font-size:{f["size_display"]}; '
        f'font-weight:{f["weight_black"]};">'
        f'{value_text}'
        f'</span>'
        f'<br><span style="'
        f'color:{c["text_secondary"]}; '
        f'font-size:{f["size_body"]};">'
        f'{body_text}'
        f'</span>'
        f'</div>'
    )


def status_danger(value_text: str, body_text: str, **kwargs) -> str:
    """Status card merah — runway kritis / saldo minus."""
    c = COLOR
    return _status_card(
        bg=c["danger_bg"],
        border_color=c["danger_border"],
        label_color=c["danger_text"],
        label_text="⚠️ KRITIS",
        value_text=value_text,
        body_text=body_text,
        css_class="afp-status-danger",
        **kwargs,
    )


def status_warning(value_text: str, body_text: str, **kwargs) -> str:
    """Status card kuning — runway mulai menipis."""
    c = COLOR
    return _status_card(
        bg=c["warning_bg"],
        border_color=c["warning_border"],
        label_color=c["warning_text"],
        label_text="⚠️ HATI-HATI",
        value_text=value_text,
        body_text=body_text,
        css_class="afp-status-warning",
        **kwargs,
    )


def status_success(value_text: str, body_text: str, **kwargs) -> str:
    """Status card hijau — runway aman."""
    c = COLOR
    return _status_card(
        bg=c["success_bg"],
        border_color=c["success_border"],
        label_color=c["success_text"],
        label_text="✅ AMAN",
        value_text=value_text,
        body_text=body_text,
        css_class="afp-status-success",
        **kwargs,
    )


def empty_state(
    icon: str,
    title: str,
    body: str,
    variant: str = "success",
) -> str:
    """
    Empty state card dengan icon, judul, dan deskripsi.

    variant: "success" | "warning" | "info"
    """
    c = COLOR
    variant_map = {
        "success": (c["success_bg"],  c["success_border"], "afp-status-success"),
        "warning": (c["warning_bg"],  c["warning_border"], "afp-status-warning"),
        "info":    (c["info_bg"],     c["info_border"],    "afp-status-info"),
    }
    bg, border, css_class = variant_map.get(variant, variant_map["success"])
    f = FONT
    r = RADIUS
    bw = BORDER["accent_width"]

    return (
        f'<div class="{css_class}" style="'
        f'background:{bg}; '
        f'border-left:{bw} solid {border}; '
        f'border-radius:{r["md"]}; '
        f'border-top-left-radius:0; '
        f'border-bottom-left-radius:0; '
        f'padding:{SPACE["xl"]}; '
        f'text-align:center;">'
        f'<div style="font-size:2rem; margin-bottom:{SPACE["sm"]};">{icon}</div>'
        f'<div style="'
        f'color:{c["text_primary"]}; '
        f'font-weight:{f["weight_bold"]}; '
        f'font-size:{f["size_md"]}; '
        f'margin-bottom:{SPACE["xs"]};">'
        f'{title}'
        f'</div>'
        f'<div style="'
        f'color:{c["text_secondary"]}; '
        f'font-size:{f["size_body"]};">'
        f'{body}'
        f'</div>'
        f'</div>'
    )


def envelope_card(
    name: str,
    allocated_amount: float,
    percentage: float,
    color: dict,
) -> str:
    """
    Card untuk satu amplop virtual.
    color dict: {"bg": str, "bar": str, "text": str}
    """
    f = FONT
    r = RADIUS
    bw = BORDER["accent_width"]
    c = COLOR

    return (
        f'<div class="afp-envelope-card" style="'
        f'background:{color["bg"]}; '
        f'border-left:{bw} solid {color["bar"]}; '
        f'border-radius:{r["md"]}; '
        f'border-top-left-radius:0; '
        f'border-bottom-left-radius:0; '
        f'padding:{SPACE["md"]} {SPACE["xl"]}; '
        f'margin-bottom:{SPACE["md"]};">'

        f'<div style="display:flex; justify-content:space-between; align-items:center;">'
        f'<span style="color:{color["text"]}; font-weight:{f["weight_medium"]}; font-size:{f["size_body"]};">'
        f'{name}'
        f'</span>'
        f'<span style="color:{color["text"]}; font-weight:{f["weight_black"]}; font-size:{f["size_lg"]};">'
        f'Rp {allocated_amount:,.0f}'
        f'</span>'
        f'</div>'

        f'<div style="background:{c["surface_border"]}; border-radius:{r["sm"]}; height:8px; margin-top:{SPACE["sm"]}; overflow:hidden;">'
        f'<div style="background:{color["bar"]}; width:{int(percentage)}%; height:100%; border-radius:{r["sm"]};"></div>'
        f'</div>'

        f'<span style="'
        f'color:{c["text_secondary"]}; '
        f'font-size:{f["size_sm"]}; '
        f'text-transform:{f["transform_upper"]}; '
        f'letter-spacing:{f["tracking_wide"]};">'
        f'Alokasi {percentage}%'
        f'</span>'
        f'</div>'
    )


def hero_banner(title: str, subtitle: str) -> str:
    """
    Hero banner hijau di bagian atas halaman.
    Styling sepenuhnya dikelola oleh class .afp-hero di tokens.py
    sehingga responsive breakpoint otomatis berlaku.
    """
    return (
        f'<div class="afp-hero">'
        f'<h1>{title}</h1>'
        f'<p>{subtitle}</p>'
        f'</div>'
    )


def login_card(title: str, subtitle: str, prompt: str) -> str:
    """
    Card login terpusat untuk halaman PIN gate.
    Styling dikelola oleh class .afp-login-card di tokens.py.

    title    — nama aplikasi
    subtitle — tagline singkat
    prompt   — instruksi input PIN
    """
    return (
        f'<div class="afp-login-wrap">'
        f'<div class="afp-login-card">'
        f'<div class="afp-login-icon">💼</div>'
        f'<h1>{title}</h1>'
        f'<p class="afp-login-subtitle">{subtitle}</p>'
        f'<hr>'
        f'<p class="afp-login-prompt">{prompt}</p>'
        f'</div>'
        f'</div>'
    )


def section_gap() -> str:
    """
    Spacer antar section utama halaman.
    Ukuran diatur lewat class .afp-section-gap di tokens.py —
    otomatis menyesuaikan breakpoint mobile/tablet/desktop.

    Penggunaan:
        st.markdown(section_gap(), unsafe_allow_html=True)
    """
    return '<div class="afp-section-gap"></div>'