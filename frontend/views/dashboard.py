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

MONTHLY_SEASONALITY = {
    "Gen": +2.1, "Feb": +1.4, "Mar": -0.8, "Apr": +1.9, "Mag": +0.3, "Giu": +1.1,
    "Lug": +2.7, "Ago": -0.9, "Set": -1.8, "Ott": +0.6, "Nov": +3.2, "Dic": +2.0,
}

# Top Italian stocks per monitoraggio
TOP_ITALIAN_STOCKS = [
    {"name":"Ferrari","symbol":"RACE.MI"},
    {"name":"Stellantis","symbol":"STLAM.MI"},
    {"name":"Enel","symbol":"ENEL.MI"},
    {"name":"UniCredit","symbol":"UCG.MI"},
    {"name":"ENI","symbol":"ENI.MI"},
    {"name":"Intesa SP","symbol":"ISP.MI"},
    {"name":"Leonardo","symbol":"LDO.MI"},
    {"name":"Generali","symbol":"G.MI"},
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


@st.cache_data(ttl=180)  # Cache 3 minuti per dati più freschi
def _load_top_movers():
    """Carica TOP MOVERS real-time da Borsa Italiana"""
    results = []
    for stock in TOP_ITALIAN_STOCKS:
        try:
            ticker = yf.Ticker(stock["symbol"])
            hist = ticker.history(period="5d")
            info = ticker.info

            if hist.empty or len(hist) < 2:
                continue

            last_price = hist["Close"].iloc[-1]
            prev_price = hist["Close"].iloc[-2]
            change_pct = ((last_price - prev_price) / prev_price) * 100

            # Volume formattato
            volume = hist["Volume"].iloc[-1]
            vol_str = f"{volume/1e6:.1f}M" if volume >= 1e6 else f"{volume/1e3:.0f}K"

            # Market cap
            market_cap = info.get("marketCap", 0)
            cap_str = f"€{market_cap/1e9:.1f}B" if market_cap >= 1e9 else f"€{market_cap/1e6:.0f}M"

            results.append({
                "Titolo": stock["name"],
                "Ticker": stock["symbol"],
                "Prezzo": f"€{last_price:.2f}",
                "Var%": change_pct,
                "Volume": vol_str,
                "Market Cap": cap_str,
            })
            time.sleep(0.1)
        except Exception as e:
            continue

    # Ordina per variazione percentuale (assoluta) decrescente
    results.sort(key=lambda x: abs(x["Var%"]), reverse=True)
    return pd.DataFrame(results[:10])  # Top 10


@st.cache_data(ttl=600)  # Cache 10 minuti
def _load_macro_indicators():
    """Carica indicatori macro real-time"""
    macros = []

    # EUR/USD
    try:
        eurusd = yf.Ticker("EURUSD=X")
        eur_hist = eurusd.history(period="5d")
        if not eur_hist.empty and len(eur_hist) >= 2:
            eur_price = eur_hist["Close"].iloc[-1]
            eur_prev = eur_hist["Close"].iloc[-2]
            eur_change = ((eur_price - eur_prev) / eur_prev) * 100
            macros.append({
                "title": "EUR/USD",
                "value": f"{eur_price:.4f}",
                "delta": f"{'▲' if eur_change >= 0 else '▼'} {abs(eur_change):.2f}%",
                "direction": "pos" if eur_change >= 0 else "neg"
            })
    except:
        pass

    # VIX (volatilità)
    try:
        vix = yf.Ticker("^VIX")
        vix_hist = vix.history(period="5d")
        if not vix_hist.empty and len(vix_hist) >= 2:
            vix_price = vix_hist["Close"].iloc[-1]
            vix_prev = vix_hist["Close"].iloc[-2]
            vix_change = ((vix_price - vix_prev) / vix_prev) * 100
            macros.append({
                "title": "VIX (Volatilità)",
                "value": f"{vix_price:.2f}",
                "delta": f"{'▲' if vix_change >= 0 else '▼'} {abs(vix_change):.1f}%",
                "direction": "neg" if vix_change >= 0 else "pos"  # VIX alto = negativo
            })
    except:
        pass

    # Gold
    try:
        gold = yf.Ticker("GC=F")
        gold_hist = gold.history(period="1y")
        if not gold_hist.empty and len(gold_hist) >= 2:
            gold_price = gold_hist["Close"].iloc[-1]
            gold_ytd_start = gold_hist["Close"].iloc[0]
            gold_ytd = ((gold_price - gold_ytd_start) / gold_ytd_start) * 100
            macros.append({
                "title": "Oro /oz",
                "value": f"${gold_price:.0f}",
                "delta": f"{'▲' if gold_ytd >= 0 else '▼'} {abs(gold_ytd):.1f}% YTD",
                "direction": "pos" if gold_ytd >= 0 else "neg"
            })
    except:
        pass

    # BTP 10Y (dati statici - aggiornare manualmente)
    macros.append({
        "title": "BTP 10Y Yield",
        "value": "3.45%",
        "delta": "▼ -0.12pp",
        "direction": "pos"  # Yield scende = positivo
    })

    # Inflazione IT (dati statici)
    macros.append({
        "title": "Inflazione IT",
        "value": "1.8%",
        "delta": "▼ -0.2pp",
        "direction": "pos"  # Inflazione scende = positivo
    })

    # Tasso BCE (dati statici)
    macros.append({
        "title": "BCE Tasso",
        "value": "3.00%",
        "delta": "▼ -0.25pp",
        "direction": "pos"  # Tassi scendono = positivo
    })

    return macros


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

                    # TITOLO SOPRA IL GRAFICO (ben visibile)
                    st.markdown(f"""
                    <div style="text-align:center;margin-bottom:8px;">
                        <div style="font-size:16px;font-weight:800;color:#FFFFFF;margin-bottom:4px;">{name}</div>
                        <div style="font-size:18px;font-weight:700;color:{color};">{format_number_eur(current_val, decimals=2)}</div>
                        <div style="font-size:20px;font-weight:800;color:{color};">{'+' if perf_6m >= 0 else ''}{format_percentage(perf_6m, decimals=1)}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Mini chart MIGLIORATO con ANGOLI ARROTONDATI
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
                        margin=dict(l=50, r=15, t=10, b=40),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(255,255,255,0.95)",
                        showlegend=False,
                        xaxis=dict(
                            showgrid=True,
                            gridcolor="#e5e7eb",
                            gridwidth=0.5,
                            showticklabels=True,
                            tickfont=dict(size=12, color="#FFFFFF", family="Arial", weight=700),
                            nticks=5
                        ),
                        yaxis=dict(
                            showgrid=True,
                            gridcolor="#e5e7eb",
                            gridwidth=0.5,
                            showticklabels=True,
                            tickfont=dict(size=13, color="#FFFFFF", family="Arial", weight=700),
                            tickformat=",.0f"
                        ),
                    )

                    # Wrapper con ANGOLI ARROTONDATI
                    st.markdown('<div style="border-radius:12px;overflow:hidden;border:2px solid #D4AF37;">', unsafe_allow_html=True)
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Top Movers ────────────────────────────────────────────────────────────
    st.markdown('<h2 style="color:#FFFFFF !important;font-size:1.8rem;font-weight:800;margin:40px 0 20px 0;padding-bottom:12px;border-bottom:2px solid #D4AF37;">🔥 Top Movers – Borsa Italiana (Real-Time)</h2>', unsafe_allow_html=True)

    with st.spinner("Caricamento top movers..."):
        df_movers = _load_top_movers()

    if df_movers.empty:
        st.warning("⚠️ Impossibile caricare dati top movers")
    else:
        # Funzione per colorare la colonna Var%
        def color_change(val):
            if val > 0:
                return f'background-color: #22c55e; color: white; font-weight: 700; border-radius: 6px; padding: 4px 8px;'
            elif val < 0:
                return f'background-color: #ef4444; color: white; font-weight: 700; border-radius: 6px; padding: 4px 8px;'
            return ''

        # Styled dataframe con colori rosso/verde
        st.dataframe(
            df_movers.style.applymap(color_change, subset=["Var%"]).format({
                "Var%": "{:+.2f}%"
            }),
            width="stretch",
            hide_index=True,
            height=320,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Indicatori Macro (Real-Time) ──────────────────────────────────────────
    st.markdown('<h2 style="color:#FFFFFF !important;font-size:1.8rem;font-weight:800;margin:40px 0 20px 0;padding-bottom:12px;border-bottom:2px solid #D4AF37;">📐 Indicatori Macro (Real-Time)</h2>', unsafe_allow_html=True)

    with st.spinner("Caricamento indicatori macro..."):
        macros = _load_macro_indicators()

    if not macros:
        st.warning("⚠️ Impossibile caricare indicatori macro")
    else:
        mc = st.columns(len(macros))
        for c, macro in zip(mc, macros):
            with c:
                # Colore background basato su direzione
                bg_color = "#22c55e" if macro["direction"] == "pos" else "#ef4444"
                st.markdown(f"""
                <div class="fin-card" style="text-align:center;padding:14px 12px;background:{bg_color};border-radius:10px;">
                    <div style="font-size:0.75rem;color:#FFFFFF;font-weight:600;margin-bottom:6px;">{macro['title']}</div>
                    <div style="font-size:1.4rem;color:#FFFFFF;font-weight:800;margin:8px 0;">{macro['value']}</div>
                    <div style="font-size:0.75rem;color:#FFFFFF;font-weight:600;">{macro['delta']}</div>
                </div>
                """, unsafe_allow_html=True)
