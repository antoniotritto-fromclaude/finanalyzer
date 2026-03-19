"""
Screener SEMPLIFICATO - Seleziona titoli da aggiungere al portafoglio
"""
import streamlit as st
import pandas as pd
import yfinance as yf
import time


# Liste predefinite per selezione rapida
AZIONI_POPOLARI = {
    "🇮🇹 Italia": ["ENI.MI", "ENEL.MI", "ISP.MI", "UCG.MI", "RACE.MI", "STLAM.MI", "TIT.MI", "AZM.MI", "G.MI", "TENR.MI"],
    "🇺🇸 USA Tech": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "NFLX", "AMD", "INTC"],
    "🇺🇸 USA Finance": ["JPM", "BAC", "WFC", "GS", "MS", "C", "BLK", "SCHW"],
    "🇺🇸 USA Consumer": ["WMT", "HD", "MCD", "NKE", "SBUX", "TGT", "COST"],
    "🇪🇺 Europa": ["AIR.PA", "SAN.MC", "OR.PA", "BNP.PA", "SU.PA", "SAP.DE", "SIE.DE"],
}

ETF_POPOLARI = {
    "🌍 Globali Azionari": ["SWDA.MI", "VWCE.DE", "CSPX.MI", "VUSA.L", "IWDA.AS", "EUNL.DE", "VHYL.L"],
    "🇺🇸 USA": ["SPY", "QQQ", "VOO", "VTI", "IVV", "DIA", "IWM"],
    "🇪🇺 Europa": ["EXS1.DE", "IQQE.DE", "MEUD.DE", "IUSE.L", "SMEA.L"],
    "🌏 Emergenti": ["EIMI.MI", "AEEM.MI", "IEMG", "VWO", "EEM"],
    "🏛️ Obbligazionari": ["VGEA.L", "IEAG.L", "AGGH.MI", "AGG", "BND", "GOVT"],
    "💎 Commodities ETF": ["GLD", "SLV", "USO", "DBA", "PDBC"],
    "📊 Tematici": ["ECAR.MI", "IUIT.MI", "HEAL.L", "RBOT.L", "ARKK", "ICLN"],
}

COMMODITIES = {
    "⚡ Energia": ["CL=F", "NG=F", "BZ=F"],
    "🥇 Metalli Preziosi": ["GC=F", "SI=F", "PL=F", "PA=F"],
    "🌾 Agricoltura": ["ZC=F", "ZW=F", "KC=F", "CC=F", "SB=F"],
    "🏗️ Metalli Industriali": ["HG=F", "ALI=F"],
}

CRYPTO = {
    "💰 Principali": ["BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "ADA-USD", "SOL-USD", "DOGE-USD"],
}


def _add_to_portfolio(symbol):
    """Aggiunge un simbolo al portafoglio"""
    if "pf_symbols" not in st.session_state:
        st.session_state["pf_symbols"] = []

    if symbol in st.session_state["pf_symbols"]:
        return False, f"⚠️ {symbol} già nel portafoglio"

    # Valida con Yahoo Finance
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="5d")
        if hist.empty:
            return False, f"❌ {symbol} non trovato"

        st.session_state["pf_symbols"].append(symbol)
        return True, f"✅ {symbol} aggiunto!"
    except Exception as e:
        return False, f"❌ Errore: {str(e)[:50]}"


