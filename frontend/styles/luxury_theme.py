"""
🎨 Luxury Design System - Premium Financial Analytics Theme

Colori palette luxury:
- Primary: Deep Blue (#0A1628) - Autorità, fiducia
- Accent Gold: (#D4AF37) - Lusso, prestigio
- Secondary: Slate Gray (#2D3748) - Eleganza
- Success: Emerald (#10B981) - Crescita
- Warning: Amber (#F59E0B) - Attenzione
- Error: Ruby (#EF4444) - Rischio

Typography:
- Heading: SF Pro Display / Inter (weight 700-800)
- Body: Inter (weight 400-500)
- Numbers: SF Mono / Roboto Mono (tabular nums)
"""

# ══════════════════════════════════════════════════════════════════════
# 🎨 COLOR PALETTE LUXURY
# ══════════════════════════════════════════════════════════════════════

COLORS = {
    # Primary Colors (DARK)
    "primary": "#0A1628",           # Deep navy blue
    "primary_light": "#1E293B",     # Lighter navy
    "primary_lighter": "#334155",   # Even lighter

    # Accent Colors
    "accent_gold": "#D4AF37",       # Luxury gold
    "accent_gold_light": "#F5E6C8", # Pale gold
    "accent_silver": "#C0C0C0",     # Silver

    # Semantic Colors
    "success": "#10B981",           # Emerald green
    "success_light": "#D1FAE5",     # Pale emerald
    "warning": "#F59E0B",           # Amber
    "warning_light": "#FEF3C7",     # Pale amber
    "error": "#EF4444",             # Ruby red
    "error_light": "#FEE2E2",       # Pale red
    "info": "#3B82F6",              # Blue
    "info_light": "#DBEAFE",        # Pale blue

    # Neutral Colors (DARK THEME)
    "white": "#FFFFFF",
    "gray_50": "#1F2937",           # DARK
    "gray_100": "#374151",          # DARK
    "gray_200": "#4B5563",          # DARK
    "gray_300": "#6B7280",          # DARK
    "gray_400": "#9CA3AF",
    "gray_500": "#D1D5DB",          # LIGHT for dark bg
    "gray_600": "#E5E7EB",          # LIGHT for dark bg
    "gray_700": "#F3F4F6",          # LIGHT for dark bg
    "gray_800": "#F9FAFB",          # LIGHT for dark bg
    "gray_900": "#FFFFFF",          # LIGHT for dark bg

    # Background (DARK THEME)
    "bg_primary": "#0A1628",        # Dark navy
    "bg_secondary": "#1E293B",      # Slightly lighter
    "bg_card": "#1E293B",           # Dark cards

    # Text (DARK THEME - inverted)
    "text_primary": "#FFFFFF",      # White text
    "text_secondary": "#E5E7EB",    # Light gray
    "text_tertiary": "#9CA3AF",     # Medium gray
}

# ══════════════════════════════════════════════════════════════════════
# 📊 CHART THEME LUXURY
# ══════════════════════════════════════════════════════════════════════

CHART_COLORS = [
    "#3B82F6",  # Blue
    "#10B981",  # Emerald
    "#F59E0B",  # Amber
    "#8B5CF6",  # Purple
    "#EF4444",  # Red
    "#06B6D4",  # Cyan
    "#EC4899",  # Pink
    "#84CC16",  # Lime
]

CHART_THEME_LUXURY = {
    "paper_bgcolor": "rgba(0,0,0,0)",           # Transparent
    "plot_bgcolor": "rgba(30,41,59,0.5)",       # Dark semi-transparent

    "font": {
        "family": "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        "size": 13,
        "color": "#E5E7EB",  # Light text for dark bg
    },

    "margin": {
        "l": 60,
        "r": 40,
        "t": 80,
        "b": 60,
    },

    "xaxis": {
        "showgrid": False,
        "gridcolor": COLORS["gray_200"],
        "gridwidth": 1,
        "zeroline": False,
        "linecolor": COLORS["gray_300"],
        "linewidth": 2,
        "tickfont": {
            "family": "Inter, sans-serif",
            "size": 11,
            "color": COLORS["text_secondary"],
        },
    },

    "yaxis": {
        "showgrid": True,
        "gridcolor": COLORS["gray_200"],
        "gridwidth": 1,
        "zeroline": False,
        "linecolor": COLORS["gray_300"],
        "linewidth": 2,
        "tickfont": {
            "family": "'SF Mono', 'Roboto Mono', monospace",
            "size": 11,
            "color": COLORS["text_secondary"],
        },
    },

    "legend": {
        "bgcolor": "rgba(255,255,255,0.9)",
        "bordercolor": COLORS["gray_200"],
        "borderwidth": 1,
        "font": {
            "family": "Inter, sans-serif",
            "size": 12,
            "color": COLORS["text_primary"],
        },
        "orientation": "h",
        "yanchor": "bottom",
        "y": 1.02,
        "xanchor": "right",
        "x": 1,
    },

    "hovermode": "x unified",
    "hoverlabel": {
        "bgcolor": "rgba(255,255,255,0.95)",
        "bordercolor": COLORS["gray_300"],
        "font": {
            "family": "Inter, sans-serif",
            "size": 12,
            "color": COLORS["text_primary"],
        },
    },
}

