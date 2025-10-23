"""
Yahoo Finance Data Collector
Raccoglie dati da Yahoo Finance usando yfinance
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YahooFinanceCollector:
    """Collector per dati da Yahoo Finance"""

    def __init__(self):
        self.cache = {}

    def search_ticker(self, query: str, asset_type: Optional[str] = None) -> List[Dict]:
        """
        Cerca un ticker su Yahoo Finance

        Args:
            query: Simbolo o nome da cercare
            asset_type: Tipo di asset (stock, etf, fund, etc.)

        Returns:
            Lista di risultati con informazioni base
        """
        try:
            ticker = yf.Ticker(query)
            info = ticker.info

            if info and 'symbol' in info:
                return [{
                    'symbol': info.get('symbol', query),
                    'name': info.get('longName', info.get('shortName', '')),
                    'type': info.get('quoteType', 'Unknown'),
                    'exchange': info.get('exchange', ''),
                    'currency': info.get('currency', ''),
                    'sector': info.get('sector', ''),
                    'industry': info.get('industry', ''),
                }]
            return []
        except Exception as e:
            logger.error(f"Errore nella ricerca ticker {query}: {e}")
            return []

    def get_historical_data(
        self,
        symbol: str,
        period: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Ottiene dati storici per un simbolo

        Args:
            symbol: Simbolo del ticker
            period: Periodo (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 7y, 10y, ytd, max)
            start_date: Data inizio (YYYY-MM-DD)
            end_date: Data fine (YYYY-MM-DD)
            interval: Intervallo (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)

        Returns:
            DataFrame con dati storici (Open, High, Low, Close, Volume)
        """
        try:
            ticker = yf.Ticker(symbol)

            if period:
                df = ticker.history(period=period, interval=interval)
            else:
                df = ticker.history(start=start_date, end=end_date, interval=interval)

            return df
        except Exception as e:
            logger.error(f"Errore nel recupero dati storici per {symbol}: {e}")
            return pd.DataFrame()

    def get_ticker_info(self, symbol: str) -> Dict:
        """
        Ottiene informazioni dettagliate su un ticker

        Args:
            symbol: Simbolo del ticker

        Returns:
            Dizionario con informazioni complete
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                'symbol': info.get('symbol', symbol),
                'name': info.get('longName', info.get('shortName', '')),
                'type': info.get('quoteType', ''),
                'exchange': info.get('exchange', ''),
                'currency': info.get('currency', ''),
                'current_price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
                'previous_close': info.get('previousClose', 0),
                'open': info.get('open', 0),
                'day_high': info.get('dayHigh', 0),
                'day_low': info.get('dayLow', 0),
                'volume': info.get('volume', 0),
                'market_cap': info.get('marketCap', 0),
                'beta': info.get('beta', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'description': info.get('longBusinessSummary', ''),
            }
        except Exception as e:
            logger.error(f"Errore nel recupero info per {symbol}: {e}")
            return {}

    def get_multiple_tickers_data(
        self,
        symbols: List[str],
        period: str = "1y",
        interval: str = "1d"
    ) -> Dict[str, pd.DataFrame]:
        """
        Ottiene dati storici per multipli ticker

        Args:
            symbols: Lista di simboli
            period: Periodo di dati
            interval: Intervallo dati

        Returns:
            Dizionario {symbol: DataFrame}
        """
        result = {}

        for symbol in symbols:
            df = self.get_historical_data(symbol, period=period, interval=interval)
            if not df.empty:
                result[symbol] = df
            else:
                logger.warning(f"Nessun dato trovato per {symbol}")

        return result

    def get_dividends(self, symbol: str) -> pd.DataFrame:
        """
        Ottiene la storia dei dividendi

        Args:
            symbol: Simbolo del ticker

        Returns:
            DataFrame con dividendi
        """
        try:
            ticker = yf.Ticker(symbol)
            return ticker.dividends
        except Exception as e:
            logger.error(f"Errore nel recupero dividendi per {symbol}: {e}")
            return pd.DataFrame()

    def get_financials(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """
        Ottiene i dati finanziari di un'azienda

        Args:
            symbol: Simbolo del ticker

        Returns:
            Dizionario con income_statement, balance_sheet, cash_flow
        """
        try:
            ticker = yf.Ticker(symbol)
            return {
                'income_statement': ticker.income_stmt,
                'balance_sheet': ticker.balance_sheet,
                'cash_flow': ticker.cashflow,
            }
        except Exception as e:
            logger.error(f"Errore nel recupero dati finanziari per {symbol}: {e}")
            return {}


# Funzioni di utilità
def get_italian_stocks() -> List[str]:
    """Restituisce una lista di simboli di azioni italiane comuni"""
    return [
        'ENI.MI',      # Eni
        'ISP.MI',      # Intesa Sanpaolo
        'UCG.MI',      # UniCredit
        'TIT.MI',      # Telecom Italia
        'ENEL.MI',     # Enel
        'G.MI',        # Generali
        'STLAM.MI',    # Stellantis
        'TEN.MI',      # Tenaris
        'LDO.MI',      # Leonardo
        'RACE.MI',     # Ferrari
    ]


def get_italian_etfs() -> List[str]:
    """Restituisce una lista di ETF italiani/europei comuni"""
    return [
        'SWDA.MI',     # iShares Core MSCI World
        'VWCE.DE',     # Vanguard FTSE All-World
        'CSSPX.MI',    # iShares Core S&P 500
        'EIMI.MI',     # iShares Core MSCI EM IMI
    ]
