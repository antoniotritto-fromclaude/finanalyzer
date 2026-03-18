"""
Quantum Screener - Ricerca avanzata strumenti finanziari
"""
import streamlit as st
import pandas as pd
from frontend.styles.design import badge, color_pct, chip, stars
from backend.data_collectors.justetf import JustETFCollector
from backend.data_collectors.morningstar import MorningstarCollector
from backend.data_collectors.quantalys import QuantalysCollector

etf_col  = JustETFCollector()
ms_col   = MorningstarCollector()
qly_col  = QuantalysCollector()


def _etf_screener():
    st.subheader("📡 ETF Screener – JustETF")

    f1, f2, f3, f4 = st.columns(4)
    with f1:
        category = st.selectbox("Categoria", [
            "Tutti","Azionario Globale","Azionario USA","Azionario Europa","Azionario Italia",
            "Azionario Emergenti","Obbligazionario","Commodities - Oro","Azionario Settoriale"
        ])
    with f2:
        dist = st.selectbox("Distribuzione", ["Tutti","Accumulazione","Distribuzione"])
    with f3:
        repl = st.selectbox("Replica", ["Tutti","Fisica","Sintetica"])
    with f4:
        max_ter = st.slider("TER max (%)", 0.0, 2.0, 1.0, 0.05)

    etfs = etf_col.get_popular_etfs()
    df   = pd.DataFrame(etfs)

    if category != "Tutti":
        df = df[df["category"] == category]
    if dist != "Tutti":
        df = df[df["distribution"] == dist]
    if repl != "Tutti":
        df = df[df["replication"] == repl]
    df = df[df["ter"] <= max_ter]
    df = df.sort_values("ter")

    st.markdown(f"**{len(df)} ETF trovati**", unsafe_allow_html=True)
    st.markdown("""
    <div class="fin-card" style="padding:0;overflow:hidden;">
    <table class="fin-table">
        <thead><tr>
            <th>#</th><th>Nome ETF</th><th>ISIN</th><th>Ticker</th>
            <th>Categoria</th><th>TER</th><th>Replica</th><th>Distribuzione</th><th>Paese</th>
        </tr></thead><tbody>
    """ + "".join([f"""
        <tr>
            <td class="rank-num">{row['rank']}</td>
            <td style="font-weight:600;min-width:200px;">{row['name']}</td>
            <td><code style="font-size:0.72rem;background:#f3f4f6;padding:2px 6px;border-radius:4px;">{row['isin']}</code></td>
            <td>{chip(row['ticker'], 'blue')}</td>
            <td style="font-size:0.78rem;">{row.get('category','')}</td>
            <td>{chip(f"{row['ter']:.2f}%", 'green' if row['ter']<=0.20 else ('orange' if row['ter']<=0.50 else 'red'))}</td>
            <td>{chip(row['replication'], 'blue' if row['replication']=='Fisica' else 'gray')}</td>
            <td>{chip(row['distribution'], 'purple' if row['distribution']=='Accumulazione' else 'teal')}</td>
            <td>{row['domicile']}</td>
        </tr>
    """ for _, row in df.iterrows()]) + "</tbody></table></div>", unsafe_allow_html=True)


def _fund_screener():
    st.subheader("⭐ Fund Screener – Morningstar + Quantalys")

    tab_ms, tab_q = st.tabs(["🌟 Morningstar Top Funds", "📊 Quantalys – Per Categoria"])

    with tab_ms:
        funds = ms_col.get_top_funds_italy()
        df = pd.DataFrame(funds)

        f1, f2 = st.columns(2)
        with f1:
            type_filter = st.selectbox("Tipo", ["Tutti"] + sorted(df["type"].unique().tolist()))
        with f2:
            cat_filter = st.selectbox("Categoria", ["Tutti"] + sorted(df["category"].unique().tolist()))

        if type_filter != "Tutti":
            df = df[df["type"] == type_filter]
        if cat_filter != "Tutti":
            df = df[df["category"] == cat_filter]

        st.markdown("""
        <div class="fin-card" style="padding:0;overflow:hidden;">
        <table class="fin-table">
            <thead><tr>
                <th>Nome Fondo</th><th>ISIN</th><th>Categoria</th><th>Rating</th>
                <th>TER</th><th>YTD</th><th>1 Anno</th><th>3 Anni</th>
            </tr></thead><tbody>
        """ + "".join([f"""
            <tr>
                <td style="font-weight:600;min-width:220px;">{r['name']}</td>
                <td><code style="font-size:0.72rem;">{r['isin']}</code></td>
                <td style="font-size:0.78rem;">{r['category']}</td>
                <td>{stars(r['rating'])}</td>
                <td>{chip(f"{r['ter']:.2f}%", 'green' if r['ter']<1 else 'orange')}</td>
                <td>{color_pct(r['ytd'])}</td>
                <td>{color_pct(r['1y'])}</td>
                <td>{color_pct(r['3y'])}</td>
            </tr>
        """ for _, r in df.iterrows()]) + "</tbody></table></div>", unsafe_allow_html=True)

    with tab_q:
        categories_data = qly_col.get_best_funds_by_category()
        sel_cat = st.selectbox("Seleziona Categoria", list(categories_data.keys()))
        funds_q = categories_data[sel_cat]

        st.markdown("""
        <div class="fin-card" style="padding:0;overflow:hidden;">
        <table class="fin-table">
            <thead><tr>
                <th>Nome Fondo</th><th>ISIN</th><th>Rating</th>
                <th>TER</th><th>1 Anno</th><th>3 Anni</th><th>5 Anni</th><th>Rischio</th>
            </tr></thead><tbody>
        """ + "".join([f"""
            <tr>
                <td style="font-weight:600;min-width:220px;">{f['name']}</td>
                <td><code style="font-size:0.72rem;">{f['isin']}</code></td>
                <td>{stars(f['rating'])}</td>
                <td>{chip(f"{f['ter']:.2f}%", 'green' if f['ter']<1 else 'orange')}</td>
                <td>{color_pct(f['1y'])}</td>
                <td>{color_pct(f['3y'])}</td>
                <td>{color_pct(f['5y'])}</td>
                <td>{'⚡' * f['risk']}</td>
            </tr>
        """ for f in funds_q]) + "</tbody></table></div>", unsafe_allow_html=True)


