"""
Currency Converter - Convert prices to EUR
Uses Yahoo Finance exchange rates for real-time conversion
"""
import yfinance as yf
import pandas as pd
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Cache for exchange rates (to avoid repeated API calls)
_exchange_rate_cache: Dict[str, float] = {}


def get_exchange_rate(from_currency: str, to_currency: str = "EUR") -> Optional[float]:
    """
    Get exchange rate from one currency to another

    Args:
        from_currency: Source currency (e.g., "USD", "GBP")
        to_currency: Target currency (default "EUR")

    Returns:
        Exchange rate or None if not available

    Example:
        >>> rate = get_exchange_rate("USD", "EUR")
        >>> print(f"1 USD = {rate} EUR")
    """
    # If same currency, return 1
    if from_currency == to_currency:
        return 1.0

    # If EUR is source, just invert
    if from_currency == "EUR":
        return 1.0

    # Check cache
    cache_key = f"{from_currency}{to_currency}"
    if cache_key in _exchange_rate_cache:
        return _exchange_rate_cache[cache_key]

    try:
        # Yahoo Finance uses format: USDEUR=X for USD to EUR
        ticker_symbol = f"{from_currency}{to_currency}=X"
        ticker = yf.Ticker(ticker_symbol)

        # Get latest price (exchange rate)
        hist = ticker.history(period="1d")

        if not hist.empty and "Close" in hist.columns:
            rate = float(hist["Close"].iloc[-1])
            _exchange_rate_cache[cache_key] = rate
            logger.info(f"Exchange rate {from_currency}/{to_currency}: {rate}")
            return rate
        else:
            logger.warning(f"No exchange rate found for {from_currency}/{to_currency}")
            return None

    except Exception as e:
        logger.error(f"Error fetching exchange rate {from_currency}/{to_currency}: {e}")
        return None


def convert_to_eur(value: float, from_currency: str) -> Optional[float]:
    """
    Convert a value to EUR

    Args:
        value: Amount in source currency
        from_currency: Source currency code

    Returns:
        Value in EUR or None if conversion failed
    """
    if from_currency == "EUR" or from_currency == "€":
        return value

    rate = get_exchange_rate(from_currency, "EUR")

    if rate is not None:
        return value * rate
    else:
        logger.warning(f"Cannot convert {value} {from_currency} to EUR - using original value")
        return value  # Return original value if conversion fails


def convert_series_to_eur(series: pd.Series, from_currency: str) -> pd.Series:
    """
    Convert a pandas Series of prices to EUR

    Args:
        series: Price series
        from_currency: Source currency

    Returns:
        Converted series in EUR
    """
    if from_currency == "EUR" or from_currency == "€":
        return series

    rate = get_exchange_rate(from_currency, "EUR")

    if rate is not None:
        return series * rate
    else:
        logger.warning(f"Cannot convert series from {from_currency} to EUR - using original values")
        return series


def get_currency_symbol(ticker_symbol: str) -> str:
    """
    Get currency for a ticker symbol using Yahoo Finance

    Args:
        ticker_symbol: Stock/ETF ticker

    Returns:
        Currency code (e.g., "USD", "EUR", "GBP")
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        currency = info.get("currency", "USD")
        return currency
    except Exception as e:
        logger.debug(f"Cannot determine currency for {ticker_symbol}, defaulting to USD: {e}")
        return "USD"


def clear_cache():
    """Clear the exchange rate cache"""
    global _exchange_rate_cache
    _exchange_rate_cache.clear()
    logger.info("Exchange rate cache cleared")


# Common currency mappings
CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "JPY": "¥",
    "CHF": "CHF",
    "CAD": "C$",
    "AUD": "A$",
    "CNY": "¥",
    "HKD": "HK$",
}


if __name__ == "__main__":
    # Test
    print("Testing Currency Converter...")

    # Test USD to EUR
    rate = get_exchange_rate("USD", "EUR")
    print(f"USD/EUR rate: {rate}")

    # Test conversion
    usd_value = 100
    eur_value = convert_to_eur(usd_value, "USD")
    print(f"{usd_value} USD = {eur_value} EUR")

    # Test GBP to EUR
    rate_gbp = get_exchange_rate("GBP", "EUR")
    print(f"GBP/EUR rate: {rate_gbp}")
