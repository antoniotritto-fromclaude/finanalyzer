"""
Portfolio Builder + Ottimizzazione Markowitz
"""
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import time
from frontend.styles.design import badge, color_pct, chip
from frontend.components.charts import (
    line_chart, pie_chart, efficient_frontier_chart, heatmap_correlation
)
from backend.analyzers.portfolio_optimizer import PortfolioOptimizer


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
        df = pd.DataFrame(prices).dropna()
        return df
    return pd.DataFrame()


def render():
    st.title("💼 Costruttore di Portafoglio")

    st.markdown("""
    <div class="fin-card" style="background:#f0fdf4;border-left:4px solid #22c55e;padding:16px;">
        <b>✅ Portafoglio Multi-Asset:</b> Puoi aggiungere qualsiasi asset:
        <ul style="margin:4px 0 0 0;padding-left:20px;">
            <li><b>📈 Azioni</b>: AAPL, ENI.MI, MSFT, etc.</li>
            <li><b>📡 ETF</b>: SWDA.MI, SPY, VWCE.DE, etc.</li>
            <li><b>🌾 Commodities</b>: GC=F (Gold), CL=F (Petrolio), etc.</li>
            <li><b>💰 Crypto</b>: BTC-USD, ETH-USD, etc.</li>
        </ul>
        💡 <b>Tip:</b> Usa lo <b>Screener</b> per aggiungere rapidamente titoli da liste predef inite!
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
    act_cols = st.columns(2)

    with act_cols[0]:
        show_data = st.button("📈 Visualizza Storico", use_container_width=True)
    with act_cols[1]:
        optimize = st.button("🎯 Ottimizza Markowitz", type="primary", use_container_width=True)

    # ── Carica prezzi ─────────────────────────────────────────────────────────
    if show_data or optimize or st.session_state.get("pf_prices_loaded"):
        with st.spinner("Caricamento prezzi..."):
            prices_df = _load_prices(symbols, period=period_sel)

        if prices_df.empty:
            st.error("❌ Impossibile caricare i prezzi. Verifica i simboli e la connessione.")
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
