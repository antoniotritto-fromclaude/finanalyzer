# FinAnalyzer - Piattaforma di Analisi Finanziaria

Una piattaforma completa per l'analisi di strumenti finanziari italiani e internazionali.

## Caratteristiche

- **Ricerca Multi-Fonte**: Integrazione con TradingView, Morningstar, Investing.com, Yahoo Finance, JustETF, e Certificati e Derivati
- **Strumenti Supportati**: Azioni, Obbligazioni, Fondi d'Investimento, ETF, Certificati, Commodities
- **Ottimizzazione Portfolio**: Implementazione della teoria di Markowitz con frontiera efficiente
- **Analisi Volatilità**: Calcolo e visualizzazione della volatilità di portafoglio
- **Backtesting**: Test storici a 1, 3, 5, 7 anni
- **Predizioni**: Modello predittivo a 6 mesi con scenari normale, peggiore, migliore

## Tecnologie

- **Backend**: Python 3.9+ con FastAPI
- **Data Analysis**: Pandas, NumPy, SciPy
- **Portfolio Optimization**: PyPortfolioOpt
- **Machine Learning**: Scikit-learn
- **Data Sources**: yfinance, requests, BeautifulSoup4
- **Frontend**: Streamlit
- **Visualizzazioni**: Plotly, Matplotlib

## Struttura del Progetto

```
finanalyzer/
├── backend/
│   ├── data_collectors/    # Moduli per raccolta dati
│   ├── analyzers/          # Moduli di analisi
│   ├── models/             # Modelli predittivi
│   └── api/                # API REST
├── frontend/               # Interfaccia Streamlit
├── tests/                  # Test unitari
└── requirements.txt        # Dipendenze
```

## Installazione

```bash
pip install -r requirements.txt
```

## Uso

```bash
# Avviare il backend
python -m uvicorn backend.api.main:app --reload

# Avviare il frontend
streamlit run frontend/app.py
```

## Licenza

MIT
