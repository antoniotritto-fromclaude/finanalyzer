#!/bin/bash

# 🍎 Script di Setup Automatico per macOS
# FinAnalyzer Installation

echo "🚀 FinAnalyzer - Setup per macOS"
echo "=================================="
echo ""

# Colori per output
GREEN='\033[0.32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funzione per stampare messaggi colorati
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# 1. Verifica Python
echo "1️⃣  Verifica Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python trovato: $PYTHON_VERSION"
else
    print_error "Python 3 non trovato!"
    print_info "Installalo con: brew install python"
    exit 1
fi

# 2. Verifica/Crea Virtual Environment
echo ""
echo "2️⃣  Setup Virtual Environment..."
if [ -d "venv" ]; then
    print_info "Virtual environment già esistente"
else
    print_info "Creazione virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment creato"
fi

# 3. Attiva Virtual Environment
echo ""
echo "3️⃣  Attivazione Virtual Environment..."
source venv/bin/activate
print_success "Virtual environment attivo"

# 4. Aggiorna pip
echo ""
echo "4️⃣  Aggiornamento pip..."
pip install --upgrade pip --quiet
print_success "pip aggiornato"

# 5. Installa dipendenze base
echo ""
echo "5️⃣  Installazione dipendenze base..."
print_info "Questo potrebbe richiedere qualche minuto..."

pip install --quiet pandas numpy scipy 2>&1 | grep -v "Requirement already satisfied" || true
print_success "Pandas, NumPy, SciPy installati"

# 6. Installa yfinance e dipendenze
echo ""
echo "6️⃣  Installazione yfinance..."
pip install --quiet yfinance requests beautifulsoup4 lxml 2>&1 | grep -v "Requirement already satisfied" || true
pip install --quiet curl-cffi frozendict peewee websockets platformdirs 2>&1 | grep -v "Requirement already satisfied" || true
print_success "yfinance installato"

# 7. Installa visualizzazione
echo ""
echo "7️⃣  Installazione librerie visualizzazione..."
pip install --quiet plotly matplotlib 2>&1 | grep -v "Requirement already satisfied" || true
print_success "Plotly e Matplotlib installati"

# 8. Installa Streamlit
echo ""
echo "8️⃣  Installazione Streamlit..."
pip install --quiet streamlit 2>&1 | grep -v "Requirement already satisfied" || true
print_success "Streamlit installato"

# 9. Installa scikit-learn
echo ""
echo "9️⃣  Installazione Scikit-learn..."
pip install --quiet scikit-learn 2>&1 | grep -v "Requirement already satisfied" || true
print_success "Scikit-learn installato"

# 10. Installa FastAPI (opzionale)
echo ""
echo "🔟 Installazione FastAPI (opzionale)..."
pip install --quiet fastapi uvicorn python-dotenv 2>&1 | grep -v "Requirement already satisfied" || true
print_success "FastAPI installato"

# 11. Test installazione
echo ""
echo "🧪 Test installazione..."
python3 -c "import yfinance; import pandas; import streamlit; print('OK')" 2>&1
if [ $? -eq 0 ]; then
    print_success "Tutti i moduli importati correttamente!"
else
    print_error "Errore nell'importazione moduli"
    print_info "Prova a eseguire: python3 test_installation.py"
fi

# 12. Riepilogo
echo ""
echo "=================================="
echo "✨ Installazione Completata!"
echo "=================================="
echo ""
echo "Per avviare l'applicazione:"
echo ""
echo "  1. Attiva il virtual environment (se non già attivo):"
echo "     source venv/bin/activate"
echo ""
echo "  2. Avvia Streamlit:"
echo "     streamlit run frontend/app.py"
echo ""
echo "  Oppure usa lo shortcut:"
echo "     ./run.sh"
echo ""
echo "L'applicazione si aprirà automaticamente nel browser!"
echo ""
print_info "Documentazione completa: INSTALL_MAC.md"
print_info "Guida uso: USAGE.md"
echo ""
