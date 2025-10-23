"""
FinAnalyzer - Frontend Streamlit
Interfaccia utente per la piattaforma di analisi finanziaria
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
import os

# Aggiungi il path per importare i moduli backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.data_collectors.unified_collector import UnifiedDataCollector
from backend.analyzers.portfolio_optimizer import PortfolioOptimizer
from backend.analyzers.backtest import BacktestEngine
from backend.models.predictor import PortfolioPredictor

# Configurazione pagina
st.set_page_config(
    page_title="FinAnalyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizzato
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Inizializza session state
if 'collector' not in st.session_state:
    st.session_state.collector = UnifiedDataCollector()
if 'portfolio_symbols' not in st.session_state:
    st.session_state.portfolio_symbols = []
if 'portfolio_weights' not in st.session_state:
    st.session_state.portfolio_weights = {}


def main():
    """Funzione principale"""

    # Header
    st.markdown('<div class="main-header">📊 FinAnalyzer</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem;">Piattaforma Completa di Analisi Finanziaria</p>', unsafe_allow_html=True)

    # Sidebar
    st.sidebar.title("Menu Navigazione")
    page = st.sidebar.selectbox(
        "Seleziona una funzione",
        [
            "🏠 Home",
            "🔍 Ricerca Strumenti",
            "💼 Costruisci Portafoglio",
            "📈 Ottimizzazione Markowitz",
            "⏮️ Backtest",
            "🔮 Predizioni Future",
            "📋 Liste Predefinite"
        ]
    )

    # Routing pagine
    if page == "🏠 Home":
        show_home()
    elif page == "🔍 Ricerca Strumenti":
        show_search()
    elif page == "💼 Costruisci Portafoglio":
        show_portfolio_builder()
    elif page == "📈 Ottimizzazione Markowitz":
        show_optimization()
    elif page == "⏮️ Backtest":
        show_backtest()
    elif page == "🔮 Predizioni Future":
        show_predictions()
    elif page == "📋 Liste Predefinite":
        show_lists()


def show_home():
    """Pagina home"""
    st.markdown('<div class="sub-header">Benvenuto in FinAnalyzer</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("""
        ### 🔍 Ricerca
        Cerca e analizza strumenti finanziari da multiple fonti:
        - Yahoo Finance
        - Investing.com
        - Morningstar
        - E altri...
        """)

    with col2:
        st.success("""
        ### 📊 Analisi
        Ottimizza il tuo portafoglio con:
        - Teoria di Markowitz
        - Frontiera Efficiente
        - Analisi di volatilità
        - Sharpe Ratio
        """)

    with col3:
        st.warning("""
        ### 🔮 Previsioni
        Prevedi il futuro con:
        - Scenari a 6 mesi
        - Monte Carlo Simulation
        - Value at Risk
        - Backtesting storico
        """)

    st.markdown("---")

    st.markdown("""
    ### 📚 Funzionalità Principali

    **1. Ricerca Multi-Fonte**: Cerca azioni, obbligazioni, ETF, fondi, certificati e commodities

    **2. Costruzione Portafoglio**: Crea il tuo portafoglio personalizzato

    **3. Ottimizzazione Markowitz**: Trova i pesi ottimali per massimizzare rendimento/minimizzare rischio

    **4. Backtest**: Testa il tuo portafoglio su dati storici (1, 3, 5, 7 anni)

    **5. Predizioni**: Ottieni scenari futuri (normale, peggiore, migliore) a 6 mesi

    **6. Analisi Volatilità**: Comprendi il rischio del tuo portafoglio

    ---

    ### 🚀 Come Iniziare

    1. Vai su **Ricerca Strumenti** per trovare asset
    2. Costruisci il tuo portafoglio in **Costruisci Portafoglio**
    3. Ottimizzalo con **Ottimizzazione Markowitz**
    4. Testalo con **Backtest**
    5. Guarda le predizioni in **Predizioni Future**
    """)


def show_search():
    """Pagina ricerca strumenti"""
    st.markdown('<div class="sub-header">🔍 Ricerca Strumenti Finanziari</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        search_query = st.text_input(
            "Cerca un titolo (simbolo o nome)",
            placeholder="es: AAPL, Tesla, BTP, VWCE.DE"
        )

    with col2:
        asset_type = st.selectbox(
            "Tipo di asset",
            ["Tutti", "Azioni", "ETF", "Obbligazioni", "Fondi", "Commodities"]
        )

    if st.button("🔍 Cerca", type="primary"):
        if search_query:
            with st.spinner("Ricerca in corso..."):
                results = st.session_state.collector.search_all_sources(search_query)

                if results:
                    st.success(f"Trovati {len(results)} risultati")

                    for result in results:
                        with st.expander(f"{result.get('name', 'N/A')} ({result.get('symbol', 'N/A')})"):
                            col1, col2 = st.columns(2)

                            with col1:
                                st.write(f"**Simbolo**: {result.get('symbol', 'N/A')}")
                                st.write(f"**Nome**: {result.get('name', 'N/A')}")
                                st.write(f"**Tipo**: {result.get('type', 'N/A')}")
                                st.write(f"**Exchange**: {result.get('exchange', 'N/A')}")

                            with col2:
                                st.write(f"**Valuta**: {result.get('currency', 'N/A')}")
                                st.write(f"**Settore**: {result.get('sector', 'N/A')}")
                                st.write(f"**Fonte**: {result.get('source', 'N/A')}")

                            if st.button(f"➕ Aggiungi al portafoglio", key=f"add_{result.get('symbol')}"):
                                symbol = result.get('symbol')
                                if symbol not in st.session_state.portfolio_symbols:
                                    st.session_state.portfolio_symbols.append(symbol)
                                    st.success(f"{symbol} aggiunto al portafoglio!")
                                else:
                                    st.warning(f"{symbol} già presente nel portafoglio")
                else:
                    st.warning("Nessun risultato trovato")
        else:
            st.warning("Inserisci un termine di ricerca")

    # Mostra portafoglio corrente
    if st.session_state.portfolio_symbols:
        st.markdown("---")
        st.markdown("### 💼 Portafoglio Corrente")
        st.write(", ".join(st.session_state.portfolio_symbols))


def show_portfolio_builder():
    """Pagina costruzione portafoglio"""
    st.markdown('<div class="sub-header">💼 Costruisci il Tuo Portafoglio</div>', unsafe_allow_html=True)

    # Aggiungi simboli manualmente
    st.markdown("### Aggiungi Simboli")

    col1, col2 = st.columns([3, 1])

    with col1:
        new_symbol = st.text_input(
            "Simbolo del titolo",
            placeholder="es: AAPL, MSFT, ENI.MI"
        )

    with col2:
        if st.button("➕ Aggiungi"):
            if new_symbol and new_symbol not in st.session_state.portfolio_symbols:
                # Valida il simbolo
                with st.spinner("Validazione simbolo..."):
                    info = st.session_state.collector.get_asset_info(new_symbol)
                    if info and info.get('symbol'):
                        st.session_state.portfolio_symbols.append(new_symbol)
                        st.success(f"{new_symbol} aggiunto!")
                        st.rerun()
                    else:
                        st.error(f"Simbolo {new_symbol} non valido")
            elif new_symbol in st.session_state.portfolio_symbols:
                st.warning("Simbolo già presente")

    # Mostra portafoglio
    if st.session_state.portfolio_symbols:
        st.markdown("---")
        st.markdown("### 📊 Il Tuo Portafoglio")

        # Tabella con simboli e opzione rimozione
        for i, symbol in enumerate(st.session_state.portfolio_symbols):
            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                st.write(f"**{symbol}**")

            with col2:
                # Peso (per ora manuale, poi verrà dall'ottimizzazione)
                weight = st.number_input(
                    f"Peso %",
                    min_value=0.0,
                    max_value=100.0,
                    value=100.0 / len(st.session_state.portfolio_symbols),
                    key=f"weight_{symbol}"
                )
                st.session_state.portfolio_weights[symbol] = weight / 100.0

            with col3:
                if st.button("🗑️", key=f"remove_{symbol}"):
                    st.session_state.portfolio_symbols.remove(symbol)
                    if symbol in st.session_state.portfolio_weights:
                        del st.session_state.portfolio_weights[symbol]
                    st.rerun()

        # Normalizza i pesi
        total_weight = sum(st.session_state.portfolio_weights.values())
        if abs(total_weight - 1.0) > 0.01:
            st.warning(f"⚠️ I pesi totali sono {total_weight*100:.1f}% (devono sommare al 100%)")

        # Visualizza dati storici
        if st.button("📈 Visualizza Dati Storici"):
            with st.spinner("Caricamento dati..."):
                prices_df = st.session_state.collector.get_historical_prices(
                    st.session_state.portfolio_symbols,
                    period="1y"
                )

                if not prices_df.empty:
                    st.markdown("### 📊 Prezzi Storici (1 anno)")

                    # Normalizza i prezzi a 100
                    normalized_prices = (prices_df / prices_df.iloc[0]) * 100

                    fig = go.Figure()
                    for col in normalized_prices.columns:
                        fig.add_trace(go.Scatter(
                            x=normalized_prices.index,
                            y=normalized_prices[col],
                            mode='lines',
                            name=col
                        ))

                    fig.update_layout(
                        title="Performance Normalizzata (Base 100)",
                        xaxis_title="Data",
                        yaxis_title="Valore (Base 100)",
                        hovermode='x unified'
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("Errore nel caricamento dati")

    else:
        st.info("👆 Aggiungi dei simboli per iniziare")


def show_optimization():
    """Pagina ottimizzazione Markowitz"""
    st.markdown('<div class="sub-header">📈 Ottimizzazione Portafoglio - Teoria di Markowitz</div>', unsafe_allow_html=True)

    if not st.session_state.portfolio_symbols:
        st.warning("⚠️ Aggiungi dei simboli al portafoglio prima di ottimizzare")
        return

    st.markdown(f"**Portafoglio**: {', '.join(st.session_state.portfolio_symbols)}")

    # Opzioni di ottimizzazione
    col1, col2 = st.columns(2)

    with col1:
        optimization_type = st.selectbox(
            "Tipo di Ottimizzazione",
            [
                "Massimizza Sharpe Ratio",
                "Minimizza Volatilità",
                "Rendimento Target",
                "Rischio Target"
            ]
        )

    with col2:
        period = st.selectbox(
            "Periodo Dati Storici",
            ["1y", "2y", "3y", "5y", "7y", "10y"]
        )

    target_return = None
    target_volatility = None

    if optimization_type == "Rendimento Target":
        target_return = st.slider("Rendimento Target Annuale (%)", 0.0, 50.0, 15.0) / 100

    elif optimization_type == "Rischio Target":
        target_volatility = st.slider("Volatilità Target Annuale (%)", 0.0, 50.0, 15.0) / 100

    if st.button("🎯 Ottimizza Portafoglio", type="primary"):
        with st.spinner("Ottimizzazione in corso..."):
            try:
                # Carica dati
                prices_df = st.session_state.collector.get_historical_prices(
                    st.session_state.portfolio_symbols,
                    period=period
                )

                if prices_df.empty:
                    st.error("Errore nel caricamento dati")
                    return

                # Ottimizza
                optimizer = PortfolioOptimizer(prices_df)
                optimizer.calculate_expected_returns()
                optimizer.calculate_covariance_matrix()

                if optimization_type == "Massimizza Sharpe Ratio":
                    result = optimizer.optimize_max_sharpe()
                elif optimization_type == "Minimizza Volatilità":
                    result = optimizer.optimize_min_volatility()
                elif optimization_type == "Rendimento Target":
                    result = optimizer.optimize_efficient_return(target_return)
                elif optimization_type == "Rischio Target":
                    result = optimizer.optimize_efficient_risk(target_volatility)

                # Mostra risultati
                st.success("✅ Ottimizzazione completata!")

                # Metriche
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Rendimento Atteso Annuale", f"{result['expected_return']*100:.2f}%")

                with col2:
                    st.metric("Volatilità Annuale", f"{result['volatility']*100:.2f}%")

                with col3:
                    st.metric("Sharpe Ratio", f"{result['sharpe_ratio']:.2f}")

                # Pesi ottimali
                st.markdown("### 📊 Pesi Ottimali")

                weights_df = pd.DataFrame([
                    {'Simbolo': symbol, 'Peso': weight*100, 'Peso_norm': weight}
                    for symbol, weight in result['weights'].items()
                    if weight > 0.001  # Mostra solo pesi significativi
                ]).sort_values('Peso', ascending=False)

                col1, col2 = st.columns(2)

                with col1:
                    st.dataframe(
                        weights_df[['Simbolo', 'Peso']].style.format({'Peso': '{:.2f}%'}),
                        use_container_width=True
                    )

                with col2:
                    fig = px.pie(
                        weights_df,
                        values='Peso',
                        names='Simbolo',
                        title='Allocazione Portafoglio'
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # Aggiorna session state con pesi ottimali
                st.session_state.portfolio_weights = result['weights']

                # Frontiera efficiente
                st.markdown("### 📈 Frontiera Efficiente di Markowitz")

                with st.spinner("Calcolo frontiera efficiente..."):
                    volatilities, returns = optimizer.calculate_efficient_frontier(points=50)

                    fig = go.Figure()

                    # Frontiera efficiente
                    fig.add_trace(go.Scatter(
                        x=volatilities,
                        y=returns,
                        mode='lines',
                        name='Frontiera Efficiente',
                        line=dict(color='blue', width=3)
                    ))

                    # Portafoglio ottimale
                    fig.add_trace(go.Scatter(
                        x=[result['volatility']],
                        y=[result['expected_return']],
                        mode='markers',
                        name='Portafoglio Ottimale',
                        marker=dict(color='red', size=15, symbol='star')
                    ))

                    # Asset individuali
                    for symbol in st.session_state.portfolio_symbols:
                        symbol_return = optimizer.mu[symbol]
                        symbol_volatility = optimizer.S.loc[symbol, symbol] ** 0.5

                        fig.add_trace(go.Scatter(
                            x=[symbol_volatility],
                            y=[symbol_return],
                            mode='markers+text',
                            name=symbol,
                            text=[symbol],
                            textposition="top center",
                            marker=dict(size=10)
                        ))

                    fig.update_layout(
                        title='Frontiera Efficiente di Markowitz',
                        xaxis_title='Volatilità (Rischio)',
                        yaxis_title='Rendimento Atteso',
                        hovermode='closest'
                    )

                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"Errore durante l'ottimizzazione: {str(e)}")


def show_backtest():
    """Pagina backtest"""
    st.markdown('<div class="sub-header">⏮️ Backtest Storico</div>', unsafe_allow_html=True)

    if not st.session_state.portfolio_symbols:
        st.warning("⚠️ Aggiungi dei simboli al portafoglio prima di fare backtest")
        return

    if not st.session_state.portfolio_weights:
        st.warning("⚠️ Ottimizza il portafoglio prima o imposta i pesi manualmente")
        return

    st.markdown(f"**Portafoglio**: {', '.join(st.session_state.portfolio_symbols)}")

    # Opzioni backtest
    col1, col2 = st.columns(2)

    with col1:
        periods = st.multiselect(
            "Periodi di Test (anni)",
            [1, 3, 5, 7],
            default=[1, 3, 5]
        )

    with col2:
        initial_value = st.number_input(
            "Valore Iniziale (€)",
            min_value=1000.0,
            value=10000.0,
            step=1000.0
        )

    if st.button("▶️ Esegui Backtest", type="primary"):
        with st.spinner("Esecuzione backtest in corso..."):
            try:
                # Carica dati
                max_period = max(periods) if periods else 5
                prices_df = st.session_state.collector.get_historical_prices(
                    st.session_state.portfolio_symbols,
                    period=f"{max_period}y"
                )

                if prices_df.empty:
                    st.error("Errore nel caricamento dati")
                    return

                # Backtest
                backtest_engine = BacktestEngine(prices_df)
                results = backtest_engine.backtest_multiple_periods(
                    weights=st.session_state.portfolio_weights,
                    periods=periods,
                    initial_value=initial_value
                )

                st.success("✅ Backtest completato!")

                # Mostra risultati per ogni periodo
                for years, result in results.items():
                    st.markdown(f"### 📊 Backtest a {years} Anno/i")

                    # Metriche principali
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric(
                            "Rendimento Totale",
                            f"{result['total_return']*100:.2f}%",
                            delta=f"{result['annual_return']*100:.2f}% annuo"
                        )

                    with col2:
                        st.metric("Valore Finale", f"€{result['final_value']:,.2f}")

                    with col3:
                        st.metric("Sharpe Ratio", f"{result['sharpe_ratio']:.2f}")

                    with col4:
                        st.metric("Max Drawdown", f"{result['max_drawdown']*100:.2f}%")

                    # Metriche aggiuntive
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("Volatilità Annuale", f"{result['annual_volatility']*100:.2f}%")

                    with col2:
                        st.metric("Sortino Ratio", f"{result['sortino_ratio']:.2f}")

                    with col3:
                        st.metric("Calmar Ratio", f"{result['calmar_ratio']:.2f}")

                    with col4:
                        st.metric("Win Rate", f"{result['win_rate']*100:.1f}%")

                    # Grafico valore portafoglio nel tempo
                    if 'portfolio_value_over_time' in result:
                        portfolio_values = pd.Series(result['portfolio_value_over_time'])

                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=portfolio_values.index,
                            y=portfolio_values.values,
                            mode='lines',
                            name='Valore Portafoglio',
                            fill='tonexty',
                            line=dict(color='green')
                        ))

                        fig.add_hline(
                            y=initial_value,
                            line_dash="dash",
                            line_color="red",
                            annotation_text="Valore Iniziale"
                        )

                        fig.update_layout(
                            title=f'Evoluzione Valore Portafoglio ({years} anno/i)',
                            xaxis_title='Data',
                            yaxis_title='Valore (€)',
                            hovermode='x unified'
                        )

                        st.plotly_chart(fig, use_container_width=True)

                    st.markdown("---")

            except Exception as e:
                st.error(f"Errore durante il backtest: {str(e)}")


def show_predictions():
    """Pagina predizioni future"""
    st.markdown('<div class="sub-header">🔮 Predizioni Future - Scenari a 6 Mesi</div>', unsafe_allow_html=True)

    if not st.session_state.portfolio_symbols:
        st.warning("⚠️ Aggiungi dei simboli al portafoglio prima di fare predizioni")
        return

    if not st.session_state.portfolio_weights:
        st.warning("⚠️ Ottimizza il portafoglio prima o imposta i pesi manualmente")
        return

    st.markdown(f"**Portafoglio**: {', '.join(st.session_state.portfolio_symbols)}")

    # Opzioni
    col1, col2 = st.columns(2)

    with col1:
        months = st.slider("Mesi di Predizione", 1, 12, 6)

    with col2:
        initial_value = st.number_input(
            "Valore Iniziale (€)",
            min_value=1000.0,
            value=10000.0,
            step=1000.0
        )

    if st.button("🔮 Genera Predizioni", type="primary"):
        with st.spinner("Generazione predizioni in corso..."):
            try:
                # Carica dati
                prices_df = st.session_state.collector.get_historical_prices(
                    st.session_state.portfolio_symbols,
                    period="3y"  # Usa 3 anni per predizioni
                )

                if prices_df.empty:
                    st.error("Errore nel caricamento dati")
                    return

                # Predici
                predictor = PortfolioPredictor(prices_df)
                scenarios = predictor.predict_portfolio_scenarios(
                    weights=st.session_state.portfolio_weights,
                    months=months,
                    initial_value=initial_value
                )

                st.success("✅ Predizioni generate!")

                # Mostra scenari
                st.markdown("### 📊 Scenari Previsti")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown("#### 🟢 Scenario Migliore")
                    best = scenarios['best_scenario']
                    st.metric(
                        "Valore Finale",
                        f"€{best['final_value']:,.2f}",
                        delta=f"{best['return_percentage']:.2f}%"
                    )

                with col2:
                    st.markdown("#### 🟡 Scenario Normale")
                    normal = scenarios['normal_scenario']
                    st.metric(
                        "Valore Finale",
                        f"€{normal['final_value']:,.2f}",
                        delta=f"{normal['return_percentage']:.2f}%"
                    )

                with col3:
                    st.markdown("#### 🔴 Scenario Peggiore")
                    worst = scenarios['worst_scenario']
                    st.metric(
                        "Valore Finale",
                        f"€{worst['final_value']:,.2f}",
                        delta=f"{worst['return_percentage']:.2f}%"
                    )

                # Statistiche
                st.markdown("### 📈 Statistiche Predittive")

                stats = scenarios['statistics']

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Valore Medio Atteso", f"€{stats['mean_value']:,.2f}")

                with col2:
                    st.metric("Deviazione Standard", f"€{stats['std_value']:,.2f}")

                with col3:
                    st.metric("Rendimento Atteso", f"{stats['expected_return']*100:.2f}%")

                with col4:
                    st.metric("Probabilità di Perdita", f"{stats['probability_of_loss']*100:.1f}%")

                # Grafico percorsi predittivi
                if 'predictions' in scenarios:
                    st.markdown("### 📊 Evoluzione Scenari nel Tempo")

                    predictions = scenarios['predictions']

                    fig = go.Figure()

                    # Scenario normale
                    fig.add_trace(go.Scatter(
                        x=list(range(len(predictions['normal_path']))),
                        y=predictions['normal_path'],
                        mode='lines',
                        name='Scenario Normale',
                        line=dict(color='blue', width=3)
                    ))

                    # Scenario migliore
                    fig.add_trace(go.Scatter(
                        x=list(range(len(predictions['best_path']))),
                        y=predictions['best_path'],
                        mode='lines',
                        name='Scenario Migliore',
                        line=dict(color='green', width=2, dash='dash')
                    ))

                    # Scenario peggiore
                    fig.add_trace(go.Scatter(
                        x=list(range(len(predictions['worst_path']))),
                        y=predictions['worst_path'],
                        mode='lines',
                        name='Scenario Peggiore',
                        line=dict(color='red', width=2, dash='dash')
                    ))

                    # Valore iniziale
                    fig.add_hline(
                        y=initial_value,
                        line_dash="dot",
                        line_color="gray",
                        annotation_text="Valore Iniziale"
                    )

                    fig.update_layout(
                        title=f'Scenari Predittivi a {months} Mesi',
                        xaxis_title='Giorni',
                        yaxis_title='Valore Portafoglio (€)',
                        hovermode='x unified'
                    )

                    st.plotly_chart(fig, use_container_width=True)

                # Value at Risk
                var_result = predictor.calculate_value_at_risk(
                    weights=st.session_state.portfolio_weights,
                    initial_value=initial_value
                )

                st.markdown("### ⚠️ Value at Risk (VaR)")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "VaR 95% (1 giorno)",
                        f"€{abs(var_result['var_value']):,.2f}",
                        help="Perdita massima attesa nel 95% dei casi in 1 giorno"
                    )

                with col2:
                    st.metric(
                        "CVaR 95% (1 giorno)",
                        f"€{abs(var_result['cvar_value']):,.2f}",
                        help="Perdita media attesa quando si supera il VaR"
                    )

            except Exception as e:
                st.error(f"Errore durante le predizioni: {str(e)}")


def show_lists():
    """Pagina liste predefinite"""
    st.markdown('<div class="sub-header">📋 Liste Predefinite</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🏛️ Obbligazioni", "💰 ETF", "🌾 Commodities"])

    with tab1:
        st.markdown("### Obbligazioni Governative Italiane")

        if st.button("📥 Carica Obbligazioni"):
            with st.spinner("Caricamento..."):
                bonds = st.session_state.collector.get_bonds("italy")

                if bonds:
                    st.success(f"Trovate {len(bonds)} obbligazioni")
                    df = pd.DataFrame(bonds)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("Dati non disponibili al momento")

    with tab2:
        st.markdown("### ETF Popolari")

        if st.button("📥 Carica ETF"):
            with st.spinner("Caricamento..."):
                etfs = st.session_state.collector.get_etfs("italy")

                if etfs:
                    st.success(f"Trovati {len(etfs)} ETF")
                    df = pd.DataFrame(etfs)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("Dati non disponibili al momento")

    with tab3:
        st.markdown("### Commodities")

        if st.button("📥 Carica Commodities"):
            with st.spinner("Caricamento..."):
                commodities = st.session_state.collector.get_commodities()

                if commodities:
                    st.success(f"Trovate {len(commodities)} commodities")
                    df = pd.DataFrame(commodities)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("Dati non disponibili al momento")


if __name__ == "__main__":
    main()
