"""
Investing.com Data Collector - ENHANCED VERSION
Raccoglie dati da investing.com per azioni, fondi, commodities, indici, crypto
Con rate limiting intelligente per evitare blocchi
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import Optional, Dict
import logging
import re
import time

logger = logging.getLogger(__name__)


class InvestingCollector:
    BASE_URL = "https://it.investing.com"
    SEARCH_URL = "https://it.investing.com/search/service/search"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://it.investing.com/",
        "DNT": "1",
        "Connection": "keep-alive",
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self._last_request_time = 0
        self._min_delay = 1.5  # 1.5 secondi minimo tra richieste

    def _rate_limit(self):
        """Rate limiting per evitare ban"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_delay:
            wait_time = self._min_delay - elapsed
            logger.debug(f"[Investing] Rate limiting: waiting {wait_time:.2f}s")
            time.sleep(wait_time)
        self._last_request_time = time.time()

    @staticmethod
    def is_investing_url(text: str) -> bool:
        """Verifica se il testo è un URL Investing.com"""
        return "investing.com" in text.lower() and ("http://" in text or "https://" in text)

    @staticmethod
    def extract_instrument_from_url(url: str) -> Optional[str]:
        """
        Estrae l'identificatore dello strumento da URL Investing.com

        Esempi:
            https://it.investing.com/equities/apple-computer-inc → equities/apple-computer-inc
            https://it.investing.com/funds/azimut-az-bond-patriot-a-eur → funds/azimut-az-bond-patriot-a-eur
            https://it.investing.com/commodities/gold → commodities/gold
            https://it.investing.com/crypto/bitcoin → crypto/bitcoin
        """
        # Pattern: /tipo/nome-strumento
        match = re.search(
            r'investing\.com/(equities|commodities|crypto|indices|currencies|etfs|funds)/([^?/]+)',
            url,
            re.IGNORECASE
        )
        if match:
            instrument_type = match.group(1)
            instrument_name = match.group(2)
            logger.info(f"[Investing] Extracted: {instrument_type}/{instrument_name}")
            return f"{instrument_type}/{instrument_name}"
        return None

    def search(self, query: str, max_results: int = 10) -> list:
        """
        Cerca strumento su Investing.com

        Args:
            query: Testo ricerca (nome, ticker, ISIN)
            max_results: Numero massimo risultati

        Returns:
            Lista di dict con {name, url, type, exchange}
        """
        self._rate_limit()

        try:
            params = {
                "search_text": query,
                "term": query,
                "country_id": 0,
                "tab_id": "All",
            }

            r = self.session.get(self.SEARCH_URL, params=params, timeout=10)

            if r.status_code != 200:
                logger.warning(f"[Investing] Search failed: HTTP {r.status_code}")
                return []

            # Parse HTML risposta
            soup = BeautifulSoup(r.content, "lxml")
            results = []

            # Cerca tutti i risultati
            for item in soup.select(".js-search-result-item, .searchResults li"):
                name_elem = item.select_one(".second a, a.title")
                if name_elem:
                    results.append({
                        "name": name_elem.get_text(strip=True),
                        "url": self.BASE_URL + name_elem.get("href", ""),
                        "type": (item.select_one(".third, .type") and
                                item.select_one(".third, .type").get_text(strip=True)) or "",
                        "exchange": (item.select_one(".fourth, .exchange") and
                                    item.select_one(".fourth, .exchange").get_text(strip=True)) or "",
                        "source": "Investing.com"
                    })

            logger.info(f"[Investing] Search '{query}': {len(results)} results")
            return results[:max_results]

        except Exception as e:
            logger.error(f"[Investing] Search error: {e}")
            return []

    def get_historical_prices(self, instrument_path: str, years: int = 3) -> Optional[pd.Series]:
        """
        Ottiene prezzi storici da Investing.com

        Args:
            instrument_path: Path strumento (es: "equities/apple-computer-inc" o "funds/azimut-az-bond")
            years: Anni di storico

        Returns:
            pandas Series con prezzi o None

        Note:
            Investing.com usa JavaScript per caricare i grafici.
            Questo metodo cerca di estrarre dati dalla tabella HTML storica.
        """
        self._rate_limit()

        try:
            # URL dati storici
            url = f"{self.BASE_URL}/{instrument_path}-historical-data"

            logger.info(f"[Investing] Fetching historical data from {url}")

            r = self.session.get(url, timeout=15)
            r.raise_for_status()

            soup = BeautifulSoup(r.content, "lxml")

            prices_data = {}

            # Cerca tabella dati storici (pattern comuni)
            table = soup.select_one(
                "#curr_table, .historicalTbl, table.genTbl, table.common-table, table[data-test='historical-data-table']"
            )

            if table:
                rows = table.select("tbody tr, tr")
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) >= 2:
                        try:
                            # Col 0: Data, Col 1: Prezzo chiusura (o NAV per fondi)
                            date_str = cols[0].get_text(strip=True)
                            price_str = cols[1].get_text(strip=True).replace(",", ".").replace(" ", "")

                            # Prova diversi formati data
                            date = None
                            for fmt in ["%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d", "%d.%m.%Y"]:
                                try:
                                    date = pd.to_datetime(date_str, format=fmt)
                                    break
                                except:
                                    continue

                            if date is None:
                                date = pd.to_datetime(date_str, errors="coerce")

                            price = float(price_str)

                            if pd.notna(date):
                                prices_data[date] = price
                        except Exception:
                            continue

            if prices_data:
                series = pd.Series(prices_data).sort_index()
                logger.info(f"[Investing] ✅ {len(series)} historical points")
                return series
            else:
                logger.warning(f"[Investing] No historical data for {instrument_path}")
                return None

        except Exception as e:
            logger.error(f"[Investing] Error fetching prices: {e}")
            return None


# Istanza globale
investing_collector = InvestingCollector()
