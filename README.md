# FinAnalyzer Pro 📊

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**Piattaforma professionale di analisi finanziaria** con design moderno, ottimizzazione di portafoglio (Markowitz), backtest storici e predizioni Monte Carlo.

🌐 **[Demo Live](https://finanalyzer.streamlit.app)** | 📖 **[Guida Uso](USAGE.md)** | 🚀 **[Deploy Guide](DEPLOY.md)**

---

## ✨ Caratteristiche

### 📊 Dashboard Mercati
- Overview mercati globali (S&P 500, FTSE MIB, DAX, Nasdaq)
- Stagionalità mensile e performance settoriale
- Top movers Borsa Italiana
- Indicatori macro (inflazione, tassi, VIX)

### 🔭 Quantum Screener
- **ETF** da JustETF (filtri TER, replica, distribuzione)
- **Fondi** da Morningstar e Quantalys (rating ⭐)
- **Obbligazioni** italiane e europee (BTP, Bund)
- **Commodities** con prezzi live

### 📋 Fundamentals
- Analisi singolo titolo con metriche P/E, EPS, Beta
- Grafici candlestick e storici multi-anno
- Statistiche rendimento e volatilità

### 💼 Portfolio Builder
- Costruzione portafoglio personalizzato
- **Ottimizzazione Markowitz** (max Sharpe, min volatilità)
- **Frontiera efficiente** interattiva
- Matrice di correlazione

### ⏮️ Backtest Storico
- Test su 1, 3, 5, 7 anni
- 9 metriche: Sharpe, Sortino, Calmar, Max Drawdown
- Confronto con S&P 500
- Supporto ribilanciamento

### 🔮 Predizioni Future
- **Simulazioni Monte Carlo** (1K-25K)
- **3 scenari** a 6 mesi (normale, peggiore, migliore)
- Value at Risk (VaR 95%)
- Probabilità di perdita

---

## 🎨 Design

Design professionale ispirato a TradingView e dashboard finanziarie moderne:
- Sfondo blu gradiente
- Card bianche con angoli arrotondati
- Badge colorati per sezioni
- Grafici interattivi Plotly
- Tipografia Inter

---

## 🌐 Fonti Dati

| Fonte | Utilizzo |
|-------|----------|
| 📈 **Yahoo Finance** | Prezzi storici, dati real-time |
| 🌐 **Morningstar IT** | Fondi italiani, obbligazioni |
| 📡 **JustETF** | Database ETF europei |
| 📊 **Quantalys** | Migliori fondi per categoria |
| 💹 **Investing.com** | Liste commodities |

---

## 🚀 Quick Start

### Installazione

```bash
# Clone
git clone https://github.com/TUO_USERNAME/finanalyzer.git
cd finanalyzer

# Setup (Mac/Linux)
./setup_mac.sh

# Oppure manuale
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Avvio Locale

```bash
streamlit run frontend/app.py
```

Apri: http://localhost:8501

### Deploy Online (GRATIS)

Leggi la guida completa: **[DEPLOY.md](DEPLOY.md)**

Streamlit Cloud deploy in 3 minuti:
1. Pusha su GitHub
2. Vai su https://share.streamlit.io
3. Connetti il repo e clicca "Deploy"

---

## 📖 Documentazione

- **[START_HERE.md](START_HERE.md)** - Guida rapida per iniziare
- **[USAGE.md](USAGE.md)** - Guida completa con esempi
- **[DEPLOY.md](DEPLOY.md)** - Come deployare online
- **[INSTALL_MAC.md](INSTALL_MAC.md)** - Installazione macOS
- **[FIX_README.md](FIX_README.md)** - Risoluzione problemi

---

## 🛠️ Tecnologie

- **Frontend**: Streamlit 1.30+
- **Data Analysis**: Pandas, NumPy, SciPy
- **Financial**: yfinance, PyPortfolioOpt (opzionale)
- **ML**: Scikit-learn (Monte Carlo)
- **Charts**: Plotly, Matplotlib
- **Backend**: FastAPI (opzionale per API REST)

---

## 📊 Screenshots

### Dashboard
![Dashboard](docs/screenshots/dashboard.png)

### Portfolio Optimizer
![Markowitz](docs/screenshots/markowitz.png)

### Predictions
![Predictions](docs/screenshots/predictions.png)

---

## 🤝 Contributi

Contributi benvenuti!

1. Fork del progetto
2. Crea un branch (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

---

## ⚠️ Disclaimer

**Questo software è fornito a scopo educativo e informativo.**

- ❌ NON costituisce consulenza finanziaria
- ❌ I rendimenti passati NON garantiscono risultati futuri
- ❌ Le predizioni sono simulazioni statistiche
- ✅ Consulta sempre un consulente finanziario professionista
- ✅ Investi solo capitale che puoi permetterti di perdere

---

## 📄 Licenza

MIT License - vedi [LICENSE](LICENSE)

---

## 💬 Supporto

- 🐛 Bug reports: [GitHub Issues](https://github.com/TUO_USERNAME/finanalyzer/issues)
- 💡 Feature requests: [GitHub Discussions](https://github.com/TUO_USERNAME/finanalyzer/discussions)
- 📧 Email: tuo@email.com

---

## 🌟 Star History

Se questo progetto ti è utile, lascia una ⭐ su GitHub!

---

**Made with ❤️ in Italy 🇮🇹**

**Powered by Claude Code 🤖**

---

## 📈 Roadmap

- [ ] Integrazione Alpha Vantage API
- [ ] Export report PDF
- [ ] Alert email/telegram
- [ ] Multi-currency support
- [ ] Dark mode
- [ ] Mobile app
- [ ] Paper trading simulator
- [ ] Social features (condivisione portfolio)

---

**Happy Trading! 📊💰**
