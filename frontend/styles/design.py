"""
Design System - CSS Professionale per FinAnalyzer
Stile ispirato a TradingView / dashboard finanziarie professionali
"""

MAIN_CSS = """
<style>
/* ===== GOOGLE FONTS ===== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ===== ROOT VARIABLES (DARK THEME) ===== */
:root {
    --bg-primary: #0A1628;
    --bg-secondary: #1E293B;
    --card-bg: #1E293B;
    --card-shadow: 0 4px 24px rgba(0,0,0,0.30);
    --card-shadow-hover: 0 8px 32px rgba(0,0,0,0.40);
    --card-radius: 20px;
    --badge-radius: 50px;
    --blue-dark: #1a4f8a;
    --blue-mid:  #2471c8;
    --blue-light: #56a0e8;
    --teal:      #0ea5c9;
    --green:     #22c55e;
    --red:       #ef4444;
    --orange:    #f59e0b;
    --purple:    #8b5cf6;
    --text-dark: #FFFFFF;
    --text-mid:  #E5E7EB;
    --text-light: #9CA3AF;
    --border:    #334155;
}

/* ===== GLOBAL ===== */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

.main .block-container {
    padding: 1.5rem 2rem 3rem 2rem;
    max-width: 1400px;
}

/* ===== DARK THEME TEXT COLORS ===== */
/* Force ALL text to be white/light on dark background */

/* Headers - white */
.main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
    color: #FFFFFF !important;
}

/* All text elements - light gray */
.main p, .main span, .main label, .main div, .main li, .main a {
    color: #E5E7EB !important;
}

/* Streamlit markdown containers */
.main [data-testid="stMarkdownContainer"] h1,
.main [data-testid="stMarkdownContainer"] h2,
.main [data-testid="stMarkdownContainer"] h3 {
    color: #FFFFFF !important;
}

.main [data-testid="stMarkdownContainer"] p,
.main [data-testid="stMarkdownContainer"] span,
.main [data-testid="stMarkdownContainer"] div {
    color: #E5E7EB !important;
}

/* Streamlit widgets labels */
.stTextInput label,
.stSelectbox label,
.stCheckbox label,
.stRadio label,
.stNumberInput label,
.stTextArea label,
.stDateInput label,
.stTimeInput label {
    color: #E5E7EB !important;
    font-weight: 500 !important;
}

/* Input fields - white background with dark text */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
    color: #0A1628 !important;
    background: #FFFFFF !important;
}

.stSelectbox select {
    color: #0A1628 !important;
    background: #FFFFFF !important;
}

/* Markdown text */
.main .stMarkdown,
.main .stMarkdown p,
.main .stMarkdown span,
.main .stMarkdown div,
.main .stMarkdown li {
    color: #E5E7EB !important;
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
    color: #9CA3AF !important;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: #FFFFFF !important;
}

/* Buttons text (keep primary button readable) */
button[kind="primary"] {
    background: #2471c8 !important;
    color: #FFFFFF !important;
}

/* Info/warning/success boxes (keep dark text on colored bg) */
.main [data-testid="stAlert"] p,
.main [data-testid="stAlert"] span {
    color: #0A1628 !important;
}

/* ===== LIGHT BACKGROUND BOXES - FORCE DARK TEXT ===== */
/* Exception for light-colored info boxes with inline styles */
/* These boxes need DARK text (#0A1628) instead of light text */

/* Target divs with light backgrounds */
.main div[style*="background:#d1fae5"],
.main div[style*="background:#f0f9ff"],
.main div[style*="background:#fff3cd"],
.main div[style*="background:#fefce8"],
.main div[style*="background:#fef3c7"],
.main div[style*="background:#dbeafe"],
.main div[style*="background:#dcfce7"],
.main div[style*="background:#d1fae5;"],
.main div[style*="background:#f0f9ff;"],
.main div[style*="background:#fff3cd;"],
.main div[style*="background:#fefce8;"],
.main div[style*="background:#fef3c7;"],
.main div[style*="background:#dbeafe;"],
.main div[style*="background:#dcfce7;"] {
    color: #0A1628 !important;
}

/* Also target ALL children elements inside light boxes */
.main div[style*="background:#d1fae5"] *,
.main div[style*="background:#f0f9ff"] *,
.main div[style*="background:#fff3cd"] *,
.main div[style*="background:#fefce8"] *,
.main div[style*="background:#fef3c7"] *,
.main div[style*="background:#dbeafe"] *,
.main div[style*="background:#dcfce7"] *,
.main div[style*="background:#d1fae5;"] *,
.main div[style*="background:#f0f9ff;"] *,
.main div[style*="background:#fff3cd;"] *,
.main div[style*="background:#fefce8;"] *,
.main div[style*="background:#fef3c7;"] *,
.main div[style*="background:#dbeafe;"] *,
.main div[style*="background:#dcfce7;"] * {
    color: #0A1628 !important;
}

/* Keep Streamlit header visible for sidebar toggle */
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 3rem !important;
}
footer { display: none !important; }
#MainMenu { display: none !important; }

/* Style the sidebar toggle button */
button[kind="header"] {
    background: white !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
}
button[kind="header"]:hover {
    background: #f0f6fc !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
}

/* ===== BACKGROUND ===== */
.stApp {
    background: linear-gradient(135deg, #0A1628 0%, #1E293B 50%, #0F1A2D 100%);
    min-height: 100vh;
}

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1A3A5C 0%, #1E4464 50%, #224B6E 100%) !important;
    border-right: none !important;
}

section[data-testid="stSidebar"] .stRadio label,
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] li {
    color: #c8ddf5 !important;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #ffffff !important;
}

/* ===== MODERN MENU NAVIGATION ===== */
/* Hide default radio button circles */
section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label > div:first-child {
    display: none !important;
}

/* Style menu items */
section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label {
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    padding: 12px 16px !important;
    margin: 4px 0 !important;
    border-radius: 12px !important;
    cursor: pointer !important;
    color: #a8c8e8 !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    transition: all 0.25s ease !important;
    background: transparent !important;
    border-left: 3px solid transparent !important;
    position: relative !important;
}

/* Hover effect */
section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:hover {
    background: rgba(255,255,255,0.08) !important;
    color: #e0edf8 !important;
    transform: translateX(2px) !important;
}

/* Selected item with arrow */
section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label[data-checked="true"] {
    background: linear-gradient(90deg, rgba(255,255,255,0.18), rgba(255,255,255,0.10)) !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    border-left: 3px solid #22c55e !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
}

/* Arrow indicator on selected item */
section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label[data-checked="true"]::before {
    content: "▶" !important;
    position: absolute !important;
    left: 8px !important;
    font-size: 0.7rem !important;
    color: #22c55e !important;
    animation: pulse 2s ease-in-out infinite !important;
}

/* Pulse animation for arrow */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* Text content inside label */
section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label > div {
    color: inherit !important;
    padding-left: 8px !important;
}

/* ===== TOP HEADER ===== */
.app-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.5rem;
    padding: 0 0 1rem 0;
    border-bottom: 1px solid rgba(36,113,200,0.2);
}
.app-logo {
    font-size: 1.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #1a4f8a, #2471c8, #0ea5c9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.5px;
}
.app-subtitle {
    color: var(--text-light);
    font-size: 0.85rem;
    font-weight: 400;
    margin-top: 2px;
}

/* ===== SECTION BADGE ===== */
.section-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 22px;
    border-radius: var(--badge-radius);
    font-size: 1.05rem;
    font-weight: 700;
    letter-spacing: 0.3px;
    margin-bottom: 1.2rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.10);
}
.badge-blue    { background: linear-gradient(135deg, #1a4f8a, #2471c8); color: #fff; }
.badge-teal    { background: linear-gradient(135deg, #0284c7, #0ea5c9); color: #fff; }
.badge-green   { background: linear-gradient(135deg, #15803d, #22c55e); color: #fff; }
.badge-purple  { background: linear-gradient(135deg, #6d28d9, #8b5cf6); color: #fff; }
.badge-orange  { background: linear-gradient(135deg, #b45309, #f59e0b); color: #fff; }
.badge-dark    { background: linear-gradient(135deg, #0f172a, #1e3a5f); color: #fff; }

/* ===== CARDS ===== */
.fin-card {
    background: var(--card-bg);
    border-radius: var(--card-radius);
    box-shadow: var(--card-shadow);
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.2rem;
    transition: box-shadow 0.25s;
    border: 1px solid rgba(180,210,240,0.4);
}
.fin-card:hover {
    box-shadow: var(--card-shadow-hover);
}
.fin-card-title {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: var(--text-light);
    margin-bottom: 6px;
}
.fin-card-value {
    font-size: 1.8rem;
    font-weight: 800;
    color: var(--text-dark);
    line-height: 1.1;
}
.fin-card-delta {
    font-size: 0.85rem;
    font-weight: 600;
    margin-top: 4px;
}
.delta-pos { color: var(--green); }
.delta-neg { color: var(--red); }
.delta-neu { color: var(--text-light); }

/* ===== METRIC RING CARDS (Seasonality style) ===== */
.ring-metric {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 14px;
    background: var(--card-bg);
    border-radius: 16px;
    box-shadow: var(--card-shadow);
    text-align: center;
}
.ring-label { font-size: 0.7rem; font-weight: 600; color: var(--text-light); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
.ring-value { font-size: 1rem; font-weight: 800; color: var(--text-dark); }
.ring-sub   { font-size: 0.75rem; font-weight: 500; margin-top: 2px; }

/* ===== TABLES ===== */
.fin-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 0.82rem;
}
.fin-table thead tr th {
    background: #f0f6fc;
    color: var(--text-light);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 10px 12px;
    border-bottom: 2px solid var(--border);
    font-size: 0.72rem;
}
.fin-table tbody tr {
    border-bottom: 1px solid var(--border);
    transition: background 0.15s;
}
.fin-table tbody tr:hover { background: #f5f9ff; }
.fin-table tbody td {
    padding: 9px 12px;
    color: var(--text-mid);
    vertical-align: middle;
}
.rank-num {
    font-weight: 700;
    color: var(--text-light);
    font-size: 0.78rem;
}

/* ===== CHIPS / TAGS ===== */
.chip {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 50px;
    font-size: 0.72rem;
    font-weight: 600;
}
.chip-green  { background: #dcfce7; color: #15803d; }
.chip-red    { background: #fee2e2; color: #b91c1c; }
.chip-blue   { background: #dbeafe; color: #1d4ed8; }
.chip-orange { background: #fef3c7; color: #b45309; }
.chip-gray   { background: #f3f4f6; color: #4b5563; }
.chip-purple { background: #ede9fe; color: #6d28d9; }

/* ===== SEARCH BAR ===== */
.stTextInput > div > div > input {
    border-radius: 12px !important;
    border: 1.5px solid var(--border) !important;
    padding: 10px 16px !important;
    font-size: 0.9rem !important;
    background: white !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--blue-mid) !important;
    box-shadow: 0 0 0 3px rgba(36,113,200,0.15) !important;
}

/* ===== BUTTONS ===== */
.stButton > button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px !important;
    padding: 0.5rem 1.4rem !important;
    transition: all 0.2s !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1a4f8a, #2471c8) !important;
    border: none !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(36,113,200,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 16px rgba(36,113,200,0.4) !important;
}

/* ===== SELECTBOX ===== */
.stSelectbox > div > div {
    border-radius: 12px !important;
    border: 1.5px solid var(--border) !important;
    background: white !important;
}

/* ===== TABS ===== */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.6);
    border-radius: 14px;
    padding: 4px;
    gap: 4px;
    border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    font-weight: 600;
    font-size: 0.85rem;
    color: var(--text-light) !important;
    padding: 8px 18px;
    transition: all 0.2s;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: var(--blue-dark) !important;
    box-shadow: 0 2px 8px rgba(36,113,200,0.15);
}

/* ===== EXPANDER ===== */
.streamlit-expanderHeader {
    border-radius: 12px !important;
    background: rgba(255,255,255,0.7) !important;
    font-weight: 600 !important;
    border: 1px solid var(--border) !important;
}

/* ===== PLOTLY CHARTS ===== */
.js-plotly-plot {
    border-radius: 16px;
}

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(36,113,200,0.3); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: rgba(36,113,200,0.5); }

/* ===== STREAMLIT METRIC OVERRIDE ===== */
[data-testid="metric-container"] {
    background: white;
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 14px 18px;
    box-shadow: var(--card-shadow);
}
[data-testid="metric-container"] label {
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    color: var(--text-light) !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
    font-weight: 800 !important;
    color: var(--text-dark) !important;
}

/* ===== DIVIDERS ===== */
hr {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.5rem 0;
}

/* ===== DATAFRAME STYLE ===== */
[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid var(--border);
}

/* ===== SPINNER ===== */
.stSpinner > div {
    border-color: var(--blue-mid) transparent transparent transparent !important;
}

/* ===== WARNINGS / INFO ===== */
.stAlert {
    border-radius: 12px !important;
    border-left-width: 4px !important;
}
</style>
"""


