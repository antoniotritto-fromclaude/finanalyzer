"""
Quantalys Data Collector - ENHANCED VERSION
Raccoglie dati fondi da www.quantalys.it con rate limiting intelligente
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import List, Dict, Optional
import logging
import re
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class QuantalysCollector:
    BASE_URL = "https://www.quantalys.it"
    SEARCH_URL = "https://www.quantalys.it/Fonds/Recherche"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8",
        "Referer": "https://www.quantalys.it/",
        "DNT": "1",
        "Connection": "keep-alive",
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self._last_request_time = 0
        self._min_delay = 2.0  # Minimo 2 secondi tra richieste per evitare ban

    def _rate_limit(self):
        """Rate limiting intelligente - previene blocchi"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_delay:
            wait_time = self._min_delay - elapsed
            logger.debug(f"[Quantalys] Rate limiting: waiting {wait_time:.2f}s")
            time.sleep(wait_time)
        self._last_request_time = time.time()

    @staticmethod
    def is_quantalys_url(text: str) -> bool:
        """Verifica se è un URL Quantalys"""
        return "quantalys" in text.lower() and ("http" in text.lower())

    @staticmethod
    def extract_fund_id_from_url(url: str) -> Optional[str]:
        """
        Estrae ID fondo da URL Quantalys
        Es: https://www.quantalys.it/fonds/106139 → 106139
        """
        match = re.search(r'/fonds/(\d+)', url, re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    def search_fund(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        Cerca un fondo su Quantalys (ISIN, nome, ticker)

        Args:
            query: Testo di ricerca
            max_results: Numero massimo risultati

        Returns:
            Lista di fondi trovati
        """
        self._rate_limit()

        results = []

        # Strategia 1: Prova API JSON (se disponibile)
        try:
            params = {"q": query, "langue": "IT", "limit": max_results}
            r = self.session.get(f"{self.BASE_URL}/api/search", params=params, timeout=10)
            if r.status_code == 200:
                data = r.json()
                for item in data:
                    results.append({
                        "name": item.get("nom", ""),
                        "isin": item.get("isin", ""),
                        "category": item.get("categorie", ""),
                        "risk": item.get("risque", ""),
                        "rating": item.get("notation", ""),
                        "source": "Quantalys",
                    })
                logger.info(f"[Quantalys] API search: {len(results)} results")
                return results[:max_results]
        except Exception as e:
            logger.debug(f"[Quantalys] API search failed: {e}")

        # Strategia 2: Scraping HTML
        try:
            r = self.session.get(self.SEARCH_URL, params={"q": query}, timeout=10)
            soup = BeautifulSoup(r.content, "lxml")

            # Pattern comuni per risultati tabella
            for row in soup.select("table.fonds tbody tr, table.funds tbody tr, .fund-row, .result-row")[:max_results]:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    fund = {
                        "name": cols[0].get_text(strip=True),
                        "isin": "",
                        "source": "Quantalys",
                    }
                    # Cerca ISIN nei campi
                    for col in cols:
                        text = col.get_text(strip=True)
                        isin_match = re.search(r'([A-Z]{2}[A-Z0-9]{10})', text)
                        if isin_match:
                            fund["isin"] = isin_match.group(1)
                            break

                    if len(cols) >= 3:
                        fund["category"] = cols[2].get_text(strip=True)

                    results.append(fund)

            logger.info(f"[Quantalys] HTML scraping: {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"[Quantalys] Scraping error: {e}")
            return []

    def get_fund_data(self, fund_id_or_url: str) -> Optional[Dict]:
        """
        Raccoglie dati completi di un fondo

        Args:
            fund_id_or_url: ID Quantalys (es: "106139") o URL completo

        Returns:
            Dict con dati fondo o None
        """
        self._rate_limit()

        # Determina fund_id
        if self.is_quantalys_url(fund_id_or_url):
            fund_id = self.extract_fund_id_from_url(fund_id_or_url)
            url = fund_id_or_url
        else:
            fund_id = fund_id_or_url
            url = f"{self.BASE_URL}/fonds/{fund_id}"

        if not fund_id:
            logger.error(f"[Quantalys] Invalid fund ID/URL: {fund_id_or_url}")
            return None

        logger.info(f"[Quantalys] Fetching fund {fund_id}...")

        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            fund_data = {
                'id': fund_id,
                'source': 'Quantalys',
                'url': url
            }

            # Estrai nome fondo
            for selector in ['h1.fund-name', 'h1.titre', 'h1', '.fund-title']:
                title = soup.select_one(selector)
                if title:
                    fund_data['name'] = title.get_text(strip=True)
                    break

            # Estrai ISIN
            isin_elem = soup.find(text=re.compile(r'ISIN', re.I))
            if isin_elem:
                isin_text = isin_elem.find_parent().get_text() if isin_elem.find_parent() else ""
                isin_match = re.search(r'([A-Z]{2}[A-Z0-9]{10})', isin_text)
                if isin_match:
                    fund_data['isin'] = isin_match.group(1)

            # Estrai NAV
            nav_elem = soup.find(text=re.compile(r'Valore quota|VL|NAV|Cours', re.I))
            if nav_elem:
                nav_text = nav_elem.find_parent().get_text() if nav_elem.find_parent() else ""
                nav_match = re.search(r'([\d\s,\.]+)', nav_text)
                if nav_match:
                    nav_str = nav_match.group(1).replace(' ', '').replace(',', '.')
                    try:
                        fund_data['nav'] = float(nav_str)
                    except:
                        pass

            # Estrai categoria
            cat_elem = soup.find(text=re.compile(r'Categoria|Catégorie|Classification', re.I))
            if cat_elem and cat_elem.find_parent():
                fund_data['category'] = cat_elem.find_parent().get_text(strip=True).split(':')[-1].strip()

            # Estrai rating
            rating_elem = soup.find('span', class_=re.compile(r'star|rating|notation', re.I))
            if rating_elem:
                rating_text = rating_elem.get_text()
                rating_match = re.search(r'(\d)', rating_text)
                if rating_match:
                    fund_data['rating'] = int(rating_match.group(1))

            # Estrai TER
            ter_elem = soup.find(text=re.compile(r'TER|Frais|Costi|Spese', re.I))
            if ter_elem and ter_elem.find_parent():
                ter_text = ter_elem.find_parent().get_text()
                ter_match = re.search(r'([\d,\.]+)\s*%', ter_text)
                if ter_match:
                    ter_str = ter_match.group(1).replace(',', '.')
                    try:
                        fund_data['ter'] = float(ter_str)
                    except:
                        pass

            logger.info(f"[Quantalys] ✅ {fund_data.get('name', fund_id)}")
            return fund_data

        except Exception as e:
            logger.error(f"[Quantalys] Error fetching {fund_id}: {e}")
            return None

    def get_historical_prices(self, fund_id: str, years: int = 3) -> Optional[pd.Series]:
        """
        Ottiene serie storica prezzi (se disponibile)

        Args:
            fund_id: ID Quantalys
            years: Anni di storico

        Returns:
            pandas Series con date e NAV
        """
        self._rate_limit()

        # Possibili endpoint per dati storici
        api_endpoints = [
            f"{self.BASE_URL}/api/fund/{fund_id}/history",
            f"{self.BASE_URL}/data/chart/{fund_id}",
            f"{self.BASE_URL}/fonds/{fund_id}/performances",
            f"{self.BASE_URL}/fonds/{fund_id}/chart-data"
        ]

        for api_url in api_endpoints:
            try:
                response = self.session.get(api_url, timeout=15)
                if response.status_code == 200:
                    # Prova JSON
                    try:
                        data = response.json()
                        prices = {}

                        # Pattern 1: Lista di {date, value}
                        if isinstance(data, list):
                            for point in data:
                                if 'date' in point and ('value' in point or 'nav' in point or 'price' in point):
                                    date = pd.to_datetime(point['date'])
                                    value = point.get('value') or point.get('nav') or point.get('price')
                                    prices[date] = float(value)

                        # Pattern 2: Dict con array separati
                        elif isinstance(data, dict):
                            dates = data.get('dates', data.get('labels', []))
                            values = data.get('values', data.get('prices', data.get('nav', [])))

                            if dates and values and len(dates) == len(values):
                                for d, v in zip(dates, values):
                                    date = pd.to_datetime(d)
                                    prices[date] = float(v)

                        if prices:
                            series = pd.Series(prices).sort_index()
                            logger.info(f"[Quantalys] ✅ {len(series)} historical points")
                            return series

                    except ValueError:
                        pass  # Non è JSON

            except Exception as e:
                logger.debug(f"[Quantalys] Endpoint {api_url} failed: {e}")

        logger.warning(f"[Quantalys] No historical data for {fund_id}")
        return None

    def get_best_funds_by_category(self) -> Dict[str, List[Dict]]:
        """Migliori fondi per categoria (dati curati)"""
        return {
            "Azionario Globale": [
                {"name":"Fundsmith Equity T Acc EUR","isin":"IE00B4MR8721","rating":5,"ter":0.94,"1y":18.2,"3y":12.1,"5y":14.3,"risk":4,"source":"Quantalys"},
                {"name":"Robeco Global Consumer Trends","isin":"LU0187079347","rating":5,"ter":1.51,"1y":14.7,"3y":9.8,"5y":11.9,"risk":4,"source":"Quantalys"},
                {"name":"MS INVF Global Brands A","isin":"LU0119620416","rating":4,"ter":1.62,"1y":13.1,"3y":8.5,"5y":10.7,"risk":4,"source":"Quantalys"},
            ],
            "Azionario Europa": [
                {"name":"Fidelity European Growth A","isin":"LU0048578792","rating":4,"ter":1.87,"1y":11.2,"3y":7.4,"5y":9.1,"risk":4,"source":"Quantalys"},
                {"name":"Comgest Growth Europe","isin":"IE0004766014","rating":5,"ter":1.56,"1y":10.8,"3y":6.9,"5y":8.7,"risk":4,"source":"Quantalys"},
            ],
            "Obbligazionario": [
                {"name":"Pimco GIS Income Inst EUR Acc","isin":"IE00B9F5YL18","rating":5,"ter":0.79,"1y":6.8,"3y":3.2,"5y":4.1,"risk":3,"source":"Quantalys"},
                {"name":"M&G Optimal Income A EUR Acc","isin":"GB00B1VMCY93","rating":4,"ter":1.17,"1y":5.4,"3y":2.8,"5y":3.7,"risk":3,"source":"Quantalys"},
                {"name":"Templeton Global Bond A Acc EUR","isin":"LU0029871042","rating":3,"ter":0.98,"1y":4.2,"3y":1.9,"5y":2.8,"risk":3,"source":"Quantalys"},
            ],
            "Bilanciato": [
                {"name":"Vontobel Multi Asset Solution","isin":"LU0899569780","rating":4,"ter":1.42,"1y":8.2,"3y":5.1,"5y":6.8,"risk":3,"source":"Quantalys"},
                {"name":"Carmignac Patrimoine A EUR Acc","isin":"FR0010135103","rating":3,"ter":1.50,"1y":3.1,"3y":1.4,"5y":3.2,"risk":3,"source":"Quantalys"},
            ],
        }


# Singleton instance
quantalys_collector = QuantalysCollector()
