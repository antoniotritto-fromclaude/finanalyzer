"""
Smart Data Loader - Yahoo Finance + Morningstar
Carica prezzi da fonti multiple con fallback automatico
"""
import pandas as pd
import yfinance as yf
import time
import re
from typing import List, Dict
import logging

from backend.data_collectors.morningstar import MorningstarCollector
from backend.data_collectors.justetf import justetf_collector
from backend.data_collectors.investing import investing_collector
from backend.cache.funds_cache import funds_cache

logger = logging.getLogger(__name__)


def is_isin(symbol: str) -> bool:
    """
    Rileva se un simbolo è un codice ISIN

    ISIN format: 2 lettere paese + 10 caratteri alfanumerici
    Esempi: IT0005239881, LU1234567890, IE00B4L5Y983
    """
    pattern = r'^[A-Z]{2}[A-Z0-9]{10}$'
    return bool(re.match(pattern, symbol.upper()))


def load_prices_smart(symbols: List[str], period: str = "3y") -> pd.DataFrame:
    """
    Carica prezzi storici da multiple fonti: Yahoo Finance, Morningstar, JustETF, Investing.com

    Routing automatico:
        - URL Investing.com → Investing.com
        - URL Morningstar → Morningstar
        - ISIN codes → Morningstar (priorità) o JustETF (fallback)
        - Tickers → Yahoo Finance

    Args:
        symbols: Lista di simboli (ticker, ISIN, URLs)
        period: Periodo storico ("1y", "3y", "5y", "max")

    Returns:
        DataFrame con colonne per ogni simbolo e date come index
        Colonne mancanti se simbolo non trovato

    Example:
        >>> symbols = ["AAPL", "IT0005239881", "https://investing.com/equities/apple"]
        >>> df = load_prices_smart(symbols, period="3y")
        >>> print(df.columns)
        Index(['AAPL', 'IT0005239881', 'https://investing.com/equities/apple'])
    """
    prices = {}
    ms_collector = MorningstarCollector()

    # Converti period in anni per Morningstar
    period_years = {
        "1y": 1,
        "2y": 2,
        "3y": 3,
        "5y": 5,
        "7y": 7,
        "max": 10,
    }.get(period, 3)

    for symbol in symbols:
        logger.info(f"Caricamento prezzi per {symbol}...")

        # Check 0: È un fondo inserito manualmente?
        if symbol.startswith("MANUAL_"):
            logger.info(f"  → Rilevato fondo manuale: {symbol}")
            try:
                # Importa streamlit per accedere a session_state
                import streamlit as st
                manual_funds = st.session_state.get("manual_funds", {})

                if symbol in manual_funds:
                    fund_data = manual_funds[symbol]
                    nav = fund_data.get("nav", 100.0)
                    perf = fund_data.get("performance", {})

                    # Genera serie storica sintetica basata su performance
                    # Oggi = NAV corrente
                    # 1 anno fa = NAV / (1 + perf_1y/100)
                    # 3 anni fa = NAV / ((1 + perf_3y/100)^3)
                    # 5 anni fa = NAV / ((1 + perf_5y/100)^5)

                    dates = [pd.Timestamp.now()]
                    values = [nav]

                    perf_1y = perf.get("1y", 0) / 100
                    perf_3y = perf.get("3y", 0) / 100
                    perf_5y = perf.get("5y", 0) / 100

                    # Calcola NAV storico
                    if perf_1y != 0:
                        nav_1y = nav / (1 + perf_1y)
                        dates.append(pd.Timestamp.now() - pd.DateOffset(years=1))
                        values.append(nav_1y)

                    if perf_3y != 0:
                        nav_3y = nav / ((1 + perf_3y) ** 3)
                        dates.append(pd.Timestamp.now() - pd.DateOffset(years=3))
                        values.append(nav_3y)

                    if perf_5y != 0:
                        nav_5y = nav / ((1 + perf_5y) ** 5)
                        dates.append(pd.Timestamp.now() - pd.DateOffset(years=5))
                        values.append(nav_5y)

                    # Crea serie temporale
                    manual_series = pd.Series(dict(zip(dates, values))).sort_index()

                    # Interpola per avere dati intermedi
                    manual_series = manual_series.resample('D').interpolate(method='linear')

                    logger.info(f"  ✅ Fondo manuale caricato: {len(manual_series)} punti sintetici")
                    prices[symbol] = manual_series
                else:
                    logger.warning(f"  ⚠️  Fondo manuale {symbol} non trovato in session_state")

            except Exception as e:
                logger.error(f"  ❌ Errore caricamento fondo manuale: {e}")
            continue

        # Check 1: È un URL Investing.com?
        if investing_collector.is_investing_url(symbol):
            logger.info(f"  → Rilevato URL Investing.com: {symbol}")
            instrument_path = investing_collector.extract_instrument_from_url(symbol)

            if not instrument_path:
                logger.error(f"  ❌ Impossibile estrarre strumento da URL: {symbol}")
                continue

            cache_key = f"INV_{instrument_path.replace('/', '_')}"

            # Step 1: Prova cache
            cached_prices = funds_cache.get_prices(cache_key)
            if cached_prices is not None and not cached_prices.empty:
                logger.info(f"  ✅ Caricato da cache ({len(cached_prices)} punti)")
                prices[symbol] = cached_prices
                funds_cache.add_recent(cache_key, instrument_path, "Investing.com")
                continue

            # Step 2: Scraping Investing.com
            logger.info(f"  → Scraping Investing.com ({instrument_path})...")
            try:
                inv_prices = investing_collector.get_historical_prices(instrument_path, years=period_years)

                if inv_prices is not None and not inv_prices.empty:
                    funds_cache.set_prices(cache_key, instrument_path, inv_prices)
                    funds_cache.add_recent(cache_key, instrument_path, "Investing.com")

                    logger.info(f"  ✅ Caricato da Investing.com ({len(inv_prices)} punti)")
                    prices[symbol] = inv_prices
                else:
                    logger.warning(f"  ❌ Nessun dato trovato per {instrument_path}")

            except Exception as e:
                logger.error(f"  ❌ Errore Investing.com: {e}")

        # Check 2: È un URL Morningstar?
        elif ms_collector.is_morningstar_url(symbol):
            logger.info(f"  → Rilevato URL Morningstar: {symbol}")
            fund_id = ms_collector.extract_fund_id_from_url(symbol)

            if not fund_id:
                logger.error(f"  ❌ Impossibile estrarre ID da URL: {symbol}")
                logger.error(f"  💡 Formati supportati: ?id=XXX, /fondi/XXX, /funds/XXX")
                continue

            # Usa fund_id come chiave per cache
            cache_key = f"MS_{fund_id}"

            # Step 1: Prova cache
            cached_prices = funds_cache.get_prices(cache_key)
            if cached_prices is not None and not cached_prices.empty:
                logger.info(f"  ✅ Caricato da cache ({len(cached_prices)} punti)")
                prices[symbol] = cached_prices
                # Aggiorna timestamp nei recenti (lo sposta in cima)
                funds_cache.add_recent(cache_key, f"Fund_{fund_id}", "Morningstar")
                continue

            # Step 2: Scraping Morningstar diretto
            logger.info(f"  → Scraping Morningstar (ID: {fund_id})...")
            try:
                fund_prices = ms_collector.get_historical_prices_by_id(fund_id, years=period_years)

                if fund_prices is not None and not fund_prices.empty:
                    # Salva in cache con cache_key
                    fund_name = f"Fund_{fund_id}"
                    funds_cache.set_prices(cache_key, fund_name, fund_prices)

                    # Aggiungi a recenti
                    funds_cache.add_recent(cache_key, fund_name, "Morningstar")

                    logger.info(f"  ✅ Caricato da Morningstar ({len(fund_prices)} punti)")
                    prices[symbol] = fund_prices
                else:
                    logger.warning(f"  ❌ Nessun dato trovato per fund_id {fund_id}")

            except Exception as e:
                logger.error(f"  ❌ Errore Morningstar per fund_id {fund_id}: {e}")

        # Check 3: È un ISIN?
        elif is_isin(symbol):
            # ═══ FONDO/ETF CON ISIN → Usa Morningstar O JustETF ═══
            logger.info(f"  → Rilevato ISIN: {symbol}")

            # Step 1: Prova cache
            cached_prices = funds_cache.get_prices(symbol)
            if cached_prices is not None and not cached_prices.empty:
                logger.info(f"  ✅ Caricato da cache ({len(cached_prices)} punti)")
                prices[symbol] = cached_prices
                # Aggiorna timestamp nei recenti (lo sposta in cima)
                funds_cache.add_recent(symbol, symbol, "Cache")
                continue

            # Step 2: Prova Morningstar
            logger.info(f"  → Tentativo #1: Morningstar...")
            fund_prices = None
            source_used = None

            try:
                fund_prices = ms_collector.get_historical_prices_by_isin(symbol, years=period_years)
                if fund_prices is not None and not fund_prices.empty:
                    source_used = "Morningstar"
                    logger.info(f"  ✅ Trovato su Morningstar ({len(fund_prices)} punti)")
            except Exception as e:
                logger.debug(f"  Morningstar fallito: {e}")

            # Step 3: Se Morningstar fallisce, prova JustETF
            if fund_prices is None or fund_prices.empty:
                logger.info(f"  → Tentativo #2: JustETF...")
                try:
                    fund_prices = justetf_collector.get_historical_prices_by_isin(symbol, years=period_years)
                    if fund_prices is not None and not fund_prices.empty:
                        source_used = "JustETF"
                        logger.info(f"  ✅ Trovato su JustETF ({len(fund_prices)} punti)")
                except Exception as e:
                    logger.debug(f"  JustETF fallito: {e}")

            # Step 4: Salva se trovato
            if fund_prices is not None and not fund_prices.empty:
                funds_cache.set_prices(symbol, symbol, fund_prices)
                funds_cache.add_recent(symbol, symbol, source_used)
                prices[symbol] = fund_prices
            else:
                logger.warning(f"  ❌ ISIN {symbol} non trovato su Morningstar né JustETF")

        else:
            # Check 4: TICKER STANDARD → Usa Yahoo Finance
            logger.info(f"  → Rilevato ticker: {symbol}")

            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period, auto_adjust=True)

                if not hist.empty and "Close" in hist.columns:
                    logger.info(f"  ✅ Caricato da Yahoo Finance ({len(hist)} punti)")
                    prices[symbol] = hist["Close"]
                else:
                    logger.warning(f"  ❌ Nessun dato trovato per ticker {symbol}")

            except Exception as e:
                logger.error(f"  ❌ Errore Yahoo Finance per {symbol}: {e}")

        # Rate limiting
        time.sleep(0.3)

    # Crea DataFrame unificato
    if prices:
        df = pd.DataFrame(prices)
        # Allinea date e riempi NaN (forward fill then backward fill)
        df = df.ffill().bfill()
        logger.info(f"✅ Dataset completo: {len(df)} giorni, {len(df.columns)} asset")
        return df
    else:
        logger.warning("❌ Nessun dato caricato")
        return pd.DataFrame()


