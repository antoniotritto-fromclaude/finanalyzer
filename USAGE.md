# Guida all'Uso di FinAnalyzer

## 🚀 Quick Start

### 1. Installazione

```bash
# Clona il repository
git clone <repository-url>
cd finanalyzer

# Installa le dipendenze
pip install -r requirements.txt
```

### 2. Avvio dell'Applicazione

#### Opzione A: Solo Frontend (Streamlit)

```bash
streamlit run frontend/app.py
```

L'applicazione sarà disponibile su `http://localhost:8501`

#### Opzione B: Backend + Frontend

**Terminal 1 - Backend:**
```bash
python -m uvicorn backend.api.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
streamlit run frontend/app.py
```

## 📖 Guida Funzionalità

### 1. Ricerca Strumenti Finanziari

**Cosa puoi cercare:**
- Azioni (es: AAPL, MSFT, ENI.MI, ISP.MI)
- ETF (es: VWCE.DE, SWDA.MI, CSSPX.MI)
- Obbligazioni (BTP, titoli di stato)
- Fondi d'investimento
- Commodities (oro, petrolio, ecc.)
- Certificati

**Come fare:**
1. Vai su "Ricerca Strumenti"
2. Inserisci il simbolo o nome (es: "Tesla" o "TSLA")
3. Clicca "Cerca"
4. Aggiungi i risultati al portafoglio

**Esempi di simboli italiani:**
- `ENI.MI` - Eni
- `ISP.MI` - Intesa Sanpaolo
- `UCG.MI` - UniCredit
- `ENEL.MI` - Enel
- `RACE.MI` - Ferrari

### 2. Costruzione Portafoglio

**Passo per passo:**
1. Vai su "Costruisci Portafoglio"
2. Aggiungi simboli uno alla volta
3. Imposta i pesi manualmente (opzionale)
4. Visualizza dati storici per ogni asset

**Esempio di portafoglio bilanciato:**
```
40% SWDA.MI (MSCI World ETF)
30% CSSPX.MI (S&P 500 ETF)
20% EIMI.MI (Emerging Markets ETF)
10% ENI.MI (Azioni italiane)
```

### 3. Ottimizzazione con Markowitz

**Teoria:**
La teoria di Markowitz trova il portafoglio ottimale che:
- Massimizza il rendimento per un dato livello di rischio
- Minimizza il rischio per un dato livello di rendimento

**Strategie disponibili:**

#### A. Massimizza Sharpe Ratio (Raccomandato)
- Trova il miglior rapporto rendimento/rischio
- Ideale per investitori che cercano efficienza

#### B. Minimizza Volatilità
- Riduce al minimo il rischio
- Ideale per investitori conservativi

#### C. Rendimento Target
- Imposta un obiettivo di rendimento (es: 15% annuo)
- Minimizza il rischio necessario per raggiungerlo

#### D. Rischio Target
- Imposta un obiettivo di volatilità (es: 10% annuo)
- Massimizza il rendimento per quel livello di rischio

**Come usarlo:**
1. Vai su "Ottimizzazione Markowitz"
2. Seleziona il tipo di ottimizzazione
3. Scegli il periodo storico (consigliato: 3-5 anni)
4. Clicca "Ottimizza Portafoglio"
5. Visualizza la frontiera efficiente e i pesi ottimali

**Interpretazione risultati:**
- **Expected Return**: Rendimento annuale atteso
- **Volatility**: Rischio annuale (deviazione standard)
- **Sharpe Ratio**: Rendimento per unità di rischio (>1 è buono, >2 è ottimo)

### 4. Backtest Storico

**Cos'è:**
Testa come si sarebbe comportato il tuo portafoglio negli anni passati.

**Periodi disponibili:**
- 1 anno
- 3 anni
- 5 anni
- 7 anni

**Metriche importanti:**

- **Rendimento Totale**: Guadagno/perdita totale nel periodo
- **Sharpe Ratio**: Efficienza del portafoglio
- **Max Drawdown**: Massima perdita dal picco
- **Volatilità**: Quanto oscilla il valore
- **Sortino Ratio**: Sharpe Ratio che considera solo il rischio negativo
- **Calmar Ratio**: Rendimento / Max Drawdown
- **Win Rate**: % di giorni positivi

**Come interpretare:**
- Sharpe > 1: Buono
- Sharpe > 2: Molto buono
- Max Drawdown < 20%: Accettabile
- Max Drawdown > 50%: Molto rischioso

