"""
Dashboard - Pagina principale con overview mercati
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
import time
from datetime import datetime, timedelta
from frontend.styles.design import badge, card_metric, color_pct, chip, stars, MAIN_CSS
from frontend.components.charts import line_chart, bar_chart, seasonality_bar
from frontend.utils.formatters import format_currency_eur, format_number_eur, format_percentage

# Questi saranno caricati dinamicamente da Yahoo Finance
MARKET_INDICES = [
    {"name":"S&P 500","symbol":"^GSPC"},
    {"name":"FTSE MIB","symbol":"FTSEMIB.MI"},
    {"name":"EURO STOXX 50","symbol":"^STOXX50E"},
    {"name":"DAX","symbol":"^GDAXI"},
    {"name":"Nasdaq","symbol":"^IXIC"},
    {"name":"Hang Seng","symbol":"^HSI"},
    {"name":"Nikkei 225","symbol":"^N225"},
    {"name":"Hang Seng China","symbol":"^HSCE"},
    {"name":"Gold","symbol":"GC=F"},
]

# Asset per grafici 6 mesi
ASSET_6M_CHARTS = [
    {"name":"EURO STOXX 600","symbol":"^STOXX","color":"#2471c8"},
    {"name":"S&P 500","symbol":"^GSPC","color":"#22c55e"},
    {"name":"Dow Jones","symbol":"^DJI","color":"#0ea5c9"},
    {"name":"Russell 1000","symbol":"^RUI","color":"#8b5cf6"},
    {"name":"Petrolio (WTI)","symbol":"CL=F","color":"#f59e0b"},
    {"name":"Gas Naturale","symbol":"NG=F","color":"#ef4444"},
    {"name":"Bitcoin","symbol":"BTC-USD","color":"#f59e0b"},
    {"name":"Gold","symbol":"GC=F","color":"#fbbf24"},
    {"name":"Silver","symbol":"SI=F","color":"#9ca3af"},
    {"name":"Cacao","symbol":"CC=F","color":"#92400e"},
    {"name":"Caffè","symbol":"KC=F","color":"#78350f"},
]

SECTOR_PERF = {
    "Tecnologia": +22.4,
    "Energia":    +8.6,
    "Finanza":    +14.2,
    "Salute":     +5.1,
    "Utilities":  -2.3,
    "Immobiliare":-4.7,
    "Materiali":  +3.8,
    "Industriali":+10.9,
}

MONTHLY_SEASONALITY = {
    "Gen": +2.1, "Feb": +1.4, "Mar": -0.8, "Apr": +1.9, "Mag": +0.3, "Giu": +1.1,
    "Lug": +2.7, "Ago": -0.9, "Set": -1.8, "Ott": +0.6, "Nov": +3.2, "Dic": +2.0,
}

TOP_MOVERS = [
    {"name":"Ferrari","symbol":"RACE.MI","price":"429.50","change":+4.2,"vol":"1.2M","cap":"80.1B"},
    {"name":"Stellantis","symbol":"STLAM.MI","price":"18.32","change":+2.8,"vol":"8.4M","cap":"57.3B"},
    {"name":"Enel","symbol":"ENEL.MI","price":"6.74","change":-1.9,"vol":"22.1M","cap":"67.5B"},
    {"name":"UniCredit","symbol":"UCG.MI","price":"37.82","change":+3.1,"vol":"11.3M","cap":"47.9B"},
    {"name":"ENI","symbol":"ENI.MI","price":"14.97","change":-0.7,"vol":"9.8M","cap":"46.2B"},
    {"name":"Intesa SP","symbol":"ISP.MI","price":"3.64","change":+1.4,"vol":"53.2M","cap":"67.8B"},
]


@st.cache_data(ttl=300)  # Cache 5 minuti
def _load_market_indices():
    """Carica dati real-time degli indici principali"""
    results = []
    for idx in MARKET_INDICES:
        try:
            ticker = yf.Ticker(idx["symbol"])
            hist = ticker.history(period="ytd")
            if hist.empty:
                continue

            last_price = hist["Close"].iloc[-1]
            prev_price = hist["Close"].iloc[-2] if len(hist) > 1 else last_price
            change_pct = ((last_price - prev_price) / prev_price) * 100

            # YTD return
            first_price = hist["Close"].iloc[0]
            ytd_return = ((last_price - first_price) / first_price) * 100

            results.append({
                "name": idx["name"],
                "symbol": idx["symbol"],
                "price": format_number_eur(last_price, decimals=2),
                "change": change_pct,
                "ytd": ytd_return,
            })
            time.sleep(0.1)  # Rate limiting
        except Exception as e:
            st.warning(f"⚠️ Errore caricamento {idx['name']}: {e}")
            continue
    return results


@st.cache_data(ttl=300)  # Cache 5 minuti
def _load_asset_6m_data(symbol):
    """Carica dati ultimi 6 mesi per un asset"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="6mo")
        if not hist.empty:
            return hist["Close"]
    except:
        pass
    return pd.Series()


