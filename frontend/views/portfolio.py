"""
Portfolio Builder + Ottimizzazione Markowitz
"""
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import time
from datetime import datetime
from frontend.styles.design import badge, color_pct, chip
from frontend.components.charts import (
    line_chart, pie_chart, efficient_frontier_chart, heatmap_correlation
)
from backend.analyzers.portfolio_optimizer import PortfolioOptimizer
from backend.data_loader import load_prices_smart


def _load_prices(symbols, period="3y"):
    """
    Carica prezzi da Yahoo Finance O Morningstar
    Supporta ticker standard E ISIN fondi
    """
    return load_prices_smart(symbols, period=period)


def render():
    st.title("💼 Costruttore di Portafoglio")

    st.markdown("""
    <div class="fin-card" style="background:#f0fdf4;border-left:4px solid #22c55e;padding:16px;">
        <b>✅ Portafoglio Multi-Asset:</b> Aggiungi asset con ticker Yahoo Finance:
        <ul style="margin:4px 0 0 0;padding-left:20px;">
            <li><b>📈 Azioni</b>: AAPL, ENI.MI, MSFT, GOOGL, etc.</li>
            <li><b>📡 ETF</b>: SWDA.MI, SPY, VWCE.DE, QQQ, etc.</li>
            <li><b>🌾 Commodities</b>: GC=F (Gold), CL=F (Petrolio), NG=F (Gas), etc.</li>
            <li><b>💰 Crypto</b>: BTC-USD, ETH-USD, SOL-USD, etc.</li>
        </ul>
        <div style="margin-top:10px;padding:8px;background:#fef3c7;border-radius:6px;font-size:0.85rem;">
            ⚠️ <b>Non supportati:</b> Fondi comuni con ISIN - usa ETF equivalenti!<br>
            💡 <b>Tip:</b> Usa lo <b>Screener</b> per selezione rapida da liste predefinite
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Session state ─────────────────────────────────────────────────────────
    if "pf_symbols" not in st.session_state:
        st.session_state["pf_symbols"] = []
    if "pf_weights" not in st.session_state:
        st.session_state["pf_weights"] = {}

    # ── Aggiungi simbolo ──────────────────────────────────────────────────────
    col_a, col_b = st.columns([4, 1])
    with col_a:
        new_sym = st.text_input(
            "Aggiungi simbolo (Yahoo Finance)",
            placeholder="Es: AAPL, ENI.MI, VWCE.DE, SPY",
            key="pf_add_input",
            help="Inserisci il simbolo Yahoo Finance del titolo da aggiungere"
        )
    with col_b:
        st.markdown("<br>", unsafe_allow_html=True)
        add_clicked = st.button("➕ Aggiungi", use_container_width=True, type="primary")

    # Gestione aggiunta simbolo
    if add_clicked and new_sym:
        sym = new_sym.strip().upper()
        if not sym:
            st.warning("⚠️ Inserisci un simbolo valido")
        elif sym in st.session_state["pf_symbols"]:
            st.warning(f"⚠️ {sym} è già nel portafoglio")
        else:
            # Valida simbolo con Yahoo Finance
            with st.spinner(f"Verifica {sym}..."):
                try:
                    test_ticker = yf.Ticker(sym)
                    test_hist = test_ticker.history(period="5d")
                    if test_hist.empty:
                        st.error(f"❌ Simbolo {sym} non trovato su Yahoo Finance")
                    else:
                        st.session_state["pf_symbols"].append(sym)
                        st.success(f"✅ {sym} aggiunto al portafoglio!")
                        time.sleep(0.5)
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Errore: {sym} non valido ({str(e)})")

    # Portafogli rapidi (opzionale, in expander)
    with st.expander("📋 Portafogli Rapidi (Opzionale)"):
        st.markdown("Carica un portafoglio predefinito per iniziare velocemente:")
        pre_cols = st.columns(3)
        presets = {
            "🌍 Globale Bilanciato": ["SWDA.MI","EIMI.MI","CSSPX.MI"],
            "🇮🇹 Borsa Italiana":    ["ENI.MI","ISP.MI","ENEL.MI","RACE.MI"],
            "💻 Tech USA":           ["AAPL","MSFT","GOOGL","NVDA"],
        }
        for col, (name, syms) in zip(pre_cols, presets.items()):
            with col:
                if st.button(name, use_container_width=True, key=f"preset_{name}"):
                    st.session_state["pf_symbols"] = syms.copy()
                    st.success(f"✅ Caricato: {name}")
                    time.sleep(0.5)
                    st.rerun()

    # ── Portfolio corrente ────────────────────────────────────────────────────
    symbols = st.session_state["pf_symbols"]

    if not symbols:
        st.info("💡 Aggiungi almeno 2 simboli per costruire il portafoglio.")
        return

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader(f"📊 Portafoglio – {len(symbols)} Titoli")

    # Pesi manuali
    weight_cols = st.columns(min(len(symbols), 5))
    total_w = 0
    for i, sym in enumerate(symbols):
        col = weight_cols[i % 5]
        default_w = round(100 / len(symbols), 1)
        w = col.number_input(sym, 0.0, 100.0, default_w, 1.0, key=f"w_{sym}", label_visibility="visible")
        st.session_state["pf_weights"][sym] = w / 100
        total_w += w

    if abs(total_w - 100) > 0.5:
        st.warning(f"⚠️ I pesi sommano a {total_w:.1f}% (devono fare 100%)")

    # Rimuovi simboli
    rem_cols = st.columns(len(symbols))
    for col, sym in zip(rem_cols, symbols):
        if col.button(f"✕ {sym}", key=f"rem_{sym}"):
            st.session_state["pf_symbols"].remove(sym)
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Azioni ────────────────────────────────────────────────────────────────
    period_sel = st.selectbox("Periodo storico", ["1y","2y","3y","5y"], index=2)
    act_cols = st.columns(3)

    with act_cols[0]:
        show_data = st.button("📈 Visualizza Storico", use_container_width=True)
    with act_cols[1]:
        optimize = st.button("🎯 Ottimizza Markowitz", type="primary", use_container_width=True)
    with act_cols[2]:
        generate_pdf = st.button("📄 Genera Report PDF", use_container_width=True)

    # ── Carica prezzi ─────────────────────────────────────────────────────────
    if show_data or optimize or st.session_state.get("pf_prices_loaded"):
        with st.spinner("Caricamento prezzi..."):
            prices_df = _load_prices(symbols, period=period_sel)

        if prices_df.empty:
            st.error("❌ Impossibile caricare i prezzi per questi simboli.")
            st.warning("""
            **Possibili cause:**
            - Simboli non validi su Yahoo Finance
            - ISIN fondi comuni non supportati (es: IT0005239881)
            - Problemi di connessione

            **Soluzioni:**
            - Usa ticker standard (AAPL, SPY, ENI.MI)
            - Sostituisci fondi con ETF equivalenti
            - Verifica simboli su [Yahoo Finance](https://finance.yahoo.com)
            """)
            return

        st.session_state["pf_prices_loaded"] = True

        # Performance normalizzata
        norm = (prices_df / prices_df.iloc[0]) * 100
        fig = line_chart(norm, title="Performance Normalizzata (Base 100)", normalize=False, height=320)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.85)")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # Matrice correlazione
        if len(prices_df.columns) >= 2:
            corr = prices_df.pct_change().dropna().corr()
            fig_corr = heatmap_correlation(corr, height=300)
            fig_corr.update_layout(paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_corr, use_container_width=True, config={"displayModeBar": False})

        # ── Ottimizzazione ────────────────────────────────────────────────────
        if optimize and len(prices_df.columns) >= 2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("🎯 Ottimizzazione Markowitz")

            opt_type = st.selectbox("Strategia", [
                "Massimizza Sharpe Ratio",
                "Minimizza Volatilità",
            ])

            with st.spinner("Ottimizzazione in corso..."):
                try:
                    optimizer = PortfolioOptimizer(prices_df)
                    optimizer.calculate_expected_returns()
                    optimizer.calculate_covariance_matrix()

                    if "Sharpe" in opt_type:
                        result = optimizer.optimize_max_sharpe()
                    else:
                        result = optimizer.optimize_min_volatility()

                    weights_opt = result["weights"]
                    exp_ret = result["expected_return"]
                    vol     = result["volatility"]
                    sharpe  = result["sharpe_ratio"]

                    # ── Metriche ──────────────────────────────────────────────
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.metric("Rendimento Atteso", f"{exp_ret*100:.2f}%")
                    with m2:
                        st.metric("Volatilità", f"{vol*100:.2f}%")
                    with m3:
                        st.metric("Sharpe Ratio", f"{sharpe:.2f}")

                    # ── Pesi ottimali ─────────────────────────────────────────
                    col_pie, col_weights = st.columns(2)

                    with col_pie:
                        labels = [k for k, v in weights_opt.items() if v > 0.01]
                        values = [v * 100 for v in weights_opt.values() if v > 0.01]
                        fig_pie = pie_chart(labels, values, title="Allocazione Ottimale", height=300)
                        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)")
                        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

                    with col_weights:
                        st.markdown("**Pesi Ottimali:**")
                        rows_w = "".join([f"""
                        <tr>
                            <td style="font-weight:600;">{sym}</td>
                            <td>{chip(f'{w*100:.1f}%', 'blue')}</td>
                            <td>
                                <div style="background:#e5eef8;border-radius:8px;height:10px;width:100%;overflow:hidden;">
                                    <div style="background:#2471c8;height:10px;width:{w*100:.0f}%;border-radius:8px;"></div>
                                </div>
                            </td>
                        </tr>
                        """ for sym, w in weights_opt.items() if w > 0.01])
                        st.markdown(f"""
                        <div class="fin-card" style="padding:0;overflow:hidden;">
                        <table class="fin-table"><thead><tr>
                            <th>Simbolo</th><th>Peso</th><th>Barra</th>
                        </tr></thead><tbody>{rows_w}</tbody></table></div>
                        """, unsafe_allow_html=True)

                    # ── Frontiera Efficiente ──────────────────────────────────
                    with st.spinner("Calcolo frontiera efficiente..."):
                        vols_ef, rets_ef = optimizer.calculate_efficient_frontier(points=40)

                    if vols_ef and rets_ef:
                        asset_vols = [float(np.sqrt(optimizer.S.loc[s, s])) for s in optimizer.symbols]
                        asset_rets = [float(optimizer.mu[s]) for s in optimizer.symbols]
                        fig_ef = efficient_frontier_chart(
                            vols_ef, rets_ef,
                            vol, exp_ret,
                            optimizer.symbols, asset_vols, asset_rets,
                            height=420,
                        )
                        fig_ef.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.85)")
                        st.plotly_chart(fig_ef, use_container_width=True, config={"displayModeBar": False})

                    # Salva pesi ottimali
                    st.session_state["pf_weights"] = weights_opt

                except Exception as e:
                    st.error(f"❌ Errore ottimizzazione: {e}")

    # ── PDF Report Generation ─────────────────────────────────────────────────
    if generate_pdf:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📄 Generazione Report PDF")

        # Collect data for PDF
        portfolio_name = st.text_input(
            "Nome Portafoglio",
            value=f"Portfolio-{datetime.now().strftime('%Y%m%d')}",
            key="pdf_portfolio_name"
        )

        initial_value = st.number_input(
            "Capitale Iniziale (€)",
            min_value=1000.0,
            max_value=10_000_000.0,
            value=10000.0,
            step=1000.0,
            key="pdf_initial_value"
        )

        include_backtest = st.checkbox("Includi Backtest", value=True, key="pdf_backtest")
        include_predictions = st.checkbox("Includi Predizioni", value=True, key="pdf_predictions")

        if st.button("⬇️ Scarica Report PDF", type="primary", use_container_width=True):
            with st.spinner("Generazione report PDF in corso... ⏳"):
                try:
                    from backend.reports.pdf_generator import generate_portfolio_report
                    from backend.analyzers.backtest import BacktestEngine
                    from backend.models.predictor import PortfolioPredictor
                    from datetime import datetime

                    # Normalize weights
                    weights = st.session_state.get("pf_weights", {})
                    if not weights or set(weights.keys()) != set(symbols):
                        weights = {s: 1/len(symbols) for s in symbols}
                    total_w = sum(weights.values())
                    weights_clean = {s: w/total_w for s, w in weights.items()}

                    # Load prices for backtest and predictions
                    backtest_results = None
                    prediction_results = None

                    if include_backtest or include_predictions:
                        prices_df = _load_prices(symbols, period="3y")

                        if not prices_df.empty:
                            # Backtest
                            if include_backtest:
                                try:
                                    engine = BacktestEngine(prices_df)
                                    backtest_results = engine.backtest_portfolio(
                                        weights=weights_clean,
                                        start_date=(prices_df.index[-1] - pd.DateOffset(years=1)).strftime("%Y-%m-%d"),
                                        end_date=prices_df.index[-1].strftime("%Y-%m-%d"),
                                        initial_value=initial_value,
                                    )
                                except Exception as e:
                                    st.warning(f"⚠️ Backtest non disponibile: {e}")

                            # Predictions
                            if include_predictions:
                                try:
                                    predictor = PortfolioPredictor(prices_df)
                                    scenarios = predictor.predict_portfolio_scenarios(
                                        weights=weights_clean,
                                        months=6,
                                        initial_value=initial_value,
                                        num_simulations=5000,
                                    )
                                    prediction_results = {"scenarios": scenarios}
                                except Exception as e:
                                    st.warning(f"⚠️ Predizioni non disponibili: {e}")

                    # Generate PDF
                    pdf_bytes = generate_portfolio_report(
                        portfolio_name=portfolio_name,
                        symbols=symbols,
                        weights=weights_clean,
                        initial_value=initial_value,
                        backtest_results=backtest_results,
                        prediction_results=prediction_results,
                    )

                    # Download button
                    st.success("✅ Report PDF generato con successo!")

                    filename = f"{portfolio_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"

                    st.download_button(
                        label="📥 Scarica Report",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True,
                    )

                except Exception as e:
                    st.error(f"❌ Errore generazione PDF: {e}")
                    import traceback
                    st.code(traceback.format_exc())