def _bond_screener():
    st.subheader("🏛️ Obbligazioni – Morningstar")

    bonds = ms_col.get_bonds_italy()
    df = pd.DataFrame(bonds)

    f1, f2 = st.columns(2)
    with f1:
        btype = st.selectbox("Tipo", ["Tutti"] + sorted(df["type"].unique().tolist()))
    with f2:
        country = st.selectbox("Paese", ["Tutti"] + sorted(df["paese"].unique().tolist()))

    if btype != "Tutti":
        df = df[df["type"] == btype]
    if country != "Tutti":
        df = df[df["paese"] == country]

    df_sorted = df.sort_values("rendimento", ascending=False)

    # Display con st.dataframe nativo (NO HTML ESCAPE!)
    st.dataframe(
        df_sorted,
        use_container_width=True,
        hide_index=True,
        column_config={
            "name": st.column_config.TextColumn("Nome", width="large"),
            "isin": st.column_config.TextColumn("ISIN", width="medium"),
            "type": st.column_config.TextColumn("Tipo", width="small"),
            "scadenza": st.column_config.TextColumn("Scadenza", width="medium"),
            "cedola": st.column_config.NumberColumn(
                "Cedola",
                format="%.2f%%",
                width="small",
            ),
            "rendimento": st.column_config.NumberColumn(
                "Rendimento",
                format="%.2f%%",
                width="small",
            ),
            "rating": st.column_config.TextColumn("Rating", width="small"),
            "paese": st.column_config.TextColumn("Paese", width="small"),
        },
        height=400,
    )


def _commodity_screener():
    st.subheader("🌾 Commodities – Mercati Globali")
    import yfinance as yf, time

    commodities = ms_col.get_commodities()

    prices_live = {}
    with st.spinner("Caricamento prezzi live..."):
        for c in commodities:
            try:
                t = yf.Ticker(c["symbol"])
                hist = t.history(period="5d")
                if not hist.empty:
                    prices_live[c["symbol"]] = {
                        "last":   hist["Close"].iloc[-1],
                        "prev":   hist["Close"].iloc[-2] if len(hist) > 1 else hist["Close"].iloc[-1],
                        "volume": hist["Volume"].iloc[-1],
                    }
                time.sleep(0.3)
            except:
                pass

    rows_html = ""
    for c in commodities:
        sym  = c["symbol"]
        info = prices_live.get(sym, {})
        last = info.get("last", 0)
        prev = info.get("prev", last)
        chg  = ((last - prev) / prev * 100) if prev else 0
        price_str  = f"{last:.2f}" if last else "N/D"
        change_str = color_pct(chg) if last else "–"

        rows_html += f"""
        <tr>
            <td style="font-weight:600;">{c['name']}</td>
            <td>{chip(sym,'gray')}</td>
            <td><b>{price_str}</b></td>
            <td>{c['unit']}</td>
            <td>{change_str}</td>
            <td>{chip(c['category'], 'orange' if 'Energia' in c['category'] else ('green' if 'Agricoltura' in c['category'] else 'blue'))}</td>
        </tr>"""

    st.markdown(f"""
    <div class="fin-card" style="padding:0;overflow:hidden;">
    <table class="fin-table">
        <thead><tr><th>Commodity</th><th>Simbolo</th><th>Prezzo</th><th>Unità</th><th>Var%</th><th>Categoria</th></tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    </div>
    """, unsafe_allow_html=True)


def render():
    st.title("🔍 Screener Avanzato")
    st.markdown("Ricerca e analisi di ETF, Fondi, Obbligazioni e Commodities")
    st.markdown("---")

    tab_etf, tab_fund, tab_bond, tab_comm = st.tabs([
        "📡 ETF", "⭐ Fondi", "🏛️ Obbligazioni", "🌾 Commodities"
    ])

    with tab_etf:
        _etf_screener()
    with tab_fund:
        _fund_screener()
    with tab_bond:
        _bond_screener()
    with tab_comm:
        _commodity_screener()
