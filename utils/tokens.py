# ============================================================
# DESIGN TOKENS — ARSITEK FINANSIAL PRIBADI
# Single source of truth untuk semua nilai visual.
# Ubah di sini → berlaku di seluruh aplikasi.
# ============================================================

# ── COLOR PRIMITIVES ────────────────────────────────────────
# Warna dasar brand. Jangan dipakai langsung di komponen —
# gunakan semantic aliases di bawah.

_green_dark   = "#1a2e1a"
_green_base   = "#2d6a4f"
_green_mid    = "#40916c"
_green_light  = "#f0fdf4"

_amber_base   = "#d97706"
_amber_light  = "#fffbeb"

_red_base     = "#dc2626"
_red_light    = "#fef2f2"

_blue_base    = "#0284c7"
_blue_light   = "#f0f9ff"

_text_primary   = "#1a1a2e"
_text_secondary = "#6b7280"
_text_white     = "#ffffff"
_text_mint      = "#A7F3D0"   # dipakai di hero banner subtitle

_surface_page   = "#f8f6f2"
_surface_border = "#e5e1d8"

# ── SEMANTIC COLOR ALIASES ──────────────────────────────────
# Gunakan nama ini di komponen — bukan primitive di atas.

COLOR = {
    # Brand
    "brand_dark":    _green_dark,
    "brand_base":    _green_base,
    "brand_mid":     _green_mid,
    "brand_light":   _green_light,

    # Status — success
    "success_bg":    _green_light,
    "success_border": _green_base,
    "success_text":  _green_base,

    # Status — warning
    "warning_bg":    _amber_light,
    "warning_border": _amber_base,
    "warning_text":  _amber_base,

    # Status — danger
    "danger_bg":     _red_light,
    "danger_border": _red_base,
    "danger_text":   _red_base,

    # Status — info
    "info_bg":       _blue_light,
    "info_border":   _blue_base,
    "info_text":     _blue_base,

    # Text
    "text_primary":   _text_primary,
    "text_secondary": _text_secondary,
    "text_white":     _text_white,
    "text_mint":      _text_mint,

    # Surface
    "surface_page":   _surface_page,
    "surface_border": _surface_border,

    # Sidebar
    "sidebar_bg":    _green_dark,
}

# ── TYPOGRAPHY ───────────────────────────────────────────────

FONT = {
    "size_xs":     "11px",
    "size_sm":     "12px",
    "size_body":   "14px",
    "size_md":     "16px",
    "size_lg":     "18px",
    "size_display": "32px",

    "weight_normal": "400",
    "weight_medium": "600",
    "weight_bold":   "700",
    "weight_black":  "800",

    "transform_upper": "uppercase",
    "tracking_wide":   "0.05em",
    "line_height":     "1.5",
}

# ── SPACING ──────────────────────────────────────────────────

SPACE = {
    "xs":  "4px",
    "sm":  "8px",
    "md":  "16px",
    "lg":  "20px",
    "xl":  "24px",
    "2xl": "32px",
    "3xl": "48px",
}

# ── SHAPE ────────────────────────────────────────────────────

RADIUS = {
    "sm":  "4px",
    "md":  "8px",
    "lg":  "12px",
}

BORDER = {
    "accent_width": "4px",   # border-left pada status card
    "default":      "1px",
}

# ── ENVELOPE COLORS ──────────────────────────────────────────
# Palet untuk virtual_envelopes — urutan dipertahankan.

ENVELOPE_PALETTE = [
    {"bg": _green_light,  "bar": _green_base, "text": _text_primary},
    {"bg": "#ECFDF5",     "bar": "#059669",   "text": "#064E3B"},
    {"bg": "#EFF6FF",     "bar": "#3B82F6",   "text": "#1E3A5F"},
    {"bg": "#FFF7ED",     "bar": "#EA580C",   "text": "#9A3412"},
    {"bg": "#FAF5FF",     "bar": "#9333EA",   "text": "#581C87"},
    {"bg": "#FDF2F8",     "bar": "#DB2777",   "text": "#9D174D"},
]