# ══════════════════════════════════════════════════════════════════════
# 🎨 CSS LUXURY STYLES
# ══════════════════════════════════════════════════════════════════════

LUXURY_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ═══════════════════════════════════════════════════════════════════
   🎨 GLOBAL STYLES
   ═══════════════════════════════════════════════════════════════════ */

:root {{
    --color-primary: {COLORS["primary"]};
    --color-accent-gold: {COLORS["accent_gold"]};
    --color-success: {COLORS["success"]};
    --color-warning: {COLORS["warning"]};
    --color-error: {COLORS["error"]};
    --color-info: {COLORS["info"]};

    --bg-primary: {COLORS["bg_primary"]};
    --bg-card: {COLORS["bg_card"]};

    --text-primary: {COLORS["text_primary"]};
    --text-secondary: {COLORS["text_secondary"]};
    --text-tertiary: {COLORS["text_tertiary"]};

    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);

    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 20px;
}}

/* Body */
body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: linear-gradient(135deg, #0A1628 0%, #1E293B 50%, #0F1A2D 100%);
    color: var(--text-primary);
}}

/* ═══════════════════════════════════════════════════════════════════
   📦 LUXURY CARDS
   ═══════════════════════════════════════════════════════════════════ */

.luxury-card {{
    background: var(--bg-card);
    border-radius: var(--radius-lg);
    padding: 28px 32px;
    box-shadow: var(--shadow-lg);
    border: 1px solid {COLORS["gray_200"]};
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(10px);
    background: linear-gradient(135deg,
        rgba(30,41,59,0.95) 0%,
        rgba(51,65,85,0.85) 100%);
}}

.luxury-card:hover {{
    box-shadow: var(--shadow-xl);
    transform: translateY(-2px);
    border-color: {COLORS["accent_gold"]};
}}

.luxury-card-compact {{
    background: var(--bg-card);
    border-radius: var(--radius-md);
    padding: 20px 24px;
    box-shadow: var(--shadow-md);
    border: 1px solid {COLORS["gray_200"]};
    transition: all 0.3s ease;
}}

/* ═══════════════════════════════════════════════════════════════════
   📊 METRIC CARDS
   ═══════════════════════════════════════════════════════════════════ */

.metric-card {{
    text-align: center;
    padding: 24px 20px;
    background: linear-gradient(135deg,
        rgba(30,41,59,0.95) 0%,
        rgba(51,65,85,0.85) 100%);
    border-radius: var(--radius-md);
    border: 1px solid {COLORS["gray_200"]};
    box-shadow: var(--shadow-md);
    transition: all 0.3s ease;
}}

.metric-card:hover {{
    box-shadow: var(--shadow-lg);
    transform: translateY(-1px);
}}

.metric-label {{
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-tertiary);
    margin-bottom: 8px;
}}

.metric-value {{
    font-size: 1.75rem;
    font-weight: 800;
    font-family: 'SF Mono', 'Roboto Mono', monospace;
    font-variant-numeric: tabular-nums;
    color: var(--text-primary);
    line-height: 1.2;
    margin-bottom: 4px;
}}

