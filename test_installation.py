"""
Test di Installazione FinAnalyzer
Verifica che tutte le dipendenze siano installate correttamente
"""
import sys

print("🧪 Test Installazione FinAnalyzer")
print("=" * 50)
print("")

# Test imports
tests = [
    ("pandas", "Pandas (Data Analysis)"),
    ("numpy", "NumPy (Numerical Computing)"),
    ("scipy", "SciPy (Scientific Computing)"),
    ("requests", "Requests (HTTP Library)"),
    ("bs4", "BeautifulSoup4 (Web Scraping)"),
    ("plotly", "Plotly (Visualizzazione)"),
    ("matplotlib", "Matplotlib (Grafici)"),
    ("streamlit", "Streamlit (Frontend)"),
    ("sklearn", "Scikit-learn (Machine Learning)"),
]

# Test opzionali
optional_tests = [
    ("yfinance", "yfinance (Dati Finanziari)"),
    ("fastapi", "FastAPI (API Backend)"),
    ("uvicorn", "Uvicorn (Server ASGI)"),
]

passed = 0
failed = 0
warnings = 0

print("📦 Test Dipendenze Essenziali:")
print("-" * 50)

for module, name in tests:
    try:
        __import__(module)
        print(f"✅ {name}")
        passed += 1
    except ImportError as e:
        print(f"❌ {name} - NON INSTALLATO")
        print(f"   Errore: {e}")
        failed += 1

print("")
print("📦 Test Dipendenze Opzionali:")
print("-" * 50)

for module, name in optional_tests:
    try:
        __import__(module)
        print(f"✅ {name}")
        passed += 1
    except ImportError as e:
        print(f"⚠️  {name} - Non installato (opzionale)")
        print(f"   Installa con: pip install {module}")
        warnings += 1

# Test yfinance specifico
print("")
print("🔍 Test yfinance (Accesso Dati Finanziari):")
print("-" * 50)

try:
    import yfinance as yf
    import fix_multitasking  # Import the fix first

    print("✅ yfinance importato")
    print(f"   Versione: {yf.__version__}")

    # Test download rapido
    print("   Test download AAPL...")
    try:
        ticker = yf.Ticker("AAPL")
        hist = ticker.history(period="5d")

        if not hist.empty:
            print(f"   ✅ Download riuscito - {len(hist)} giorni di dati")
            last_price = hist['Close'].iloc[-1]
            print(f"   💰 Ultimo prezzo AAPL: ${last_price:.2f}")
        else:
            print("   ⚠️  Download vuoto - Potrebbe essere un problema temporaneo")
            warnings += 1

    except Exception as e:
        print(f"   ⚠️  Errore download: {e}")
        print("   Questo potrebbe essere temporaneo. Riprova più tardi.")
        warnings += 1

except ImportError:
    print("❌ yfinance non installato")
    print("   Installa con: pip install yfinance")
    failed += 1
except Exception as e:
    print(f"⚠️  Errore: {e}")
    warnings += 1

# Test Python version
print("")
print("🐍 Versione Python:")
print("-" * 50)
print(f"   Python {sys.version}")
version_info = sys.version_info
if version_info.major == 3 and version_info.minor >= 9:
    print("   ✅ Versione compatibile (3.9+)")
    passed += 1
else:
    print("   ⚠️  Versione Python potrebbe essere troppo vecchia")
    print("   Consigliato: Python 3.9 o superiore")
    warnings += 1

# Test imports backend
print("")
print("🔧 Test Moduli Backend:")
print("-" * 50)

try:
    sys.path.insert(0, '.')
    from backend.data_collectors.unified_collector import UnifiedDataCollector
    print("✅ Data Collectors")
    passed += 1
except Exception as e:
    print(f"❌ Data Collectors - {e}")
    failed += 1

try:
    from backend.analyzers.portfolio_optimizer import PortfolioOptimizer
    print("✅ Portfolio Optimizer")
    passed += 1
except Exception as e:
    print(f"❌ Portfolio Optimizer - {e}")
    failed += 1

try:
    from backend.analyzers.backtest import BacktestEngine
    print("✅ Backtest Engine")
    passed += 1
except Exception as e:
    print(f"❌ Backtest Engine - {e}")
    failed += 1

try:
    from backend.models.predictor import PortfolioPredictor
    print("✅ Predictive Models")
    passed += 1
except Exception as e:
    print(f"❌ Predictive Models - {e}")
    failed += 1

# Riepilogo
print("")
print("=" * 50)
print("📊 Riepilogo Test:")
print("=" * 50)
print(f"✅ Test passati:  {passed}")
print(f"❌ Test falliti:  {failed}")
print(f"⚠️  Avvertimenti:  {warnings}")
print("")

if failed == 0:
    print("🎉 SUCCESSO! Tutte le dipendenze essenziali sono installate!")
    print("")
    print("Prossimi passi:")
    print("  1. Avvia l'applicazione:")
    print("     streamlit run frontend/app.py")
    print("")
    print("  2. Oppure usa lo script:")
    print("     ./run.sh")
    print("")
else:
    print("⚠️  Alcuni test sono falliti!")
    print("")
    print("Risoluzione:")
    print("  1. Attiva il virtual environment:")
    print("     source venv/bin/activate")
    print("")
    print("  2. Installa le dipendenze mancanti:")
    print("     pip install -r requirements.txt")
    print("")
    print("  3. O esegui lo script di setup:")
    print("     ./setup_mac.sh")
    print("")

if warnings > 0 and failed == 0:
    print("ℹ️  Ci sono alcuni avvertimenti, ma l'applicazione dovrebbe funzionare.")
    print("   Se riscontri problemi, controlla INSTALL_MAC.md")
    print("")

print("=" * 50)
