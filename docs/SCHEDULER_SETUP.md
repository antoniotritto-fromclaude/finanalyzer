# 📅 Macro Report Scheduler - Guida Setup

Sistema di generazione automatica report macro-finanziari con scheduling intelligente.

## 🎯 Caratteristiche

- ✅ **Generazione automatica** a orari programmati
- ✅ **Anticipo configurabile** (default: 1h 30min prima della pubblicazione)
- ✅ **Giorni personalizzabili** (es. solo Lun-Ven)
- ✅ **Pulizia automatica** dei report vecchi
- ✅ **Export multi-formato** (Telegram, WhatsApp, Email)
- ✅ **Logging completo** di tutte le operazioni

---

## ⚙️ Configurazione Base

### Orari Default

| Parametro | Valore | Descrizione |
|-----------|--------|-------------|
| **Orario Pubblicazione** | 08:15 | Quando vuoi ricevere il report |
| **Anticipo Generazione** | 90 minuti | Quanto tempo prima generarlo |
| **Orario Generazione** | 06:45 | Calcolato automaticamente |
| **Giorni Attivi** | Lun-Ven | Quando eseguire |

### Modificare Configurazione

Apri `/backend/schedulers/macro_scheduler.py` e modifica:

```python
REPORT_CONFIG = {
    "target_publish_time": "08:15",  # ← Cambia qui
    "generation_advance_minutes": 90,  # ← Cambia qui
    "active_days": [1, 2, 3, 4, 5],  # ← 1=Lun, 7=Dom
    ...
}
```

**Oppure** usa l'interfaccia web in **🌍 Macro Report** → **⚙️ Impostazioni Scheduler**

---

## 🚀 Metodi di Esecuzione

### 1️⃣ **Manuale (Test)**

Genera un report immediatamente:

```bash
cd /home/user/finanalyzer
python run_scheduler.py --once
```

Output:
```
▶️  Generazione singola report...
🔄 Avvio generazione report automatico...
✅ Report salvato: /home/user/finanalyzer/reports/macro/macro_report_20260413_0645.txt
✅ Completato!
```

---

### 2️⃣ **Interattivo (Foreground)**

Avvia lo scheduler e visualizza log in tempo reale:

```bash
python run_scheduler.py
```

Output:
```
============================================================
🚀 AVVIO MACRO REPORT SCHEDULER
============================================================
📅 Orario pubblicazione target: 08:15
⏰ Anticipo generazione: 90 minuti
🕐 Orario generazione: 06:45
📆 Giorni attivi: [1, 2, 3, 4, 5] (Lun=1, Dom=7)
📁 Output directory: /home/user/finanalyzer/reports/macro
⏭️  Prossima generazione: 14/04/2026 06:45:00
============================================================
🔄 Scheduler in esecuzione (modalità blocking)...
   Premi CTRL+C per interrompere
```

Lo scheduler rimane attivo e genera report automaticamente ogni giorno all'orario configurato.

---

### 3️⃣ **Background (Daemon)**

Avvia come servizio in background:

```bash
nohup python run_scheduler.py --daemon > scheduler.log 2>&1 &
```

Controlla se è attivo:

```bash
ps aux | grep run_scheduler
```

Ferma lo scheduler:

```bash
pkill -f run_scheduler.py
```

---

### 4️⃣ **Cron Job (Consigliato per Produzione)**

Configura cron per eseguire automaticamente:

```bash
crontab -e
```

Aggiungi questa riga (esegue ogni giorno alle 06:45):

```cron
45 6 * * 1-5 cd /home/user/finanalyzer && /usr/bin/python3 run_scheduler.py --once >> /home/user/finanalyzer/scheduler.log 2>&1
```

Spiegazione:
```
45       → Minuto (06:45)
6        → Ora (06:45)
*        → Ogni giorno del mese
*        → Ogni mese
1-5      → Lun-Ven (1=Lun, 5=Ven)
```

**Esempi Cron:**

| Cron | Descrizione |
|------|-------------|
| `45 6 * * 1-5` | Lun-Ven alle 06:45 |
| `0 7 * * *` | Ogni giorno alle 07:00 |
| `30 5 * * 1,3,5` | Lun, Mer, Ven alle 05:30 |
| `0 8,14,20 * * *` | Ogni giorno alle 08:00, 14:00, 20:00 |

Verifica cron attivi:

```bash
crontab -l
```

---

### 5️⃣ **Systemd Service (Linux)**

Crea servizio systemd per auto-start al boot:

**1. Crea file service:**

```bash
sudo nano /etc/systemd/system/macro-scheduler.service
```

**2. Inserisci configurazione:**

```ini
[Unit]
Description=FinAnalyzer Macro Report Scheduler
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/user/finanalyzer
ExecStart=/usr/bin/python3 /home/user/finanalyzer/run_scheduler.py --daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**3. Attiva servizio:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable macro-scheduler.service
sudo systemctl start macro-scheduler.service
```

**4. Controlla stato:**

```bash
sudo systemctl status macro-scheduler.service
```

**5. Visualizza log:**

```bash
sudo journalctl -u macro-scheduler.service -f
```

---

## 📁 Directory e File

### Struttura File

