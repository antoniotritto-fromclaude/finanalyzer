# 🚨 GUIDA: Fondi vs ETF - Perché i Fondi non Funzionano

## ❌ **PROBLEMA**

**I fondi comuni NON sono supportati** in FinAnalyzer perché:

1. Usano codici **ISIN** (es: IT0005239881, LU1234567890)
2. Yahoo Finance **non supporta ISIN**
3. Yahoo Finance funziona solo con **ticker standard**

---

## ✅ **SOLUZIONE: Usa ETF Invece di Fondi**

Gli ETF sono **equivalenti** (o migliori) dei fondi comuni:

### **Vantaggi ETF vs Fondi:**

| Caratteristica | Fondi Comuni | ETF |
|----------------|--------------|-----|
| **Disponibilità dati** | ❌ NO Yahoo Finance | ✅ SI Yahoo Finance |
| **Costi (TER)** | 1-2% annuo | 0.05-0.5% annuo |
| **Liquidità** | 1 volta/giorno | Tempo reale |
| **Trasparenza** | Bassa | Alta |
| **Backtesting** | ❌ Impossibile | ✅ Possibile |

---

## 📊 **CONVERSIONI CONSIGLIATE**

### **Fondi Azionari → ETF Equivalenti**

| Tipo Fondo | ETF Consigliato | Ticker | TER |
|------------|-----------------|--------|-----|
| Azionario Globale | iShares MSCI World | SWDA.MI | 0.20% |
| Azionario USA | Vanguard S&P 500 | VUSA.L | 0.07% |
| Azionario Europa | iShares Core STOXX Europe 600 | EXS1.DE | 0.20% |
| Azionario Italia | Lyxor FTSE MIB | MIBEX.MI | 0.35% |
| Azionario Emergenti | iShares MSCI Emerging Markets | EIMI.MI | 0.18% |

### **Fondi Obbligazionari → ETF Equivalenti**

| Tipo Fondo | ETF Consigliato | Ticker | TER |
|------------|-----------------|--------|-----|
| Obbligazionario Globale | iShares Core Global Aggregate Bond | AGGH.MI | 0.10% |
| Obbligazionario EUR | Vanguard EUR Eurozone Government Bond | VGEA.L | 0.12% |
| Corporate Bond | iShares EUR Corp Bond | IEAG.L | 0.20% |
| US Treasury | Vanguard US Government Bond | GOVT | 0.05% |

### **Fondi Bilanciati → ETF Mix**

**Esempio: Portafoglio 60% Azioni / 40% Obbligazioni**

```
60% SWDA.MI (MSCI World)
40% AGGH.MI (Global Aggregate Bond)
```

---

## 🔍 **COME TROVARE L'ETF GIUSTO**

### **1. Per Categoria Geografica:**

```
Globale     → SWDA.MI, VWCE.DE, CSPX.MI
USA         → SPY, QQQ, VOO, VTI
Europa      → EXS1.DE, IQQE.DE
Italia      → MIBEX.MI
Emergenti   → EIMI.MI, AEEM.MI, VWO
```

### **2. Per Settore:**

```
Tech        → QQQ, IUIT.MI
Healthcare  → HEAL.L
Energy      → XLE
Finance     → XLF
```

### **3. Per Tipo Asset:**

```
Obbligazioni → AGGH.MI, VGEA.L, BND
Commodities  → GLD (oro), SLV (argento), USO (petrolio)
Real Estate  → VNQ, IQQP.DE
```

---

## 💡 **COME USARE IN FINANALYZER**

### **Step 1: Vai su Screener**
```
🔍 Screener → Tab "📡 ETF"
```

### **Step 2: Seleziona Categoria**
```
Espandi: "🌍 Globali Azionari"
Clicca: [SWDA.MI]
```

### **Step 3: Vai su Portafoglio**
```
💼 Portafoglio → Vedi SWDA.MI aggiunto
```

### **Step 4: Aggiungi Altri ETF**
```
Torna su Screener
Espandi: "🏛️ Obbligazionari"
Clicca: [AGGH.MI]
```

### **Step 5: Ottimizza**
```
💼 Portafoglio → Imposta pesi
Clicca: "🎯 Ottimizza Markowitz"
```

---

## 📈 **PORTAFOGLI ESEMPIO CON ETF**

### **Portafoglio Conservativo (Basso Rischio)**
```
30% SWDA.MI  (Azionario Globale)
50% AGGH.MI  (Obbligazionario Globale)
10% GLD      (Oro)
10% Cash
```

### **Portafoglio Bilanciato (Medio Rischio)**
```
50% SWDA.MI  (Azionario Globale)
20% EIMI.MI  (Emergenti)
25% AGGH.MI  (Obbligazionario)
5% BTC-USD   (Crypto)
```

### **Portafoglio Aggressivo (Alto Rischio)**
```
40% SPY      (S&P 500)
30% QQQ      (Nasdaq Tech)
20% EIMI.MI  (Emergenti)
10% ARKK     (Innovation ETF)
```

### **Portafoglio Italia Focus**
```
40% MIBEX.MI (FTSE MIB)
30% EXS1.DE  (Europa)
20% SWDA.MI  (Globale)
10% AGGH.MI  (Bond)
```

---

## 🚀 **VANTAGGI PRATICI**

### **Con Fondi Comuni (ISIN):**
```
❌ Errore: "Impossibile caricare prezzi"
❌ No backtest
❌ No predizioni
❌ No grafici real-time
```

### **Con ETF (Ticker Yahoo):**
```
✅ Prezzi real-time
✅ Backtest 1/3/5/7 anni
✅ Predizioni Monte Carlo
✅ Grafici 6 mesi
✅ Ottimizzazione Markowitz
```

---

## 📚 **RISORSE UTILI**

- **JustETF**: [justetf.com](https://www.justetf.com/it/) - Compara ETF europei
- **ETF.com**: [etf.com](https://www.etf.com/) - Database ETF USA
- **Morningstar**: [morningstar.it](https://www.morningstar.it/) - Rating ETF

---

## ⚠️ **DISCLAIMER**

- Gli ETF sono strumenti finanziari con rischi
- Le performance passate non garantiscono risultati futuri
- Consulta un consulente finanziario prima di investire
- Questa guida è solo a scopo educativo

---

**Ora puoi costruire portafogli completi con ETF invece di fondi!** 🎉
