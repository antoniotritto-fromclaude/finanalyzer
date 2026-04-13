# 🧪 TEST MACRO REPORT SCHEDULER

Guida rapida per testare il sistema di generazione automatica report.

---

## ⚡ QUICK START - TEST IMMEDIATO

### 1️⃣ **Test Generazione Singola** (Consigliato per iniziare)

```bash
cd /home/user/finanalyzer
python run_scheduler.py --once
```

**Cosa fa:**
- ✅ Genera un report immediatamente
- ✅ Salva in `/home/user/finanalyzer/reports/macro/`
- ✅ Mostra output completo
- ✅ Esce al termine (non rimane attivo)

**Output Atteso:**
```
▶️  Generazione singola report...
============================================================
🤖 MACRO REPORT SCHEDULER - 13/04/2026 10:30:15
============================================================
🔄 Avvio generazione report automatico...
📊 Scaricamento 52 asset...
💶 Conversione prezzi in EUR...
✅ Dataset completo: 5 giorni, 52 asset (prezzi in EUR)
✅ Report generato con successo
✅ Report salvato: /home/user/finanalyzer/reports/macro/macro_report_20260413_1030.txt
📊 Report disponibile: /home/user/finanalyzer/reports/macro/macro_report_20260413_1030.txt
⏰ Pronto per pubblicazione alle 08:15
============================================================
✅ Completato!
```

---

### 2️⃣ **Visualizza Report Generato**

```bash
cat /home/user/finanalyzer/reports/macro/macro_report_*.txt | head -100
```

**Oppure apri il file direttamente:**
```bash
ls -lth /home/user/finanalyzer/reports/macro/
```

---

### 3️⃣ **Visualizza Configurazione**

```bash
python run_scheduler.py --info
```

**Output Atteso:**
```
======================================================================
📊 MACRO REPORT SCHEDULER - CONFIGURAZIONE
======================================================================

🎯 Orario Pubblicazione Target:  08:15
⏰ Anticipo Generazione:         90 minuti
🕐 Orario Generazione Calcolato: 06:45
📅 Prossima Esecuzione:          17/04/2026 06:45:00  ← Prossimo Giovedì
📆 Giorni Attivi:                [1, 4] (1=Lun, 7=Dom)
📁 Directory Output:             /home/user/finanalyzer/reports/macro
📊 Report Salvati:               1/30

======================================================================
```

**Nota:** La prossima esecuzione sarà **Lunedì o Giovedì alle 06:45**

---

### 4️⃣ **Test con Output Dettagliato** (Debug)

```bash
python run_scheduler.py --once --verbose
```

**Cosa fa:**
- Mostra TUTTI i passaggi (debug level)
- Utile per trovare errori
- Mostra ogni asset scaricato
- Mostra calcoli e conversioni

---

### 5️⃣ **Test Scheduler Interattivo** (Attesa Automatica)

```bash
python run_scheduler.py
```

**Cosa fa:**
- ✅ Avvia lo scheduler
- ✅ Aspetta fino al prossimo Lunedì o Giovedì alle 06:45
- ✅ Genera automaticamente il report
- ✅ Rimane attivo per esecuzioni future

**Per uscire:** Premi `CTRL+C`

**Output Atteso:**
```
============================================================
🚀 AVVIO MACRO REPORT SCHEDULER
============================================================
📅 Orario pubblicazione target: 08:15
⏰ Anticipo generazione: 90 minuti
🕐 Orario generazione: 06:45
📆 Giorni attivi: [1, 4] (Lun=1, Dom=7)
📁 Output directory: /home/user/finanalyzer/reports/macro
⏭️  Prossima generazione: 17/04/2026 06:45:00
============================================================
🔄 Scheduler in esecuzione (modalità blocking)...
   Premi CTRL+C per interrompere
```

---

## 📅 **CONFIGURAZIONE GIORNI: LUNEDÌ E GIOVEDÌ**

### **Configurazione Attuale:**

```python
"active_days": [1, 4]  # 1 = Lunedì, 4 = Giovedì
```

**Calendario Esecuzioni:**
```
Lun  Mar  Mer  Gio  Ven  Sab  Dom
✅   ❌   ❌   ✅   ❌   ❌   ❌
```

**Orario:**
- 🕐 Generazione: **06:45** (Lunedì e Giovedì)
- 🎯 Pubblicazione: **08:15** (1h 30min dopo)

---

## 🔧 **SETUP CRON PER AUTOMAZIONE**

### **Configurazione Cron Consigliata:**

```bash
crontab -e
```

**Aggiungi questa riga:**
```cron
45 6 * * 1,4 cd /home/user/finanalyzer && /usr/bin/python3 run_scheduler.py --once >> /home/user/finanalyzer/scheduler.log 2>&1
```

**Spiegazione:**
```
45    → Minuto 45
6     → Ora 6 (06:45)
*     → Ogni giorno del mese
*     → Ogni mese
1,4   → Lunedì (1) e Giovedì (4)
```

**Verifica cron attivo:**
```bash
crontab -l
```

---

## 📊 **LINK E COMANDI RAPIDI**

### **🔗 Link Diretti:**