def badge(label: str, icon: str = "", color: str = "blue") -> str:
    """Genera un badge HTML per i titoli di sezione"""
    cls = f"badge-{color}"
    ico = f"{icon} " if icon else ""
    return f'<div class="section-badge {cls}">{ico}{label}</div>'


def card_metric(title: str, value: str, delta: str = "", delta_pos: bool = True, icon: str = "") -> str:
    """Card metrica singola"""
    delta_cls = "delta-pos" if delta_pos else "delta-neg"
    delta_html = f'<div class="fin-card-delta {delta_cls}">{delta}</div>' if delta else ""
    return f"""
    <div class="fin-card" style="text-align:center;">
        <div class="fin-card-title">{icon} {title}</div>
        <div class="fin-card-value">{value}</div>
        {delta_html}
    </div>
    """


def color_pct(value: float, decimals: int = 2) -> str:
    """Restituisce HTML colorato per percentuali"""
    sign = "+" if value >= 0 else ""
    cls = "delta-pos" if value >= 0 else "delta-neg"
    return f'<span class="{cls}" style="font-weight:600;">{sign}{value:.{decimals}f}%</span>'


def chip(text: str, color: str = "blue") -> str:
    """Chip/badge colorato"""
    return f'<span class="chip chip-{color}">{text}</span>'


def stars(n: int) -> str:
    """Stelle Morningstar"""
    full = "★" * min(n, 5)
    empty = "☆" * (5 - min(n, 5))
    return f'<span style="color:#f59e0b;font-size:1rem;">{full}</span><span style="color:#d1d5db;">{empty}</span>'
