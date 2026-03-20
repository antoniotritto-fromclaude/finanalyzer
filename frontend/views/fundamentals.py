"""
Fundamentals – Analisi fondamentale di un singolo titolo
"""
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import time
from frontend.styles.design import badge, color_pct, chip
from frontend.components.charts import line_chart, candle_chart, bar_chart
from frontend.utils.formatters import format_currency_eur, format_number_eur, format_percentage


def _get_data(symbol: str):
    try:
        t = yf.Ticker(symbol)
        hist_1y = t.history(period="1y")
        hist_5y = t.history(period="5y")

        # Prova a caricare info, ma gestisci fallimenti comuni
        info = {}
        info_loaded = False
        try:
            raw_info = t.info
            # Verifica che info contenga dati validi (non solo chiavi vuote)
            if raw_info and len(raw_info) > 5:
                info = raw_info
                info_loaded = True
        except Exception as e:
            # Yahoo Finance info spesso fallisce per titoli non-US
            pass

        # Calcola metriche base dai dati storici se info non disponibile
        if not info_loaded and not hist_1y.empty:
            info["_calculated"] = True
            info["fiftyTwoWeekHigh"] = hist_1y["High"].max()
            info["fiftyTwoWeekLow"] = hist_1y["Low"].min()

        return t, hist_1y, hist_5y, info, info_loaded
    except Exception as e:
        return None, pd.DataFrame(), pd.DataFrame(), {}, False


def _metric_card(label: str, value: str, sub: str = "", color: str = "#2471c8"):
    return f"""
    <div class="fin-card" style="text-align:center;padding:12px 10px;">
        <div class="fin-card-title" style="font-size:0.7rem;">{label}</div>
        <div class="fin-card-value" style="font-size:1.15rem;color:{color};">{value}</div>
        {f'<div style="font-size:0.72rem;color:#9ca3af;margin-top:3px;">{sub}</div>' if sub else ''}
    </div>"""