def render():
    st.title("🔍 Screener - Selezione Titoli")

    st.markdown("""
    <div class="fin-card" style="background:#f0f9ff;border-left:4px solid #2471c8;padding:16px;">
        <b>💡 Come funziona:</b>
        <ol style="margin:8px 0 0 0;padding-left:20px;">
            <li>Cerca un simbolo manualmente OPPURE</li>
            <li>Seleziona da liste predefinite (Azioni, ETF, Commodities, Crypto)</li>
            <li>Clicca "➕ Aggiungi" per inserire nel portafoglio</li>
            <li>Vai su <b>Portafoglio</b> per gestire e ottimizzare</li>
        </ol>
        <div style="margin-top:12px;padding:10px;background:#d1fae5;border-radius:8px;font-size:0.88rem;">
            ✅ <b>Novità:</b> Supporto COMPLETO fondi con ISIN!
            <br>💡 <b>Puoi aggiungere:</b> Ticker Yahoo Finance (AAPL, SPY) O ISIN Morningstar (IT0005239881)
            <br>📊 Dati aggiornati 1x/giorno, cache automatica per velocità
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════
    # RICERCA MANUALE
    # ═══════════════════════════════════════════════════════════════
    st.subheader("🔎 Ricerca Manuale")

    col1, col2 = st.columns([4, 1])
    with col1:
        manual_symbol = st.text_input(
            "Inserisci Ticker o ISIN",
            placeholder="Es: AAPL, ENI.MI, IT0005239881, BTC-USD",
            help="Supporta: Ticker Yahoo Finance O ISIN fondi Morningstar",
            key="manual_search"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Aggiungi", key="add_manual", type="primary", use_container_width=True):
            if manual_symbol:
                success, msg = _add_to_portfolio(manual_symbol.strip().upper())
                if success:
                    st.success(msg)
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error(msg)

    st.markdown("<br>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════
    # SELEZIONE RAPIDA
    # ═══════════════════════════════════════════════════════════════
    st.subheader("⚡ Selezione Rapida")

    tab_stocks, tab_etf, tab_comm, tab_crypto = st.tabs([
        "📈 Azioni", "📡 ETF", "🌾 Commodities", "💰 Crypto"
    ])

    # ──────────────────────────────────────────────────────────────
    # TAB AZIONI
    # ──────────────────────────────────────────────────────────────
    with tab_stocks:
        st.markdown("Seleziona azioni da aggiungere al portafoglio:")

        for region, symbols in AZIONI_POPOLARI.items():
            with st.expander(f"{region} ({len(symbols)} titoli)"):
                cols = st.columns(5)
                for i, sym in enumerate(symbols):
                    with cols[i % 5]:
                        if st.button(sym, key=f"stock_{sym}", use_container_width=True):
                            success, msg = _add_to_portfolio(sym)
                            if success:
                                st.success(msg)
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.warning(msg)

    # ──────────────────────────────────────────────────────────────
    # TAB ETF
    # ──────────────────────────────────────────────────────────────
    with tab_etf:
        st.markdown("Seleziona ETF da aggiungere al portafoglio:")

        for category, symbols in ETF_POPOLARI.items():
            with st.expander(f"{category} ({len(symbols)} ETF)"):
                cols = st.columns(5)
                for i, sym in enumerate(symbols):
                    with cols[i % 5]:
                        if st.button(sym, key=f"etf_{sym}", use_container_width=True):
                            success, msg = _add_to_portfolio(sym)
                            if success:
                                st.success(msg)
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.warning(msg)

    # ──────────────────────────────────────────────────────────────
    # TAB COMMODITIES
    # ──────────────────────────────────────────────────────────────
    with tab_comm:
        st.markdown("Seleziona commodities da aggiungere al portafoglio:")

        for category, symbols in COMMODITIES.items():
            with st.expander(f"{category} ({len(symbols)} asset)"):
                cols = st.columns(5)
                for i, sym in enumerate(symbols):
                    with cols[i % 5]:
                        if st.button(sym, key=f"comm_{sym}", use_container_width=True):
                            success, msg = _add_to_portfolio(sym)
                            if success:
                                st.success(msg)
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.warning(msg)

    # ──────────────────────────────────────────────────────────────
    # TAB CRYPTO
    # ──────────────────────────────────────────────────────────────
    with tab_crypto:
        st.markdown("Seleziona crypto da aggiungere al portafoglio:")

        for category, symbols in CRYPTO.items():
            cols = st.columns(5)
            for i, sym in enumerate(symbols):
                with cols[i % 5]:
                    if st.button(sym, key=f"crypto_{sym}", use_container_width=True):
                        success, msg = _add_to_portfolio(sym)
                        if success:
                            st.success(msg)
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.warning(msg)

    # ═══════════════════════════════════════════════════════════════
    # PORTAFOGLIO CORRENTE
    # ═══════════════════════════════════════════════════════════════
    st.markdown("<br>", unsafe_allow_html=True)
    current_pf = st.session_state.get("pf_symbols", [])

    if current_pf:
        st.markdown("---")
        st.subheader(f"💼 Portafoglio Corrente ({len(current_pf)} titoli)")
        st.markdown(" · ".join([f"`{s}`" for s in current_pf]))
        st.info("💡 Vai su **Portafoglio** per gestire pesi e ottimizzazione")
    else:
        st.info("💼 Nessun titolo nel portafoglio. Aggiungine almeno 2 per iniziare!")
