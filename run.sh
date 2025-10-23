#!/bin/bash

# FinAnalyzer Startup Script

echo "🚀 Avvio FinAnalyzer..."
echo ""

# Controlla se le dipendenze sono installate
if ! command -v streamlit &> /dev/null; then
    echo "⚠️  Streamlit non trovato. Installazione dipendenze..."
    pip install -r requirements.txt
fi

echo "📊 Avvio interfaccia Streamlit..."
echo ""
echo "L'applicazione sarà disponibile su: http://localhost:8501"
echo ""
echo "Per interrompere, premi Ctrl+C"
echo ""

streamlit run frontend/app.py
