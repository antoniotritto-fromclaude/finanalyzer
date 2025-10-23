# 🔧 FIX per Errore "Caricamento Dati"

## Il Problema

Se vedi "ERRORE NEL CARICAMENTO DEI DATI" quando provi a visualizzare grafici o fare backtest, è probabilmente dovuto a:

1. **Dipendenze mancanti** - yfinance e le sue dipendenze non sono installate correttamente
2. **Multitasking module** - Un modulo richiesto da yfinance che può avere problemi di installazione
3. **Yahoo Finance 403** - Yahoo potrebbe temporaneamente bloccare le richieste (raro sul Mac locale)

## ✅ Soluzione Rapida (per Mac)

### Metodo 1: Script Automatico (CONSIGLIATO)

```bash
cd finanalyzer
chmod +x setup_mac.sh
./setup_mac.sh
```

Questo installerà tutto automaticamente!

### Metodo 2: Installazione Manuale

```bash
# 1. Crea e attiva virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Installa dipendenze essenziali
pip install pandas numpy scipy

# 3. Installa yfinance e dipendenze
pip install yfinance
pip install curl-cffi frozendict peewee websockets platformdirs

# 4. Installa visualizzazione e frontend
pip install plotly matplotlib streamlit

# 5. Installa scikit-learn
pip install scikit-learn

# 6. Installa FastAPI (opzionale)
pip install fastapi uvicorn python-dotenv
```

### 3. Testa l'installazione

```bash
python3 test_installation.py
```

Dovresti vedere molti ✅ verdi!

### 4. Avvia l'app

```bash
streamlit run frontend/app.py
```

---

## 🐛 Se il problema persiste

### Test 1: Verifica yfinance

Apri Python e prova:

```python
python3
>>> import yfinance as yf
>>> ticker = yf.Ticker("AAPL")
>>> hist = ticker.history(period="5d")
>>> print(hist)
```

Se vedi dati → yfinance funziona! ✅
Se vedi errori → continua sotto ⬇️

### Test 2: Verifica connessione Internet

```bash
ping yahoo.com
```

Se non risponde → controlla la tua connessione internet

### Test 3: Prova simboli diversi

A volte alcuni simboli non funzionano. Prova:

**Azioni USA:**
- AAPL (Apple)
- MSFT (Microsoft)
- GOOGL (Google)

**Invece di:**
- Simboli italiani (ENI.MI, ISP.MI) che potrebbero avere meno dati
- Simboli oscuri o delisted

### Test 4: Problemi con Multitasking

Se vedi errori tipo "module 'multitasking' has no attribute...", il fix è già incluso!

Il file `fix_multitasking.py` risolve automaticamente il problema. Assicurati che sia presente nella cartella principale.

### Test 5: HTTP 403 Errors

Se vedi "HTTP Error 403: Access denied":

**Cause:**
- Yahoo Finance sta bloccando temporaneamente il tuo IP
- Troppi requests troppo velocemente
- Firewall/antivirus che blocca le richieste

**Soluzioni:**
1. Aspetta 5-10 minuti e riprova
2. Riavvia il router
3. Usa una VPN diversa
4. Prova in un momento diverso della giornata
5. Controlla il firewall/antivirus

---

## 📝 Checklist Completa

Segui questa checklist per risolvere il problema:

- [ ] Python 3.9+ installato (`python3 --version`)
- [ ] Virtual environment creato (`venv` folder esiste)
- [ ] Virtual environment attivo (vedi `(venv)` nel prompt)
- [ ] yfinance installato (`pip list | grep yfinance`)
- [ ] Tutte le dipendenze installate (`pip list`)
- [ ] Internet funzionante (`ping yahoo.com`)
- [ ] Test installazione OK (`python3 test_installation.py`)
- [ ] `fix_multitasking.py` presente nella cartella
- [ ] Streamlit si avvia senza errori

---

## 🎯 Test Rapido nell'App

Una volta avviata, prova in ordine:

### 1. Test Simbolo Semplice
- Vai su "Costruisci Portafoglio"
- Aggiungi "AAPL"
- Se funziona → ✅ tutto OK!
- Se fallisce → continua...

### 2. Test con Simboli Alternativi
Prova questi simboli conosciuti per funzionare:
- **SPY** (ETF S&P 500)
- **MSFT** (Microsoft)
- **GOOGL** (Google)

### 3. Test Periodo Più Corto
Invece di "1y", prova:
- **1mo** (1 mese) - Meno dati da scaricare
- **3mo** (3 mesi)

---

## 💡 Tips Avanzati

### Pulizia Cache yfinance

A volte la cache di yfinance si corrompe:

```bash
# Trova e rimuovi la cache
rm -rf ~/.cache/py-yfinance
```

### Reinstallazione Pulita yfinance

```bash
pip uninstall yfinance -y
pip install yfinance --no-cache-dir --force-reinstall
```

### Debug Mode

Per vedere più informazioni sugli errori, aggiungi all'inizio di `frontend/app.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 🆘 Ancora Problemi?

Se hai fatto tutto e non funziona ancora:

### 1. Controlla i Log

Guarda il Terminal dove hai avviato Streamlit. Cerca messaggi di errore tipo:
- `ModuleNotFoundError` → Dipendenza mancante
- `HTTP Error 403` → Yahoo sta bloccando
- `ConnectionError` → Problema internet

### 2. Modalità Demo (Coming Soon)

Stiamo aggiungendo una modalità demo con dati simulati per testare l'app anche offline!

### 3. Usa l'API Alternativa

Se Yahoo Finance continua a bloccare, considera:
- Alpha Vantage (richiede API key gratuita)
- IEX Cloud (limitato ma gratuito)
- Polygon.io (API key gratuita)

---

## 📚 Documentazione Completa

- **INSTALL_MAC.md** - Guida installazione completa per Mac
- **USAGE.md** - Guida uso dell'applicazione
- **README.md** - Documentazione tecnica

---

## ✅ Problema Risolto?

Quando tutto funziona, dovresti vedere:

✅ Grafici si caricano
✅ Backtest funziona
✅ Ottimizzazione mostra risultati
✅ Predizioni generano scenari

**Buon trading! 📈**

---

*Ultimo aggiornamento: 2025*
