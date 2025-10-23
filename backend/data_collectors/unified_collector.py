"""
Unified Data Collector
Aggrega dati da multiple fonti
"""
from typing import List, Dict, Optional
import pandas as pd
from .yahoo_finance import YahooFinanceCollector
from .investing_com import InvestingComCollector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UnifiedDataCollector:
    """Collector unificato che aggrega dati da multiple fonti"""

    def __init__(self):
        self.yahoo = YahooFinanceCollector()
        self.investing = InvestingComCollector()

    def search_all_sources(self, query: str, asset_type: Optional[str] = None) -> List[Dict]:
        """
        Cerca su tutte le fonti disponibili

        Args:
            query: Termine di ricerca
            asset_type: Tipo di asset (stock, bond, etf, fund, commodity, certificate)

        Returns:
            Lista aggregata di risultati
        """
        all_results = []

        # Yahoo Finance (sempre disponibile)
        yahoo_results = self.yahoo.search_ticker(query, asset_type)
        for result in yahoo_results:
            result['source'] = 'yahoo_finance'
            all_results.append(result)

        # Investing.com
        try:
            investing_results = self.investing.search_instrument(query)
            all_results.extend(investing_results)
        except Exception as e:
            logger.warning(f"Errore in ricerca Investing.com: {e}")

        # Rimuovi duplicati basati sul simbolo
        unique_results = {}
        for result in all_results:
            symbol = result.get('symbol', '')
            if symbol and symbol not in unique_results:
                unique_results[symbol] = result

        return list(unique_results.values())

    def get_historical_prices(
        self,
        symbols: List[str],
        period: str = "1y",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Ottiene prezzi storici per multipli simboli

        Args:
            symbols: Lista di simboli
            period: Periodo (1y, 3y, 5y, 7y)
            start_date: Data inizio (YYYY-MM-DD)
            end_date: Data fine (YYYY-MM-DD)

        Returns:
            DataFrame con colonne multi-level (symbol, price_type)
        """
        all_data = {}

        for symbol in symbols:
            try:
                if start_date and end_date:
                    df = self.yahoo.get_historical_data(
                        symbol,
                        start_date=start_date,
                        end_date=end_date
                    )
                else:
                    df = self.yahoo.get_historical_data(symbol, period=period)

                if not df.empty:
                    # Usa solo la colonna Close per l'analisi di portfolio
                    all_data[symbol] = df['Close']
            except Exception as e:
                logger.error(f"Errore nel recupero dati per {symbol}: {e}")

        if all_data:
            # Crea un DataFrame con tutti i simboli
            result = pd.DataFrame(all_data)
            return result
        else:
            return pd.DataFrame()

    def get_asset_info(self, symbol: str) -> Dict:
        """
        Ottiene informazioni dettagliate su un asset

        Args:
            symbol: Simbolo dell'asset

        Returns:
            Dizionario con informazioni complete
        """
        # Prova prima con Yahoo Finance
        info = self.yahoo.get_ticker_info(symbol)

        if info:
            return info

        # Se Yahoo Finance fallisce, potresti provare altre fonti
        logger.warning(f"Informazioni limitate per {symbol}")
        return {'symbol': symbol}

    def get_bonds(self, country: str = "italy") -> List[Dict]:
        """
        Ottiene lista di obbligazioni

        Args:
            country: Paese

        Returns:
            Lista di obbligazioni
        """
        return self.investing.get_bonds_list(country)

    def get_commodities(self) -> List[Dict]:
        """
        Ottiene lista di commodities

        Returns:
            Lista di commodities
        """
        return self.investing.get_commodities_list()

    def get_etfs(self, country: str = "italy") -> List[Dict]:
        """
        Ottiene lista di ETF

        Args:
            country: Paese

        Returns:
            Lista di ETF
        """
        etfs_investing = self.investing.get_etf_list(country)

        # Aggiungi anche ETF comuni da Yahoo
        italian_etfs = self.yahoo.get_italian_etfs() if country == "italy" else []

        all_etfs = etfs_investing.copy()

        for symbol in italian_etfs:
            info = self.yahoo.get_ticker_info(symbol)
            if info:
                all_etfs.append({
                    'symbol': symbol,
                    'name': info.get('name', ''),
                    'source': 'yahoo_finance'
                })

        return all_etfs

    def validate_symbols(self, symbols: List[str]) -> Dict[str, bool]:
        """
        Valida una lista di simboli

        Args:
            symbols: Lista di simboli da validare

        Returns:
            Dizionario {symbol: is_valid}
        """
        result = {}

        for symbol in symbols:
            try:
                info = self.yahoo.get_ticker_info(symbol)
                result[symbol] = bool(info and info.get('symbol'))
            except Exception:
                result[symbol] = False

        return result
