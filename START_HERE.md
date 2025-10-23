# 🍎 INIZIA QUI - FinAnalyzer per Mac

## 🎯 Setup Veloce (5 minuti)

### 1️⃣ Scarica il Codice

Se non l'hai già fatto:

```bash
git clone <url-repository>
cd finanalyzer
```

### 2️⃣ Esegui Setup Automatico

```bash
chmod +x setup_mac.sh
./setup_mac.sh
```

Aspetta che finisca (2-3 minuti). Vedrai molti ✅ verdi!

### 3️⃣ Testa l'Installazione

```bash
python3 test_installation.py
```

Dovresti vedere:
- ✅ Tutti i moduli importati
- ✅ yfinance funzionante
- ✅ Download dati OK
- 🎉 SUCCESSO!

### 4️⃣ Avvia l'App

```bash
./run.sh
```

Oppure:

```bash
source venv/bin/activate
streamlit run frontend/app.py
```

L'app si aprirà automaticamente nel browser su `http://localhost:8501`

---

## 🚀 Primo Utilizzo

### Test Rapido

1. **Ricerca un Simbolo:**
   - Clicca su "🔍 Ricerca Strumenti"
   - Cerca "AAPL"
   - Dovresti vedere "Apple Inc."

2. **Costruisci un Portafoglio:**
   - Vai su "💼 Costruisci Portafoglio"
   - Aggiungi: AAPL, MSFT, GOOGL
   - Clicca "📈 Visualizza Dati Storici"
   - Dovresti vedere un grafico!

3. **Ottimizza (Markowitz):**
   - Vai su "📈 Ottimizzazione Markowitz"
   - Seleziona "Massimizza Sharpe Ratio"
   - Clicca "🎯 Ottimizza Portafoglio"
   - Vedrai: pesi ottimali + frontiera efficiente!

4. **Backtest:**
   - Vai su "⏮️ Backtest"
   - Seleziona periodi: 1, 3, 5 anni
   - Clicca "▶️ Esegui Backtest"
   - Vedrai performance storiche!

5. **Predizioni:**
   - Vai su "🔮 Predizioni Future"
   - Imposta 6 mesi
   - Clicca "🔮 Genera Predizioni"
   - Vedrai 3 scenari: normale, peggiore, migliore!

---

## ⚠️ Hai Problemi?

### Errore: "Caricamento dati"

Leggi: **FIX_README.md** (guida completa!)

**Quick fix:**
```bash
source venv/bin/activate
pip install yfinance curl-cffi frozendict peewee websockets
```

### Errore: "No module named..."

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### HTTP 403 Errors

- Aspetta 5 minuti e riprova
- Prova simboli USA (AAPL, MSFT) invece di italiani
- Controlla la connessione internet

---

## 📚 Documentazione

- **START_HERE.md** ← Sei qui!
- **FIX_README.md** - Risoluzione problemi
- **INSTALL_MAC.md** - Guida installazione dettagliata
- **USAGE.md** - Guida uso completa con esempi
- **README.md** - Documentazione tecnica

---

## 🎓 Esempi di Portafoglio

### Portafoglio Conservativo
```
50% SPY (S&P 500 ETF)
30% AGG (Bond ETF)
20% GLD (Gold ETF)
```

### Portafoglio Growth
```
40% AAPL (Apple)
30% MSFT (Microsoft)
20% GOOGL (Google)
10% NVDA (Nvidia)
```

### Portafoglio Italiano
```
40% SWDA.MI (MSCI World ETF)
30% ENI.MI (Eni)
20% ISP.MI (Intesa Sanpaolo)
10% ENEL.MI (Enel)
```

### Portafoglio Bilanciato Globale
```
50% VWCE.DE (Vanguard All-World)
20% EIMI.MI (Emerging Markets)
20% SWDA.MI (MSCI World)
10% Cash
```

---

## 💡 Tips & Tricks

### Simboli che Funzionano Sempre

**USA:**
- AAPL, MSFT, GOOGL, AMZN, TSLA
- SPY, QQQ, IWM (ETF)

**Italiani:**
- ENI.MI, ISP.MI, UCG.MI, ENEL.MI, RACE.MI
- SWDA.MI, CSSPX.MI (ETF)

**Europei:**
- VWCE.DE, EIMI.MI (ETF)

### Periodi Consigliati

- **Ottimizzazione:** 3-5 anni
- **Backtest:** 1, 3, 5, 7 anni
- **Predizioni:** 6 mesi (default)

### Performance

- **Sharpe Ratio:**
  - > 1: Buono
  - > 2: Molto buono
  - > 3: Eccellente

- **Max Drawdown:**
  - < 10%: Molto basso
  - 10-20%: Accettabile
  - > 20%: Alto rischio

---

## 🔄 Aggiornamenti

Per aggiornare all'ultima versione:

```bash
cd finanalyzer
git pull
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

---

## 🆘 Supporto

**Hai ancora problemi?**

1. Leggi **FIX_README.md**
2. Esegui `python3 test_installation.py`
3. Controlla i log nel Terminal
4. Verifica internet: `ping yahoo.com`

**Checklist rapida:**
- [ ] Python 3.9+ installato
- [ ] Virtual environment attivo (vedi `(venv)`)
- [ ] `pip list | grep yfinance` mostra yfinance installato
- [ ] Internet funzionante
- [ ] Test installazione OK

---

## ✨ Features Principali

✅ Ricerca strumenti da multiple fonti
✅ Ottimizzazione portfolio (Markowitz)
✅ Frontiera efficiente visualizzata
✅ Backtest storici (1-7 anni)
✅ Predizioni a 6 mesi (3 scenari)
✅ Analisi volatilità
✅ Metriche avanzate (Sharpe, Sortino, Calmar)
✅ Grafici interattivi
✅ Interface intuitiva

---

## 🎉 Pronto!

Una volta che vedi l'app nel browser, sei pronto per analizzare i tuoi investimenti!

**Inizia con qualcosa di semplice:**
1. Cerca "AAPL"
2. Aggiungilo al portafoglio
3. Visualizza dati storici
4. Gioca con le funzionalità!

**Buon trading! 📈💰**

---

*Domande? Leggi la documentazione completa in USAGE.md*
