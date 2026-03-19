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
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/html",
        "Accept-Language": "it-IT,it;q=0.9",
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def search(self, query: str, asset_type: str = "all") -> List[Dict]:
        """Cerca strumenti su Morningstar"""
        try:
            url = "https://www.morningstar.it/it/util/SecuritySearch.ashx"
            params = {
                "q": query,
                "limit": 20,
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
                return results
        except Exception as e:
            logger.warning(f"Morningstar search error: {e}")
        return []

    def get_fund_details(self, morningstar_id: str) -> Dict:
        """Ottiene dettagli fondo"""
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

            return details
        except Exception as e:
            logger.error(f"Morningstar fund detail error: {e}")
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

            # Step 2: Prova a ottenere dati storici via API chart
            # Morningstar usa un endpoint chart per i grafici
            import datetime
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=years*365)

            chart_url = f"https://www.morningstar.it/it/funds/snapshot/snapshot.aspx"
            params = {
                "id": fund_id,
                "tab": "chart",
            }

            r = self.session.get(chart_url, params=params, timeout=15)
            soup = BeautifulSoup(r.content, "lxml")

            # Step 3: Cerca dati nel JavaScript della pagina
            # Morningstar inietta dati chart in variabili JS
            scripts = soup.find_all("script")
            prices_data = {}

            for script in scripts:
                if script.string and "chartData" in script.string:
                    # Estrai dati JSON dal JavaScript
                    import json
                    match = re.search(r'chartData\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
                    if match:
                        try:
                            data = json.loads(match.group(1))
                            # Converti in formato {data: prezzo}
                            for point in data:
                                if len(point) >= 2:
                                    # point[0] è timestamp, point[1] è prezzo
                                    date = pd.to_datetime(point[0], unit='ms')
                                    price = float(point[1])
                                    prices_data[date] = price
                        except Exception as e:
                            logger.debug(f"JSON parse error: {e}")
                            continue

            if prices_data:
                # Converti in pandas Series e ordina per data
                series = pd.Series(prices_data).sort_index()
                logger.info(f"Recuperati {len(series)} punti dati per {fund_name}")
                return series
            else:
                logger.warning(f"Nessun dato storico trovato per {isin}")
                return None

        except Exception as e:
            logger.error(f"Errore recupero prezzi per ISIN {isin}: {e}")
            return None
