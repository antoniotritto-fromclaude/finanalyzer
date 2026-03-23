"""
🔍 Asset Search Module
Advanced search for stocks, ETFs, crypto, and commodities
"""
import yfinance as yf
import requests
from typing import List, Dict, Optional
import pandas as pd


# ══════════════════════════════════════════════════════════════════════
# 📈 STOCKS SEARCH (Yahoo Finance)
# ══════════════════════════════════════════════════════════════════════

def search_stocks(query: str, max_results: int = 20) -> List[Dict]:
    """
    Search stocks globally using Yahoo Finance

    Args:
        query: Search term (name, ticker, or keyword)
        max_results: Maximum number of results

    Returns:
        List of dicts with: symbol, name, exchange, type
    """
    try:
        # Use yfinance Ticker search
        results = []

        # Try direct ticker lookup first
        try:
            ticker = yf.Ticker(query.upper())
            info = ticker.info
            if info and 'symbol' in info:
                results.append({
                    'symbol': info.get('symbol', query.upper()),
                    'name': info.get('longName', info.get('shortName', 'N/A')),
                    'exchange': info.get('exchange', 'N/A'),
                    'type': 'stock',
                    'currency': info.get('currency', 'USD')
                })
        except:
            pass

        # Yahoo Finance search API (unofficial)
        try:
            url = f"https://query2.finance.yahoo.com/v1/finance/search"
            params = {
                'q': query,
                'quotesCount': max_results,
                'newsCount': 0,
                'enableFuzzyQuery': False,
                'quotesQueryId': 'tss_match_phrase_query'
            }
            headers = {'User-Agent': 'Mozilla/5.0'}

            response = requests.get(url, params=params, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                quotes = data.get('quotes', [])

                for quote in quotes[:max_results]:
                    if quote.get('quoteType') in ['EQUITY', 'ETF']:
                        results.append({
                            'symbol': quote.get('symbol'),
                            'name': quote.get('longname', quote.get('shortname', 'N/A')),
                            'exchange': quote.get('exchange', 'N/A'),
                            'type': quote.get('quoteType', 'stock').lower(),
                            'currency': quote.get('currency', 'USD')
                        })
        except:
            pass

        return results[:max_results]

    except Exception as e:
        print(f"Error searching stocks: {e}")
        return []


# ══════════════════════════════════════════════════════════════════════
# 📡 ETF SEARCH (Yahoo Finance - comprehensive ETF database)
# ══════════════════════════════════════════════════════════════════════

def search_etfs(query: str, max_results: int = 20) -> List[Dict]:
    """
    Search ETFs globally using Yahoo Finance

    Args:
        query: Search term (name, ticker, or keyword)
        max_results: Maximum number of results

    Returns:
        List of dicts with: symbol, name, exchange, type
    """
    try:
        results = []

        # Yahoo Finance search focusing on ETFs
        url = f"https://query2.finance.yahoo.com/v1/finance/search"
        params = {
            'q': query,
            'quotesCount': max_results * 2,  # Get more to filter ETFs
            'newsCount': 0,
            'enableFuzzyQuery': True,
            'quotesQueryId': 'tss_match_phrase_query'
        }
        headers = {'User-Agent': 'Mozilla/5.0'}

        response = requests.get(url, params=params, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            quotes = data.get('quotes', [])

            for quote in quotes:
                # Filter only ETFs
                if quote.get('quoteType') == 'ETF':
                    results.append({
                        'symbol': quote.get('symbol'),
                        'name': quote.get('longname', quote.get('shortname', 'N/A')),
                        'exchange': quote.get('exchange', 'N/A'),
                        'type': 'etf',
                        'currency': quote.get('currency', 'USD')
                    })

                    if len(results) >= max_results:
                        break

        return results

    except Exception as e:
        print(f"Error searching ETFs: {e}")
        return []


# ══════════════════════════════════════════════════════════════════════
# 💰 CRYPTO SEARCH (Yahoo Finance - uses BTC-USD, ETH-USD format)
# ══════════════════════════════════════════════════════════════════════

def search_crypto(query: str, max_results: int = 20) -> List[Dict]:
    """
    Search cryptocurrencies using Yahoo Finance (format: BTC-USD, ETH-USD)

    Args:
        query: Search term (name or ticker)
        max_results: Maximum number of results

    Returns:
        List of dicts with: symbol, name, type
    """
    try:
        results = []

        # Try direct crypto lookup (e.g., BTC -> BTC-USD)
        crypto_query = query.upper()
        if not crypto_query.endswith('-USD'):
            crypto_query = f"{crypto_query}-USD"

        try:
            ticker = yf.Ticker(crypto_query)
            info = ticker.info
            if info and 'symbol' in info:
                results.append({
                    'symbol': info.get('symbol', crypto_query),
                    'name': info.get('longName', info.get('shortName', crypto_query)),
                    'type': 'crypto',
                    'currency': 'USD'
                })
        except:
            pass

        # Yahoo Finance search for cryptocurrencies
        url = f"https://query2.finance.yahoo.com/v1/finance/search"
        params = {
            'q': f"{query} crypto",
            'quotesCount': max_results * 2,
            'newsCount': 0,
            'enableFuzzyQuery': True
        }
        headers = {'User-Agent': 'Mozilla/5.0'}

        response = requests.get(url, params=params, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            quotes = data.get('quotes', [])

            for quote in quotes:
                symbol = quote.get('symbol', '')
                # Filter crypto symbols (end with -USD, -EUR, etc.)
                if quote.get('quoteType') == 'CRYPTOCURRENCY' or '-USD' in symbol or '-EUR' in symbol:
                    results.append({
                        'symbol': symbol,
                        'name': quote.get('longname', quote.get('shortname', symbol)),
                        'type': 'crypto',
                        'currency': 'USD'
                    })

                    if len(results) >= max_results:
                        break

        return results[:max_results]

    except Exception as e:
        print(f"Error searching crypto: {e}")
        return []


# ══════════════════════════════════════════════════════════════════════
# 🌾 COMMODITIES SEARCH (Yahoo Finance - format: GC=F, CL=F, etc.)
# ══════════════════════════════════════════════════════════════════════

# Popular commodities dictionary for quick lookup
POPULAR_COMMODITIES = {
    # Metals
    'gold': 'GC=F',
    'silver': 'SI=F',
    'copper': 'HG=F',
    'platinum': 'PL=F',
    'palladium': 'PA=F',

    # Energy
    'crude oil': 'CL=F',
    'brent': 'BZ=F',
    'natural gas': 'NG=F',
    'heating oil': 'HO=F',
    'gasoline': 'RB=F',

    # Agriculture
    'corn': 'ZC=F',
    'wheat': 'ZW=F',
    'soybeans': 'ZS=F',
    'sugar': 'SB=F',
    'coffee': 'KC=F',
    'cotton': 'CT=F',
    'cocoa': 'CC=F',

    # Livestock
    'cattle': 'LE=F',
    'hogs': 'HE=F',
}

def search_commodities(query: str, max_results: int = 20) -> List[Dict]:
    """
    Search commodities using Yahoo Finance (format: GC=F for Gold, CL=F for Oil)

    Args:
        query: Search term (name or ticker)
        max_results: Maximum number of results

    Returns:
        List of dicts with: symbol, name, type
    """
    try:
        results = []
        query_lower = query.lower()

        # Check popular commodities first
        for name, symbol in POPULAR_COMMODITIES.items():
            if query_lower in name or query_lower in symbol.lower():
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    if info:
                        results.append({
                            'symbol': symbol,
                            'name': info.get('longName', name.title()),
                            'type': 'commodity',
                            'currency': info.get('currency', 'USD')
                        })
                except:
                    results.append({
                        'symbol': symbol,
                        'name': name.title(),
                        'type': 'commodity',
                        'currency': 'USD'
                    })

        # Yahoo Finance search for futures
        if len(results) < max_results:
            url = f"https://query2.finance.yahoo.com/v1/finance/search"
            params = {
                'q': query,
                'quotesCount': max_results,
                'newsCount': 0,
                'enableFuzzyQuery': True
            }
            headers = {'User-Agent': 'Mozilla/5.0'}

            response = requests.get(url, params=params, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                quotes = data.get('quotes', [])

                for quote in quotes:
                    symbol = quote.get('symbol', '')
                    # Filter futures/commodities (end with =F)
                    if quote.get('quoteType') == 'FUTURE' or '=F' in symbol:
                        results.append({
                            'symbol': symbol,
                            'name': quote.get('longname', quote.get('shortname', symbol)),
                            'type': 'commodity',
                            'currency': quote.get('currency', 'USD')
                        })

        return results[:max_results]

    except Exception as e:
        print(f"Error searching commodities: {e}")
        return []


# ══════════════════════════════════════════════════════════════════════
# 🔍 UNIVERSAL SEARCH (All asset types)
# ══════════════════════════════════════════════════════════════════════

def search_all_assets(query: str, max_results: int = 20) -> Dict[str, List[Dict]]:
    """
    Search all asset types at once

    Args:
        query: Search term
        max_results: Maximum results per category

    Returns:
        Dict with keys: stocks, etfs, crypto, commodities
    """
    return {
        'stocks': search_stocks(query, max_results),
        'etfs': search_etfs(query, max_results),
        'crypto': search_crypto(query, max_results),
        'commodities': search_commodities(query, max_results),
    }


# ══════════════════════════════════════════════════════════════════════
# 🧪 TEST FUNCTIONS
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Testing asset search...")

    # Test stocks
    print("\n📈 STOCKS (Apple):")
    stocks = search_stocks("apple")
    for s in stocks[:3]:
        print(f"  {s['symbol']} - {s['name']}")

    # Test ETFs
    print("\n📡 ETFs (S&P 500):")
    etfs = search_etfs("s&p 500")
    for e in etfs[:3]:
        print(f"  {e['symbol']} - {e['name']}")

    # Test Crypto
    print("\n💰 CRYPTO (Bitcoin):")
    crypto = search_crypto("bitcoin")
    for c in crypto[:3]:
        print(f"  {c['symbol']} - {c['name']}")

    # Test Commodities
    print("\n🌾 COMMODITIES (Gold):")
    commodities = search_commodities("gold")
    for c in commodities[:3]:
        print(f"  {c['symbol']} - {c['name']}")
