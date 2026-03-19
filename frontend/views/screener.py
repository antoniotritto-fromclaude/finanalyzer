"""
Screener SEMPLIFICATO - Seleziona titoli da aggiungere al portafoglio
"""
import streamlit as st
import pandas as pd
import yfinance as yf
import time


# Liste predefinite per selezione rapida (formato: ticker: nome)
AZIONI_POPOLARI = {
    "🇮🇹 Italia": {
        "ENI.MI": "ENI", "ENEL.MI": "Enel", "ISP.MI": "Intesa Sanpaolo",
        "UCG.MI": "UniCredit", "RACE.MI": "Ferrari", "STLAM.MI": "Stellantis",
        "TIT.MI": "Telecom Italia", "AZM.MI": "Azimut", "G.MI": "Generali", "TENR.MI": "Tenaris"
    },
    "🇺🇸 USA Tech": {
        "AAPL": "Apple", "MSFT": "Microsoft", "GOOGL": "Alphabet (Google)",
        "AMZN": "Amazon", "NVDA": "NVIDIA", "META": "Meta (Facebook)",
        "TSLA": "Tesla", "NFLX": "Netflix", "AMD": "AMD", "INTC": "Intel"
    },
    "🇺🇸 USA Finance": {
        "JPM": "JPMorgan Chase", "BAC": "Bank of America", "WFC": "Wells Fargo",
        "GS": "Goldman Sachs", "MS": "Morgan Stanley", "C": "Citigroup",
        "BLK": "BlackRock", "SCHW": "Charles Schwab"
    },
    "🇺🇸 USA Consumer": {
        "WMT": "Walmart", "HD": "Home Depot", "MCD": "McDonald's",
        "NKE": "Nike", "SBUX": "Starbucks", "TGT": "Target", "COST": "Costco"
    },
    "🇪🇺 Europa": {
        "AIR.PA": "Airbus", "SAN.MC": "Santander", "OR.PA": "L'Oréal",
        "BNP.PA": "BNP Paribas", "SU.PA": "Schneider Electric", "SAP.DE": "SAP", "SIE.DE": "Siemens"
    },
}

ETF_POPOLARI = {
    "🌍 Globali Azionari": {
        "SWDA.MI": "iShares MSCI World", "VWCE.DE": "Vanguard FTSE All-World (Acc)",
        "CSPX.MI": "iShares S&P 500", "VUSA.L": "Vanguard S&P 500",
        "IWDA.AS": "iShares MSCI World (Acc)", "EUNL.DE": "Lyxor MSCI World", "VHYL.L": "Vanguard FTSE High Div"
    },
    "🇺🇸 USA": {
        "SPY": "SPDR S&P 500", "QQQ": "Invesco QQQ (Nasdaq-100)", "VOO": "Vanguard S&P 500",
        "VTI": "Vanguard Total Market", "IVV": "iShares S&P 500", "DIA": "SPDR Dow Jones", "IWM": "iShares Russell 2000"
    },
    "🇪🇺 Europa": {
        "EXS1.DE": "iShares STOXX 600", "IQQE.DE": "iShares MSCI EMU", "MEUD.DE": "Amundi MSCI Europe",
        "IUSE.L": "iShares MSCI Europe", "SMEA.L": "iShares MSCI Europe Small Cap"
    },
    "🌏 Emergenti": {
        "EIMI.MI": "iShares MSCI EM IMI", "AEEM.MI": "Amundi MSCI EM", "IEMG": "iShares MSCI EM",
        "VWO": "Vanguard FTSE EM", "EEM": "iShares MSCI EM"
    },
    "🏛️ Obbligazionari": {
        "VGEA.L": "Vanguard EUR Govt Bond", "IEAG.L": "iShares EUR Agg Bond", "AGGH.MI": "iShares Global Agg Bond",
        "AGG": "iShares US Agg Bond", "BND": "Vanguard Total Bond", "GOVT": "iShares US Treasury"
    },
    "💎 Commodities ETF": {
        "GLD": "SPDR Gold Trust", "SLV": "iShares Silver", "USO": "US Oil Fund",
        "DBA": "Invesco Agriculture", "PDBC": "Invesco Commodities"
    },
    "📊 Tematici": {
        "ECAR.MI": "iShares Electric Vehicles", "IUIT.MI": "iShares Automation & Robotics", "HEAL.L": "iShares Healthcare",
        "RBOT.L": "iShares Robotics", "ARKK": "ARK Innovation", "ICLN": "iShares Clean Energy"
    },
}

COMMODITIES = {
    "⚡ Energia": {
        "CL=F": "Petrolio WTI", "NG=F": "Gas Naturale", "BZ=F": "Petrolio Brent"
    },
    "🥇 Metalli Preziosi": {
        "GC=F": "Oro", "SI=F": "Argento", "PL=F": "Platino", "PA=F": "Palladio"
    },
    "🌾 Agricoltura": {
        "ZC=F": "Mais", "ZW=F": "Grano", "KC=F": "Caffè", "CC=F": "Cacao", "SB=F": "Zucchero"
    },
    "🏗️ Metalli Industriali": {
        "HG=F": "Rame", "ALI=F": "Alluminio"
    },
}

