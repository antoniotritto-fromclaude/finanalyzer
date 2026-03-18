"""
JustETF Data Collector
Raccoglie dati ETF da www.justetf.com
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import List, Dict, Optional
import logging
import time
import re

logger = logging.getLogger(__name__)

class JustETFCollector:
    BASE_URL = "https://www.justetf.com"
    SEARCH_URL = "https://www.justetf.com/it/find-etf.html"
    API_URL   = "https://www.justetf.com/api/etfs"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8",
        "Accept": "application/json, text/html",
        "Referer": "https://www.justetf.com/it/"
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def search_etf(self, query: str) -> List[Dict]:
        """Cerca ETF per nome o ISIN"""
        try:
            params = {
                "query": query,
                "currency": "EUR",
                "domicileCountry": "",
                "distributionPolicy": "",
                "assetClass": "",
                "groupField": "index",
                "sortField": "ter",
                "sortOrder": "asc",
                "offset": 0,
                "limit": 20,
                "lang": "it",
            }
            r = self.session.get(self.API_URL, params=params, timeout=10)
            if r.status_code == 200:
                data = r.json()
                etfs = []
                for item in data.get("values", []):
                    etfs.append({
                        "isin": item.get("isin", ""),
                        "name": item.get("name", ""),
                        "ticker": item.get("ticker", ""),
                        "currency": item.get("currency", "EUR"),
                        "ter": item.get("ter", 0),
                        "size": item.get("totalExpenseRatio", 0),
                        "replication": item.get("replicationMethod", ""),
                        "distribution": item.get("distributionPolicy", ""),
                        "domicile": item.get("domicileCountry", ""),
                        "source": "JustETF",
                    })
                return etfs
        except Exception as e:
            logger.warning(f"JustETF API error: {e}")

        # Fallback: scraping HTML
        return self._scrape_etf_list(query)

    def _scrape_etf_list(self, query: str = "") -> List[Dict]:
        """Scrape lista ETF dalla pagina HTML"""
        try:
            params = {"search": query} if query else {}
            r = self.session.get(self.SEARCH_URL, params=params, timeout=10)
            soup = BeautifulSoup(r.content, "lxml")
            rows = soup.select("table.etf-list tbody tr")
            etfs = []
            for row in rows[:30]:
                cols = row.find_all("td")
                if len(cols) >= 4:
                    etfs.append({
                        "name": cols[0].get_text(strip=True),
                        "isin": cols[1].get_text(strip=True),
                        "ter": cols[2].get_text(strip=True),
                        "size": cols[3].get_text(strip=True),
                        "source": "JustETF",
                    })
            return etfs
        except Exception as e:
            logger.error(f"JustETF scraping error: {e}")
            return []

    def get_popular_etfs(self) -> List[Dict]:
        """Restituisce ETF popolari hardcoded + dati arricchiti"""
        popular = [
            {"isin":"IE00B4L5Y983","name":"iShares Core MSCI World UCITS ETF","ticker":"SWDA","ter":0.20,"category":"Azionario Globale","currency":"USD","distribution":"Accumulazione","replication":"Fisica","domicile":"IE"},
            {"isin":"IE00B3RBWM25","name":"Vanguard FTSE All-World UCITS ETF","ticker":"VWRL","ter":0.22,"category":"Azionario Globale","currency":"USD","distribution":"Distribuzione","replication":"Fisica","domicile":"IE"},
            {"isin":"IE00BK5BQT80","name":"Vanguard FTSE All-World UCITS ETF (Acc)","ticker":"VWCE","ter":0.22,"category":"Azionario Globale","currency":"EUR","distribution":"Accumulazione","replication":"Fisica","domicile":"IE"},
            {"isin":"IE00B5BMR087","name":"iShares Core S&P 500 UCITS ETF","ticker":"CSPX","ter":0.07,"category":"Azionario USA","currency":"USD","distribution":"Accumulazione","replication":"Fisica","domicile":"IE"},
            {"isin":"IE00B44Z5B48","name":"iShares Core MSCI Emerging Markets IMI","ticker":"EIMI","ter":0.18,"category":"Azionario Emergenti","currency":"USD","distribution":"Accumulazione","replication":"Fisica","domicile":"IE"},
            {"isin":"LU0274208692","name":"Xtrackers MSCI World Swap UCITS ETF","ticker":"XDWD","ter":0.19,"category":"Azionario Globale","currency":"EUR","distribution":"Accumulazione","replication":"Sintetica","domicile":"LU"},
            {"isin":"IE00B52MJY50","name":"iShares MSCI Europe UCITS ETF","ticker":"IMEU","ter":0.12,"category":"Azionario Europa","currency":"EUR","distribution":"Distribuzione","replication":"Fisica","domicile":"IE"},
            {"isin":"IE00B0M63177","name":"iShares MSCI AC Far East ex-Japan UCITS ETF","ticker":"IFFF","ter":0.74,"category":"Azionario Asia","currency":"USD","distribution":"Distribuzione","replication":"Fisica","domicile":"IE"},
            {"isin":"IE00B14X4S71","name":"iShares MSCI Japan UCITS ETF","ticker":"IJPN","ter":0.48,"category":"Azionario Giappone","currency":"USD","distribution":"Distribuzione","replication":"Fisica","domicile":"IE"},
            {"isin":"IE00B4WXJJ64","name":"iShares MSCI Italy UCITS ETF","ticker":"ITLY","ter":0.35,"category":"Azionario Italia","currency":"EUR","distribution":"Distribuzione","replication":"Fisica","domicile":"IE"},
            {"isin":"IE00B6R52036","name":"iShares Global Clean Energy UCITS ETF","ticker":"INRG","ter":0.65,"category":"Azionario Settoriale","currency":"USD","distribution":"Accumulazione","replication":"Fisica","domicile":"IE"},
            {"isin":"IE00B3F81R35","name":"iShares Core € Corp Bond UCITS ETF","ticker":"IEAC","ter":0.20,"category":"Obbligazionario Corporate EUR","currency":"EUR","distribution":"Distribuzione","replication":"Fisica","domicile":"IE"},
            {"isin":"IE00B1FZS350","name":"iShares € Govt Bond UCITS ETF","ticker":"IEGE","ter":0.20,"category":"Obbligazionario Governativo EUR","currency":"EUR","distribution":"Distribuzione","replication":"Fisica","domicile":"IE"},
            {"isin":"IE00B4WXJH41","name":"iShares Physical Gold ETC","ticker":"IGLN","ter":0.12,"category":"Commodities - Oro","currency":"USD","distribution":"Accumulazione","replication":"Fisica","domicile":"IE"},
            {"isin":"IE00B579F325","name":"iShares MSCI World Small Cap UCITS ETF","ticker":"WLDS","ter":0.35,"category":"Azionario Globale Small Cap","currency":"USD","distribution":"Accumulazione","replication":"Fisica","domicile":"IE"},
        ]
        for i, e in enumerate(popular):
            e["source"] = "JustETF"
            e["rank"] = i + 1
        return popular
