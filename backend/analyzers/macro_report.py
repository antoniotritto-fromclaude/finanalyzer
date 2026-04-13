"""
Macro Financial Report Generator
Generates dynamic macro-financial reports with geographical analysis
"""
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════
# 🌍 GEOGRAPHICAL ASSET MAPPING
# ══════════════════════════════════════════════════════════════════

MACRO_ASSETS = {
    # 💵 VALUTE
    "currencies": {
        "DXY": {"name": "Dollaro USA (DXY)", "region": "North America"},
        "EURUSD=X": {"name": "EUR/USD", "region": "Europe"},
        "GBPUSD=X": {"name": "GBP/USD", "region": "Europe"},
        "JPYUSD=X": {"name": "USD/JPY", "region": "Asia"},
        "AUDUSD=X": {"name": "AUD/USD", "region": "Asia"},
        "CADUSD=X": {"name": "USD/CAD", "region": "North America"},
        "MXNUSD=X": {"name": "USD/MXN", "region": "South America"},
        "BRLUSD=X": {"name": "USD/BRL", "region": "South America"},
        "CNHUSD=X": {"name": "USD/CNH", "region": "Asia"},
    },

    # 📊 INDICI PER REGIONE
    "indices": {
        # Nord America
        "^GSPC": {"name": "S&P 500", "region": "USA"},
        "^DJI": {"name": "Dow Jones", "region": "USA"},
        "^IXIC": {"name": "Nasdaq", "region": "USA"},
        "^GSPTSE": {"name": "TSX Canada", "region": "Canada"},

        # Sud America
        "^MERV": {"name": "Merval Argentina", "region": "Argentina"},
        "^BVSP": {"name": "Bovespa Brasile", "region": "Brasile"},
        "^MXX": {"name": "IPC Messico", "region": "Messico"},
        "^COLCAP": {"name": "COLCAP Colombia", "region": "Colombia"},

        # Europa
        "^STOXX50E": {"name": "Euro Stoxx 50", "region": "Europa"},
        "^FTSE": {"name": "FTSE 100 UK", "region": "Europa"},
        "^GDAXI": {"name": "DAX Germania", "region": "Europa"},
        "^FCHI": {"name": "CAC 40 Francia", "region": "Europa"},

        # Nord Africa (limitato su Yahoo Finance)
        "EGX30.CA": {"name": "EGX 30 Egitto", "region": "Nord Africa"},

        # Medio Oriente
        "^TASI": {"name": "Tadawul Arabia Saudita", "region": "Medio Oriente"},

        # Asia
        "^N225": {"name": "Nikkei 225 Giappone", "region": "Giappone"},
        "000001.SS": {"name": "Shanghai Composite", "region": "Cina"},
        "^HSI": {"name": "Hang Seng Hong Kong", "region": "Cina"},
        "^AXJO": {"name": "ASX 200 Australia", "region": "Australia"},
        "^KLSE": {"name": "KLSE Malesia", "region": "Malesia"},
        "^JKSE": {"name": "Jakarta Indonesia", "region": "Indonesia"},

        # Sudafrica
        "^J203": {"name": "JSE Top 40 Sudafrica", "region": "Sudafrica"},
    },

    # 🛢️ COMMODITIES
    "commodities": {
        "CL=F": {"name": "Petrolio WTI", "type": "Energia"},
        "BZ=F": {"name": "Brent Oil", "type": "Energia"},
        "NG=F": {"name": "Gas Naturale", "type": "Energia"},
        "GC=F": {"name": "Oro", "type": "Metalli Preziosi"},
        "SI=F": {"name": "Argento", "type": "Metalli Preziosi"},
        "HG=F": {"name": "Rame", "type": "Metalli Industriali"},
        "ZW=F": {"name": "Grano", "type": "Agricoltura"},
        "ZC=F": {"name": "Mais", "type": "Agricoltura"},
    },

    # 🏭 SETTORI
    "sectors": {
        "XLE": {"name": "Energia", "type": "Settore"},
        "XLF": {"name": "Finanza", "type": "Settore"},
        "XLK": {"name": "Tecnologia", "type": "Settore"},
        "XLV": {"name": "Healthcare", "type": "Settore"},
        "XLI": {"name": "Industriali", "type": "Settore"},
        "XLY": {"name": "Consumer Discretionary", "type": "Settore"},
        "XLP": {"name": "Consumer Staples", "type": "Settore"},
        "XLB": {"name": "Materiali", "type": "Settore"},
        "ITA": {"name": "Difesa & Aerospazio", "type": "Settore"},
    }
}


