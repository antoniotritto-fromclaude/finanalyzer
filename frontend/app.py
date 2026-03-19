"""
FinAnalyzer Pro – Piattaforma di Analisi Finanziaria Professionale
"""
# ── Fix multitasking PRIMA di tutto ──────────────────────────────────────────
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    import fix_multitasking  # noqa
except Exception:
    pass

import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinAnalyzer Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

from frontend.styles.design import MAIN_CSS
st.markdown(MAIN_CSS, unsafe_allow_html=True)

# ── Import pagine ─────────────────────────────────────────────────────────────
from frontend.views import dashboard, screener, fundamentals, portfolio, backtest, predictions

# ── Sidebar Navigation ────────────────────────────────────────────────────────
with st.sidebar:
    # Logo
    st.markdown("""
    <div style="padding:16px 8px 8px 8px;text-align:center;">
        <div style="font-size:1.6rem;font-weight:900;color:#ffffff;letter-spacing:-0.5px;">
            FinAnalyzer Pro
        </div>
        <div style="font-size:0.72rem;color:#7fb3d3;margin-top:2px;letter-spacing:0.5px;">
            PIATTAFORMA DI ANALISI FINANZIARIA
        </div>
    </div>
    <hr style="border-color:rgba(255,255,255,0.1);margin:10px 0 16px 0;">
    """, unsafe_allow_html=True)

    # Navigation
    st.markdown("""
    <div style="font-size:0.68rem;font-weight:700;color:#7fb3d3;text-transform:uppercase;
                letter-spacing:0.8px;margin-bottom:8px;padding:0 4px;">Menu Principale</div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigazione",
        options=[
            "🏠 Dashboard",
            "🔍 Screener",
            "📊 Analisi Titolo",
            "💼 Portafoglio",
            "📈 Backtest",
            "🔮 Predizioni",
        ],
        label_visibility="collapsed",
    )

    st.markdown("<hr style='border-color:rgba(255,255,255,0.1);margin:16px 0;'>", unsafe_allow_html=True)

    # Fonti dati
    st.markdown("""
    <div style="padding:0 4px;">
        <div style="font-size:0.68rem;font-weight:700;color:#7fb3d3;text-transform:uppercase;
                    letter-spacing:0.8px;margin-bottom:8px;">Fonti Dati</div>
    """, unsafe_allow_html=True)

    sources = [
        ("📈", "Yahoo Finance", "#22c55e"),
        ("🌐", "Morningstar IT", "#22c55e"),
        ("📡", "JustETF", "#22c55e"),
        ("📊", "Quantalys", "#22c55e"),
        ("💹", "Investing.com", "#22c55e"),
        ("📉", "TradingView", "#22c55e"),
        ("🎯", "FINVIZ", "#22c55e"),
    ]
    for icon, name, color in sources:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;padding:4px 0;">
            <span style="font-size:0.9rem;">{icon}</span>
            <span style="font-size:0.78rem;color:#c8ddf5;">{name}</span>
            <span style="margin-left:auto;width:8px;height:8px;border-radius:50%;
                         background:{color};display:inline-block;"></span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:rgba(255,255,255,0.1);margin:16px 0;'>", unsafe_allow_html=True)

    # Portafoglio corrente
    pf = st.session_state.get("pf_symbols", [])
    st.markdown(f"""
    <div style="padding:0 4px;">
        <div style="font-size:0.68rem;font-weight:700;color:#7fb3d3;text-transform:uppercase;
                    letter-spacing:0.8px;margin-bottom:8px;">Portafoglio Corrente</div>
        <div style="font-size:0.8rem;color:#e0edf8;">
            {'<br>'.join([f'· {s}' for s in pf]) if pf else '<span style="color:#7fb3d3;font-style:italic;">Nessun titolo</span>'}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Top Header ────────────────────────────────────────────────────────────────
from datetime import datetime
now = datetime.now()

st.markdown(f"""
<div class="app-header">
    <div>
        <div class="app-logo">FinAnalyzer Pro</div>
        <div class="app-subtitle">Piattaforma Avanzata di Analisi Finanziaria</div>
    </div>
    <div style="text-align:right;">
        <div style="font-size:0.85rem;font-weight:600;color:#374151;">
            {now.strftime('%A, %d %B %Y')}
        </div>
        <div style="font-size:0.75rem;color:#9ca3af;">
            Aggiornato: {now.strftime('%H:%M')}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Routing ───────────────────────────────────────────────────────────────────
try:
    if "Dashboard" in page:
        dashboard.render()
    elif "Screener" in page:
        screener.render()
    elif "Analisi Titolo" in page:
        fundamentals.render()
    elif "Portafoglio" in page:
        portfolio.render()
    elif "Backtest" in page:
        backtest.render()
    elif "Predizioni" in page:
        predictions.render()
    else:
        st.error(f"❌ Pagina non trovata: {page}")
except Exception as e:
    st.error(f"❌ Errore nel caricamento della pagina: {str(e)}")
    import traceback
    st.code(traceback.format_exc())