def render():
    st.markdown('<h1 style="color:#FFFFFF !important;font-size:2.5rem;font-weight:800;margin-bottom:20px;">📊 Dashboard Mercati</h1>', unsafe_allow_html=True)
    st.markdown("---")

    # ── Market Overview ────────────────────────────────────────────────────────
    st.markdown('<h2 style="color:#FFFFFF !important;font-size:1.8rem;font-weight:800;margin:40px 0 20px 0;padding-bottom:12px;border-bottom:2px solid #D4AF37;">🌍 Mercati Principali – Dati Real-Time</h2>', unsafe_allow_html=True)

    with st.spinner("Caricamento indici..."):
        market_data = _load_market_indices()

    if not market_data:
        st.error("❌ Impossibile caricare dati di mercato")
        return

    cols = st.columns(len(market_data))
    for col, mkt in zip(cols, market_data):
        with col:
            pos = mkt["change"] >= 0
            chg_str = f"{'▲' if pos else '▼'} {abs(mkt['change']):.2f}%"
            st.markdown(f"""
            <div class="fin-card" style="text-align:center;padding:12px 10px;">
                <div class="fin-card-title" style="font-size:0.7rem;">{mkt['name']}</div>
                <div class="fin-card-value" style="font-size:1.25rem;">{mkt['price']}</div>
                <div class="fin-card-delta {'delta-pos' if pos else 'delta-neg'}">{chg_str}</div>
                <div style="font-size:0.68rem;color:#9ca3af;margin-top:3px;">YTD {color_pct(mkt['ytd'])}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Grafici 6 Mesi Asset ──────────────────────────────────────────────────
    st.markdown('<h2 style="color:#FFFFFF !important;font-size:1.8rem;font-weight:800;margin:40px 0 20px 0;padding-bottom:12px;border-bottom:2px solid #D4AF37;">📈 Performance Ultimi 6 Mesi – Asset Globali</h2>', unsafe_allow_html=True)

    with st.spinner("Caricamento dati asset..."):
        asset_data = {}
        for asset in ASSET_6M_CHARTS:
            data = _load_asset_6m_data(asset["symbol"])
            if not data.empty:
                asset_data[asset["name"]] = {
                    "data": data,
                    "color": asset["color"]
                }
            time.sleep(0.1)

    if not asset_data:
        st.warning("⚠️ Impossibile caricare dati asset")
    else:
        # Grid 3x4 per 11 asset (ultima cella vuota)
        for i in range(0, len(asset_data), 3):
            cols = st.columns(3)
            items = list(asset_data.items())[i:i+3]

            for col, (name, info) in zip(cols, items):
                with col:
                    data = info["data"]
                    color = info["color"]

                    # Performance 6M
                    perf_6m = ((data.iloc[-1] / data.iloc[0]) - 1) * 100

                    # Valori min/max per scaling
                    min_val = data.min()
                    max_val = data.max()
                    current_val = data.iloc[-1]

                    # Mini chart MIGLIORATO
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=data.index,
                        y=data.values,
                        mode="lines",
                        line=dict(color=color, width=3),
                        fill="tozeroy",
                        fillcolor=f"rgba{tuple(list(bytes.fromhex(color[1:])) + [0.15])}",
                        name=name,
                        hovertemplate="<b>%{x|%d %b}</b><br>Prezzo: %{y:,.2f}<extra></extra>"
                    ))

                    fig.update_layout(
                        height=200,
                        margin=dict(l=10, r=10, t=60, b=30),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(255,255,255,0.9)",
                        title=dict(
                            text=f"<b style='font-size:14px;'>{name}</b><br>"
                                 f"<span style='font-size:16px;font-weight:700;color:{color};'>{format_number_eur(current_val, decimals=2)}</span><br>"
                                 f"<span style='font-size:18px;font-weight:800;color:{color};'>{'+' if perf_6m >= 0 else ''}{format_percentage(perf_6m, decimals=1)}</span>",
                            font=dict(size=12),
                            x=0.5,
                            xanchor="center",
                            y=0.95,
                            yanchor="top"
                        ),
                        showlegend=False,
                        xaxis=dict(
                            showgrid=False,
                            showticklabels=True,
                            tickfont=dict(size=9, color="#6b7280"),
                            nticks=4
                        ),
                        yaxis=dict(
                            showgrid=True,
                            gridcolor="#e5e7eb",
                            gridwidth=0.5,
                            showticklabels=True,
                            tickfont=dict(size=10, color="#374151"),
                            tickformat=",.0f"
                        ),
                    )
                    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Settori Performance ───────────────────────────────────────────────────
    st.markdown('<h2 style="color:#FFFFFF !important;font-size:1.8rem;font-weight:800;margin:40px 0 20px 0;padding-bottom:12px;border-bottom:2px solid #D4AF37;">🏭 Settori – Performance YTD</h2>', unsafe_allow_html=True)
    sectors = list(SECTOR_PERF.keys())
    values  = list(SECTOR_PERF.values())
    colors  = ["#22c55e" if v >= 0 else "#ef4444" for v in values]
    fig2 = bar_chart(values, sectors, title="", colors=colors, horizontal=True, height=300)
    fig2.update_traces(texttemplate=[f"{v:+.1f}%" for v in values], textposition="outside")
    fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.85)")
    st.plotly_chart(fig2, width="stretch", config={"displayModeBar": False})

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Top Movers ────────────────────────────────────────────────────────────
    st.markdown('<h2 style="color:#FFFFFF !important;font-size:1.8rem;font-weight:800;margin:40px 0 20px 0;padding-bottom:12px;border-bottom:2px solid #D4AF37;">🔥 Top Movers – Borsa Italiana</h2>', unsafe_allow_html=True)

    # Crea DataFrame dai dati
    df_movers = pd.DataFrame(TOP_MOVERS)
    df_movers.index = df_movers.index + 1  # Start from 1

    # Display con st.dataframe nativo (NO HTML ESCAPE!)
    st.dataframe(
        df_movers,
        width="stretch",
        hide_index=False,
        column_config={
            "name": st.column_config.TextColumn("Titolo", width="medium"),
            "symbol": st.column_config.TextColumn("Ticker", width="small"),
            "price": st.column_config.TextColumn("Prezzo", width="small"),
            "change": st.column_config.NumberColumn(
                "Var%",
                format="%.2f%%",
                width="small",
            ),
            "vol": st.column_config.TextColumn("Volume", width="small"),
            "cap": st.column_config.TextColumn("Market Cap", width="medium"),
        },
        height=280,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Quick Stats ────────────────────────────────────────────────────────────
    st.markdown('<h2 style="color:#FFFFFF !important;font-size:1.8rem;font-weight:800;margin:40px 0 20px 0;padding-bottom:12px;border-bottom:2px solid #D4AF37;">📐 Indicatori Macro</h2>', unsafe_allow_html=True)
    mc = st.columns(6)
    macros = [
        ("Inflazione IT","5.9%","▼ -0.3pp","neg"),
        ("BCE Tasso","4.25%","stable","neu"),
        ("BTP 10Y Yield","3.92%","▲ +0.08","neg"),
        ("EUR/USD","1.0832","▲ +0.12%","pos"),
        ("VIX","16.4","▼ -8.2%","pos"),
        ("Oro /oz","$2,335","▲ +14.3% YTD","pos"),
    ]
    for c, (title, val, delta, direction) in zip(mc, macros):
        with c:
            st.markdown(f"""
            <div class="fin-card" style="text-align:center;padding:12px 10px;">
                <div class="fin-card-title" style="font-size:0.7rem;">{title}</div>
                <div class="fin-card-value" style="font-size:1.2rem;">{val}</div>
                <div class="fin-card-delta delta-{'pos' if direction=='pos' else ('neg' if direction=='neg' else 'neu')}"
                     style="font-size:0.72rem;">{delta}</div>
            </div>
            """, unsafe_allow_html=True)