# ══════════════════════════════════════════════════════════════════
# 📈 DATA COLLECTION
# ══════════════════════════════════════════════════════════════════

def get_market_data(symbols: List[str], period: str = "5d") -> pd.DataFrame:
    """
    Scarica dati di mercato per una lista di simboli

    Args:
        symbols: Lista di ticker symbols
        period: Periodo di dati ("1d", "5d", "1mo")

    Returns:
        DataFrame con prezzi di chiusura per ogni simbolo
    """
    data = {}

    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)

            if not hist.empty and "Close" in hist.columns:
                data[symbol] = hist["Close"]
                logger.debug(f"✅ {symbol}: {len(hist)} data points")
            else:
                logger.warning(f"⚠️ {symbol}: Nessun dato disponibile")

        except Exception as e:
            logger.error(f"❌ Errore scaricamento {symbol}: {e}")

    if data:
        df = pd.DataFrame(data)
        return df.ffill().bfill()  # Fill missing data
    else:
        return pd.DataFrame()


def calculate_returns(prices: pd.DataFrame, periods: int = 5) -> pd.DataFrame:
    """
    Calcola i rendimenti percentuali

    Args:
        prices: DataFrame con prezzi
        periods: Numero di periodi per il calcolo

    Returns:
        DataFrame con rendimenti percentuali
    """
    if len(prices) < 2:
        return pd.DataFrame()

    returns = ((prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0]) * 100
    return returns


def calculate_correlations(prices: pd.DataFrame, min_periods: int = 3) -> pd.DataFrame:
    """
    Calcola matrice di correlazione tra asset

    Args:
        prices: DataFrame con prezzi
        min_periods: Numero minimo di periodi validi

    Returns:
        Matrice di correlazione
    """
    if len(prices) < min_periods:
        return pd.DataFrame()

    returns = prices.pct_change().dropna()

    if len(returns) < 2:
        return pd.DataFrame()

    corr = returns.corr()
    return corr


# ══════════════════════════════════════════════════════════════════
# 🎯 ALERT GENERATION
# ══════════════════════════════════════════════════════════════════

def detect_correlations(corr_matrix: pd.DataFrame, threshold: float = 0.7) -> List[Dict]:
    """
    Rileva correlazioni forti tra asset

    Args:
        corr_matrix: Matrice di correlazione
        threshold: Soglia minima di correlazione (default 0.7)

    Returns:
        Lista di correlazioni rilevate
    """
    alerts = []

    if corr_matrix.empty:
        return alerts

    # Trova correlazioni forti (positive o negative)
    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)):
            asset1 = corr_matrix.columns[i]
            asset2 = corr_matrix.columns[j]
            corr_value = corr_matrix.iloc[i, j]

            if abs(corr_value) >= threshold:
                direction = "positiva" if corr_value > 0 else "negativa"
                alerts.append({
                    "asset1": asset1,
                    "asset2": asset2,
                    "correlation": corr_value,
                    "direction": direction,
                    "strength": "forte" if abs(corr_value) > 0.85 else "moderata"
                })

    return alerts


