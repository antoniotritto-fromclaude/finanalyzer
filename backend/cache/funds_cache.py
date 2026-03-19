"""
Sistema di cache per dati fondi Morningstar
Evita scraping ripetuti, aggiorna 1x/giorno
"""
import json
import os
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

CACHE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(CACHE_DIR, "funds_data.json")
CACHE_TTL_HOURS = 24  # Cache valida per 24 ore


class FundsCache:
    """Gestisce cache locale per dati fondi"""

    def __init__(self):
        self.cache_file = CACHE_FILE
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        """Crea directory cache se non esiste"""
        os.makedirs(CACHE_DIR, exist_ok=True)

    def _load_cache(self) -> dict:
        """Carica cache da file JSON"""
        if not os.path.exists(self.cache_file):
            return {}
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Errore lettura cache: {e}")
            return {}

    def _save_cache(self, data: dict):
        """Salva cache su file JSON"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Errore scrittura cache: {e}")

    def get_prices(self, isin: str) -> Optional[pd.Series]:
        """
        Recupera prezzi dalla cache

        Args:
            isin: Codice ISIN del fondo

        Returns:
            pandas Series con prezzi storici se in cache e valida
            None se non in cache o scaduta
        """
        cache = self._load_cache()

        if isin not in cache:
            logger.debug(f"ISIN {isin} non in cache")
            return None

        entry = cache[isin]
        last_update = datetime.fromisoformat(entry.get("last_update", "2000-01-01"))
        now = datetime.now()

        # Verifica se cache è ancora valida (< 24h)
        if now - last_update > timedelta(hours=CACHE_TTL_HOURS):
            logger.info(f"Cache per {isin} scaduta (aggiornata {last_update})")
            return None

        # Converti dati in pandas Series
        prices_dict = entry.get("prices", {})
        if not prices_dict:
            return None

        # Converti date string → datetime
        prices = {}
        for date_str, price in prices_dict.items():
            try:
                date = pd.to_datetime(date_str)
                prices[date] = float(price)
            except:
                continue

        if prices:
            series = pd.Series(prices).sort_index()
            logger.info(f"Cache hit per {isin}: {len(series)} punti dati")
            return series

        return None

    def set_prices(self, isin: str, name: str, prices: pd.Series):
        """
        Salva prezzi nella cache

        Args:
            isin: Codice ISIN del fondo
            name: Nome del fondo
            prices: pandas Series con prezzi storici
        """
        cache = self._load_cache()

        # Converti pandas Series → dict con date ISO string
        prices_dict = {}
        for date, price in prices.items():
            date_str = date.isoformat()[:10]  # Solo YYYY-MM-DD
            prices_dict[date_str] = float(price)

        cache[isin] = {
            "name": name,
            "isin": isin,
            "last_update": datetime.now().isoformat(),
            "num_points": len(prices_dict),
            "prices": prices_dict,
        }

        self._save_cache(cache)
        logger.info(f"Cache salvata per {isin}: {len(prices_dict)} punti dati")

    def clear(self, isin: Optional[str] = None):
        """
        Cancella cache

        Args:
            isin: Se specificato, cancella solo questo ISIN.
                  Se None, cancella tutta la cache.
        """
        if isin is None:
            # Cancella tutto
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
            logger.info("Cache completa cancellata")
        else:
            # Cancella solo un ISIN
            cache = self._load_cache()
            if isin in cache:
                del cache[isin]
                self._save_cache(cache)
                logger.info(f"Cache cancellata per {isin}")

    def get_info(self) -> dict:
        """Restituisce info sulla cache"""
        cache = self._load_cache()
        info = {
            "total_funds": len(cache),
            "cache_file": self.cache_file,
            "funds": []
        }

        for isin, data in cache.items():
            info["funds"].append({
                "isin": isin,
                "name": data.get("name"),
                "last_update": data.get("last_update"),
                "num_points": data.get("num_points", 0),
            })

        return info


# Istanza globale
funds_cache = FundsCache()