.metric-value-large {{
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--color-accent-gold) 0%, #B8860B 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

.metric-sublabel {{
    font-size: 0.8rem;
    color: var(--text-tertiary);
    font-weight: 500;
}}

/* ═══════════════════════════════════════════════════════════════════
   🏷️ BADGES & CHIPS
   ═══════════════════════════════════════════════════════════════════ */

.badge-luxury {{
    display: inline-block;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    box-shadow: var(--shadow-sm);
    border: 1px solid transparent;
    transition: all 0.2s ease;
}}

.badge-success {{
    background: linear-gradient(135deg, {COLORS["success"]} 0%, #059669 100%);
    color: white;
    border-color: {COLORS["success"]};
}}

.badge-warning {{
    background: linear-gradient(135deg, {COLORS["warning"]} 0%, #D97706 100%);
    color: white;
    border-color: {COLORS["warning"]};
}}

.badge-error {{
    background: linear-gradient(135deg, {COLORS["error"]} 0%, #DC2626 100%);
    color: white;
    border-color: {COLORS["error"]};
}}

.badge-gold {{
    background: linear-gradient(135deg, {COLORS["accent_gold"]} 0%, #B8860B 100%);
    color: {COLORS["primary"]};
    border-color: {COLORS["accent_gold"]};
    box-shadow: 0 4px 8px rgba(212, 175, 55, 0.3);
}}

/* ═══════════════════════════════════════════════════════════════════
   📈 CHART CONTAINERS
   ═══════════════════════════════════════════════════════════════════ */

.chart-container {{
    background: linear-gradient(135deg,
        rgba(30,41,59,0.95) 0%,
        rgba(51,65,85,0.85) 100%);
    border-radius: var(--radius-lg);
    padding: 24px;
    box-shadow: var(--shadow-lg);
    border: 1px solid {COLORS["gray_200"]};
    backdrop-filter: blur(10px);
    margin: 20px 0;
}}

.chart-title {{
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
}}

.chart-title::before {{
    content: "";
    width: 4px;
    height: 24px;
    background: linear-gradient(180deg, var(--color-accent-gold) 0%, #B8860B 100%);
    border-radius: 2px;
}}

/* ═══════════════════════════════════════════════════════════════════
   🎯 SECTION HEADERS
   ═══════════════════════════════════════════════════════════════════ */

.section-header {{
    font-size: 1.5rem;
    font-weight: 800;
    color: var(--text-primary);
    margin: 32px 0 20px 0;
    display: flex;
    align-items: center;
    gap: 12px;
}}

.section-header::before {{
    content: "";
    width: 6px;
    height: 32px;
    background: linear-gradient(180deg, var(--color-accent-gold) 0%, #B8860B 100%);
    border-radius: 3px;
    box-shadow: 0 2px 8px rgba(212, 175, 55, 0.4);
}}

/* ═══════════════════════════════════════════════════════════════════
   🔘 BUTTONS
   ═══════════════════════════════════════════════════════════════════ */

.btn-luxury {{
    background: linear-gradient(135deg, var(--color-accent-gold) 0%, #B8860B 100%);
    color: var(--color-primary);
    border: none;
    border-radius: var(--radius-md);
    padding: 14px 32px;
    font-size: 1rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    box-shadow: 0 4px 12px rgba(212, 175, 55, 0.4);
    cursor: pointer;
    transition: all 0.3s ease;
}}

.btn-luxury:hover {{
    box-shadow: 0 6px 16px rgba(212, 175, 55, 0.6);
    transform: translateY(-2px);
}}

.btn-luxury:active {{
    transform: translateY(0);
}}

/* ═══════════════════════════════════════════════════════════════════
   📊 TABLES
   ═══════════════════════════════════════════════════════════════════ */

.luxury-table {{
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    background: var(--bg-card);
    border-radius: var(--radius-md);
    overflow: hidden;
    box-shadow: var(--shadow-md);
}}

.luxury-table thead {{
    background: linear-gradient(135deg, {COLORS["primary"]} 0%, {COLORS["primary_light"]} 100%);
    color: white;
}}

.luxury-table thead th {{
    padding: 16px 20px;
    text-align: left;
    font-weight: 700;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

.luxury-table tbody tr {{
    border-bottom: 1px solid {COLORS["gray_200"]};
    transition: background 0.2s ease;
}}

.luxury-table tbody tr:hover {{
    background: {COLORS["gray_50"]};
}}

.luxury-table tbody td {{
    padding: 16px 20px;
    font-size: 0.95rem;
    color: var(--text-primary);
}}

/* ═══════════════════════════════════════════════════════════════════
   ⚡ ANIMATIONS
   ═══════════════════════════════════════════════════════════════════ */

@keyframes fadeInUp {{
    from {{
        opacity: 0;
        transform: translateY(20px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

.fade-in-up {{
    animation: fadeInUp 0.6s ease-out;
}}

@keyframes shimmer {{
    0% {{
        background-position: -1000px 0;
    }}
    100% {{
        background-position: 1000px 0;
    }}
}}

.shimmer {{
    background: linear-gradient(
        90deg,
        {COLORS["gray_100"]} 0%,
        {COLORS["gray_200"]} 50%,
        {COLORS["gray_100"]} 100%
    );
    background-size: 1000px 100%;
    animation: shimmer 2s infinite;
}}

/* ═══════════════════════════════════════════════════════════════════
   📱 RESPONSIVE
   ═══════════════════════════════════════════════════════════════════ */

@media (max-width: 768px) {{
    .luxury-card {{
        padding: 20px 24px;
    }}

    .metric-value {{
        font-size: 1.5rem;
    }}

    .metric-value-large {{
        font-size: 2rem;
    }}

    .section-header {{
        font-size: 1.25rem;
    }}
}}

</style>
"""


def get_luxury_css():
    """Restituisce il CSS luxury completo"""
    return LUXURY_CSS


def get_chart_theme():
    """Restituisce il tema Plotly luxury"""
    return CHART_THEME_LUXURY.copy()


def get_colors():
    """Restituisce la palette colori"""
    return COLORS.copy()