CRYPTO = {
    "💰 Principali": {
        "BTC-USD": "Bitcoin", "ETH-USD": "Ethereum", "BNB-USD": "Binance Coin",
        "XRP-USD": "Ripple", "ADA-USD": "Cardano", "SOL-USD": "Solana", "DOGE-USD": "Dogecoin"
    },
}


def _add_to_portfolio(symbol):
    """Aggiunge un simbolo al portafoglio"""
    import logging
    logger = logging.getLogger(__name__)

    if "pf_symbols" not in st.session_state:
        st.session_state["pf_symbols"] = []

    if symbol in st.session_state["pf_symbols"]:
        return False, f"⚠️ Già nel portafoglio"

    # Valida con Yahoo Finance, Morningstar, JustETF, o Investing.com
    try:
        from backend.data_loader import load_prices_smart, is_isin
        from backend.data_collectors.morningstar import MorningstarCollector
        from backend.data_collectors.investing import investing_collector

        # DEBUG: Log input
        logger.info(f"[SCREENER] Validating: {symbol}")

        # Determina il tipo di input PRIMA di caricare
        is_ms_url = "morningstar" in symbol.lower() and ("http" in symbol.lower())
        is_inv_url = "investing" in symbol.lower() and ("http" in symbol.lower())
        is_isin_code = is_isin(symbol)

        logger.info(f"[SCREENER] Type detection: MS_URL={is_ms_url}, INV_URL={is_inv_url}, ISIN={is_isin_code}")

        # Determina fonte prevista
        if is_ms_url:
            expected_source = "Morningstar"
            fund_id = MorningstarCollector.extract_fund_id_from_url(symbol)
            if not fund_id:
                return False, f"❌ Impossibile estrarre ID da URL Morningstar. Verifica il formato."
            display_name = f"Fondo {fund_id}"
        elif is_inv_url:
            expected_source = "Investing.com"
            instrument = investing_collector.extract_instrument_from_url(symbol)
            if not instrument:
                return False, f"❌ Impossibile estrarre strumento da URL Investing.com. Verifica il formato."
            display_name = instrument
        elif is_isin_code:
            expected_source = "Morningstar/JustETF"
            display_name = f"ISIN {symbol}"
        else:
            expected_source = "Yahoo Finance"
            display_name = f"Ticker {symbol}"

        # Test caricamento prezzi
        logger.info(f"[SCREENER] Loading prices from {expected_source}...")
        prices_df = load_prices_smart([symbol], period="5d")

        logger.info(f"[SCREENER] Result: {len(prices_df)} rows, columns={list(prices_df.columns)}")

        if prices_df.empty or symbol not in prices_df.columns:
            return False, f"❌ {display_name} non trovato su {expected_source}. Verifica l'input."

        st.session_state["pf_symbols"].append(symbol)
        return True, f"✅ {display_name} aggiunto! ({expected_source})"

    except Exception as e:
        logger.error(f"[SCREENER] Exception: {e}", exc_info=True)
        return False, f"❌ Errore: {str(e)[:150]}"


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
                # Non uppercase gli URL! Solo i ticker normali
                clean_symbol = manual_symbol.strip()
                if not ("http://" in clean_symbol or "https://" in clean_symbol):
                    clean_symbol = clean_symbol.upper()

                success, msg = _add_to_portfolio(clean_symbol)
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

        for region, stocks_dict in AZIONI_POPOLARI.items():
            with st.expander(f"{region} ({len(stocks_dict)} titoli)"):
                cols = st.columns(4)
                for i, (ticker, name) in enumerate(stocks_dict.items()):
                    with cols[i % 4]:
                        # Tronca nome se troppo lungo
                        display_name = name[:15] + "..." if len(name) > 15 else name
                        if st.button(f"{display_name}\n({ticker})", key=f"stock_{ticker}", use_container_width=True, help=f"{name} - {ticker}"):
                            success, msg = _add_to_portfolio(ticker)
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

        for category, etfs_dict in ETF_POPOLARI.items():
            with st.expander(f"{category} ({len(etfs_dict)} ETF)"):
                cols = st.columns(4)
                for i, (ticker, name) in enumerate(etfs_dict.items()):
                    with cols[i % 4]:
                        display_name = name[:18] + "..." if len(name) > 18 else name
                        if st.button(f"{display_name}\n({ticker})", key=f"etf_{ticker}", use_container_width=True, help=f"{name} - {ticker}"):
                            success, msg = _add_to_portfolio(ticker)
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

        for category, comm_dict in COMMODITIES.items():
            with st.expander(f"{category} ({len(comm_dict)} asset)"):
                cols = st.columns(4)
                for i, (ticker, name) in enumerate(comm_dict.items()):
                    with cols[i % 4]:
                        if st.button(f"{name}\n({ticker})", key=f"comm_{ticker}", use_container_width=True, help=f"{name} - {ticker}"):
                            success, msg = _add_to_portfolio(ticker)
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

        for category, crypto_dict in CRYPTO.items():
            cols = st.columns(4)
            for i, (ticker, name) in enumerate(crypto_dict.items()):
                with cols[i % 4]:
                    if st.button(f"{name}\n({ticker})", key=f"crypto_{ticker}", use_container_width=True, help=f"{name} - {ticker}"):
                        success, msg = _add_to_portfolio(ticker)
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
