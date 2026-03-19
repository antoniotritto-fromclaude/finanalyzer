"""
Investing.com Data Collector
Raccoglie dati da investing.com per azioni, commodities, indici, crypto
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import Optional, Dict
import logging
import re

logger = logging.getLogger(__name__)


class InvestingCollector:
    BASE_URL = "https://it.investing.com"
    SEARCH_URL = "https://it.investing.com/search/service/search"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/html",
        "Accept-Language": "it-IT,it;q=0.9",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://it.investing.com/",
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    @staticmethod
    def is_investing_url(text: str) -> bool:
        """Verifica se il testo è un URL Investing.com"""
        return "investing.com" in text.lower() and ("http://" in text or "https://" in text)

    @staticmethod
    def extract_instrument_from_url(url: str) -> Optional[str]:
        """
        Estrae l'identificatore dello strumento da URL Investing.com

        Esempi:
            https://it.investing.com/equities/apple-computer-inc
            https://it.investing.com/commodities/gold
            https://it.investing.com/crypto/bitcoin
        """
        # Pattern: /tipo/nome-strumento
        match = re.search(r'investing\.com/(equities|commodities|crypto|indices|currencies|etfs)/([^?/]+)', url, re.IGNORECASE)
        if match:
            instrument_type = match.group(1)
            instrument_name = match.group(2)
            logger.info(f"Estratto da URL Investing: {instrument_type}/{instrument_name}")
            return f"{instrument_type}/{instrument_name}"
        return None

    def search(self, query: str) -> list:
        """
        Cerca strumento su Investing.com

        Returns:
            Lista di dict con {name, url, type, exchange}
        """
        try:
            params = {
                "search_text": query,
                "term": query,
                "country_id": 0,
                "tab_id": "All",
            }

            r = self.session.get(self.SEARCH_URL, params=params, timeout=10)

            if r.status_code != 200:
                logger.warning(f"Investing.com search failed: status {r.status_code}")
                return []

            # Parse HTML risposta
            soup = BeautifulSoup(r.content, "lxml")
            results = []

            # Cerca tutti i risultati
            for item in soup.select(".js-search-result-item"):
                name = item.select_one(".second a")
                if name:
                    results.append({
                        "name": name.get_text(strip=True),
                        "url": self.BASE_URL + name.get("href", ""),
                        "type": item.select_one(".third")and item.select_one(".third").get_text(strip=True) or "",
                        "exchange": item.select_one(".fourth") and item.select_one(".fourth").get_text(strip=True) or "",
                        "source": "Investing.com"
                    })

            logger.info(f"Investing.com search '{query}': {len(results)} risultati")
            return results[:10]  # Max 10 risultati

        except Exception as e:
            logger.error(f"Errore ricerca Investing.com: {e}")
            return []

    def get_historical_prices(self, instrument_path: str, years: int = 3) -> Optional[pd.Series]:
        """
        Ottiene prezzi storici da Investing.com

        Args:
            instrument_path: Path strumento (es: "equities/apple-computer-inc")
            years: Anni di storico

        Returns:
            pandas Series con prezzi o None

        Note:
            Investing.com usa JavaScript per caricare i grafici.
            Questo metodo cerca di estrarre dati dalla pagina HTML o API interna.
        """
        try:
            url = f"{self.BASE_URL}/{instrument_path}-historical-data"

            r = self.session.get(url, timeout=15)
            soup = BeautifulSoup(r.content, "lxml")

            prices_data = {}

            # Cerca tabella dati storici
            table = soup.select_one("#curr_table, .historicalTbl, table.genTbl")
            if table:
                rows = table.select("tbody tr")
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) >= 2:
                        try:
                            # Col 0: Data, Col 1: Prezzo chiusura
                            date_str = cols[0].get_text(strip=True)
                            price_str = cols[1].get_text(strip=True).replace(",", ".")

                            date = pd.to_datetime(date_str, format="%d/%m/%Y", errors="coerce")
                            price = float(price_str)

                            if pd.notna(date):
                                prices_data[date] = price
                        except Exception as e:
                            continue

            if prices_data:
                series = pd.Series(prices_data).sort_index()
                logger.info(f"Recuperati {len(series)} punti dati da Investing.com")
                return series
            else:
                logger.warning(f"Nessun dato storico trovato su Investing.com per {instrument_path}")
                return None

        except Exception as e:
            logger.error(f"Errore recupero prezzi Investing.com: {e}")
            return None


# Istanza globale
investing_collector = InvestingCollector()
