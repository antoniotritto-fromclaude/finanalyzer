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
RECENT_FILE = os.path.join(CACHE_DIR, "recent_funds.json")
CACHE_TTL_HOURS = 24  # Cache valida per 24 ore
MAX_RECENT_FUNDS = 20  # Mantieni solo ultimi 20 fondi


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

    def _load_recent(self) -> list:
        """Carica lista fondi recenti"""
        if not os.path.exists(RECENT_FILE):
            return []
        try:
            with open(RECENT_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Errore lettura recent: {e}")
            return []

    def _save_recent(self, recent: list):
        """Salva lista fondi recenti"""
        try:
            with open(RECENT_FILE, 'w', encoding='utf-8') as f:
                json.dump(recent, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Errore scrittura recent: {e}")

    def add_recent(self, identifier: str, name: str, source: str = "Morningstar"):
        """
        Aggiunge un fondo alla lista recenti

        Args:
            identifier: ISIN, URL, o cache_key
            name: Nome del fondo
            source: Fonte dati (Morningstar, Yahoo Finance)
        """
        recent = self._load_recent()

        # Rimuovi se già presente (lo sposteremo in cima)
        recent = [r for r in recent if r.get("id") != identifier]

        # Aggiungi in cima
        recent.insert(0, {
            "id": identifier,
            "name": name,
            "source": source,
            "added": datetime.now().isoformat(),
        })

        # Mantieni solo ultimi 20
        recent = recent[:MAX_RECENT_FUNDS]

        self._save_recent(recent)
        logger.info(f"Aggiunto a recenti: {name} ({identifier})")

        # Cleanup cache: rimuovi fondi non più nei recenti
        self._cleanup_old_cache(recent)

    def get_recent(self) -> list:
        """
        Restituisce lista fondi recenti

        Returns:
            Lista di dict con {id, name, source, added}
        """
        return self._load_recent()

    def _cleanup_old_cache(self, recent: list):
        """
        Rimuove dalla cache i fondi non più nei recenti 20

        Args:
            recent: Lista fondi recenti
        """
        cache = self._load_cache()
        recent_ids = {r.get("id") for r in recent}

        # Trova fondi da rimuovere
        to_remove = [isin for isin in cache.keys() if isin not in recent_ids]

        if to_remove:
            for isin in to_remove:
                del cache[isin]
            self._save_cache(cache)
            logger.info(f"Cleanup cache: rimossi {len(to_remove)} fondi vecchi")

    def clear_recent(self):
        """Cancella lista recenti"""
        if os.path.exists(RECENT_FILE):
            os.remove(RECENT_FILE)
        logger.info("Lista recenti cancellata")


# Istanza globale
funds_cache = FundsCache()
