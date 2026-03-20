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
from backend.data_loader import load_prices_smart
from frontend.utils.formatters import format_currency_eur, format_number_eur, format_percentage


def _load_prices(symbols, max_years=7):
    """
    Carica prezzi da Yahoo Finance O Morningstar
    Supporta ticker standard E ISIN fondi
    """
    period = f"{max_years}y"
    return load_prices_smart(symbols, period=period)


def _metric_html(label, value, sub="", color="#2471c8"):
    return f"""
    <div class="fin-card" style="text-align:center;padding:12px 10px;">
        <div class="fin-card-title" style="font-size:0.7rem;">{label}</div>
        <div class="fin-card-value" style="font-size:1.15rem;color:{color};">{value}</div>
        {f'<div style="font-size:0.72rem;color:#9ca3af;">{sub}</div>' if sub else ''}
    </div>"""


def render():
    st.title("📈 Backtest Storico")
    st.markdown("Testa le performance del tuo portafoglio su dati storici")
    st.markdown("---")

    # ── Legge simboli dalla session ───────────────────────────────────────────
    symbols = st.session_state.get("pf_symbols", [])
    weights = st.session_state.get("pf_weights", {})

    if not symbols:
        st.warning("⚠️ Prima aggiungi titoli nella sezione **Portafoglio**.")
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
            st.error("❌ Dati storici non disponibili per questi simboli.")
            st.warning("""
            **Possibili cause:**
            - Simboli non validi su Yahoo Finance (ISIN fondi non supportati)
            - Dati storici insufficienti

            **Soluzione:** Usa solo ticker standard (Azioni, ETF, Commodities con formato Yahoo Finance)
            """)
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
            st.subheader(f"📅 Backtest – {years} Anno{'i' if years>1 else ''}")

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
                    ("Rendimento Totale", ("+" if result['total_return']>=0 else "") + format_percentage(result['total_return']*100, decimals=1),   result['total_return']>=0),
                    ("Rendimento Annuo",  ("+" if result['annual_return']>=0 else "") + format_percentage(result['annual_return']*100, decimals=1),  result['annual_return']>=0),
                    ("Sharpe Ratio",      format_number_eur(result['sharpe_ratio'], decimals=2),         result['sharpe_ratio']>=1),
                    ("Max Drawdown",      format_percentage(result['max_drawdown']*100, decimals=1),     result['max_drawdown']>-0.1),
                    ("Valore Finale",     format_currency_eur(result['final_value'], decimals=0),        result['final_value']>initial_value),
                ]
                for col, (lbl, val, positive) in zip(mc, m_data):
                    with col:
                        color = "#22c55e" if positive else "#ef4444"
                        st.markdown(_metric_html(lbl, val, color=color), unsafe_allow_html=True)

                mc2 = st.columns(4)
                m2_data = [
                    ("Volatilità",   format_percentage(result['annual_volatility']*100, decimals=1)),
                    ("Sortino",      format_number_eur(result['sortino_ratio'], decimals=2)),
                    ("Calmar",       format_number_eur(result['calmar_ratio'], decimals=2)),
                    ("Win Rate",     format_percentage(result['win_rate']*100, decimals=0)),
                ]
                for col, (lbl, val) in zip(mc2, m2_data):
                    with col:
                        st.markdown(_metric_html(lbl, val, color="#2471c8"), unsafe_allow_html=True)

                # ── Grafico portafoglio totale ────────────────────────────────────────
                st.markdown("#### 📊 Andamento Portafoglio Totale")
                pv = pd.Series(result["portfolio_value_over_time"])
                pv.index = pd.to_datetime(list(result["portfolio_value_over_time"].keys()))
                pv_df = pd.DataFrame({"Portafoglio Totale": pv})

                # Aggiungi benchmark se disponibile
                if bench_prices:
                    bench_series = list(bench_prices.values())[0]
                    bench_aligned = bench_series.reindex(pv_df.index, method="nearest").dropna()
                    bench_norm = bench_aligned / bench_aligned.iloc[0] * initial_value
                    pv_df["S&P 500 (benchmark)"] = bench_norm

                fig = line_chart(pv_df, title=f"Valore Complessivo Portafoglio – {years} Anno/i",
                                 y_title="Valore (€)", height=320)
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.85)")
                fig.add_hline(y=initial_value, line_dash="dot", line_color="#9ca3af",
                              annotation_text=f"Investimento iniziale: {format_currency_eur(initial_value, decimals=0)}")
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

                # ── Grafico componenti individuali ────────────────────────────────────
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### 📈 Performance Componenti Individuali")

                st.info(f"""
                **💡 Come viene calcolato il portafoglio totale:**

                Il valore del portafoglio è la **somma pesata** dei singoli strumenti secondo i pesi assegnati:

                {''.join([f"- **{symbol}**: {format_percentage(weights_clean[symbol]*100, decimals=1)} del capitale totale ({format_currency_eur(initial_value * weights_clean[symbol], decimals=0)})  " for symbol in avail])}

                Il rendimento totale NON è la media semplice, ma tiene conto dei pesi di ciascuno strumento.
                """)

                # Calcola performance individuali normalizzate
                start_date = (prices_df.index[-1] - pd.DateOffset(years=years))
                individual_df = pd.DataFrame()

                for symbol in avail:
                    symbol_prices = prices_df[symbol]
                    symbol_prices_period = symbol_prices[symbol_prices.index >= start_date]

                    if len(symbol_prices_period) > 0:
                        # Normalizza a initial_value * weight
                        weight = weights_clean[symbol]
                        investment = initial_value * weight
                        normalized = symbol_prices_period / symbol_prices_period.iloc[0] * investment
                        individual_df[symbol] = normalized

                if not individual_df.empty:
                    fig_ind = line_chart(individual_df,
                                        title=f"Contributo Individuale di Ogni Strumento – {years} Anno/i",
                                        y_title="Valore (€)", height=300)
                    fig_ind.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.85)")
                    st.plotly_chart(fig_ind, use_container_width=True, config={"displayModeBar": False})

                    # Tabella performance individuali
                    st.markdown("**Performance Individuali:**")
                    perf_rows = []
                    for symbol in avail:
                        if symbol in individual_df.columns:
                            start_val = individual_df[symbol].iloc[0]
                            end_val = individual_df[symbol].iloc[-1]
                            ret = (end_val / start_val - 1) * 100
                            weight = weights_clean[symbol]
                            contribution = ret * weight

                            perf_rows.append({
                                "Strumento": symbol,
                                "Peso": format_percentage(weight * 100, decimals=1),
                                "Rendimento": ("+" if ret >= 0 else "") + format_percentage(ret, decimals=1),
                                "Contributo al Totale": ("+" if contribution >= 0 else "") + format_percentage(contribution, decimals=2),
                            })

                    perf_table = pd.DataFrame(perf_rows)
                    st.dataframe(perf_table, use_container_width=True, hide_index=True)
                else:
                    st.warning("⚠️ Dati insufficienti per calcolare le performance individuali")

                # Drawdown
                fig_dd = drawdown_chart(pv, height=200)
                fig_dd.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.85)")
                st.plotly_chart(fig_dd, use_container_width=True, config={"displayModeBar": False})

            except Exception as e:
                st.error(f"Backtest {years}y fallito: {e}")