def render():
    st.title("📊 Analisi Fondamentale")

    # Info fonti dati
    st.markdown("""
    <div class="fin-card" style="background:#f0f9ff;border-left:4px solid #0ea5c9;padding:14px 18px;">
        <b>📈 Fonti Dati:</b> Questa analisi utilizza dati da <b>Yahoo Finance</b> in tempo reale.
        Include prezzi, metriche fondamentali, grafici storici e statistiche di rendimento.
        <br><br>
        💡 <b>Nota:</b> Titoli USA (AAPL, MSFT) hanno dati più completi.
        Titoli internazionali (es. *.MI, *.DE) potrebbero mostrare solo prezzi e grafici.
        Per fondi usa <b>Screener</b> con codici ISIN.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_sym, col_btn = st.columns([4, 1])
    with col_sym:
        symbol = st.text_input(
            "Simbolo Titolo (Yahoo Finance)",
            value="AAPL",
            placeholder="Es: AAPL, ENI.MI, MSFT, VWCE.DE, BTC-USD",
            help="Inserisci il simbolo Yahoo Finance del titolo da analizzare"
        )
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        search = st.button("🔍 Analizza", type="primary", use_container_width=True)

    if not search and "fund_symbol" not in st.session_state:
        st.info("Inserisci un simbolo e clicca Analizza.")
        return

    if search:
        st.session_state["fund_symbol"] = symbol
    symbol = st.session_state.get("fund_symbol", symbol)

    with st.spinner(f"Caricamento dati per {symbol}..."):
        ticker, hist_1y, hist_5y, info, info_loaded = _get_data(symbol)

    if hist_1y.empty:
        st.error(f"❌ Nessun dato trovato per **{symbol}**. Verifica il simbolo.")
        return

    # Avviso se info non caricato
    if not info_loaded:
        st.warning("""
        ⚠️ **Dati fondamentali limitati**: Yahoo Finance non ha restituito dati completi per questo titolo.
        I grafici e l'analisi dei prezzi sono disponibili, ma alcune metriche (P/E, EPS, Market Cap) potrebbero non essere disponibili.
        """)
        st.markdown("<br>", unsafe_allow_html=True)

    # ── Header titolo ──────────────────────────────────────────────────────────
    name  = info.get("longName", info.get("shortName", symbol))
    exch  = info.get("exchange", "")
    curr  = info.get("currency", "")
    last  = hist_1y["Close"].iloc[-1]
    prev  = hist_1y["Close"].iloc[-2] if len(hist_1y) > 1 else last
    chg   = (last - prev) / prev * 100

    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown(f"""
        <div class="fin-card" style="padding:18px 22px;">
            <div style="font-size:0.78rem;color:#9ca3af;font-weight:600;letter-spacing:0.5px;">{exch} · {curr}</div>
            <div style="font-size:1.6rem;font-weight:800;color:#0f1c2e;">{name}</div>
            <div style="font-size:1.25rem;font-weight:700;color:#2471c8;">
                {curr} {format_number_eur(last, decimals=2)}
                &nbsp;<span class="{'delta-pos' if chg>=0 else 'delta-neg'}" style="font-size:1rem;">
                    {'▲' if chg>=0 else '▼'} {format_percentage(abs(chg), decimals=2)}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_h2:
        mktcap = info.get("marketCap", 0)
        mktcap_str = f"${mktcap/1e9:.1f}B" if mktcap >= 1e9 else (f"${mktcap/1e6:.0f}M" if mktcap else "N/D")
        st.markdown(_metric_card("Market Cap", mktcap_str), unsafe_allow_html=True)

    # ── Metriche fondamentali ─────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    mc = st.columns(6)

    # Fix per dividendYield: controlla None esplicitamente
    div_yield = info.get("dividendYield")
    div_yield_pct = div_yield * 100 if div_yield is not None else None

    metrics = [
        ("P/E (TTM)",      info.get("trailingPE"),       "{:.1f}"),
        ("EPS (TTM)",      info.get("trailingEps"),      "{:.2f}"),
        ("P/B Ratio",      info.get("priceToBook"),      "{:.2f}"),
        ("Div. Yield",     div_yield_pct,                "{:.2f}%"),
        ("Beta",           info.get("beta"),             "{:.2f}"),
        ("52W High",       info.get("fiftyTwoWeekHigh"), "{:.2f}"),
    ]
    for col, (label, val, fmt) in zip(mc, metrics):
        with col:
            v_str = fmt.format(val) if val is not None else "N/D"
            st.markdown(_metric_card(label, v_str), unsafe_allow_html=True)

    # ── Grafici ───────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    tab_1y, tab_5y, tab_candle = st.tabs(["📈 Prezzo 1 Anno", "📊 Storico 5 Anni", "🕯️ Candlestick"])

    with tab_1y:
        if not hist_1y.empty:
            df_plot = hist_1y[["Close"]].rename(columns={"Close": symbol})
            fig = line_chart(df_plot, title=f"{symbol} – Prezzo Ultimi 12 Mesi",
                             y_title=f"Prezzo ({curr})", filled=True, height=340)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.85)")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with tab_5y:
        if not hist_5y.empty:
            df_plot = hist_5y[["Close"]].rename(columns={"Close": symbol})
            fig = line_chart(df_plot, title=f"{symbol} – Storico 5 Anni",
                             y_title=f"Prezzo ({curr})", filled=True, height=340)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.85)")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with tab_candle:
        if not hist_1y.empty:
            fig = candle_chart(hist_1y, title=f"{symbol} – Candlestick", height=360)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.85)")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── Statistiche rendimento ────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📐 Analisi Rendimento")

    rets = hist_1y["Close"].pct_change().dropna()
    ann_ret = rets.mean() * 252
    ann_vol = rets.std() * np.sqrt(252)
    sharpe  = ann_ret / ann_vol if ann_vol > 0 else 0
    max_dd  = ((hist_1y["Close"] / hist_1y["Close"].cummax()) - 1).min()
    ytd_ret = (hist_1y["Close"].iloc[-1] / hist_1y["Close"].iloc[0] - 1) * 100

    sc = st.columns(5)
    stat_data = [
        ("Rendimento YTD",   f"{ytd_ret:+.1f}%",   ytd_ret >= 0),
        ("Rendimento Annuo", f"{ann_ret*100:+.1f}%", ann_ret >= 0),
        ("Volatilità",       f"{ann_vol*100:.1f}%",  None),
        ("Sharpe Ratio",     f"{sharpe:.2f}",        None),
        ("Max Drawdown",     f"{max_dd*100:.1f}%",   max_dd > -0.1),
    ]
    for col, (label, val, pos) in zip(sc, stat_data):
        with col:
            color = ("#22c55e" if pos else "#ef4444") if pos is not None else "#2471c8"
            st.markdown(_metric_card(label, val, color=color), unsafe_allow_html=True)

    # ── Business Summary ──────────────────────────────────────────────────────
    desc = info.get("longBusinessSummary", "")
    if desc:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("📝 Descrizione Azienda"):
            st.write(desc)

    # ── Link Fonti Esterne ────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🔗 Fonti Esterne e Link Utili"):
        st.markdown(f"""
        Approfondisci l'analisi con queste fonti esterne:

        **Dati Fondamentali:**
        - [Yahoo Finance - {symbol}](https://finance.yahoo.com/quote/{symbol})
        - [FINVIZ - {symbol}](https://finviz.com/quote.ashx?t={symbol})
        - [MarketWatch - {symbol}](https://www.marketwatch.com/investing/stock/{symbol})

        **Analisi Tecnica:**
        - [TradingView - {symbol}](https://www.tradingview.com/symbols/{symbol}/)
        - [Investing.com - {symbol}](https://www.investing.com/search/?q={symbol})

        **News & Sentiment:**
        - [Google Finance - {symbol}](https://www.google.com/finance/quote/{symbol})
        - [Seeking Alpha - {symbol}](https://seekingalpha.com/symbol/{symbol})

        ---

        💡 **Aggiungi Link Custom:**
        """)

        custom_url = st.text_input(
            "URL personalizzato (opzionale)",
            placeholder="https://esempio.com/analisi-titolo",
            key=f"custom_url_{symbol}"
        )
        if custom_url:
            st.markdown(f"🔗 [Apri Link Custom]({custom_url})")

        st.info("💡 Queste risorse esterne possono fornire analisi aggiuntive, dati in tempo reale e sentiment di mercato.")
