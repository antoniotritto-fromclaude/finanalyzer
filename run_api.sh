#!/bin/bash

# FinAnalyzer API Startup Script

echo "🚀 Avvio FinAnalyzer API..."
echo ""

# Controlla se le dipendenze sono installate
if ! command -v uvicorn &> /dev/null; then
    echo "⚠️  Uvicorn non trovato. Installazione dipendenze..."
    pip install -r requirements.txt
fi

echo "🔧 Avvio API Backend..."
echo ""
echo "L'API sarà disponibile su: http://localhost:8000"
echo "Documentazione API: http://localhost:8000/docs"
echo ""
echo "Per interrompere, premi Ctrl+C"
echo ""

python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
