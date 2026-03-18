"""
Backtest storico – 1, 3, 5, 7 anni
"""
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import time
import plotly.graph_objects as go
from frontend.styles.design import badge, color_pct, chip
from frontend.components.charts import line_chart, bar_chart, drawdown_chart
from backend.analyzers.backtest import BacktestEngine


def _load_prices(symbols, max_years=7):
    prices = {}
    for sym in symbols:
        try:
            t = yf.Ticker(sym)
            h = t.history(period=f"{max_years}y", auto_adjust=True)
            if not h.empty:
                prices[sym] = h["Close"]
            time.sleep(0.3)
        except:
            pass
    if prices:
        return pd.DataFrame(prices).dropna()
    return pd.DataFrame()


def _metric_html(label, value, sub="", color="#2471c8"):
    return f"""
    <div class="fin-card" style="text-align:center;padding:12px 10px;">
        <div class="fin-card-title" style="font-size:0.7rem;">{label}</div>
        <div class="fin-card-value" style="font-size:1.15rem;color:{color};">{value}</div>
        {f'<div style="font-size:0.72rem;color:#9ca3af;">{sub}</div>' if sub else ''}
    </div>"""


def render():
    st.markdown(badge("Backtest Storico", "⏮️", "dark"), unsafe_allow_html=True)

    # ── Legge simboli dalla session ───────────────────────────────────────────
    symbols = st.session_state.get("pf_symbols", [])
    weights = st.session_state.get("pf_weights", {})

    if not symbols:
        st.warning("⚠️ Prima aggiungi titoli in **Portfolio Builder**.")
        return

    st.markdown(f"**Portafoglio:** {', '.join([chip(s,'blue') for s in symbols])}", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Controlli ─────────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    with c1:
        periods = st.multiselect("Periodi (anni)", [1, 3, 5, 7], default=[1, 3, 5])
    with c2:
        initial_value = st.number_input("Capitale Iniziale (€)", 1000.0, 1_000_000.0, 10_000.0, 1000.0)
    with c3:
        rebal = st.selectbox("Ribilanciamento", ["Nessuno","Mensile","Trimestrale","Annuale"])
        rebal_map = {"Nessuno": None, "Mensile": "monthly", "Trimestrale": "quarterly", "Annuale": "yearly"}

    if st.button("▶️ Esegui Backtest", type="primary", use_container_width=True):
        if not periods:
            st.warning("Seleziona almeno un periodo.")
            return

        max_years = max(periods)
        with st.spinner(f"Caricamento dati storici ({max_years} anni)..."):
            prices_df = _load_prices(symbols, max_years)

        if prices_df.empty:
            st.error("❌ Dati non disponibili. Controlla la connessione e i simboli.")
            return

        # Pesi uniformi se non ottimizzati
        if not weights or set(weights.keys()) != set(symbols):
            n = len(symbols)
            weights = {s: 1/n for s in symbols}

        # Filtra solo simboli con dati
        avail = [s for s in symbols if s in prices_df.columns]
        if len(avail) < len(symbols):
            st.warning(f"Dati mancanti per: {set(symbols)-set(avail)}")
        weights_clean = {s: weights.get(s, 1/len(avail)) for s in avail}
        total_w = sum(weights_clean.values())
        weights_clean = {s: w/total_w for s, w in weights_clean.items()}

        # ── Benchmark (S&P 500) ──────────────────────────────────────────────
        bench_prices = {}
        try:
            t_bench = yf.Ticker("^GSPC")
            h_bench = t_bench.history(period=f"{max_years}y", auto_adjust=True)
            if not h_bench.empty:
                bench_prices["S&P 500"] = h_bench["Close"]
        except:
            pass

        engine = BacktestEngine(prices_df)

        # ── Risultati per periodo ─────────────────────────────────────────────
        for years in sorted(periods):
            st.markdown(f"<br>", unsafe_allow_html=True)
            st.markdown(badge(f"📅 Backtest – {years} Anno{'i' if years>1 else ''}", color="teal"), unsafe_allow_html=True)

            try:
                result = engine.backtest_portfolio(
                    weights=weights_clean,
                    start_date=(prices_df.index[-1] - pd.DateOffset(years=years)).strftime("%Y-%m-%d"),
                    end_date=prices_df.index[-1].strftime("%Y-%m-%d"),
                    initial_value=initial_value,
                    rebalance_frequency=rebal_map[rebal],
                )

                # Metriche
                mc = st.columns(5)
                m_data = [
                    ("Rendimento Totale", f"{result['total_return']*100:+.1f}%",   result['total_return']>=0),
                    ("Rendimento Annuo",  f"{result['annual_return']*100:+.1f}%",  result['annual_return']>=0),
                    ("Sharpe Ratio",      f"{result['sharpe_ratio']:.2f}",         result['sharpe_ratio']>=1),
                    ("Max Drawdown",      f"{result['max_drawdown']*100:.1f}%",     result['max_drawdown']>-0.1),
                    ("Valore Finale",     f"€{result['final_value']:,.0f}",        result['final_value']>initial_value),
                ]
                for col, (lbl, val, positive) in zip(mc, m_data):
                    with col:
                        color = "#22c55e" if positive else "#ef4444"
                        st.markdown(_metric_html(lbl, val, color=color), unsafe_allow_html=True)

                mc2 = st.columns(4)
                m2_data = [
                    ("Volatilità",   f"{result['annual_volatility']*100:.1f}%"),
                    ("Sortino",      f"{result['sortino_ratio']:.2f}"),
                    ("Calmar",       f"{result['calmar_ratio']:.2f}"),
                    ("Win Rate",     f"{result['win_rate']*100:.0f}%"),
                ]
                for col, (lbl, val) in zip(mc2, m2_data):
                    with col:
                        st.markdown(_metric_html(lbl, val, color="#2471c8"), unsafe_allow_html=True)

                # Grafico valore
                pv = pd.Series(result["portfolio_value_over_time"])
                pv.index = pd.to_datetime(list(result["portfolio_value_over_time"].keys()))
                pv_df = pd.DataFrame({"Portafoglio": pv})

                # Aggiungi benchmark se disponibile
                if bench_prices:
                    bench_series = list(bench_prices.values())[0]
                    bench_aligned = bench_series.reindex(pv_df.index, method="nearest").dropna()
                    bench_norm = bench_aligned / bench_aligned.iloc[0] * initial_value
                    pv_df["S&P 500 (benchmark)"] = bench_norm

                fig = line_chart(pv_df, title=f"Evoluzione Portafoglio – {years} Anno/i",
                                 y_title="Valore (€)", height=320)
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.85)")
                fig.add_hline(y=initial_value, line_dash="dot", line_color="#9ca3af",
                              annotation_text=f"Investimento iniziale: €{initial_value:,.0f}")
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

                # Drawdown
                fig_dd = drawdown_chart(pv, height=200)
                fig_dd.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.85)")
                st.plotly_chart(fig_dd, use_container_width=True, config={"displayModeBar": False})

            except Exception as e:
                st.error(f"Backtest {years}y fallito: {e}")