# ── CHART PALETTE ─────────────────────────────────────────────
# Dipakai oleh spending_chart.py — tetap dalam ramp hijau brand.

CHART_PALETTE_EXPENSE = [
    "#2d6a4f", "#40916c", "#52b788", "#74c69d",
    "#95d5b2", "#b7e4c7", "#d8f3dc",
]

CHART_PALETTE_INCOME = [
    "#1a2e1a", "#2d4a2d", "#3d6b3d", "#4d8b4d",
    "#63a663", "#7fbf7f", "#a3d9a3",
]


# ============================================================
# CSS INJECTION
# Panggil inject_css() sekali di app.py — menggantikan blok
# <style> yang ada saat ini. Semua token di atas otomatis
# tersinkron dengan CSS variables di :root.
# ============================================================

def get_css() -> str:
    """
    Mengembalikan string CSS lengkap yang siap di-inject via
    st.markdown(..., unsafe_allow_html=True).

    Semua nilai berasal dari token di atas — tidak ada
    hardcoded string di dalam CSS ini.
    """
    c = COLOR
    f = FONT
    s = SPACE
    r = RADIUS

    return f"""
    <style>
    /* ── CSS VARIABLES (generated from tokens.py) ─────── */
    :root {{
        --color-brand-dark:    {c['brand_dark']};
        --color-brand-base:    {c['brand_base']};
        --color-brand-mid:     {c['brand_mid']};
        --color-brand-light:   {c['brand_light']};

        --color-success-bg:     {c['success_bg']};
        --color-success-border: {c['success_border']};
        --color-success-text:   {c['success_text']};

        --color-warning-bg:     {c['warning_bg']};
        --color-warning-border: {c['warning_border']};
        --color-warning-text:   {c['warning_text']};

        --color-danger-bg:      {c['danger_bg']};
        --color-danger-border:  {c['danger_border']};
        --color-danger-text:    {c['danger_text']};

        --color-info-bg:        {c['info_bg']};
        --color-info-border:    {c['info_border']};
        --color-info-text:      {c['info_text']};

        --color-text-primary:   {c['text_primary']};
        --color-text-secondary: {c['text_secondary']};
        --color-text-white:     {c['text_white']};

        --color-surface-page:   {c['surface_page']};
        --color-surface-border: {c['surface_border']};
        --color-sidebar-bg:     {c['sidebar_bg']};

        --font-size-xs:      {f['size_xs']};
        --font-size-sm:      {f['size_sm']};
        --font-size-body:    {f['size_body']};
        --font-size-md:      {f['size_md']};
        --font-size-lg:      {f['size_lg']};
        --font-size-display: {f['size_display']};

        --font-weight-normal: {f['weight_normal']};
        --font-weight-medium: {f['weight_medium']};
        --font-weight-bold:   {f['weight_bold']};
        --font-weight-black:  {f['weight_black']};

        --space-xs:  {s['xs']};
        --space-sm:  {s['sm']};
        --space-md:  {s['md']};
        --space-lg:  {s['lg']};
        --space-xl:  {s['xl']};
        --space-2xl: {s['2xl']};
        --space-3xl: {s['3xl']};

        --radius-sm: {r['sm']};
        --radius-md: {r['md']};
        --radius-lg: {r['lg']};
        --radius-xl: 16px;
    }}

    /* ── HIDE STREAMLIT DEFAULTS ───────────────────────── */
    #MainMenu {{visibility: hidden;}}
    .stAppDeployButton {{display: none;}}
    footer {{visibility: hidden;}}
    .block-container {{
        padding-top: 1rem;
        padding-bottom: 2rem;
        padding-left: var(--space-2xl) !important;
        padding-right: var(--space-2xl) !important;
    }}

    /* ── SIDEBAR ───────────────────────────────────────── */
    [data-testid="stSidebar"] {{
        background-color: var(--color-sidebar-bg) !important;
    }}
    [data-testid="stSidebar"] * {{
        color: var(--color-text-white) !important;
    }}
    [data-testid="stSidebar"] label {{
        color: rgba(255, 255, 255, 0.8) !important;
        font-size: var(--font-size-body) !important;
    }}
    [data-testid="stSidebar"] .stSelectbox > div > div {{
        border: 1px solid var(--color-brand-mid) !important;
        background-color: rgba(255, 255, 255, 0.08) !important;
        color: var(--color-text-white) !important;
    }}
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {{
        color: var(--color-text-white) !important;
        font-weight: var(--font-weight-bold) !important;
    }}
    /* ── Input fields di sidebar — selector dari DevTools ── */
    [data-testid="stSidebar"] [data-testid="stNumberInputField"],
    [data-testid="stSidebar"] [data-testid="stDateInput"] input,
    [data-testid="stSidebar"] [data-testid="stTextInput"] input,
    [data-testid="stSidebar"] input[type="number"],
    [data-testid="stSidebar"] input[type="text"],
    [data-testid="stSidebar"] input[type="date"] {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: {c['text_primary']} !important;
        border: 1px solid var(--color-brand-mid) !important;
    }}
    /* ── Tombol +/- number input selalu terlihat ────────── */
    [data-testid="stSidebar"] [data-testid="stNumberInput"] button {{
        opacity: 1 !important;
        visibility: visible !important;
        background-color: rgba(255, 255, 255, 0.9) !important;
    }}
    [data-testid="stSidebar"] [data-testid="stNumberInput"] button p,
    [data-testid="stSidebar"] [data-testid="stNumberInput"] button svg {{
        opacity: 1 !important;
        color: {c['text_primary']} !important;
        fill: {c['text_primary']} !important;
    }}

    /* ── BUTTONS ───────────────────────────────────────── */
    .stButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primary"],
    .stButton > button[data-testid="stBaseButton-primary"],
    .stFormSubmitButton > button[data-testid="stBaseButton-primary"] {{
        background-color: var(--color-brand-base) !important;
        color: var(--color-text-white) !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        padding: 12px 24px !important;
        font-weight: var(--font-weight-medium) !important;
        transition: background-color 0.2s ease !important;
    }}
    .stButton > button[kind="primary"]:hover,
    .stFormSubmitButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="stBaseButton-primary"]:hover,
    .stFormSubmitButton > button[data-testid="stBaseButton-primary"]:hover {{
        background-color: var(--color-brand-mid) !important;
        color: var(--color-text-white) !important;
    }}
    .stButton > button[kind="secondary"],
    .stButton > button[data-testid="stBaseButton-secondary"] {{
        background-color: transparent !important;
        color: var(--color-brand-base) !important;
        border: 1px solid var(--color-brand-base) !important;
        border-radius: var(--radius-md) !important;
        font-weight: var(--font-weight-medium) !important;
        transition: background-color 0.2s ease !important;
    }}
    .stButton > button[kind="secondary"]:hover,
    .stButton > button[data-testid="stBaseButton-secondary"]:hover {{
        background-color: var(--color-brand-light) !important;
    }}

    /* ── CARDS ─────────────────────────────────────────── */
    [data-testid="stExpander"],
    [data-testid="stVerticalBlockBorderWrapper"][data-testid] {{
        border: 1px solid var(--color-surface-border) !important;
        border-radius: var(--radius-lg) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
        padding: 20px !important;
    }}

    /* ── TYPOGRAPHY ────────────────────────────────────── */
    h2, .stSubheader {{
        font-size: 24px !important;
        font-weight: var(--font-weight-bold) !important;
        color: var(--color-text-primary) !important;
    }}
    h3 {{
        font-size: var(--font-size-lg) !important;
        font-weight: var(--font-weight-medium) !important;
        color: var(--color-text-primary) !important;
    }}
    [data-testid="stMetricValue"] {{
        font-size: var(--font-size-display) !important;
        font-weight: var(--font-weight-black) !important;
        letter-spacing: -0.02em !important;
        color: var(--color-text-primary) !important;
    }}
    [data-testid="stMetricLabel"] {{
        font-size: var(--font-size-sm) !important;
        font-weight: var(--font-weight-medium) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        color: var(--color-text-secondary) !important;
    }}
    .stCaption, [data-testid="stCaptionContainer"] {{
        font-size: var(--font-size-sm) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        color: var(--color-text-secondary) !important;
    }}
    .stMarkdown p {{
        font-size: var(--font-size-body);
        color: var(--color-text-secondary);
    }}
    .stMarkdown strong {{
        color: var(--color-text-primary);
    }}

    /* ── DATAFRAME ─────────────────────────────────────── */
    [data-testid="stDataFrame"] {{
        border-radius: var(--radius-md);
        overflow: hidden;
    }}

    /* ── LOGIN CARD ────────────────────────────────────── */
    .afp-login-wrap {{
        max-width: 480px;
        margin: 60px auto 0 auto;
    }}
    .afp-login-card {{
        background: var(--color-background-primary, #ffffff);
        border: 1px solid var(--color-surface-border);
        border-radius: var(--radius-xl, 16px);
        padding: 40px;
        text-align: center;
    }}
    .afp-login-card h1 {{
        margin: 0;
        font-size: 24px;
        font-weight: var(--font-weight-black);
        color: var(--color-text-primary);
        letter-spacing: -0.03em;
    }}
    .afp-login-card .afp-login-subtitle {{
        color: var(--color-text-secondary);
        font-size: var(--font-size-body);
        margin: var(--space-sm) 0 var(--space-xl) 0;
        font-weight: var(--font-weight-normal);
    }}
    .afp-login-card hr {{
        border: none;
        border-top: 1px solid var(--color-surface-border);
        margin: 0 0 var(--space-xl) 0;
    }}
    .afp-login-card .afp-login-prompt {{
        color: var(--color-text-secondary);
        font-size: var(--font-size-body);
        margin-bottom: var(--space-md);
    }}
    .afp-login-icon {{
        font-size: 4rem;
        margin-bottom: var(--space-sm);
    }}

    /* ── HERO BANNER ───────────────────────────────────── */
    .afp-hero {{
        background: linear-gradient(135deg, var(--color-brand-dark), var(--color-brand-base));
        padding: var(--space-2xl) 36px;
        border-radius: var(--radius-lg);
        margin-bottom: var(--space-3xl);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }}
    .afp-hero h1 {{
        color: var(--color-text-white);
        margin: 0;
        font-size: 24px;
        font-weight: var(--font-weight-bold);
        letter-spacing: -0.025em;
    }}
    .afp-hero p {{
        color: {c['text_mint']};
        margin: var(--space-sm) 0 0 0;
        font-size: var(--font-size-body);
        line-height: 1.5;
    }}

    /* ── SECTION SPACER ────────────────────────────────── */
    .afp-section-gap {{
        margin-top: var(--space-3xl);
    }}

    /* ── RESPONSIVE ────────────────────────────────────── */
    @media (max-width: 768px) {{
        .afp-hero {{
            padding: var(--space-xl) var(--space-md);
            margin-bottom: var(--space-2xl);
            border-radius: var(--radius-md);
        }}
        .afp-hero h1 {{
            font-size: 20px;
        }}
        .afp-section-gap {{
            margin-top: var(--space-2xl);
        }}
    }}
    @media (max-width: 480px) {{
        .block-container {{
            padding-left: var(--space-md) !important;
            padding-right: var(--space-md) !important;
        }}
        .afp-hero {{
            padding: var(--space-md);
            margin-bottom: var(--space-xl);
        }}
        .afp-hero h1 {{
            font-size: 18px;
        }}
        .afp-hero p {{
            font-size: var(--font-size-sm);
        }}
        .afp-section-gap {{
            margin-top: var(--space-xl);
        }}
        [data-testid="stMetricValue"] {{
            font-size: 24px !important;
        }}
        h2, .stSubheader {{
            font-size: 20px !important;
        }}
    }}
    /* ── DARK MODE — prefers-color-scheme: dark ───────────
       Override semua CSS variables dan class kustom.
       Komponen native Streamlit ikut otomatis via var().
       ──────────────────────────────────────────────────── */
    @media (prefers-color-scheme: dark) {{

        /* ── Variables ── */
        :root {{
            --color-brand-dark:    #0d1f0d;
            --color-brand-base:    #52b788;
            --color-brand-mid:     #74c69d;
            --color-brand-light:   #1b3a2d;

            --color-success-bg:     #1b3a2d;
            --color-success-border: #52b788;
            --color-success-text:   #74c69d;

            --color-warning-bg:     #2d2008;
            --color-warning-border: #f59e0b;
            --color-warning-text:   #fbbf24;

            --color-danger-bg:      #2d0f0f;
            --color-danger-border:  #f87171;
            --color-danger-text:    #fca5a5;

            --color-info-bg:        #0c1f2d;
            --color-info-border:    #38bdf8;
            --color-info-text:      #7dd3fc;

            --color-text-primary:   #e8e6e0;
            --color-text-secondary: #9ca3af;
            --color-text-white:     #ffffff;

            --color-surface-page:   #0f1117;
            --color-surface-border: #2d2d2d;
            --color-sidebar-bg:     #0d1f0d;
        }}

        /* ── Metric & typography ── */
        [data-testid="stMetricValue"] {{
            color: var(--color-text-primary) !important;
        }}
        [data-testid="stMetricLabel"],
        .stCaption, [data-testid="stCaptionContainer"] {{
            color: var(--color-text-secondary) !important;
        }}
        h2, .stSubheader, h3 {{
            color: var(--color-text-primary) !important;
        }}
        .stMarkdown p {{
            color: var(--color-text-secondary);
        }}
        .stMarkdown strong {{
            color: var(--color-text-primary);
        }}

        /* ── Cards & borders ── */
        [data-testid="stExpander"],
        [data-testid="stVerticalBlockBorderWrapper"][data-testid] {{
            border-color: var(--color-surface-border) !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
        }}

        /* ── Buttons ── */
        .stButton > button[kind="secondary"],
        .stButton > button[data-testid="stBaseButton-secondary"] {{
            color: var(--color-brand-mid) !important;
            border-color: var(--color-brand-mid) !important;
        }}
        .stButton > button[kind="secondary"]:hover,
        .stButton > button[data-testid="stBaseButton-secondary"]:hover {{
            background-color: var(--color-brand-light) !important;
        }}

        /* ── Login card ── */
        .afp-login-card {{
            background: #161b22;
            border-color: var(--color-surface-border);
        }}
        .afp-login-card h1 {{
            color: var(--color-text-primary);
        }}
        .afp-login-card hr {{
            border-top-color: var(--color-surface-border);
        }}

        /* ── Status cards (border-left accent) ── */
        /* Background dan border sudah via inline style dari ui.py
           yang membaca COLOR dict — override lewat var() di atas
           cukup untuk border. Background perlu class tambahan. */
        .afp-status-success {{
            background: var(--color-success-bg) !important;
            border-left-color: var(--color-success-border) !important;
        }}
        .afp-status-warning {{
            background: var(--color-warning-bg) !important;
            border-left-color: var(--color-warning-border) !important;
        }}
        .afp-status-danger {{
            background: var(--color-danger-bg) !important;
            border-left-color: var(--color-danger-border) !important;
        }}
        .afp-status-info {{
            background: var(--color-info-bg) !important;
            border-left-color: var(--color-info-border) !important;
        }}

        /* ── Envelope cards ── */
        .afp-envelope-card {{
            filter: brightness(0.85) saturate(0.9);
        }}

        /* ── Hero banner — lebih gelap di dark mode ── */
        .afp-hero {{
            background: linear-gradient(135deg, #0d1f0d, #1b3a2d);
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        }}
    }}
    </style>
    """


def inject_css() -> None:
    """Shortcut: inject CSS langsung ke Streamlit."""
    import streamlit as st
    st.markdown(get_css(), unsafe_allow_html=True)