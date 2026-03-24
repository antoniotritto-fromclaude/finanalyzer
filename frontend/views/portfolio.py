"""
💼 Portfolio Dashboard - Unified Flow
Complete portfolio analysis in one page: composition, performance, backtest, predictions
"""
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from frontend.styles.design import badge, color_pct, chip
from frontend.components.charts import (
    line_chart, pie_chart, efficient_frontier_chart, heatmap_correlation
)
from backend.analyzers.portfolio_optimizer import PortfolioOptimizer
from backend.data_loader import load_prices_smart


# ══════════════════════════════════════════════════════════════════════
# 🎨 DARK THEME CSS (inspired by provided image)
# ══════════════════════════════════════════════════════════════════════

DARK_THEME_CSS = """
<style>
/* Dark Dashboard Theme */
.portfolio-dashboard {
    background: linear-gradient(135deg, #0A1628 0%, #1E293B 100%);
    border-radius: 16px;
    padding: 30px;
    margin: 20px 0;
    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
}

.metric-card-dark {
    background: linear-gradient(135deg, #1E293B 0%, #334155 100%);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    transition: all 0.3s ease;
}

.metric-card-dark:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(212, 175, 55, 0.2);
    border-color: #D4AF37;
}

.metric-label-dark {
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #9CA3AF;
    margin-bottom: 8px;
}

.metric-value-dark {
    font-size: 2rem;
    font-weight: 800;
    color: #FFFFFF;
    font-variant-numeric: tabular-nums;
}

.metric-value-dark.positive { color: #10B981; }
.metric-value-dark.negative { color: #EF4444; }
.metric-value-dark.gold { color: #D4AF37; }

.section-header-dark {
    font-size: 1.8rem;
    font-weight: 800;
    color: #FFFFFF !important;
    margin: 40px 0 20px 0;
    padding-bottom: 12px;
    border-bottom: 2px solid #D4AF37;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.composition-table {
    background: #1E293B;
    border-radius: 12px;
    overflow: hidden;
    margin: 20px 0;
}

.composition-table table {
    width: 100%;
    border-collapse: collapse;
}

.composition-table th {
    background: #0A1628;
    color: #D4AF37;
    padding: 15px;
    text-align: left;
    font-weight: 700;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.composition-table td {
    padding: 12px 15px;
    color: #E5E7EB;
    border-bottom: 1px solid #334155;
}

.composition-table tr:hover td {
    background: #334155;
}

.weight-bar {
    background: #334155;
    border-radius: 8px;
    height: 8px;
    width: 100%;
    overflow: hidden;
}

.weight-bar-fill {
    background: linear-gradient(90deg, #D4AF37 0%, #B8860B 100%);
    height: 100%;
    border-radius: 8px;
    transition: width 0.5s ease;
}

.status-badge {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.status-badge.success {
    background: rgba(16, 185, 129, 0.2);
    color: #10B981;
    border: 1px solid #10B981;
}

.status-badge.warning {
    background: rgba(245, 158, 11, 0.2);
    color: #F59E0B;
    border: 1px solid #F59E0B;
}

.status-badge.info {
    background: rgba(59, 130, 246, 0.2);
    color: #3B82F6;
    border: 1px solid #3B82F6;
}
</style>
"""


# ══════════════════════════════════════════════════════════════════════
# 🔧 HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════

def _load_prices(symbols, period="3y"):
    """Load prices from Yahoo Finance or Morningstar"""
    return load_prices_smart(symbols, period=period)


def _create_metric_card(label, value, trend=None, col_class=""):
    """Create dark themed metric card"""
    trend_class = ""
    if trend == "positive":
        trend_class = "positive"
    elif trend == "negative":
        trend_class = "negative"
    elif trend == "gold":
        trend_class = "gold"

    return f"""
    <div class="metric-card-dark {col_class}">
        <div class="metric-label-dark">{label}</div>
        <div class="metric-value-dark {trend_class}">{value}</div>
    </div>
    """


# ══════════════════════════════════════════════════════════════════════
# 🎯 MAIN RENDER FUNCTION
# ══════════════════════════════════════════════════════════════════════

