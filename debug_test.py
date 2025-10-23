"""
Script di debug per testare il caricamento dati
"""
import sys
import os

# Fix multitasking prima di importare yfinance
import fix_multitasking

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.data_collectors.yahoo_finance import YahooFinanceCollector
import pandas as pd

print("🔍 Test di Debug FinAnalyzer\n")

# Test 1: Importazione yfinance
print("1️⃣ Test importazione yfinance...")
try:
    import yfinance as yf
    print("✅ yfinance importato correttamente")
    print(f"   Versione: {yf.__version__}")
except Exception as e:
    print(f"❌ Errore: {e}")
    exit(1)

print("\n2️⃣ Test connessione Yahoo Finance...")
try:
    ticker = yf.Ticker("AAPL")
    info = ticker.info
    if info:
        print(f"✅ Connessione OK - Trovato: {info.get('longName', 'N/A')}")
    else:
        print("⚠️ Connessione OK ma nessun dato")
except Exception as e:
    print(f"❌ Errore: {e}")

print("\n3️⃣ Test download dati storici...")
try:
    ticker = yf.Ticker("AAPL")
    hist = ticker.history(period="1mo")
    if not hist.empty:
        print(f"✅ Dati scaricati correttamente")
        print(f"   Righe: {len(hist)}")
        print(f"   Colonne: {list(hist.columns)}")
        print(f"\n   Prime righe:")
        print(hist.head())
    else:
        print("❌ DataFrame vuoto")
except Exception as e:
    print(f"❌ Errore: {e}")

print("\n4️⃣ Test YahooFinanceCollector...")
try:
    collector = YahooFinanceCollector()

    # Test ricerca
    print("\n   Test ricerca 'AAPL':")
    results = collector.search_ticker("AAPL")
    print(f"   Risultati: {len(results)}")
    if results:
        print(f"   Primo risultato: {results[0]}")

    # Test dati storici
    print("\n   Test dati storici 'AAPL':")
    df = collector.get_historical_data("AAPL", period="1mo")
    if not df.empty:
        print(f"   ✅ Dati OK - {len(df)} righe")
    else:
        print("   ❌ DataFrame vuoto")

except Exception as e:
    print(f"❌ Errore: {e}")
    import traceback
    traceback.print_exc()

print("\n5️⃣ Test simboli italiani...")
italian_symbols = ["ENI.MI", "ISP.MI", "ENEL.MI"]
for symbol in italian_symbols:
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1mo")
        if not hist.empty:
            print(f"   ✅ {symbol}: {len(hist)} righe")
        else:
            print(f"   ❌ {symbol}: DataFrame vuoto")
    except Exception as e:
        print(f"   ❌ {symbol}: Errore - {e}")

print("\n6️⃣ Test multipli ticker...")
try:
    symbols = ["AAPL", "MSFT", "GOOGL"]
    data = yf.download(symbols, period="1mo", progress=False)
    if not data.empty:
        print(f"   ✅ Download multiplo OK - {len(data)} righe")
        print(f"   Colonne: {data.columns}")
    else:
        print("   ❌ DataFrame vuoto")
except Exception as e:
    print(f"   ❌ Errore: {e}")

print("\n" + "="*50)
print("🏁 Test completato!")
print("="*50)
