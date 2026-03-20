"""
📄 HTML Report Generator - Print-Ready Portfolio Reports

Genera report HTML pronti per la stampa (Stampa → Salva come PDF).
Più semplice e affidabile di reportlab!
"""

from datetime import datetime
from typing import Dict, List, Optional
import plotly.graph_objects as go
import base64
import io


# ══════════════════════════════════════════════════════════════════════
# 🎨 CSS PRINT-READY
# ══════════════════════════════════════════════════════════════════════

PRINT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', sans-serif;
    background: white;
    color: #0A1628;
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 40px;
}

/* ══════════════════════════════════════════════════════════════════
   📄 COVER PAGE
   ══════════════════════════════════════════════════════════════════ */

.cover-page {
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    page-break-after: always;
    background: linear-gradient(135deg, #0A1628 0%, #1E293B 100%);
    color: white;
}

.cover-title {
    font-size: 4rem;
    font-weight: 800;
    margin-bottom: 20px;
    color: #D4AF37;
    text-transform: uppercase;
    letter-spacing: 2px;
}

.cover-portfolio-name {
    font-size: 2.5rem;
    font-weight: 600;
    margin-bottom: 40px;
    color: white;
}

.cover-date {
    font-size: 1.2rem;
    color: #9CA3AF;
    margin-bottom: 60px;
}

.cover-branding {
    margin-top: 80px;
}

.cover-branding-title {
    font-size: 1.8rem;
    font-weight: 700;
    color: #D4AF37;
    margin-bottom: 10px;
}

.cover-branding-subtitle {
    font-size: 1rem;
    color: #9CA3AF;
}

.cover-line {
    width: 200px;
    height: 4px;
    background: linear-gradient(90deg, transparent, #D4AF37, transparent);
    margin: 40px auto;
}

/* ══════════════════════════════════════════════════════════════════
   📊 SECTION
   ══════════════════════════════════════════════════════════════════ */

.section {
    page-break-before: always;
    padding: 40px 0;
}

.section-title {
    font-size: 2.5rem;
    font-weight: 800;
    color: #D4AF37;
    margin-bottom: 30px;
    padding-bottom: 15px;
    border-bottom: 3px solid #D4AF37;
}

.section-content {
    margin: 30px 0;
}

/* ══════════════════════════════════════════════════════════════════
   📈 METRICS
   ══════════════════════════════════════════════════════════════════ */

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 30px;
    margin: 30px 0;
}

.metric-card {
    background: linear-gradient(135deg, #F9FAFB 0%, #F3F4F6 100%);
    border-radius: 12px;
    padding: 25px;
    text-align: center;
    border: 2px solid #E5E7EB;
}

.metric-label {
    font-size: 0.9rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #6B7280;
    margin-bottom: 12px;
}

.metric-value {
    font-size: 2.5rem;
    font-weight: 800;
    color: #0A1628;
    font-family: 'SF Mono', monospace;
    font-variant-numeric: tabular-nums;
}

.metric-value.positive {
    color: #10B981;
}

.metric-value.negative {
    color: #EF4444;
}

.metric-value.neutral {
    color: #3B82F6;
}

/* ══════════════════════════════════════════════════════════════════
   📊 TABLE
   ══════════════════════════════════════════════════════════════════ */

.data-table {
    width: 100%;
    border-collapse: collapse;
    margin: 30px 0;
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.data-table thead {
    background: linear-gradient(135deg, #0A1628 0%, #1E293B 100%);
    color: white;
}

.data-table thead th {
    padding: 18px 20px;
    text-align: left;
    font-weight: 700;
    font-size: 0.95rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.data-table tbody tr {
    border-bottom: 1px solid #E5E7EB;
}

.data-table tbody tr:nth-child(even) {
    background: #F9FAFB;
}

.data-table tbody td {
    padding: 16px 20px;
    font-size: 1rem;
}

/* ══════════════════════════════════════════════════════════════════
   🖼️ CHART
   ══════════════════════════════════════════════════════════════════ */

.chart-container {
    margin: 40px 0;
    text-align: center;
}

.chart-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #0A1628;
    margin-bottom: 20px;
    text-align: left;
    padding-left: 10px;
    border-left: 4px solid #D4AF37;
}

.chart-image {
    max-width: 100%;
    height: auto;
    border-radius: 12px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

/* ══════════════════════════════════════════════════════════════════
   ⚠️ DISCLAIMER
   ══════════════════════════════════════════════════════════════════ */

.disclaimer {
    margin-top: 60px;
    padding: 30px;
    background: #FEF3C7;
    border-left: 4px solid #F59E0B;
    border-radius: 8px;
}

.disclaimer-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #92400E;
    margin-bottom: 15px;
}

.disclaimer-text {
    font-size: 0.95rem;
    color: #78350F;
    line-height: 1.7;
}

/* ══════════════════════════════════════════════════════════════════
   🖨️ PRINT STYLES
   ══════════════════════════════════════════════════════════════════ */

@media print {
    body {
        background: white;
    }

    .no-print {
        display: none !important;
    }

    .section {
        page-break-inside: avoid;
    }

    .metric-card,
    .chart-container {
        page-break-inside: avoid;
    }

    @page {
        margin: 2cm;
    }
}

/* ══════════════════════════════════════════════════════════════════
   🔘 BUTTONS
   ══════════════════════════════════════════════════════════════════ */

.button-container {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 1000;
}

.btn-print {
    background: linear-gradient(135deg, #D4AF37 0%, #B8860B 100%);
    color: #0A1628;
    border: none;
    border-radius: 12px;
    padding: 15px 35px;
    font-size: 1.1rem;
    font-weight: 700;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(212, 175, 55, 0.4);
    transition: all 0.3s ease;
}

.btn-print:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(212, 175, 55, 0.6);
}

.btn-print:active {
    transform: translateY(0);
}
</style>
"""


# ══════════════════════════════════════════════════════════════════════
# 🖼️ CHART TO IMAGE
# ══════════════════════════════════════════════════════════════════════

def fig_to_base64(fig: go.Figure, width: int = 1200, height: int = 600) -> str:
    """
    Converte figura Plotly in base64 PNG

    Args:
        fig: Figura Plotly
        width: Larghezza immagine
        height: Altezza immagine

    Returns:
        str: Base64 encoded PNG
    """
    try:
        # Usa kaleido per export statico
        img_bytes = fig.to_image(format="png", width=width, height=height, scale=2)
        img_base64 = base64.b64encode(img_bytes).decode()
        return f"data:image/png;base64,{img_base64}"
    except Exception as e:
        # Fallback: crea placeholder
        return f"data:image/svg+xml;base64,{base64.b64encode(f'<svg width=\"{width}\" height=\"{height}\"><text x=\"50%\" y=\"50%\" text-anchor=\"middle\" fill=\"#999\">Chart: {str(e)}</text></svg>'.encode()).decode()}"


# ══════════════════════════════════════════════════════════════════════
# 📄 HTML GENERATOR
# ══════════════════════════════════════════════════════════════════════

def generate_html_report(
    portfolio_name: str,
    symbols: List[str],
    weights: Dict[str, float],
    initial_value: float,
    performance_chart: Optional[go.Figure] = None,
    correlation_chart: Optional[go.Figure] = None,
    backtest_chart: Optional[go.Figure] = None,
    prediction_chart: Optional[go.Figure] = None,
    backtest_results: Optional[Dict] = None,
    prediction_results: Optional[Dict] = None,
) -> str:
    """
    Genera HTML report completo pronto per la stampa

    Returns:
        str: HTML completo
    """

    # Data corrente
    now = datetime.now()
    date_str = now.strftime("%d %B %Y")

    # ══════════════════════════════════════════════════════════════════
    # 📄 BUILD HTML
    # ══════════════════════════════════════════════════════════════════

    html = f"""
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{portfolio_name} - Report</title>
    {PRINT_CSS}
</head>
<body>

<!-- ══════════════════════════════════════════════════════════════════
     🎨 PRINT BUTTON (hidden on print)
     ══════════════════════════════════════════════════════════════════ -->
<div class="button-container no-print">
    <button class="btn-print" onclick="window.print()">
        🖨️ Stampa / Salva PDF
    </button>
</div>

<!-- ══════════════════════════════════════════════════════════════════
     📄 COVER PAGE
     ══════════════════════════════════════════════════════════════════ -->
<div class="cover-page">
    <div class="cover-line"></div>
    <h1 class="cover-title">Portfolio Report</h1>
    <h2 class="cover-portfolio-name">{portfolio_name}</h2>
    <p class="cover-date">{date_str}</p>
    <div class="cover-line"></div>

    <div class="cover-branding">
        <div class="cover-branding-title">FinAnalyzer Pro</div>
        <div class="cover-branding-subtitle">Professional Financial Analysis Platform</div>
    </div>
</div>

<div class="container">

<!-- ══════════════════════════════════════════════════════════════════
     📊 PORTFOLIO OVERVIEW
     ══════════════════════════════════════════════════════════════════ -->
<div class="section">
    <h2 class="section-title">Portfolio Overview</h2>

    <div class="section-content">
        <table class="data-table">
            <thead>
                <tr>
                    <th>Simbolo</th>
                    <th>Peso</th>
                    <th>Allocazione</th>
                </tr>
            </thead>
            <tbody>
"""

    # Asset allocation table
    for symbol in symbols:
        weight = weights.get(symbol, 0)
        allocation = initial_value * weight
        weight_pct = f"{weight*100:.1f}%".replace(".", ",")
        allocation_eur = f"{allocation:,.0f}€".replace(",", ".")

        html += f"""
                <tr>
                    <td><strong>{symbol}</strong></td>
                    <td>{weight_pct}</td>
                    <td>{allocation_eur}</td>
                </tr>
"""

    html += f"""
            </tbody>
        </table>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Capitale Iniziale</div>
                <div class="metric-value">{initial_value:,.0f}€</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">N° Asset</div>
                <div class="metric-value">{len(symbols)}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Data Report</div>
                <div class="metric-value" style="font-size:1.5rem;">{now.strftime("%d/%m/%Y")}</div>
            </div>
        </div>
    </div>
</div>
"""

    # ══════════════════════════════════════════════════════════════════
    # 📈 PERFORMANCE CHART
    # ══════════════════════════════════════════════════════════════════
    if performance_chart:
        img_data = fig_to_base64(performance_chart, width=1200, height=500)
        html += f"""
<div class="section">
    <h2 class="section-title">Performance Normalizzata</h2>
    <div class="chart-container">
        <div class="chart-title">Andamento Storico (Base 100)</div>
        <img src="{img_data}" alt="Performance Chart" class="chart-image">
    </div>
</div>
"""

    # ══════════════════════════════════════════════════════════════════
    # 🔗 CORRELATION CHART
    # ══════════════════════════════════════════════════════════════════
    if correlation_chart:
        img_data = fig_to_base64(correlation_chart, width=1000, height=800)
        html += f"""
<div class="section">
    <h2 class="section-title">Matrice di Correlazione</h2>
    <div class="chart-container">
        <div class="chart-title">Correlazione tra Asset</div>
        <img src="{img_data}" alt="Correlation Matrix" class="chart-image">
    </div>
</div>
"""

    # ══════════════════════════════════════════════════════════════════
    # 📊 BACKTEST RESULTS
    # ══════════════════════════════════════════════════════════════════
    if backtest_results:
        html += f"""
<div class="section">
    <h2 class="section-title">Backtest Analysis</h2>

    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-label">Rendimento Totale</div>
            <div class="metric-value {'positive' if backtest_results.get('total_return', 0) >= 0 else 'negative'}">
                {'+' if backtest_results.get('total_return', 0) >= 0 else ''}{backtest_results.get('total_return', 0)*100:.1f}%
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Sharpe Ratio</div>
            <div class="metric-value neutral">
                {backtest_results.get('sharpe_ratio', 0):.2f}
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Max Drawdown</div>
            <div class="metric-value negative">
                {backtest_results.get('max_drawdown', 0)*100:.1f}%
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Volatilità Annua</div>
            <div class="metric-value neutral">
                {backtest_results.get('annual_volatility', 0)*100:.1f}%
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Win Rate</div>
            <div class="metric-value {'positive' if backtest_results.get('win_rate', 0) >= 0.5 else 'neutral'}">
                {backtest_results.get('win_rate', 0)*100:.0f}%
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Rendimento Annuo</div>
            <div class="metric-value {'positive' if backtest_results.get('annual_return', 0) >= 0 else 'negative'}">
                {'+' if backtest_results.get('annual_return', 0) >= 0 else ''}{backtest_results.get('annual_return', 0)*100:.1f}%
            </div>
        </div>
    </div>
"""

        if backtest_chart:
            img_data = fig_to_base64(backtest_chart, width=1200, height=500)
            html += f"""
    <div class="chart-container">
        <div class="chart-title">Andamento Portafoglio nel Backtest</div>
        <img src="{img_data}" alt="Backtest Chart" class="chart-image">
    </div>
"""

        html += "</div>"

    # ══════════════════════════════════════════════════════════════════
    # 🔮 PREDICTIONS
    # ══════════════════════════════════════════════════════════════════
    if prediction_results:
        scenarios = prediction_results.get('scenarios', {})

        html += f"""
<div class="section">
    <h2 class="section-title">Predictions & Scenarios</h2>

    <div class="metrics-grid">
"""

        if 'best_scenario' in scenarios:
            s = scenarios['best_scenario']
            html += f"""
        <div class="metric-card">
            <div class="metric-label">Scenario Migliore (95%)</div>
            <div class="metric-value positive">{s['final_value']:,.0f}€</div>
            <div class="metric-label" style="margin-top:10px;color:#10B981;">
                +{s['return_percentage']:.1f}%
            </div>
        </div>
"""

        if 'normal_scenario' in scenarios:
            s = scenarios['normal_scenario']
            html += f"""
        <div class="metric-card">
            <div class="metric-label">Scenario Atteso (50%)</div>
            <div class="metric-value neutral">{s['final_value']:,.0f}€</div>
            <div class="metric-label" style="margin-top:10px;color:#3B82F6;">
                {'+' if s['return_percentage'] >= 0 else ''}{s['return_percentage']:.1f}%
            </div>
        </div>
"""

        if 'worst_scenario' in scenarios:
            s = scenarios['worst_scenario']
            html += f"""
        <div class="metric-card">
            <div class="metric-label">Scenario Peggiore (5%)</div>
            <div class="metric-value negative">{s['final_value']:,.0f}€</div>
            <div class="metric-label" style="margin-top:10px;color:#EF4444;">
                {s['return_percentage']:.1f}%
            </div>
        </div>
"""

        html += "</div>"

        if prediction_chart:
            img_data = fig_to_base64(prediction_chart, width=1200, height=500)
            html += f"""
    <div class="chart-container">
        <div class="chart-title">Scenari Predittivi a 6 Mesi (Monte Carlo)</div>
        <img src="{img_data}" alt="Prediction Chart" class="chart-image">
    </div>
"""

        html += "</div>"

    # ══════════════════════════════════════════════════════════════════
    # ⚠️ DISCLAIMER
    # ══════════════════════════════════════════════════════════════════
    html += """
<div class="disclaimer">
    <div class="disclaimer-title">⚠️ Important Disclaimer</div>
    <div class="disclaimer-text">
        <p><strong>DISCLAIMER LEGALE:</strong> Questo report è stato generato da FinAnalyzer Pro
        esclusivamente a scopo informativo e educativo. Le informazioni contenute in questo documento
        non costituiscono una consulenza finanziaria, fiscale o legale e non devono essere interpretate
        come raccomandazioni di investimento.</p>
        <br>
        <p>Le performance passate non sono garanzia di risultati futuri. Gli investimenti comportano rischi,
        inclusa la possibile perdita del capitale investito. Si raccomanda di consultare un consulente
        finanziario qualificato prima di prendere qualsiasi decisione di investimento.</p>
        <br>
        <p>Tutte le analisi e proiezioni sono basate su modelli matematici e dati storici, che potrebbero
        non riflettere accuratamente le condizioni di mercato future.</p>
    </div>
</div>

</div><!-- /container -->

<script>
// Auto-open print dialog on load (optional)
// window.onload = function() { window.print(); };
</script>

</body>
</html>
"""

    return html