def render():
    # Inject dark theme CSS
    st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)

    st.markdown('<h1 style="color:#FFFFFF !important;font-size:2.5rem;font-weight:800;margin-bottom:20px;">💼 Portfolio Dashboard</h1>', unsafe_allow_html=True)

    # ── Session State Init ────────────────────────────────────────────
    if "pf_symbols" not in st.session_state:
        st.session_state["pf_symbols"] = []
    if "pf_weights" not in st.session_state:
        st.session_state["pf_weights"] = {}

    # ══════════════════════════════════════════════════════════════════
    # 📝 STEP 1: PORTFOLIO SETUP
    # ══════════════════════════════════════════════════════════════════

    st.markdown('<h3 style="color:#FFFFFF !important;font-size:1.5rem;font-weight:700;margin:20px 0;">🎯 Configurazione Portafoglio</h3>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        <div style="background:#1E293B;border-left:4px solid #D4AF37;padding:16px;border-radius:8px;color:#E5E7EB;">
            <b style="color:#D4AF37;">✅ Asset Supportati:</b>
            <ul style="margin:8px 0 0 0;padding-left:20px;color:#9CA3AF;">
                <li><b>📈 Stocks</b>: AAPL, ENI.MI, MSFT, GOOGL</li>
                <li><b>📡 ETFs</b>: SWDA.MI, SPY, VWCE.DE, QQQ</li>
                <li><b>🌾 Commodities</b>: GC=F (Gold), CL=F (Oil)</li>
                <li><b>💰 Crypto</b>: BTC-USD, ETH-USD</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        period_sel = st.selectbox(
            "📅 Periodo Analisi",
            ["1y", "2y", "3y", "5y", "10y", "max"],
            index=2,
            help="Periodo per performance e backtest"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Advanced Asset Search ─────────────────────────────────────────
    with st.expander("🔍 Ricerca Avanzata Asset (Azioni, ETF, Crypto, Commodities)", expanded=False):
        st.markdown("""
        <div style="background:#1E3A44;padding:12px;border-left:4px solid #D4AF37;border-radius:8px;margin-bottom:12px;">
            <span style="color:#FFFFFF;font-size:0.85rem;">
                🌐 <b>Cerca tra migliaia di asset</b>: Azioni globali, ETF, Criptovalute, Commodities
            </span>
        </div>
        """, unsafe_allow_html=True)

        search_query = st.text_input(
            "🔎 Cerca asset",
            placeholder="es: Apple, Bitcoin, Gold, S&P 500 ETF...",
            key="asset_search_query"
        )

        if search_query and len(search_query) >= 2:
            from backend.data_sources.asset_search import search_all_assets

            with st.spinner("🔍 Ricerca in corso..."):
                results = search_all_assets(search_query, max_results=10)

            # Display results by category
            tabs = st.tabs(["📈 Azioni", "📡 ETF", "💰 Crypto", "🌾 Commodities"])

            with tabs[0]:  # Stocks
                if results['stocks']:
                    for asset in results['stocks']:
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"**{asset['symbol']}** - {asset['name']}")
                            st.caption(f"📍 {asset['exchange']} • {asset['currency']}")
                        with col2:
                            if st.button("➕", key=f"add_stock_{asset['symbol']}", help="Aggiungi al portafoglio"):
                                if asset['symbol'] not in st.session_state["pf_symbols"]:
                                    st.session_state["pf_symbols"].append(asset['symbol'])
                                    st.success(f"✅ {asset['symbol']} aggiunto!")
                                    st.rerun()
                        st.divider()
                else:
                    st.info("Nessuna azione trovata")

            with tabs[1]:  # ETF
                if results['etfs']:
                    for asset in results['etfs']:
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"**{asset['symbol']}** - {asset['name']}")
                            st.caption(f"📍 {asset['exchange']} • {asset['currency']}")
                        with col2:
                            if st.button("➕", key=f"add_etf_{asset['symbol']}", help="Aggiungi al portafoglio"):
                                if asset['symbol'] not in st.session_state["pf_symbols"]:
                                    st.session_state["pf_symbols"].append(asset['symbol'])
                                    st.success(f"✅ {asset['symbol']} aggiunto!")
                                    st.rerun()
                        st.divider()
                else:
                    st.info("Nessun ETF trovato")

            with tabs[2]:  # Crypto
                if results['crypto']:
                    for asset in results['crypto']:
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"**{asset['symbol']}** - {asset['name']}")
                            st.caption(f"💱 {asset['currency']}")
                        with col2:
                            if st.button("➕", key=f"add_crypto_{asset['symbol']}", help="Aggiungi al portafoglio"):
                                if asset['symbol'] not in st.session_state["pf_symbols"]:
                                    st.session_state["pf_symbols"].append(asset['symbol'])
                                    st.success(f"✅ {asset['symbol']} aggiunto!")
                                    st.rerun()
                        st.divider()
                else:
                    st.info("Nessuna crypto trovata")

            with tabs[3]:  # Commodities
                if results['commodities']:
                    for asset in results['commodities']:
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"**{asset['symbol']}** - {asset['name']}")
                            st.caption(f"💵 {asset['currency']}")
                        with col2:
                            if st.button("➕", key=f"add_comm_{asset['symbol']}", help="Aggiungi al portafoglio"):
                                if asset['symbol'] not in st.session_state["pf_symbols"]:
                                    st.session_state["pf_symbols"].append(asset['symbol'])
                                    st.success(f"✅ {asset['symbol']} aggiunto!")
                                    st.rerun()
                        st.divider()
                else:
                    st.info("Nessuna commodity trovata")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Symbol Input (Direct) ─────────────────────────────────────────
    cols_input = st.columns([3, 1, 1])

    with cols_input[0]:
        new_symbol = st.text_input(
            "⚡ Aggiungi Asset Diretto (Ticker)",
            placeholder="es: AAPL, ENI.MI, BTC-USD, GC=F",
            key="new_symbol_input",
            help="Inserisci direttamente il ticker se lo conosci"
        ).upper().strip()

    with cols_input[1]:
        if st.button("➕ Aggiungi", type="primary", width="stretch"):
            if new_symbol and new_symbol not in st.session_state["pf_symbols"]:
                st.session_state["pf_symbols"].append(new_symbol)
                st.rerun()
            elif new_symbol in st.session_state["pf_symbols"]:
                st.warning(f"⚠️ {new_symbol} già presente!")

    with cols_input[2]:
        if st.button("🗑️ Reset", width="stretch"):
            st.session_state["pf_symbols"] = []
            st.session_state["pf_weights"] = {}
            st.rerun()

    # ── Save Portfolio ────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)

    save_cols = st.columns([3, 1])

    with save_cols[0]:
        portfolio_name = st.text_input(
            "💾 Nome Portafoglio",
            placeholder="es: Portafoglio Difensivo, Tech Growth, etc.",
            key="portfolio_name_input"
        ).strip()

    with save_cols[1]:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Salva Portafoglio", type="secondary", width="stretch"):
            if portfolio_name and st.session_state["pf_symbols"]:
                if "saved_portfolios" not in st.session_state:
                    st.session_state.saved_portfolios = {}

                st.session_state.saved_portfolios[portfolio_name] = {
                    "symbols": st.session_state["pf_symbols"].copy(),
                    "weights": st.session_state.get("pf_weights", {}).copy(),
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                }

                # Save to persistent storage
                from backend.storage.data_manager import save_portfolios
                if save_portfolios(st.session_state.saved_portfolios):
                    st.success(f"✅ Portafoglio '{portfolio_name}' salvato con successo!")
                else:
                    st.error(f"❌ Errore nel salvataggio del portafoglio")

                st.rerun()
            elif not portfolio_name:
                st.warning("⚠️ Inserisci un nome per il portafoglio")
            elif not st.session_state["pf_symbols"]:
                st.warning("⚠️ Aggiungi almeno un asset prima di salvare")

    # ── Current Portfolio ─────────────────────────────────────────────
    symbols = st.session_state["pf_symbols"]

    if not symbols:
        st.info("👆 **Aggiungi almeno 2 asset per iniziare l'analisi**")
        return

    # Show current symbols as chips (migliore contrasto)
    st.markdown("**Portfolio corrente:**")
    chips_html = " ".join([
        f'<span style="display:inline-block;background:#2F5F7F;color:#FFFFFF;padding:8px 16px;border-radius:20px;margin:4px;font-weight:600;border:1px solid #D4AF37;">{s}</span>'
        for s in symbols
    ])
    st.markdown(chips_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════
    # 💰 STEP 2: CAPITAL & WEIGHTS CONFIGURATION
    # ══════════════════════════════════════════════════════════════════

    st.markdown('<h3 style="color:#FFFFFF !important;font-size:1.5rem;font-weight:700;margin:20px 0;">💰 Capitale e Pesi Portfolio</h3>', unsafe_allow_html=True)

    col_capital, col_distrib = st.columns([1, 1])

    with col_capital:
        initial_capital = st.number_input(
            "💶 Capitale Iniziale (EUR)",
            min_value=100.0,
            max_value=10000000.0,
            value=10000.0,
            step=100.0,
            help="Capitale totale da investire in Euro"
        )

    with col_distrib:
        weight_mode = st.selectbox(
            "⚖️ Distribuzione Pesi",
            ["Equamente", "Personalizzata"],
            help="Equamente: peso uguale per tutti. Personalizzata: scegli % per ogni asset"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Initialize weights if not exists
    if "pf_weights" not in st.session_state:
        st.session_state["pf_weights"] = {}

    weights = {}

    if weight_mode == "Equamente":
        # Equal weights
        equal_weight = 1.0 / len(symbols)
        for symbol in symbols:
            weights[symbol] = equal_weight

        # Display weights table
        st.markdown("""
        <div style="background:#1E3A44;padding:12px;border-left:4px solid #D4AF37;border-radius:8px;margin-bottom:12px;">
            <span style="color:#FFFFFF;font-size:0.9rem;"><b>✅ Distribuzione Equa</b>: {:.1f}% per ogni asset</span>
        </div>
        """.format(equal_weight * 100), unsafe_allow_html=True)

    else:
        # Custom weights
        st.markdown("""
        <div style="background:#1E3A44;padding:12px;border-left:4px solid #D4AF37;border-radius:8px;margin-bottom:12px;">
            <span style="color:#FFFFFF;font-size:0.9rem;"><b>⚖️ Distribuzione Personalizzata</b>: Imposta il peso % per ogni asset</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**Imposta i pesi (%):**")

        cols = st.columns(min(len(symbols), 3))

        for i, symbol in enumerate(symbols):
            with cols[i % 3]:
                # Get previous weight or default
                prev_weight = st.session_state["pf_weights"].get(symbol, 100.0 / len(symbols))

                weight_pct = st.number_input(
                    f"📊 {symbol}",
                    min_value=0.0,
                    max_value=100.0,
                    value=prev_weight * 100,
                    step=1.0,
                    key=f"weight_{symbol}",
                    help=f"Peso percentuale per {symbol}"
                )
                weights[symbol] = weight_pct / 100.0

        # Validate total weight
        total_weight = sum(weights.values())

        if abs(total_weight - 1.0) > 0.01:  # Allow 1% tolerance
            st.warning(f"⚠️ **Somma pesi: {total_weight*100:.1f}%** (deve essere 100%)")
            st.info("💡 Aggiusta i pesi fino a raggiungere 100%")
        else:
            st.success(f"✅ **Somma pesi: {total_weight*100:.1f}%** - Perfetto!")

    # Save weights to session state
    st.session_state["pf_weights"] = weights

    # ── Allocation Table ──────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**📋 Allocazione Capitale:**")

    allocation_data = []
    for symbol in symbols:
        weight = weights[symbol]
        amount = initial_capital * weight
        allocation_data.append({
            "Asset": symbol,
            "Peso %": f"{weight*100:.1f}%",
            "Importo €": f"€{amount:,.2f}".replace(",", ".")
        })

    # Display as DataFrame
    df_allocation = pd.DataFrame(allocation_data)

    st.markdown("""
    <style>
    .stDataFrame {
        width: 100% !important;
    }
    .stDataFrame td, .stDataFrame th {
        color: #FFFFFF !important;
        background-color: #1E3A44 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.dataframe(df_allocation, use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # ══════════════════════════════════════════════════════════════════
    # 📊 STEP 3: LOAD DATA & ANALYSIS
    # ══════════════════════════════════════════════════════════════════

    if len(symbols) < 2:
        st.warning("⚠️ **Aggiungi almeno 2 asset per l'analisi**")
        return

    # Load prices
    with st.spinner(f"📥 Caricamento dati ({period_sel})..."):
        prices_df = _load_prices(symbols, period=period_sel)

    if prices_df.empty:
        st.error("❌ Impossibile caricare i dati. Verifica i ticker su [Yahoo Finance](https://finance.yahoo.com)")
        return

    # Calculate equal weights if not set
    weights = st.session_state.get("pf_weights", {})
    if not weights or set(weights.keys()) != set(symbols):
        weights = {s: 1/len(symbols) for s in symbols}
        st.session_state["pf_weights"] = weights

    # ══════════════════════════════════════════════════════════════════
    # 📈 SECTION 1: PORTFOLIO COMPOSITION
    # ══════════════════════════════════════════════════════════════════

    st.markdown('<h2 style="color:#FFFFFF !important;font-size:1.8rem;font-weight:800;margin:40px 0 20px 0;padding-bottom:12px;border-bottom:2px solid #D4AF37;">📊 Composizione Portfolio</h2>', unsafe_allow_html=True)

    col_pie, col_table = st.columns([1, 2])

    with col_pie:
        # Pie chart
        labels = list(weights.keys())
        values = [w * 100 for w in weights.values()]
        fig_pie = pie_chart(labels, values, title="Asset Allocation", height=350)
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E5E7EB")
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

    with col_table:
        # Composition table - COMBINED HTML
        table_html = '<div class="composition-table"><table><thead><tr><th>Asset</th><th>Peso</th><th>Allocazione Visiva</th></tr></thead><tbody>'

        for symbol, weight in weights.items():
            weight_pct = f"{weight*100:.1f}%"
            table_html += f'<tr><td style="color:#E5E7EB;"><b>{symbol}</b></td><td style="color:#E5E7EB;"><b>{weight_pct}</b></td><td><div class="weight-bar"><div class="weight-bar-fill" style="width:{weight*100}%;"></div></div></td></tr>'

        table_html += '</tbody></table></div>'

        st.markdown(table_html, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════
    # 📈 SECTION 2: PERFORMANCE & CORRELATION
    # ══════════════════════════════════════════════════════════════════

    st.markdown('<h2 style="color:#FFFFFF !important;font-size:1.8rem;font-weight:800;margin:40px 0 20px 0;padding-bottom:12px;border-bottom:2px solid #D4AF37;">📈 Performance & Correlazione</h2>', unsafe_allow_html=True)

    # Normalized performance
    norm = (prices_df / prices_df.iloc[0]) * 100
    fig_perf = line_chart(norm, title="Performance Normalizzata (Base 100)", normalize=False, height=400)
    fig_perf.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(30,41,59,0.5)",
        font=dict(color="#E5E7EB")
    )
    st.plotly_chart(fig_perf, use_container_width=True, config={"displayModeBar": False})

    # Correlation matrix
    if len(prices_df.columns) >= 2:
        st.markdown('<p style="color:#E5E7EB !important;font-weight:600;font-size:1rem;margin:20px 0 10px 0;">📊 Matrice di Correlazione:</p>', unsafe_allow_html=True)
        corr = prices_df.pct_change().dropna().corr()
        fig_corr = heatmap_correlation(corr, height=400)
        fig_corr.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E5E7EB")
        )
        st.plotly_chart(fig_corr, use_container_width=True, config={"displayModeBar": False})

    # ══════════════════════════════════════════════════════════════════
    # 🎯 SECTION 3: AUTOMATIC BACKTEST (based on selected period)
    # ══════════════════════════════════════════════════════════════════

    st.markdown('<h2 style="color:#FFFFFF !important;font-size:1.8rem;font-weight:800;margin:40px 0 20px 0;padding-bottom:12px;border-bottom:2px solid #D4AF37;">🎯 Backtest Automatico</h2>', unsafe_allow_html=True)

    st.markdown(f'<span class="status-badge info">Periodo: {period_sel}</span>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    try:
        from backend.analyzers.backtest import BacktestEngine

        with st.spinner("⏳ Esecuzione backtest..."):
            # Calculate backtest period based on selection
            end_date = prices_df.index[-1]
            if period_sel == "1y":
                start_date = end_date - pd.DateOffset(years=1)
            elif period_sel == "2y":
                start_date = end_date - pd.DateOffset(years=2)
            elif period_sel == "3y":
                start_date = end_date - pd.DateOffset(years=3)
            elif period_sel == "5y":
                start_date = end_date - pd.DateOffset(years=5)
            elif period_sel == "10y":
                start_date = end_date - pd.DateOffset(years=10)
            else:  # max
                start_date = prices_df.index[0]

            engine = BacktestEngine(prices_df)
            backtest_results = engine.backtest_portfolio(
                weights=weights,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                initial_value=initial_capital,
            )

        # Metrics grid
        m1, m2, m3, m4 = st.columns(4)

        total_ret = backtest_results.get('total_return', 0)
        sharpe = backtest_results.get('sharpe_ratio', 0)
        max_dd = backtest_results.get('max_drawdown', 0)
        ann_ret = backtest_results.get('annual_return', 0)

        with m1:
            trend = "positive" if total_ret >= 0 else "negative"
            card = _create_metric_card("Rendimento Totale", f"{total_ret*100:+.1f}%", trend)
            st.markdown(card, unsafe_allow_html=True)

        with m2:
            card = _create_metric_card("Sharpe Ratio", f"{sharpe:.2f}", "gold")
            st.markdown(card, unsafe_allow_html=True)

        with m3:
            card = _create_metric_card("Max Drawdown", f"{max_dd*100:.1f}%", "negative")
            st.markdown(card, unsafe_allow_html=True)

        with m4:
            trend = "positive" if ann_ret >= 0 else "negative"
            card = _create_metric_card("Rendimento Annuo", f"{ann_ret*100:+.1f}%", trend)
            st.markdown(card, unsafe_allow_html=True)

        # Backtest chart
        portfolio_value = backtest_results.get('portfolio_value')
        if portfolio_value is not None and len(portfolio_value) > 0:
            st.markdown("<br>", unsafe_allow_html=True)
            fig_bt = line_chart(
                pd.DataFrame({'Portafoglio': portfolio_value}),
                title=f"Andamento Portafoglio ({period_sel})",
                height=400
            )
            fig_bt.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(30,41,59,0.5)",
                font=dict(color="#E5E7EB")
            )
            st.plotly_chart(fig_bt, use_container_width=True, config={"displayModeBar": False})

        # Additional metrics
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)

        with col1:
            vol = backtest_results.get('annual_volatility', 0)
            card = _create_metric_card("Volatilità Annua", f"{vol*100:.1f}%", "info")
            st.markdown(card, unsafe_allow_html=True)

        with col2:
            win_rate = backtest_results.get('win_rate', 0)
            trend = "positive" if win_rate >= 0.5 else "warning"
            card = _create_metric_card("Win Rate", f"{win_rate*100:.0f}%", trend)
            st.markdown(card, unsafe_allow_html=True)

        with col3:
            final_value = backtest_results.get('final_value', 10000)
            profit = final_value - 10000
            trend = "positive" if profit >= 0 else "negative"
            card = _create_metric_card("P&L (su 10k€)", f"{profit:+,.0f}€", trend)
            st.markdown(card, unsafe_allow_html=True)

        st.markdown('<span class="status-badge success">✅ Backtest completato</span>', unsafe_allow_html=True)

    except Exception as e:
        st.warning(f"⚠️ Backtest non disponibile: {e}")

    # ══════════════════════════════════════════════════════════════════
    # 🔮 SECTION 4: PREDICTIONS (Optional)
    # ══════════════════════════════════════════════════════════════════

    st.markdown('<h2 style="color:#FFFFFF !important;font-size:1.8rem;font-weight:800;margin:40px 0 20px 0;padding-bottom:12px;border-bottom:2px solid #D4AF37;">🔮 Predizioni (Opzionale)</h2>', unsafe_allow_html=True)

    run_predictions = st.checkbox("🔮 **Calcola predizioni a 6 mesi (Monte Carlo)**", value=False)

    if run_predictions:
        try:
            from backend.models.predictor import PortfolioPredictor

            with st.spinner("⏳ Calcolo predizioni (1000 simulazioni)..."):
                predictor = PortfolioPredictor(prices_df)
                scenarios = predictor.predict_portfolio_scenarios(
                    weights=weights,
                    months=6,
                    initial_value=initial_capital,
                    num_simulations=1000,
                )

            # Scenarios metrics
            col1, col2, col3 = st.columns(3)

            if 'best_scenario' in scenarios:
                s = scenarios['best_scenario']
                with col1:
                    card = _create_metric_card(
                        "Scenario Migliore (95%)",
                        f"{s['final_value']:,.0f}€",
                        "positive"
                    )
                    st.markdown(card, unsafe_allow_html=True)
                    st.markdown(
                        f'<div style="text-align:center;color:#10B981;font-size:0.9rem;margin-top:8px;">+{s["return_percentage"]:.1f}%</div>',
                        unsafe_allow_html=True
                    )

            if 'normal_scenario' in scenarios:
                s = scenarios['normal_scenario']
                with col2:
                    card = _create_metric_card(
                        "Scenario Atteso (50%)",
                        f"{s['final_value']:,.0f}€",
                        "gold"
                    )
                    st.markdown(card, unsafe_allow_html=True)
                    color = "#10B981" if s['return_percentage'] >= 0 else "#EF4444"
                    sign = "+" if s['return_percentage'] >= 0 else ""
                    st.markdown(
                        f'<div style="text-align:center;color:{color};font-size:0.9rem;margin-top:8px;">{sign}{s["return_percentage"]:.1f}%</div>',
                        unsafe_allow_html=True
                    )

            if 'worst_scenario' in scenarios:
                s = scenarios['worst_scenario']
                with col3:
                    card = _create_metric_card(
                        "Scenario Peggiore (5%)",
                        f"{s['final_value']:,.0f}€",
                        "negative"
                    )
                    st.markdown(card, unsafe_allow_html=True)
                    st.markdown(
                        f'<div style="text-align:center;color:#EF4444;font-size:0.9rem;margin-top:8px;">{s["return_percentage"]:.1f}%</div>',
                        unsafe_allow_html=True
                    )

            st.markdown('<span class="status-badge success">✅ Predizioni completate</span>', unsafe_allow_html=True)

        except Exception as e:
            st.warning(f"⚠️ Predizioni non disponibili: {e}")

    # ══════════════════════════════════════════════════════════════════
    # 📄 SECTION 5: PDF EXPORT (Optional)
    # ══════════════════════════════════════════════════════════════════

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.divider()

    st.markdown('<h3 style="color:#FFFFFF !important;font-size:1.5rem;font-weight:700;margin:20px 0;">📄 Genera Report PDF</h3>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        if st.button("📥 Scarica Report", type="primary", use_container_width=True):
            try:
                from backend.reports.html_report_generator import generate_html_report
                import streamlit.components.v1 as components
                import html

                with st.spinner("📝 Generazione report..."):
                    # Generate HTML report
                    html_content = generate_html_report(
                        portfolio_name=f"Portfolio_{datetime.now().strftime('%Y%m%d')}",
                        symbols=symbols,
                        weights=weights,
                        initial_value=initial_capital,
                        performance_chart=fig_perf if 'fig_perf' in locals() else None,
                        correlation_chart=fig_corr if 'fig_corr' in locals() else None,
                        backtest_chart=fig_bt if 'fig_bt' in locals() else None,
                        backtest_results=backtest_results if 'backtest_results' in locals() else None,
                    )

                    filename = f"Portfolio_{datetime.now().strftime('%Y%m%d_%H%M')}.html"

                st.success("✅ Report generato! Apertura in una nuova finestra...")

                # Escape HTML content for JavaScript
                escaped_html = html.escape(html_content)

                # Open report in new tab using JavaScript
                components.html(f"""
                <script>
                    // Decode HTML entities
                    const htmlContent = `{escaped_html}`;
                    const decodedHTML = htmlContent
                        .replace(/&lt;/g, '<')
                        .replace(/&gt;/g, '>')
                        .replace(/&quot;/g, '"')
                        .replace(/&#x27;/g, "'")
                        .replace(/&amp;/g, '&');

                    // Open in new window
                    const newWindow = window.open('', '_blank');
                    newWindow.document.write(decodedHTML);
                    newWindow.document.close();

                    // Message for user
                    document.body.innerHTML = '<div style="padding:20px;text-align:center;font-family:Inter,sans-serif;"><h3 style="color:#10B981;">✅ Report aperto in una nuova finestra!</h3><p style="color:#6B7280;">Se non si apre automaticamente, controlla il blocco popup del browser.</p></div>';
                </script>
                """, height=100)

                st.info("**📖 Nel report aperto, usa Ctrl+P (o Cmd+P su Mac) → Salva come PDF**")

            except Exception as e:
                st.error(f"❌ Errore: {e}")
                import traceback
                st.code(traceback.format_exc())