def detect_divergences(prices: pd.DataFrame, returns: pd.Series) -> List[Dict]:
    """
    Rileva divergenze tra asset correlati

    Args:
        prices: DataFrame con prezzi
        returns: Serie con rendimenti

    Returns:
        Lista di divergenze rilevate
    """
    divergences = []

    # Esempio: Petrolio vs Dollaro (inversa attesa)
    if "CL=F" in returns.index and "DXY" in returns.index:
        oil_ret = returns["CL=F"]
        dxy_ret = returns["DXY"]

        # Divergenza: entrambi salgono o entrambi scendono
        if (oil_ret > 2 and dxy_ret > 0.5) or (oil_ret < -2 and dxy_ret < -0.5):
            divergences.append({
                "type": "Divergenza Petrolio-Dollaro",
                "description": f"Petrolio {oil_ret:+.1f}% | Dollaro {dxy_ret:+.1f}%",
                "severity": "alta" if abs(oil_ret) > 5 else "media"
            })

    return divergences


def generate_regional_summary(prices: pd.DataFrame, returns: pd.Series) -> Dict[str, Dict]:
    """
    Genera sommario per regione geografica

    Args:
        prices: DataFrame con prezzi
        returns: Serie con rendimenti

    Returns:
        Dict con sommario per regione
    """
    regional_summary = {}

    # Raggruppa indici per regione
    for symbol, info in MACRO_ASSETS["indices"].items():
        if symbol in returns.index:
            region = info["region"]
            name = info["name"]
            ret = returns[symbol]

            if region not in regional_summary:
                regional_summary[region] = {
                    "indices": [],
                    "avg_return": 0,
                    "trend": "neutrale"
                }

            regional_summary[region]["indices"].append({
                "name": name,
                "symbol": symbol,
                "return": ret
            })

    # Calcola media per regione
    for region, data in regional_summary.items():
        avg_ret = np.mean([idx["return"] for idx in data["indices"]])
        data["avg_return"] = avg_ret

        if avg_ret > 1:
            data["trend"] = "positivo ⬆️"
        elif avg_ret < -1:
            data["trend"] = "negativo ⬇️"
        else:
            data["trend"] = "neutrale ➡️"

    return regional_summary


# ══════════════════════════════════════════════════════════════════
# 📝 REPORT GENERATION
# ══════════════════════════════════════════════════════════════════

def generate_macro_report() -> str:
    """
    Genera report macro-finanziario completo

    Returns:
        Testo formattato del report
    """
    logger.info("🔄 Generazione Macro Financial Report...")

    # 1. Scarica dati
    all_symbols = []
    for category in MACRO_ASSETS.values():
        all_symbols.extend(category.keys())

    logger.info(f"📊 Scaricamento {len(all_symbols)} asset...")
    prices = get_market_data(all_symbols, period="5d")

    if prices.empty:
        return "❌ Impossibile generare report: dati non disponibili"

    # 2. Calcola rendimenti
    returns = calculate_returns(prices)

    # 3. Calcola correlazioni
    corr_matrix = calculate_correlations(prices)

    # 4. Rileva alert
    correlations = detect_correlations(corr_matrix, threshold=0.7)
    divergences = detect_divergences(prices, returns)

    # 5. Analisi regionale
    regional_summary = generate_regional_summary(prices, returns)

    # 6. Genera report formattato
    now = datetime.now()
    report = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 MACRO FINANCIAL REPORT AI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🕐 {now.strftime('%d/%m/%Y %H:%M')}

