"""
Investing.com Data Collector
Raccoglie dati da Investing.com usando web scraping
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import List, Dict, Optional
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InvestingComCollector:
    """Collector per dati da Investing.com"""

    BASE_URL = "https://it.investing.com"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def search_instrument(self, query: str) -> List[Dict]:
        """
        Cerca uno strumento su Investing.com

        Args:
            query: Nome o simbolo da cercare

        Returns:
            Lista di risultati
        """
        try:
            # Investing.com ha un'API di ricerca
            search_url = f"{self.BASE_URL}/search/?q={query}"

            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            results = []

            # Parsing della pagina di risultati
            # Nota: La struttura HTML potrebbe cambiare, questo è un esempio
            search_results = soup.find_all('div', class_='js-inner-all-results-quotes-wrapper')

            for result in search_results[:10]:  # Limita a 10 risultati
                try:
                    name = result.find('span', class_='second').text.strip() if result.find('span', class_='second') else ''
                    symbol = result.find('span', class_='third').text.strip() if result.find('span', class_='third') else ''

                    results.append({
                        'name': name,
                        'symbol': symbol,
                        'source': 'investing.com'
                    })
                except Exception as e:
                    logger.debug(f"Errore nel parsing risultato: {e}")
                    continue

            return results

        except Exception as e:
            logger.error(f"Errore nella ricerca su Investing.com: {e}")
            return []

    def get_bonds_list(self, country: str = "italy") -> List[Dict]:
        """
        Ottiene una lista di obbligazioni

        Args:
            country: Paese (italy, usa, germany, etc.)

        Returns:
            Lista di obbligazioni
        """
        try:
            # URL per obbligazioni italiane
            if country.lower() == "italy":
                url = f"{self.BASE_URL}/rates-bonds/italy-government-bonds"
            else:
                url = f"{self.BASE_URL}/rates-bonds/{country}-government-bonds"

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            bonds = []

            # Parse della tabella delle obbligazioni
            table = soup.find('table', {'id': 'cr1'})
            if table:
                rows = table.find_all('tr')[1:]  # Salta l'header

                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 4:
                        bonds.append({
                            'name': cols[0].text.strip(),
                            'yield': cols[1].text.strip(),
                            'previous': cols[2].text.strip(),
                            'high': cols[3].text.strip() if len(cols) > 3 else '',
                            'low': cols[4].text.strip() if len(cols) > 4 else '',
                        })

            return bonds

        except Exception as e:
            logger.error(f"Errore nel recupero obbligazioni: {e}")
            return []

    def get_commodities_list(self) -> List[Dict]:
        """
        Ottiene una lista di commodities

        Returns:
            Lista di commodities
        """
        try:
            url = f"{self.BASE_URL}/commodities"

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            commodities = []

            # Parse della tabella delle commodities
            table = soup.find('table', {'id': 'cross_rate_1'})
            if table:
                rows = table.find_all('tr')[1:]

                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        commodities.append({
                            'name': cols[0].text.strip(),
                            'last': cols[1].text.strip(),
                            'change': cols[2].text.strip(),
                            'change_percent': cols[3].text.strip() if len(cols) > 3 else '',
                        })

            return commodities

        except Exception as e:
            logger.error(f"Errore nel recupero commodities: {e}")
            return []

    def get_etf_list(self, country: str = "italy") -> List[Dict]:
        """
        Ottiene lista di ETF

        Args:
            country: Paese di riferimento

        Returns:
            Lista di ETF
        """
        try:
            url = f"{self.BASE_URL}/etfs/italy-etfs"

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            etfs = []

            # Parse della tabella degli ETF
            table = soup.find('table', {'id': 'etfs'})
            if table:
                rows = table.find_all('tr')[1:]

                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        etfs.append({
                            'name': cols[0].text.strip(),
                            'symbol': cols[1].text.strip() if len(cols) > 1 else '',
                            'last': cols[2].text.strip() if len(cols) > 2 else '',
                            'change_percent': cols[3].text.strip() if len(cols) > 3 else '',
                        })

            return etfs

        except Exception as e:
            logger.error(f"Errore nel recupero ETF: {e}")
            return []


# Note: Investing.com potrebbe richiedere misure anti-scraping più sofisticate
# In un'applicazione di produzione, considera l'uso di:
# - Selenium per JavaScript rendering
# - Proxy rotation
# - Rate limiting appropriato
# - Caching dei risultati