### 5. Predizioni Future (6 mesi)

**Metodologia:**
Usa simulazioni Monte Carlo (10,000 simulazioni) basate su:
- Rendimenti storici
- Volatilità storica
- Correlazioni tra asset

**Tre scenari:**

#### 🟢 Scenario Migliore (95° percentile)
- Solo il 5% delle simulazioni fa meglio
- Scenario ottimistico ma possibile

#### 🟡 Scenario Normale (50° percentile / Mediana)
- Scenario più probabile
- 50% di probabilità di fare meglio, 50% di fare peggio

#### 🔴 Scenario Peggiore (5° percentile)
- Solo il 5% delle simulazioni fa peggio
- Scenario pessimistico (Value at Risk)

**Value at Risk (VaR):**
- VaR 95%: Perdita massima attesa nel 95% dei casi
- CVaR: Perdita media quando si supera il VaR

**Nota importante:**
Le predizioni sono basate su dati storici e NON garantiscono performance future!

## 💡 Esempi Pratici

### Esempio 1: Portafoglio Conservativo Italiano

```
Obiettivo: Basso rischio, rendimento moderato
Orizzonte: 5 anni

Portafoglio:
- 50% CSSPX.MI (S&P 500)
- 30% SWDA.MI (MSCI World)
- 20% BTP (Obbligazioni italiane)

Strategia: Minimizza Volatilità
```

### Esempio 2: Portafoglio Aggressivo Growth

```
Obiettivo: Alto rendimento, alto rischio
Orizzonte: 10 anni

Portafoglio:
- 40% AAPL (Apple)
- 30% MSFT (Microsoft)
- 20% GOOGL (Google)
- 10% RACE.MI (Ferrari)

Strategia: Massimizza Sharpe Ratio
```

### Esempio 3: Portafoglio Bilanciato Globale

```
Obiettivo: Bilanciamento rischio/rendimento
Orizzonte: 7 anni

Portafoglio:
- 40% VWCE.DE (All-World ETF)
- 20% EIMI.MI (Emerging Markets)
- 20% ENI.MI (Energia)
- 10% ENEL.MI (Utilities)
- 10% Oro/Commodities

Strategia: Massimizza Sharpe Ratio
```

## ⚠️ Avvertenze

1. **Questo NON è un consiglio finanziario**
   - Le analisi sono puramente indicative
   - Consulta sempre un consulente finanziario professionista

2. **Dati storici ≠ Performance futura**
   - I rendimenti passati non garantiscono rendimenti futuri
   - I mercati possono cambiare drasticamente

3. **Diversificazione**
   - Non investire mai tutto in un singolo asset
   - Diversifica per settore, geografia e tipo di asset

4. **Orizzonte temporale**
   - Investi solo denaro che non ti serve nel breve termine
   - Per orizzonti <3 anni, considera strumenti più sicuri

5. **Costi e tasse**
   - Le simulazioni non includono commissioni di trading
   - Non includono tasse sulle plusvalenze
   - Considera questi costi nelle tue decisioni

## 🔧 Risoluzione Problemi

### Problema: "Simbolo non trovato"
**Soluzione:**
- Verifica il formato (es: per Milano usa `.MI`)
- Prova varianti del simbolo
- Cerca prima su Yahoo Finance per il simbolo corretto

### Problema: "Nessun dato disponibile"
**Soluzione:**
- Alcuni asset potrebbero non avere dati storici sufficienti
- Prova con un periodo più breve
- Verifica che il simbolo sia corretto

### Problema: "Ottimizzazione fallita"
**Soluzione:**
- Verifica che ci siano almeno 2 asset
- Controlla che ci siano dati sufficienti
- Prova con asset più liquidi/comuni

## 📚 Risorse Aggiuntive

**Siti di riferimento:**
- [Yahoo Finance](https://finance.yahoo.com/) - Dati finanziari
- [JustETF](https://www.justetf.com/it/) - ETF europei
- [Investing.com](https://it.investing.com/) - Mercati globali
- [TradingView](https://it.tradingview.com/) - Grafici e analisi

**Teoria finanziaria:**
- Teoria di Markowitz / Modern Portfolio Theory
- Sharpe Ratio e metriche di performance
- Value at Risk (VaR)
- Simulazioni Monte Carlo

## 🆘 Supporto

Per bug o domande, apri una issue su GitHub.

---

**Versione:** 1.0.0
**Ultimo aggiornamento:** 2025