"""

    # ANALISI GEOGRAFICA
    report += "🌍 ANALISI GEOGRAFICA MERCATI\n"
    report += "(performance ultimi 5 giorni)\n\n"

    # Raggruppa per macro-area
    macro_regions = {
        "🇺🇸 AMERICA DEL NORD": ["USA", "Canada"],
        "🇧🇷 AMERICA DEL SUD": ["Argentina", "Brasile", "Messico", "Colombia"],
        "🇪🇺 EUROPA": ["Europa"],
        "🌍 NORD AFRICA": ["Nord Africa", "Egitto"],
        "🕌 MEDIO ORIENTE": ["Medio Oriente"],
        "🇿🇦 SUDAFRICA": ["Sudafrica"],
        "🌏 ASIA & OCEANIA": ["Giappone", "Cina", "Australia", "Malesia", "Indonesia"]
    }

    for macro_area, regions in macro_regions.items():
        area_indices = []
        for region in regions:
            if region in regional_summary:
                area_indices.extend(regional_summary[region]["indices"])

        if area_indices:
            avg_return = np.mean([idx["return"] for idx in area_indices])
            trend_icon = "📈" if avg_return > 0 else "📉"

            report += f"{macro_area}\n"
            report += f"  Media: {avg_return:+.2f}% {trend_icon}\n"

            # Mostra top 3 performer
            sorted_indices = sorted(area_indices, key=lambda x: x["return"], reverse=True)
            for idx in sorted_indices[:3]:
                icon = "🟢" if idx["return"] > 0 else "🔴"
                report += f"  {icon} {idx['name']}: {idx['return']:+.1f}%\n"

            report += "\n"

    # VALUTE
    report += "💵 ALERT VALUTE\n"
    report += "(performance ultimi 5 giorni)\n\n"

    for symbol, info in MACRO_ASSETS["currencies"].items():
        if symbol in returns.index:
            ret = returns[symbol]
            icon = "📈" if ret > 0 else "📉"
            report += f"  {icon} {info['name']}: {ret:+.1f}%\n"

    # Dollaro in evidenza
    if "DXY" in returns.index:
        dxy_ret = returns["DXY"]
        if abs(dxy_ret) > 1:
            direction = "sale" if dxy_ret > 0 else "scende"
            report += f"\n⚠️ ALERT: Il dollaro (DXY) {direction} del {abs(dxy_ret):.1f}%\n"

    report += "\n"

    # COMMODITIES
    report += "🛢️ COMMODITIES & MATERIE PRIME\n\n"

    for symbol, info in MACRO_ASSETS["commodities"].items():
        if symbol in returns.index:
            ret = returns[symbol]
            icon = "🟢" if ret > 0 else "🔴"
            report += f"  {icon} {info['name']}: {ret:+.1f}%\n"

    report += "\n"

    # CORRELAZIONI
    if correlations:
        report += "⚠️ CORRELAZIONI DA MONITORARE\n"
        report += "(quando due asset si muovono insieme in modo anomalo)\n\n"

        for corr in correlations[:5]:  # Top 5
            # Trova nomi user-friendly
            name1 = corr["asset1"]
            name2 = corr["asset2"]

            for category in MACRO_ASSETS.values():
                if corr["asset1"] in category:
                    name1 = category[corr["asset1"]].get("name", corr["asset1"])
                if corr["asset2"] in category:
                    name2 = category[corr["asset2"]].get("name", corr["asset2"])

            icon = "↔️" if corr["direction"] == "positiva" else "⚡"
            report += f"  {icon} {name1} vs {name2}\n"
            report += f"     Correlazione {corr['direction']} ({corr['correlation']:.2f})\n"

        report += "\n"

    # DIVERGENZE
    if divergences:
        report += "🔔 DIVERGENZE RILEVATE\n\n"
        for div in divergences:
            report += f"  ⚠️ {div['type']}\n"
            report += f"     {div['description']}\n"
        report += "\n"

    # CALENDARIO EVENTI
    report += "📅 EVENTI CHIAVE DA MONITORARE\n\n"
    report += "  • Decisioni banche centrali (Fed, ECB, BoJ)\n"
    report += "  • Dati inflazione USA, Europa, Cina\n"
    report += "  • Tensioni geopolitiche (Medio Oriente)\n"
    report += "  • Prezzi commodities (petrolio, oro)\n"
    report += "  • Earnings stagione USA\n"

    report += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    report += "🤖 Powered by FinAnalyzer Pro\n"
    report += "#macrofinancialreport\n"

    logger.info("✅ Report generato con successo")
    return report


# ══════════════════════════════════════════════════════════════════
# 🧪 TEST
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("Generazione Macro Financial Report...\n")
    report = generate_macro_report()
    print(report)
