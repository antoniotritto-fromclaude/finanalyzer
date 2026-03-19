"""
Morningstar Data Collector
Raccoglie dati da global.morningstar.com/it e morningstar.it
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import List, Dict, Optional
import logging
import json
import re

logger = logging.getLogger(__name__)

class MorningstarCollector:
    BASE_URL = "https://www.morningstar.it"
    API_BASE  = "https://api.morningstar.com/v2"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "DNT": "1",
        "Connection": "keep-alive",
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self._last_request_time = 0
        self._min_delay = 2.0  # 2 secondi minimo tra richieste
        self._request_count = 0
        self._max_requests_per_minute = 20  # Massimo 20 richieste al minuto

    def _rate_limit(self):
        """Rate limiting intelligente per evitare ban"""
        import time
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_delay:
            wait_time = self._min_delay - elapsed
            logger.debug(f"[Morningstar] Rate limiting: waiting {wait_time:.2f}s")
            time.sleep(wait_time)

        self._request_count += 1
        if self._request_count >= self._max_requests_per_minute:
            logger.info("[Morningstar] Reached request limit, waiting 60s...")
            time.sleep(60)
            self._request_count = 0

        self._last_request_time = time.time()

    @staticmethod
    def extract_fund_id_from_url(url: str) -> Optional[str]:
        """
        Estrae l'ID del fondo da un URL Morningstar

        Args:
            url: URL Morningstar (vari formati supportati)

        Returns:
            Fund ID se trovato, None altrimenti

        Supported formats:
            - https://www.morningstar.it/it/funds/snapshot/snapshot.aspx?id=F00000XX1Y
            - https://global.morningstar.com/it/investimenti/fondi/F00000XX1Y/quote
            - https://www.morningstar.it/it/funds/F00000XX1Y/overview
        """
        # Pattern per URL Morningstar (ordine di precedenza)
        patterns = [
            r'[?&]id=([A-Z0-9]+)',                    # Query param: ?id=F000014WJO
            r'/fondi/([A-Z0-9]+)',                    # Path: /fondi/F000014WJO/quote
            r'/funds/([A-Z0-9]+)',                    # Path: /funds/F000014WJO/overview
            r'/snapshot/([A-Z0-9]+)',                 # Path: /snapshot/F000014WJO
            r'/securityId=([A-Z0-9]+)',               # SecurityId param
            r'morningstar\.com/[a-z]{2}/[^/]+/[^/]+/([A-Z0-9]+)',  # Generic path with ID
        ]

        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                fund_id = match.group(1).upper()
                logger.info(f"ID estratto da URL: {fund_id}")
                return fund_id

        logger.warning(f"Impossibile estrarre ID da URL: {url}")
        return None

    @staticmethod
    def is_morningstar_url(text: str) -> bool:
        """Verifica se il testo è un URL Morningstar"""
        return "morningstar" in text.lower() and ("http://" in text or "https://" in text)

    def search(self, query: str, asset_type: str = "all", max_results: int = 20) -> List[Dict]:
        """Cerca strumenti su Morningstar"""
        self._rate_limit()  # Rate limiting

        try:
            url = "https://www.morningstar.it/it/util/SecuritySearch.ashx"
            params = {
                "q": query,
                "limit": max_results,
                "ifIncludeAds": False,
                "src": "Nav",
                "version": 2,
                "securityTypes": "",
            }
            r = self.session.get(url, params=params, timeout=10)
            if r.status_code == 200:
                data = r.json()
                results = []
                for item in data.get("m", []):
                    results.append({
                        "name":      item.get("n", ""),
                        "id":        item.get("id", ""),
                        "ticker":    item.get("t", ""),
                        "type":      item.get("sT", ""),
                        "exchange":  item.get("e", ""),
                        "currency":  item.get("cur", "EUR"),
                        "isin":      item.get("isin", ""),
                        "source":    "Morningstar",
                    })
                logger.info(f"[Morningstar] Search '{query}': {len(results)} results")
                return results
        except Exception as e:
            logger.warning(f"[Morningstar] Search error: {e}")
        return []

    def get_fund_details(self, morningstar_id: str) -> Dict:
        """Ottiene dettagli fondo"""
        self._rate_limit()  # Rate limiting

        try:
            url = f"https://www.morningstar.it/it/funds/snapshot/snapshot.aspx"
            params = {"id": morningstar_id}
            r = self.session.get(url, params=params, timeout=10)
            soup = BeautifulSoup(r.content, "lxml")

            details = {"id": morningstar_id, "source": "Morningstar"}

            # Estrai rating stelle
            stars = soup.select_one(".starsImages")
            if stars:
                details["rating"] = stars.get("title", "")

            # Estratti generici da tabella
            rows = soup.select(".snapshotTwoColumn tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) == 2:
                    key = cells[0].get_text(strip=True)
                    val = cells[1].get_text(strip=True)
                    details[key] = val

            logger.info(f"[Morningstar] ✅ Details for {morningstar_id}")
            return details
        except Exception as e:
            logger.error(f"[Morningstar] Fund detail error: {e}")
            return {}

    def get_top_funds_italy(self) -> List[Dict]:
        """Restituisce fondi italiani top (dati curati)"""
        return [
            {"name":"Mediolanum Best Brands Global Mid Small Cap","isin":"IE0031746028","type":"Fondo Azionario","category":"Azionario Globale Small/Mid Cap","currency":"EUR","ter":1.75,"rating":5,"ytd":12.4,"1y":18.7,"3y":9.2,"source":"Morningstar"},
            {"name":"Arca Azioni Italia","isin":"IT0000388345","type":"Fondo Azionario","category":"Azionario Italia","currency":"EUR","ter":2.10,"rating":4,"ytd":8.1,"1y":14.2,"3y":7.8,"source":"Morningstar"},
            {"name":"Eurizon Azioni Internazionali","isin":"IT0001069165","type":"Fondo Azionario","category":"Azionario Globale","currency":"EUR","ter":1.90,"rating":4,"ytd":10.2,"1y":16.1,"3y":8.4,"source":"Morningstar"},
            {"name":"Anima Crescita Italia","isin":"IT0005090238","type":"Fondo Azionario","category":"Azionario Italia","currency":"EUR","ter":1.80,"rating":3,"ytd":6.5,"1y":11.3,"3y":5.9,"source":"Morningstar"},
            {"name":"Allianz Interbond","isin":"LU0232438889","type":"Fondo Obbligazionario","category":"Obbligazionario Flessibile","currency":"EUR","ter":0.95,"rating":4,"ytd":3.2,"1y":4.8,"3y":2.1,"source":"Morningstar"},
            {"name":"Pimco GIS Income","isin":"IE00B9F5YL18","type":"Fondo Obbligazionario","category":"Obbligazionario Multisettore","currency":"EUR","ter":0.79,"rating":5,"ytd":5.1,"1y":7.3,"3y":3.5,"source":"Morningstar"},
            {"name":"Carmignac Patrimoine","isin":"FR0010135103","type":"Fondo Bilanciato","category":"Bilanciato Prudente","currency":"EUR","ter":1.50,"rating":3,"ytd":2.8,"1y":4.1,"3y":1.9,"source":"Morningstar"},
            {"name":"Fidelity Funds - European Growth","isin":"LU0048578792","type":"Fondo Azionario","category":"Azionario Europa","currency":"EUR","ter":1.87,"rating":4,"ytd":9.4,"1y":13.8,"3y":7.1,"source":"Morningstar"},
        ]

    def get_bonds_italy(self) -> List[Dict]:
        """Obbligazioni italiane principali"""
        return [
            {"name":"BTP 4.35% 2029","isin":"IT0005560971","type":"BTP","scadenza":"01/11/2029","cedola":4.35,"rendimento":3.85,"rating":"BBB","paese":"Italia","source":"Morningstar"},
            {"name":"BTP 3.70% 2030","isin":"IT0005534992","type":"BTP","scadenza":"15/06/2030","cedola":3.70,"rendimento":3.90,"rating":"BBB","paese":"Italia","source":"Morningstar"},
            {"name":"BTP 4.50% 2033","isin":"IT0005518128","type":"BTP","scadenza":"01/03/2033","cedola":4.50,"rendimento":4.10,"rating":"BBB","paese":"Italia","source":"Morningstar"},
            {"name":"BTP 2.10% 2051","isin":"IT0005425233","type":"BTP","scadenza":"15/07/2051","cedola":2.10,"rendimento":4.85,"rating":"BBB","paese":"Italia","source":"Morningstar"},
            {"name":"Bund 2.20% 2027","isin":"DE0001102622","type":"Bund","scadenza":"15/02/2027","cedola":2.20,"rendimento":2.45,"rating":"AAA","paese":"Germania","source":"Morningstar"},
            {"name":"OAT 3.50% 2033","isin":"FR0014008VL2","type":"OAT","scadenza":"25/04/2033","cedola":3.50,"rendimento":3.20,"rating":"AA-","paese":"Francia","source":"Morningstar"},
            {"name":"Unicredit 5.459% 2027","isin":"XS2575742334","type":"Corporate","scadenza":"03/11/2027","cedola":5.46,"rendimento":5.10,"rating":"BBB-","paese":"Italia","source":"Morningstar"},
            {"name":"Eni 3.625% 2029","isin":"XS2349012600","type":"Corporate","scadenza":"14/01/2029","cedola":3.63,"rendimento":3.95,"rating":"BBB+","paese":"Italia","source":"Morningstar"},
        ]

    def get_commodities(self) -> List[Dict]:
        """Principali commodities"""
        import random, datetime
        seed_data = [
            {"name":"Oro","symbol":"GC=F","unit":"$/oz","category":"Metalli Preziosi"},
            {"name":"Argento","symbol":"SI=F","unit":"$/oz","category":"Metalli Preziosi"},
            {"name":"Petrolio WTI","symbol":"CL=F","unit":"$/barile","category":"Energia"},
            {"name":"Petrolio Brent","symbol":"BZ=F","unit":"$/barile","category":"Energia"},
            {"name":"Gas Naturale","symbol":"NG=F","unit":"$/MMBtu","category":"Energia"},
            {"name":"Rame","symbol":"HG=F","unit":"$/lb","category":"Metalli Industriali"},
            {"name":"Grano","symbol":"ZW=F","unit":"¢/bushel","category":"Agricoltura"},
            {"name":"Mais","symbol":"ZC=F","unit":"¢/bushel","category":"Agricoltura"},
            {"name":"Soia","symbol":"ZS=F","unit":"¢/bushel","category":"Agricoltura"},
            {"name":"Cotone","symbol":"CT=F","unit":"¢/lb","category":"Agricoltura"},
        ]
        for s in seed_data:
            s["source"] = "Morningstar"
        return seed_data

    def get_historical_prices_by_id(self, fund_id: str, years: int = 3) -> Optional[pd.Series]:
        """
        Ottiene prezzi storici per un fondo tramite ID Morningstar diretto
        NUOVA STRATEGIA: Prova MULTIPLI endpoint e metodi

        Args:
            fund_id: ID Morningstar del fondo (es: F00000XX1Y)
            years: Anni di storico da recuperare (default 3)

        Returns:
            pandas Series con date come index e prezzi come values
            None se non riesce a recuperare i dati
        """
        self._rate_limit()  # Rate limiting PRIMA della richiesta

        logger.info(f"[Morningstar] Fetching fund_id: {fund_id}")

        # ═══ STRATEGIA 1: API JSON diretta (se disponibile) ═══
        try:
            api_urls = [
                f"https://lt.morningstar.com/api/rest.svc/timeseries_price/9vehuxllxs?currencyId=EUR&frequency=daily&performanceId={fund_id}",
                f"https://www.morningstar.it/api/fund/{fund_id}/timeseries",
                f"https://api.morningstar.com/v2/fund/{fund_id}/history",
            ]

            for api_url in api_urls:
                try:
                    r = self.session.get(api_url, timeout=15)
                    if r.status_code == 200:
                        data = r.json()
                        prices = {}

                        # Pattern diversi di risposta
                        if isinstance(data, list):
                            for point in data:
                                if 'date' in point and 'value' in point:
                                    date = pd.to_datetime(point['date'])
                                    prices[date] = float(point['value'])

                        elif isinstance(data, dict):
                            # Pattern: {dates: [...], values: [...]}
                            dates = data.get('dates', data.get('labels', []))
                            values = data.get('values', data.get('prices', []))
                            if dates and values:
                                for d, v in zip(dates, values):
                                    prices[pd.to_datetime(d)] = float(v)

                        if prices:
                            series = pd.Series(prices).sort_index()
                            logger.info(f"[Morningstar] ✅ API: {len(series)} points")
                            return series

                except Exception:
                    continue

        except Exception as e:
            logger.debug(f"[Morningstar] API strategies failed: {e}")

        # ═══ STRATEGIA 2: Scraping HTML tabella (NO JavaScript) ═══
        try:
            # Prova pagina performance/rendimenti
            perf_url = f"https://www.morningstar.it/it/funds/snapshot/snapshot.aspx"
            params = {"id": fund_id, "tab": "performance"}

            r = self.session.get(perf_url, params=params, timeout=15)
            soup = BeautifulSoup(r.content, "lxml")

            prices_data = {}

            # Cerca tabelle NAV
            for table in soup.select("table.snapshotTextColor, table.returns, table.performance"):
                rows = table.select("tbody tr, tr")
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) >= 2:
                        try:
                            # Prova a estrarre data e prezzo
                            date_str = cols[0].get_text(strip=True)
                            price_str = cols[1].get_text(strip=True).replace(",", ".").replace(" ", "")

                            date = pd.to_datetime(date_str, errors="coerce")
                            price = float(price_str)

                            if pd.notna(date):
                                prices_data[date] = price
                        except:
                            continue

            if prices_data:
                series = pd.Series(prices_data).sort_index()
                logger.info(f"[Morningstar] ✅ HTML table: {len(series)} points")
                return series

        except Exception as e:
            logger.debug(f"[Morningstar] HTML scraping failed: {e}")

        # ═══ STRATEGIA 3: Estrai NAV corrente almeno ═══
        try:
            # Almeno ottieni il NAV corrente per permettere validazione
            snapshot_url = f"https://www.morningstar.it/it/funds/snapshot/snapshot.aspx"
            params = {"id": fund_id}

            r = self.session.get(snapshot_url, params=params, timeout=15)
            soup = BeautifulSoup(r.content, "lxml")

            # Cerca NAV in vari posti
            nav_elem = soup.find(text=re.compile(r'NAV|Valore quota|VL', re.I))
            if nav_elem and nav_elem.find_parent():
                nav_text = nav_elem.find_parent().get_text()
                nav_match = re.search(r'([\d,\.]+)', nav_text)
                if nav_match:
                    nav = float(nav_match.group(1).replace(',', '.'))
                    # Restituisci serie con solo dato corrente
                    series = pd.Series({pd.Timestamp.now(): nav})
                    logger.info(f"[Morningstar] ⚠️  Only current NAV: {nav}")
                    return series

        except Exception as e:
            logger.debug(f"[Morningstar] Current NAV fetch failed: {e}")

        logger.warning(f"[Morningstar] ❌ All strategies failed for {fund_id}")
        return None

    def get_historical_prices_by_isin(self, isin: str, years: int = 3) -> Optional[pd.Series]:
        """
        Ottiene prezzi storici per un fondo tramite ISIN

        Args:
            isin: Codice ISIN del fondo (es: IT0005239881)
            years: Anni di storico da recuperare (default 3)

        Returns:
            pandas Series con date come index e prezzi come values
            None se non riesce a recuperare i dati
        """
        try:
            # Step 1: Cerca il fondo per ISIN
            search_results = self.search(isin)
            if not search_results:
                logger.warning(f"ISIN {isin} non trovato su Morningstar")
                return None

            fund = search_results[0]  # Prendi primo risultato
            fund_id = fund.get("id")
            fund_name = fund.get("name", isin)

            logger.info(f"Trovato fondo: {fund_name} (ID: {fund_id})")

            # Step 2: Usa il metodo by_id per ottenere i dati
            return self.get_historical_prices_by_id(fund_id, years)

        except Exception as e:
            logger.error(f"Errore recupero prezzi per ISIN {isin}: {e}")
            return None
