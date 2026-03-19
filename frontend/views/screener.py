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

    # Valida con Yahoo Finance, Morningstar, JustETF, o Investing.com
    try:
        from backend.data_loader import load_prices_smart, is_isin
        from backend.data_collectors.morningstar import MorningstarCollector
        from backend.data_collectors.investing import investing_collector

        # Determina il tipo di input
        is_ms_url = MorningstarCollector.is_morningstar_url(symbol)
        is_inv_url = investing_collector.is_investing_url(symbol)
        is_isin_code = is_isin(symbol)

        # Test caricamento prezzi
        prices_df = load_prices_smart([symbol], period="5d")

        if prices_df.empty or symbol not in prices_df.columns:
            # Messaggio errore dettagliato
            if is_ms_url:
                fund_id = MorningstarCollector.extract_fund_id_from_url(symbol)
                if fund_id:
                    return False, f"❌ Fondo {fund_id} non trovato su Morningstar. Verifica l'URL o prova con l'ISIN."
                else:
                    return False, f"❌ Impossibile estrarre ID da URL Morningstar. Formato non riconosciuto."
            elif is_inv_url:
                instrument = investing_collector.extract_instrument_from_url(symbol)
                if instrument:
                    return False, f"❌ Strumento {instrument} non trovato su Investing.com. Verifica l'URL."
                else:
                    return False, f"❌ Impossibile estrarre strumento da URL Investing.com. Formato non riconosciuto."
            elif is_isin_code:
                return False, f"❌ ISIN {symbol} non trovato su Morningstar/JustETF. Verifica il codice o prova con l'URL diretto."
            else:
                return False, f"❌ Ticker {symbol} non trovato su Yahoo Finance. Verifica il simbolo."

        st.session_state["pf_symbols"].append(symbol)

        # Messaggio successo differenziato
        if is_ms_url:
            fund_id = MorningstarCollector.extract_fund_id_from_url(symbol)
            return True, f"✅ Fondo {fund_id} aggiunto! (Morningstar)"
        elif is_inv_url:
            instrument = investing_collector.extract_instrument_from_url(symbol)
            return True, f"✅ {instrument} aggiunto! (Investing.com)"
        elif is_isin_code:
            return True, f"✅ Fondo {symbol} aggiunto! (Morningstar/JustETF)"
        else:
            return True, f"✅ {symbol} aggiunto!"

    except Exception as e:
        return False, f"❌ Errore: {str(e)[:100]}"


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
            ✅ <b>Supporto MULTI-FONTE per massima copertura!</b>
            <br>💡 <b>Puoi aggiungere:</b>
            <br>&nbsp;&nbsp;&nbsp;• <b>Ticker</b> Yahoo Finance → AAPL, SPY, VWCE.DE, BTC-USD
            <br>&nbsp;&nbsp;&nbsp;• <b>ISIN</b> Morningstar/JustETF → LU2056383347, IE00B4L5Y983
            <br>&nbsp;&nbsp;&nbsp;• <b>Link</b> Morningstar → https://morningstar.it/...
            <br>&nbsp;&nbsp;&nbsp;• <b>Link</b> Investing.com → https://it.investing.com/equities/...
            <br>📊 Cache 24h automatica | 🔄 Fallback multi-fonte per massima affidabilità
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════
    # FONDI RECENTI (ultimi 20)
    # ═══════════════════════════════════════════════════════════════
    from backend.cache.funds_cache import funds_cache

    recent_funds = funds_cache.get_recent()
    if recent_funds:
        with st.expander(f"⏱️ Fondi Recenti ({len(recent_funds)}) - Accesso Rapido"):
            st.markdown("""
            <div style="font-size:0.85rem;color:#6b7280;margin-bottom:12px;">
                Gli ultimi 20 fondi cercati sono salvati in cache per accesso veloce.
                Clicca per aggiungerli al portafoglio senza attendere.
            </div>
            """, unsafe_allow_html=True)

            # Mostra in griglia 4 colonne
            cols_per_row = 4
            for i in range(0, len(recent_funds), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, col in enumerate(cols):
                    idx = i + j
                    if idx < len(recent_funds):
                        fund = recent_funds[idx]
                        with col:
                            # Tronca nome se troppo lungo
                            display_name = fund.get("name", "")[:25]
                            if len(fund.get("name", "")) > 25:
                                display_name += "..."

                            if st.button(
                                f"➕ {display_name}",
                                key=f"recent_{idx}",
                                use_container_width=True,
                                help=f"{fund.get('name')} - {fund.get('source')}"
                            ):
                                success, msg = _add_to_portfolio(fund.get("id"))
                                if success:
                                    st.success(msg)
                                else:
                                    st.warning(msg)
                                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════
    # RICERCA MANUALE
    # ═══════════════════════════════════════════════════════════════
    st.subheader("🔎 Ricerca Manuale")

    col1, col2 = st.columns([4, 1])
    with col1:
        manual_symbol = st.text_input(
            "Inserisci Ticker, ISIN o Link",
            placeholder="Es: AAPL, LU2056383347, https://morningstar.it/..., https://investing.com/...",
            help="Supporta: Ticker Yahoo Finance, ISIN (Morningstar/JustETF), URL Morningstar, URL Investing.com",
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