```
finanalyzer/
├── backend/
│   └── schedulers/
│       └── macro_scheduler.py     ← Logica scheduler
├── reports/
│   └── macro/
│       ├── macro_report_20260413_0645.txt
│       ├── macro_report_20260414_0645.txt
│       └── ...                    ← Report salvati (max 30)
├── run_scheduler.py               ← Launcher
├── scheduler.log                  ← Log operazioni
└── macro_scheduler.log            ← Log dettagliato
```

### Pulizia Automatica

Il sistema mantiene automaticamente solo gli ultimi **30 report**, eliminando i più vecchi.

Modifica il numero:

```python
"keep_last_n_reports": 30,  # ← Cambia qui
```

---

## 📱 Export e Notifiche

### Export Telegram

```python
from backend.schedulers.macro_scheduler import export_for_messaging

telegram_report = export_for_messaging("telegram")
# Invia via bot Telegram
```

### Export WhatsApp

```python
whatsapp_report = export_for_messaging("whatsapp")
# Report accorciato per limiti WhatsApp
```

### Export Email

```python
email_html = export_for_messaging("email")
# Formato HTML per email
```

---

## 🔧 Troubleshooting

### Problema: Report non generati

**Controlla:**
1. Scheduler è attivo? `ps aux | grep run_scheduler`
2. Cron è configurato? `crontab -l`
3. Permessi directory: `ls -la /home/user/finanalyzer/reports/`
4. Log errori: `tail -50 scheduler.log`

**Soluzione:**
```bash
# Test manuale
python run_scheduler.py --once

# Controlla log
tail -f macro_scheduler.log
```

---

### Problema: Orario sbagliato

**Verifica configurazione:**
```bash
python run_scheduler.py --info
```

**Modifica orario:**
Apri `/backend/schedulers/macro_scheduler.py` e cambia:
```python
"target_publish_time": "08:15",  # ← Il tuo orario desiderato
```

**Ricalcola automaticamente:**
Il sistema sottrae automaticamente 90 minuti (1h 30min).

---

### Problema: Report vuoti o errori

**Controlla connessione internet:**
```bash
ping finance.yahoo.com
```

**Test manuale con log verboso:**
```bash
python run_scheduler.py --once --verbose
```

**Verifica dipendenze:**
```bash
pip install -r requirements.txt
```

---

## 📊 Monitoraggio

### Visualizza Info Scheduler

```bash
python run_scheduler.py --info
```

### Controlla Ultimo Report

```bash
ls -lth /home/user/finanalyzer/reports/macro/ | head -5
```

### Visualizza Report

```bash
cat /home/user/finanalyzer/reports/macro/macro_report_*.txt | head -50
```

### Log Live

```bash
tail -f macro_scheduler.log
```

---

## 🎯 Best Practices

### ✅ Raccomandazioni

1. **Usa Cron per produzione** - Più affidabile di daemon custom
2. **Monitora i log** - Controlla `scheduler.log` periodicamente
3. **Test prima di deploy** - Esegui `--once` per verificare
4. **Backup configurazione** - Salva `macro_scheduler.py`
5. **Alert su fallimento** - Configura notifiche se il report non viene generato

### ⚠️ Attenzioni

1. **Orari di mercato** - Genera report quando i mercati sono chiusi (più dati completi)
2. **Rate limiting** - Yahoo Finance ha limiti, non esagerare con richieste
3. **Timezone** - Assicurati che il server sia in timezone corretto
4. **Risorse** - La generazione richiede ~30-60 secondi e banda internet

---

## 📈 Esempi Configurazione

### Esempio 1: Report Mattutino Pre-Mercato USA

```python
REPORT_CONFIG = {
    "target_publish_time": "14:30",  # 14:30 = apertura USA (ore italiane)
    "generation_advance_minutes": 90,  # Genera alle 13:00
    "active_days": [1, 2, 3, 4, 5],  # Lun-Ven
}
```

```cron
# Cron: ogni giorno feriale alle 13:00
0 13 * * 1-5 cd /home/user/finanalyzer && python3 run_scheduler.py --once
```

---

### Esempio 2: Report Serale Post-Mercato

```python
REPORT_CONFIG = {
    "target_publish_time": "23:00",  # Fine giornata
    "generation_advance_minutes": 30,  # Genera alle 22:30
    "active_days": [1, 2, 3, 4, 5],
}
```

```cron
# Cron: ogni giorno feriale alle 22:30
30 22 * * 1-5 cd /home/user/finanalyzer && python3 run_scheduler.py --once
```

---

### Esempio 3: Report Multipli Giornalieri

```python
# Mattino
45 6 * * 1-5 cd /home/user/finanalyzer && python3 run_scheduler.py --once

# Pomeriggio
0 14 * * 1-5 cd /home/user/finanalyzer && python3 run_scheduler.py --once

# Sera
30 22 * * 1-5 cd /home/user/finanalyzer && python3 run_scheduler.py --once
```

---

## 🆘 Supporto

Per problemi o domande:
1. Controlla i log: `macro_scheduler.log`
2. Esegui test: `python run_scheduler.py --once --verbose`
3. Verifica configurazione: `python run_scheduler.py --info`
4. GitHub Issues: https://github.com/antoniotritto-fromclaude/finanalyzer/issues

---

**📝 Ultimo aggiornamento:** 13/04/2026  
**🤖 Powered by:** FinAnalyzer Pro
