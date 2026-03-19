# 🔍 ANALISI COMPLETA DEI PROBLEMI - FinAnalyzer

## STATO ATTUALE

### ✅ **FUNZIONANTI**
- **Analisi Titolo**: Input manuale funziona, usa Yahoo Finance
- **Menu Sidebar**: Moderno con freccia (appena implementato)
- **Tabelle**: Native Streamlit (nessun HTML escape)

### ❌ **PROBLEMI IDENTIFICATI**

---

## 1. **FONTI DATI**

**Problema**: Manca FINVIZ nella lista
**File**: `frontend/app.py` linea 71-78
**Fix**: Aggiungere `("📊", "FINVIZ", "#22c55e")`

---

## 2. **DASHBOARD**

### 2.1 Indici con dati hardcoded
**File**: `frontend/views/dashboard.py` linea 11-18
**Problema**:
```python
MARKET_OVERVIEW = [
    {"name":"S&P 500","symbol":"^GSPC","price":"5,456.30","change":+0.38,...}
]
```
→ Dati statici, non real-time!

**Fix**: Usare `yfinance` per fetch real-time

### 2.2 Grafici 6 mesi mancanti
**File**: `frontend/views/dashboard.py` linea 71-91
**Problema**: Mostra stagionalità S&P500 invece di grafici asset
**Asset richiesti**:
- EURO STOXX 600 (^STOXX)
- S&P 500 (^GSPC)
- Dow Jones (^DJI)
- Russell 1000 (^RUI)
- Petrolio (CL=F)
- Gas Naturale (NG=F)
- Bitcoin (BTC-USD)
- Gold (GC=F)
- Silver (SI=F)
- Cacao (CC=F)
- Caffè (KC=F)

**Fix**: Creare grid di grafici 6 mesi con yfinance

---

## 3. **SCREENER**

**Problema**: Non chiaro come accedere a diverse tipologie
**File**: `frontend/views/screener.py` linea 11-35
**Fix**: Aggiungere selezione tipo asset con tabs o radio

---

## 4. **ANALISI TITOLO**

**Problema**: Usa SOLO Yahoo Finance
**File**: `frontend/views/fundamentals.py` linea 13-24
**Fonti da aggiungere**:
- ✅ Yahoo Finance (già presente)
- ⚠️ Morningstar (tramite ms_collector)
- ⚠️ FINVIZ (web scraping o API)
- ⚠️ Possibilità link custom

**Fix**: Aggiungere sezioni con dati da altre fonti

---

## 5. **PORTAFOGLIO**

**File**: `frontend/views/portfolio.py`

### Problema 1: Input non funziona?
**Linea 47-56**: Codice sembra corretto
```python
if st.button("➕ Aggiungi", use_container_width=True):
    sym = new_sym.strip().upper()
    if sym and sym not in st.session_state["pf_symbols"]:
        st.session_state["pf_symbols"].append(sym)
        st.rerun()
```

**Possibili cause**:
- Bug nel `st.rerun()` → provare `st.experimental_rerun()`
- Input non cleared dopo add → aggiungere `key` dinamico
- Validazione Yahoo Finance fallisce silenziosamente

### Problema 2: Portafogli predefiniti
**Linea 59-70**: Utente NON vuole preset
**Fix**: Rimuovere o nascondere in expander

---

## 6. **BACKTEST**

**File**: `frontend/views/backtest.py` linea 45-51
**Problema**: Dipende da `st.session_state["pf_symbols"]`
```python
symbols = st.session_state.get("pf_symbols", [])
if not symbols:
    st.warning("⚠️ Prima aggiungi titoli nella sezione **Portafoglio**.")
    return
```

**Fix**: Se Portafoglio funziona, anche Backtest funzionerà

---

## 7. **PREDIZIONI**

**File**: `frontend/views/predictions.py` linea 44-49
**Problema**: Stesso del Backtest
```python
symbols = st.session_state.get("pf_symbols", [])
if not symbols:
    st.warning("⚠️ Aggiungi titoli nella sezione **Portafoglio** prima.")
    return
```

**Fix**: Se Portafoglio funziona, anche Predizioni funzioneranno

---

## 🎯 **PIANO DI AZIONE**

### PRIORITY 1 (Critici)
1. ✅ Dashboard - Fix indici real-time
2. ✅ Dashboard - Grafici 6 mesi asset
3. ✅ Portafoglio - Fix input aggiunta titoli
4. ✅ Portafoglio - Rimuovi preset (o rendi opzionale)

### PRIORITY 2 (Importanti)
5. ✅ Screener - Selezione chiara tipo asset
6. ✅ Analisi Titolo - Aggiungere fonti extra
7. ✅ Fonti Dati - Aggiungere FINVIZ

### PRIORITY 3 (Automatici dopo P1)
8. ✅ Backtest - Funzionerà se Portafoglio OK
9. ✅ Predizioni - Funzionerà se Portafoglio OK

---

## 📋 **CHECKLIST**

- [ ] Dashboard indici real-time
- [ ] Dashboard grafici 6 mesi
- [ ] Portafoglio input fix
- [ ] Portafoglio preset rimossi
- [ ] Screener selezione asset
- [ ] Analisi Titolo multi-fonte
- [ ] FINVIZ aggiunto
- [ ] Backtest test
- [ ] Predizioni test
- [ ] Test completo end-to-end
