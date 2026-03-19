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
    Carica prezzi storici da Yahoo Finance O Morningstar

    Args:
        symbols: Lista di simboli (ticker o ISIN)
        period: Periodo storico ("1y", "3y", "5y", "max")

    Returns:
        DataFrame con colonne per ogni simbolo e date come index
        Colonne mancanti se simbolo non trovato

    Example:
        >>> symbols = ["AAPL", "IT0005239881", "SPY"]
        >>> df = load_prices_smart(symbols, period="3y")
        >>> print(df.columns)
        Index(['AAPL', 'IT0005239881', 'SPY'])
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

        # Check 1: È un URL Morningstar?
        if ms_collector.is_morningstar_url(symbol):
            logger.info(f"  → Rilevato URL Morningstar")
            fund_id = ms_collector.extract_fund_id_from_url(symbol)

            if not fund_id:
                logger.error(f"  ❌ Impossibile estrarre ID da URL: {symbol}")
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

        # Check 2: È un ISIN?
        elif is_isin(symbol):
            # ═══ FONDO CON ISIN → Usa Morningstar ═══
            logger.info(f"  → Rilevato ISIN: {symbol}")

            # Step 1: Prova cache
            cached_prices = funds_cache.get_prices(symbol)
            if cached_prices is not None and not cached_prices.empty:
                logger.info(f"  ✅ Caricato da cache ({len(cached_prices)} punti)")
                prices[symbol] = cached_prices
                # Aggiorna timestamp nei recenti (lo sposta in cima)
                funds_cache.add_recent(symbol, symbol, "Morningstar")
                continue

            # Step 2: Scraping Morningstar
            logger.info(f"  → Scraping Morningstar...")
            try:
                fund_prices = ms_collector.get_historical_prices_by_isin(symbol, years=period_years)

                if fund_prices is not None and not fund_prices.empty:
                    # Salva in cache
                    fund_name = symbol  # Usa ISIN come nome se non trovato
                    funds_cache.set_prices(symbol, fund_name, fund_prices)

                    # Aggiungi a recenti
                    funds_cache.add_recent(symbol, fund_name, "Morningstar")

                    logger.info(f"  ✅ Caricato da Morningstar ({len(fund_prices)} punti)")
                    prices[symbol] = fund_prices
                else:
                    logger.warning(f"  ❌ Nessun dato trovato per ISIN {symbol}")

            except Exception as e:
                logger.error(f"  ❌ Errore Morningstar per {symbol}: {e}")

        else:
            # ═══ TICKER STANDARD → Usa Yahoo Finance ═══
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
        # Allinea date e riempi NaN
        df = df.fillna(method='ffill').fillna(method='bfill')
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