def get_latest_price(symbol: str) -> Dict:
    """
    Ottiene prezzo più recente per un simbolo

    Returns:
        {
            "symbol": "AAPL",
            "price": 150.25,
            "change": +1.2,
            "change_pct": +0.8,
            "currency": "USD",
            "source": "Yahoo Finance" or "Morningstar"
        }
    """
    if is_isin(symbol):
        # Usa Morningstar
        cached = funds_cache.get_prices(symbol)
        if cached is not None and not cached.empty:
            last_price = cached.iloc[-1]
            prev_price = cached.iloc[-2] if len(cached) > 1 else last_price
            return {
                "symbol": symbol,
                "price": float(last_price),
                "change": float(last_price - prev_price),
                "change_pct": float((last_price - prev_price) / prev_price * 100) if prev_price != 0 else 0,
                "currency": "EUR",
                "source": "Morningstar (cached)",
            }
    else:
        # Usa Yahoo Finance
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            if not hist.empty:
                last_price = hist["Close"].iloc[-1]
                prev_price = hist["Close"].iloc[-2] if len(hist) > 1 else last_price
                info = ticker.info
                return {
                    "symbol": symbol,
                    "price": float(last_price),
                    "change": float(last_price - prev_price),
                    "change_pct": float((last_price - prev_price) / prev_price * 100) if prev_price != 0 else 0,
                    "currency": info.get("currency", "USD"),
                    "source": "Yahoo Finance",
                }
        except:
            pass

    # Fallback
    return {
        "symbol": symbol,
        "price": 0,
        "change": 0,
        "change_pct": 0,
        "currency": "EUR",
        "source": "N/A",
    }

def get_manual_fund_info(symbol: str) -> Dict:
    """
    Ottiene informazioni complete per un fondo inserito manualmente

    Args:
        symbol: ID fondo manuale (es: MANUAL_LU0738951036)

    Returns:
        Dict con tutte le info del fondo o None
    """
    if not symbol.startswith("MANUAL_"):
        return None

    try:
        import streamlit as st
        manual_funds = st.session_state.get("manual_funds", {})

        if symbol in manual_funds:
            return manual_funds[symbol]
        else:
            logger.warning(f"Fondo manuale {symbol} non trovato")
            return None

    except Exception as e:
        logger.error(f"Errore recupero info fondo manuale: {e}")
        return None


def is_manual_fund(symbol: str) -> bool:
    """Verifica se un simbolo è un fondo manuale"""
    return symbol.startswith("MANUAL_")
