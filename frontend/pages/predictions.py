"""
Predizioni Future – Scenari Monte Carlo a 6 mesi
"""
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import time
from frontend.styles.design import badge, color_pct, chip
from frontend.components.charts import prediction_chart, pie_chart, bar_chart
from backend.models.predictor import PortfolioPredictor


def _load_prices(symbols, period="3y"):
    prices = {}
    for sym in symbols:
        try:
            t = yf.Ticker(sym)
            h = t.history(period=period, auto_adjust=True)
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
    <div class="fin-card" style="text-align:center;padding:14px 10px;">
        <div class="fin-card-title" style="font-size:0.7rem;">{label}</div>
        <div class="fin-card-value" style="font-size:1.1rem;color:{color};">{value}</div>
        {f'<div style="font-size:0.72rem;color:#9ca3af;margin-top:2px;">{sub}</div>' if sub else ''}
    </div>"""


def render():
    st.markdown(badge("Predizioni Future", "🔮", "purple"), unsafe_allow_html=True)

    symbols = st.session_state.get("pf_symbols", [])
    weights = st.session_state.get("pf_weights", {})

    if not symbols:
        st.warning("⚠️ Aggiungi titoli in **Portfolio Builder** prima.")
        return

    st.markdown(f"**Portafoglio:** {' · '.join(symbols)}")
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Controlli ─────────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    with c1:
        months = st.slider("Orizzonte predittivo (mesi)", 1, 12, 6)
    with c2:
        initial_value = st.number_input("Capitale Iniziale (€)", 1000.0, 1_000_000.0, 10_000.0, 1000.0)
    with c3:
        n_sims = st.select_slider("Simulazioni Monte Carlo", [1000, 5000, 10000, 25000], value=10000)

    if st.button("🔮 Genera Scenari", type="primary", use_container_width=True):
        with st.spinner("Caricamento dati storici..."):
            prices_df = _load_prices(symbols, period="3y")

        if prices_df.empty:
            st.error("❌ Dati non disponibili.")
            return

        # Pesi pulizia
        avail = [s for s in symbols if s in prices_df.columns]
        if not weights or set(weights.keys()) != set(avail):
            weights = {s: 1/len(avail) for s in avail}
        weights_clean = {s: weights.get(s, 1/len(avail)) for s in avail}
        total_w = sum(weights_clean.values())
        weights_clean = {s: w/total_w for s, w in weights_clean.items()}

        with st.spinner(f"Esecuzione {n_sims:,} simulazioni Monte Carlo..."):
            predictor = PortfolioPredictor(prices_df)
            scenarios = predictor.predict_portfolio_scenarios(
                weights=weights_clean,
                months=months,
                initial_value=initial_value,
                num_simulations=n_sims,
            )
            var_result = predictor.calculate_value_at_risk(
                weights=weights_clean,
                initial_value=initial_value,
            )
            exp_perf = predictor.calculate_expected_performance(
                weights=weights_clean,
                months=months,
            )

        # ── Scenari principali ────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(badge(f"Scenari a {months} Mesi", "📊", "teal"), unsafe_allow_html=True)

        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            s = scenarios["best_scenario"]
            st.markdown(f"""
            <div class="fin-card" style="border-left:4px solid #22c55e;text-align:center;padding:20px;">
                <div style="font-size:0.8rem;font-weight:700;color:#15803d;text-transform:uppercase;letter-spacing:0.5px;">
                    🟢 Scenario Migliore
                </div>
                <div style="font-size:0.72rem;color:#9ca3af;margin:4px 0 10px;">Percentile 95°</div>
                <div style="font-size:2rem;font-weight:800;color:#22c55e;">€{s['final_value']:,.0f}</div>
                <div style="font-size:1.1rem;font-weight:700;color:#22c55e;">{s['return_percentage']:+.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        with sc2:
            s = scenarios["normal_scenario"]
            st.markdown(f"""
            <div class="fin-card" style="border-left:4px solid #2471c8;text-align:center;padding:20px;">
                <div style="font-size:0.8rem;font-weight:700;color:#1d4ed8;text-transform:uppercase;letter-spacing:0.5px;">
                    🟡 Scenario Atteso
                </div>
                <div style="font-size:0.72rem;color:#9ca3af;margin:4px 0 10px;">Percentile 50° (Mediana)</div>
                <div style="font-size:2rem;font-weight:800;color:#2471c8;">€{s['final_value']:,.0f}</div>
                <div style="font-size:1.1rem;font-weight:700;color:#2471c8;">{s['return_percentage']:+.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        with sc3:
            s = scenarios["worst_scenario"]
            st.markdown(f"""
            <div class="fin-card" style="border-left:4px solid #ef4444;text-align:center;padding:20px;">
                <div style="font-size:0.8rem;font-weight:700;color:#b91c1c;text-transform:uppercase;letter-spacing:0.5px;">
                    🔴 Scenario Peggiore
                </div>
                <div style="font-size:0.72rem;color:#9ca3af;margin:4px 0 10px;">Percentile 5° (VaR 95%)</div>
                <div style="font-size:2rem;font-weight:800;color:#ef4444;">€{s['final_value']:,.0f}</div>
                <div style="font-size:1.1rem;font-weight:700;color:#ef4444;">{s['return_percentage']:+.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        # ── Grafico predizioni ────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        if "predictions" in scenarios:
            pred = scenarios["predictions"]
            fig_pred = prediction_chart(
                pred["dates"],
                pred["normal_path"],
                pred["best_path"],
                pred["worst_path"],
                initial_value,
                height=380,
            )
            fig_pred.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.85)")
            st.plotly_chart(fig_pred, use_container_width=True, config={"displayModeBar": False})

        # ── Statistiche ───────────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(badge("Statistiche Predittive", "📐", "green"), unsafe_allow_html=True)

        stats = scenarios["statistics"]
        sc_cols = st.columns(4)
        stat_data = [
            ("Valore Medio Atteso", f"€{stats['mean_value']:,.0f}", "#2471c8"),
            ("Deviazione Standard",  f"€{stats['std_value']:,.0f}", "#f59e0b"),
            ("Prob. di Perdita",     f"{stats['probability_of_loss']*100:.1f}%",
             "#ef4444" if stats['probability_of_loss']>0.3 else "#22c55e"),
            ("Rendimento Atteso",    f"{stats['expected_return']*100:+.1f}%",
             "#22c55e" if stats['expected_return']>=0 else "#ef4444"),
        ]
        for col, (lbl, val, color) in zip(sc_cols, stat_data):
            with col:
                st.markdown(_metric_html(lbl, val, color=color), unsafe_allow_html=True)

        # ── VaR ───────────────────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(badge("Value at Risk (VaR) – 1 Giorno", "⚠️", "orange"), unsafe_allow_html=True)
        v1, v2, v3 = st.columns(3)
        with v1:
            st.markdown(_metric_html(
                "VaR 95% (perdita max)",
                f"€{abs(var_result['var_value']):,.0f}",
                f"={abs(var_result['var_percentage']):.2f}%",
                "#f59e0b"
            ), unsafe_allow_html=True)
        with v2:
            st.markdown(_metric_html(
                "CVaR 95% (expected shortfall)",
                f"€{abs(var_result['cvar_value']):,.0f}",
                f"={abs(var_result['cvar_percentage']):.2f}%",
                "#ef4444"
            ), unsafe_allow_html=True)
        with v3:
            vol_p = exp_perf.get("expected_volatility_period", 0)
            st.markdown(_metric_html(
                f"Volatilità attesa ({months}m)",
                f"{vol_p*100:.1f}%",
                "su base storica",
                "#8b5cf6"
            ), unsafe_allow_html=True)

        st.markdown("""
        <div class="fin-card" style="background:#fefce8;border-left:4px solid #f59e0b;margin-top:1rem;">
            <b>⚠️ Disclaimer:</b> Le predizioni sono basate su simulazioni statistiche dei dati storici.
            Non costituiscono consulenza finanziaria. I rendimenti passati non garantiscono quelli futuri.
        </div>
        """, unsafe_allow_html=True)
