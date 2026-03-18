"""
Dashboard - Pagina principale con overview mercati
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from frontend.styles.design import badge, card_metric, color_pct, chip, stars, MAIN_CSS
from frontend.components.charts import line_chart, bar_chart, seasonality_bar

MARKET_OVERVIEW = [
    {"name":"S&P 500","symbol":"^GSPC","price":"5,456.30","change":+0.38,"ytd":+16.2},
    {"name":"FTSE MIB","symbol":"FTSEMIB.MI","price":"33,820","change":-0.21,"ytd":+9.4},
    {"name":"EURO STOXX 50","symbol":"^STOXX50E","price":"4,871","change":+0.12,"ytd":+8.1},
    {"name":"DAX","symbol":"^GDAXI","price":"18,304","change":+0.28,"ytd":+11.3},
    {"name":"Nasdaq","symbol":"^IXIC","price":"17,192","change":+0.55,"ytd":+18.7},
    {"name":"Gold","symbol":"GC=F","price":"2,335","change":-0.14,"ytd":+14.3},
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


def render():
    st.title("📊 Dashboard Mercati")
    st.markdown("---")

    # ── Market Overview ────────────────────────────────────────────────────────
    st.subheader("🌍 Mercati Principali")
    cols = st.columns(len(MARKET_OVERVIEW))
    for col, mkt in zip(cols, MARKET_OVERVIEW):
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

    # ── Main row ──────────────────────────────────────────────────────────────
    col_left, col_right = st.columns([3, 2], gap="medium")

    with col_left:
        st.subheader("📅 Stagionalità S&P 500")
        fig = seasonality_bar(MONTHLY_SEASONALITY, height=260)
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.85)",
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # Ring metrics Seasonality
        ring_cols = st.columns(5)
        periods = [("1 Anno","12.7%","#22c55e"),("3 Anni","5.9%","#f59e0b"),
                   ("5 Anni","9.6%","#2471c8"),("10 Anni","6.8%","#8b5cf6"),("20 Anni","7.4%","#0ea5c9")]
        for rc, (label, val, color) in zip(ring_cols, periods):
            with rc:
                st.markdown(f"""
                <div class="ring-metric">
                    <div class="ring-label">{label}</div>
                    <div class="ring-value" style="color:{color};">{val}</div>
                    <div class="ring-sub" style="color:{color};">Media</div>
                </div>
                """, unsafe_allow_html=True)

    with col_right:
        st.subheader("🏭 Settori – Performance YTD")
        sectors = list(SECTOR_PERF.keys())
        values  = list(SECTOR_PERF.values())
        colors  = ["#22c55e" if v >= 0 else "#ef4444" for v in values]
        fig2 = bar_chart(values, sectors, title="", colors=colors, horizontal=True, height=300)
        fig2.update_traces(texttemplate=[f"{v:+.1f}%" for v in values], textposition="outside")
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.85)")
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Top Movers ────────────────────────────────────────────────────────────
    st.subheader("🔥 Top Movers – Borsa Italiana")

    # Build HTML table with proper rendering
    table_rows = "".join([f"""
        <tr>
            <td class="rank-num">{i+1}</td>
            <td><b>{m['name']}</b><br><span style="color:#9ca3af;font-size:0.7rem;">{m['symbol']}</span></td>
            <td style="font-weight:700;">{m['price']}</td>
            <td>{color_pct(m['change'])}</td>
            <td>{m['vol']}</td>
            <td>{m['cap']}</td>
        </tr>
    """ for i, m in enumerate(TOP_MOVERS)])

    st.markdown(f"""
    <div class="fin-card" style="padding:0;overflow:hidden;">
    <table class="fin-table">
        <thead><tr>
            <th>#</th><th>Titolo</th><th>Prezzo</th><th>Var%</th><th>Volume</th><th>Market Cap</th>
        </tr></thead>
        <tbody>
    {table_rows}
        </tbody>
    </table>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Quick Stats ────────────────────────────────────────────────────────────
    st.subheader("📐 Indicatori Macro")
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