| Azione | Comando |
|--------|---------|
| **Test Immediato** | `cd /home/user/finanalyzer && python run_scheduler.py --once` |
| **Vedi Config** | `cd /home/user/finanalyzer && python run_scheduler.py --info` |
| **Vedi Report** | `cat /home/user/finanalyzer/reports/macro/macro_report_*.txt` |
| **Vedi Log** | `tail -f /home/user/finanalyzer/macro_scheduler.log` |
| **Setup Cron** | `crontab -e` |

---

### **📱 Test Export Formati:**

**Telegram:**
```bash
cd /home/user/finanalyzer
python -c "from backend.schedulers.macro_scheduler import get_latest_report, export_for_messaging; print(export_for_messaging('telegram'))"
```

**WhatsApp:**
```bash
python -c "from backend.schedulers.macro_scheduler import export_for_messaging; print(export_for_messaging('whatsapp'))"
```

---

## ✅ **CHECKLIST TEST COMPLETO**

### **Step 1: Test Base**
```bash
# 1. Vai nella directory
cd /home/user/finanalyzer

# 2. Test generazione
python run_scheduler.py --once

# 3. Verifica file creato
ls -lth reports/macro/

# 4. Visualizza report
cat reports/macro/macro_report_*.txt | head -50
```

**✅ Successo se:** Vedi il report con tutti i mercati globali

---

### **Step 2: Verifica Configurazione**
```bash
# Controlla orari e giorni
python run_scheduler.py --info
```

**✅ Successo se:** 
- Giorni attivi: [1, 4] (Lunedì e Giovedì)
- Orario generazione: 06:45
- Prossima esecuzione: Lunedì o Giovedì

---

### **Step 3: Test Debug**
```bash
# Test con output verboso
python run_scheduler.py --once --verbose
```

**✅ Successo se:** Nessun errore, tutti gli asset scaricati

---

### **Step 4: Setup Automazione**
```bash
# Configura cron
crontab -e

# Aggiungi:
# 45 6 * * 1,4 cd /home/user/finanalyzer && python3 run_scheduler.py --once >> scheduler.log 2>&1

# Verifica
crontab -l
```

**✅ Successo se:** Vedi la riga nel crontab

---

### **Step 5: Attendi Prima Esecuzione Automatica**

**Aspetta fino al prossimo Lunedì o Giovedì alle 06:45**

**Poi controlla:**
```bash
# Vedi se è stato generato
ls -lth reports/macro/

# Controlla log
cat scheduler.log
```

**✅ Successo se:** Nuovo report generato automaticamente

---

## 🆘 **TROUBLESHOOTING**

### **Problema: Comando non trovato**
```bash
# Soluzione: Usa percorso assoluto Python
which python3
# Output: /usr/bin/python3

# Usa questo nel comando:
/usr/bin/python3 run_scheduler.py --once
```

---

### **Problema: Permessi negati**
```bash
# Soluzione: Rendi eseguibile
chmod +x run_scheduler.py

# Oppure usa sempre:
python run_scheduler.py --once
```

---

### **Problema: Report vuoto o errori**
```bash
# Soluzione: Test con verbose
python run_scheduler.py --once --verbose

# Controlla connessione internet
ping finance.yahoo.com

# Verifica dipendenze
pip install -r requirements.txt
```

---

### **Problema: Cron non esegue**
```bash
# Verifica log di sistema
sudo tail -f /var/log/syslog | grep CRON

# Test manuale cron command
cd /home/user/finanalyzer && /usr/bin/python3 run_scheduler.py --once

# Verifica permissions
ls -la run_scheduler.py
```

---

## 🎯 **CALENDARIO ESECUZIONI APRILE 2026**

Basato sulla configurazione **Lunedì e Giovedì alle 06:45**:

```
APRILE 2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Lun  Mar  Mer  Gio  Ven  Sab  Dom
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           1    2    3    4    5
 6    7    8    9   10   11   12
13✅ 14   15   16✅ 17   18   19
20✅ 21   22   23✅ 24   25   26
27✅ 28   29   30✅
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ = Generazione automatica alle 06:45

Prossime esecuzioni:
• Lun 20 Aprile 06:45
• Gio 23 Aprile 06:45
• Lun 27 Aprile 06:45
• Gio 30 Aprile 06:45
```

---

## 📞 **SUPPORTO RAPIDO**

**Comando All-in-One per Debug:**
```bash
cd /home/user/finanalyzer && \
echo "=== CONFIG ===" && \
python run_scheduler.py --info && \
echo -e "\n=== TEST ===" && \
python run_scheduler.py --once && \
echo -e "\n=== REPORT ===" && \
ls -lth reports/macro/ | head -3
```

---

**📝 Note Finali:**
- ⏰ Report generato: **Lunedì e Giovedì alle 06:45**
- 🎯 Pronto per pubblicazione: **08:15** (1h 30min dopo)
- 📁 Salvataggio: `/home/user/finanalyzer/reports/macro/`
- 🗑️ Pulizia automatica: conserva ultimi 30 report
- 📊 Copertura: 50+ mercati globali, 8 macro-aree

**🚀 Inizia con:** `python run_scheduler.py --once`
