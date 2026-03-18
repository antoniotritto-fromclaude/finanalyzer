# 🚀 Deploy FinAnalyzer su Streamlit Cloud

## Opzione 1: Streamlit Cloud (Consigliato - GRATIS)

### Prerequisiti
- Account GitHub (gratuito)
- Il codice deve essere su un repository GitHub pubblico o privato

### Passaggi

1. **Pusha il codice su GitHub**
   ```bash
   # Se non l'hai già fatto
   git remote add origin https://github.com/TUO_USERNAME/finanalyzer.git
   git push -u origin main
   ```

2. **Vai su Streamlit Cloud**
   - Apri: https://share.streamlit.io/
   - Clicca "Sign up" con il tuo account GitHub
   - Autorizza Streamlit ad accedere ai tuoi repository

3. **Deploy l'app**
   - Clicca "New app"
   - Seleziona:
     - Repository: `TUO_USERNAME/finanalyzer`
     - Branch: `main` (o il branch che hai pushato)
     - Main file path: `frontend/app.py`
   - Clicca "Deploy!"

4. **Attendi 5-10 minuti**
   - Streamlit installerà tutte le dipendenze
   - L'app sarà disponibile su: `https://TUO_USERNAME-finanalyzer-frontend-app-XXXXX.streamlit.app`

5. **Condividi!**
   - L'URL è pubblico e condivisibile
   - Puoi personalizzarlo nelle impostazioni

---

## Opzione 2: Render (Alternativa)

### Deploy su Render.com (anche gratis)

1. **Crea account su Render**
   - Vai su: https://render.com/
   - Sign up con GitHub

2. **New Web Service**
   - Collega il tuo repository GitHub
   - Configura:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `streamlit run frontend/app.py --server.port=$PORT --server.address=0.0.0.0`
     - **Instance Type**: Free

3. **Deploy automatico**
   - Ogni push su GitHub trigghera un nuovo deploy

---

## Opzione 3: Railway (Altra alternativa)

1. **Vai su Railway.app**
   - https://railway.app/
   - Login con GitHub

2. **New Project → Deploy from GitHub**
   - Seleziona il repository `finanalyzer`

3. **Configura**
   - Railway rileva automaticamente Streamlit
   - Aggiungi variabile d'ambiente: `PORT=8501`

4. **Deploy**
   - Automatico ad ogni push

---

## Troubleshooting

### Errore: "ModuleNotFoundError"
- Verifica che `requirements.txt` sia presente nella root
- Controlla che tutte le dipendenze siano listate

### Errore: "Port già in uso"
- Streamlit Cloud gestisce automaticamente la porta
- Localmente usa: `streamlit run frontend/app.py --server.port 8502`

### L'app si riavvia continuamente
- Controlla i log nella dashboard Streamlit Cloud
- Probabilmente manca una dipendenza o c'è un errore di import

### Dati non si caricano (HTTP 403)
- Normale per Yahoo Finance in alcuni datacenter
- Prova a riavviare l'app (Reboot nel menu)
- Se persiste, considera un server proxy o API key dedicata

---

## 🎯 URL della tua app

Una volta deployato, l'URL sarà tipo:

```
https://finanalyzer.streamlit.app
```

o

```
https://TUO-USERNAME-finanalyzer-frontend-app-ABC123.streamlit.app
```

Puoi personalizzarlo nelle Settings su Streamlit Cloud!

---

## 📊 Monitoraggio

### Streamlit Cloud Dashboard
- Vedi logs in tempo reale
- Statistiche di utilizzo
- Riavvia l'app se necessario

### Resource Limits (Free Tier)
- **CPU**: 1 CPU
- **RAM**: 1 GB
- **Storage**: 1 GB
- **Bandwidth**: Illimitato
- **Uptime**: 24/7 (ma l'app va in sleep dopo 7 giorni di inattività)

---

## 🔒 Sicurezza

### Secrets Management
Se hai API keys da aggiungere in futuro:

1. Vai su Streamlit Cloud Dashboard
2. App settings → Secrets
3. Aggiungi le tue keys in formato TOML:
   ```toml
   ALPHA_VANTAGE_KEY = "your_key"
   ```
4. Accedi nel codice con:
   ```python
   import streamlit as st
   api_key = st.secrets["ALPHA_VANTAGE_KEY"]
   ```

---

## ✅ Checklist Deploy

- [ ] Codice pushato su GitHub
- [ ] `requirements.txt` aggiornato
- [ ] `.streamlit/config.toml` presente
- [ ] Account Streamlit Cloud creato
- [ ] App deployata
- [ ] URL testato e funzionante
- [ ] Condiviso con gli amici! 🎉

---

**🎉 Done! La tua app è online!**

Condividi l'URL e inizia ad analizzare i mercati finanziari! 📊💰
