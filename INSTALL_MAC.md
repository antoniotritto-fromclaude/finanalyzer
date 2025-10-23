# 🍎 Guida Installazione per macOS

## Installazione Rapida

### Step 1: Apri Terminal

Premi `Cmd + Space`, scrivi "Terminal" e premi Invio.

### Step 2: Vai nella cartella del progetto

```bash
cd /path/to/finanalyzer
# Ad esempio: cd ~/Desktop/finanalyzer
```

### Step 3: Esegui lo script di setup automatico

```bash
chmod +x setup_mac.sh
./setup_mac.sh
```

Questo installerà tutto automaticamente!

---

## Installazione Manuale (se lo script non funziona)

### 1️⃣ Verifica Python

```bash
python3 --version
```

Dovresti vedere Python 3.9 o superiore. Se non ce l'hai:

```bash
# Installa Homebrew se non ce l'hai
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Installa Python
brew install python
```

### 2️⃣ Crea un Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

Vedrai `(venv)` davanti al prompt.

### 3️⃣ Installa Dipendenze

```bash
# Installa dipendenze base
pip install --upgrade pip
pip install pandas numpy scipy requests beautifulsoup4 lxml

# Installa yfinance e le sue dipendenze
pip install yfinance curl-cffi frozendict peewee websockets platformdirs

# Installa visualizzazione e frontend
pip install plotly matplotlib streamlit

# Installa scikit-learn per analisi
pip install scikit-learn

# Installa FastAPI per API (opzionale)
pip install fastapi uvicorn python-dotenv
```

### 4️⃣ Testa l'Installazione

```bash
python3 test_installation.py
```

Dovresti vedere output positivi. Se vedi errori HTTP 403, continua comunque - potrebbero essere temporanei.

### 5️⃣ Avvia l'Applicazione

```bash
streamlit run frontend/app.py
```

L'app si aprirà automaticamente nel browser!

---

## 🔧 Risoluzione Problemi Comuni

### Problema: "No module named 'yfinance'"

**Soluzione:**
```bash
source venv/bin/activate  # Attiva il virtual environment
pip install yfinance
```

### Problema: "HTTP 403" quando scarichi dati

**Cause possibili:**
1. Yahoo Finance sta temporaneamente bloccando il tuo IP
2. Troppi requests troppo velocemente
3. Problemi di connessione internet

**Soluzioni:**
1. Aspetta qualche minuto e riprova
2. Usa una VPN diversa
3. Riavvia il router
4. Prova simboli diversi (es. AAPL invece di ENI.MI)

### Problema: "ImportError: cannot import name..."

**Soluzione:**
```bash
# Disinstalla e reinstalla yfinance
pip uninstall yfinance -y
pip install yfinance --no-cache-dir
```

### Problema: L'app non si apre nel browser

**Soluzione:**
Apri manualmente: http://localhost:8501

### Problema: "Port 8501 already in use"

**Soluzione:**
```bash
# Usa una porta diversa
streamlit run frontend/app.py --server.port 8502
```

---

## 📊 Test Rapido

Una volta avviata l'app, prova:

1. **Ricerca Semplice:**
   - Vai su "Ricerca Strumenti"
   - Cerca "AAPL"
   - Dovresti vedere Apple Inc.

2. **Costruisci Portfolio:**
   - Vai su "Costruisci Portafoglio"
   - Aggiungi: AAPL, MSFT, GOOGL
   - Visualizza dati storici

3. **Ottimizzazione:**
   - Vai su "Ottimizzazione Markowitz"
   - Scegli "Massimizza Sharpe Ratio"
   - Clicca "Ottimizza"
   - Dovresti vedere grafici e pesi ottimali

---

## 🚀 Simboli da Provare

### Azioni USA
- AAPL (Apple)
- MSFT (Microsoft)
- GOOGL (Google)
- TSLA (Tesla)
- AMZN (Amazon)

### Azioni Italiane
- ENI.MI (Eni)
- ISP.MI (Intesa Sanpaolo)
- UCG.MI (UniCredit)
- ENEL.MI (Enel)
- RACE.MI (Ferrari)

### ETF
- SPY (S&P 500)
- VTI (Total Stock Market)
- SWDA.MI (iShares MSCI World)
- VWCE.DE (Vanguard All-World)

---

## 💡 Tips per Mac

### Shortcut Utili
- `Cmd + Space` → Apri Spotlight (per cercare Terminal)
- `Cmd + T` → Nuova tab nel Terminal
- `Ctrl + C` → Ferma l'applicazione
- `Cmd + Q` → Chiudi Terminal

### Performance
Se l'app è lenta:
```bash
# Chiudi altre applicazioni
# Aumenta memoria disponibile
# Usa Safari invece di Chrome
```

### Aggiornamenti
Per aggiornare:
```bash
cd finanalyzer
git pull
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

---

## 📞 Hai Problemi?

Se continui ad avere problemi:

1. Controlla che tutte le dipendenze siano installate:
   ```bash
   pip list
   ```

2. Verifica la versione di Python:
   ```bash
   python3 --version  # Dovrebbe essere 3.9+
   ```

3. Prova a ricreare il virtual environment:
   ```bash
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Controlla i log di Streamlit:
   - Guarda il Terminal per messaggi di errore
   - Controlla il menu hamburger (in alto a destra nell'app)

---

## ✅ Checklist Finale

Prima di usare l'app, verifica:

- [ ] Python 3.9+ installato
- [ ] Virtual environment attivo (vedi `(venv)` nel prompt)
- [ ] Tutte le dipendenze installate
- [ ] Internet funzionante
- [ ] L'app si apre su http://localhost:8501
- [ ] Riesci a cercare almeno un simbolo (es. AAPL)

Se hai tutti i check, sei pronto! 🎉

---

**Buon trading! 📈**
