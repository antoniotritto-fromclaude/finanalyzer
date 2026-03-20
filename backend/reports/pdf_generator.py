"""
📄 PDF Report Generator - Luxury Portfolio Reports

Genera report PDF professionali con:
- Cover page luxury
- Executive summary
- Performance charts
- Risk analysis
- Asset breakdown
- Predictions & scenarios
"""

import io
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image as RLImage,
    Frame,
    PageTemplate,
)
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor


# ══════════════════════════════════════════════════════════════════════
# 🎨 LUXURY COLOR PALETTE
# ══════════════════════════════════════════════════════════════════════

LUXURY_COLORS = {
    "primary": HexColor("#0A1628"),
    "gold": HexColor("#D4AF37"),
    "success": HexColor("#10B981"),
    "warning": HexColor("#F59E0B"),
    "error": HexColor("#EF4444"),
    "gray_dark": HexColor("#4B5563"),
    "gray_light": HexColor("#9CA3AF"),
    "white": HexColor("#FFFFFF"),
    "bg_light": HexColor("#F9FAFB"),
}


# ══════════════════════════════════════════════════════════════════════
# 📄 PAGE TEMPLATES
# ══════════════════════════════════════════════════════════════════════

class LuxuryReportCanvas(canvas.Canvas):
    """Canvas custom con header/footer luxury"""

    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self.pages)
        for page_num, page in enumerate(self.pages, start=1):
            self.__dict__.update(page)
            self.draw_page_decorations(page_num, page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_num, page_count):
        """Disegna header e footer luxury"""
        width, height = letter

        # Skip decorations on cover page (page 1)
        if page_num == 1:
            return

        # ── Header Luxury Line ──
        self.setStrokeColor(LUXURY_COLORS["gold"])
        self.setLineWidth(3)
        self.line(50, height - 40, width - 50, height - 40)

        # ── Header Text ──
        self.setFont("Helvetica", 9)
        self.setFillColor(LUXURY_COLORS["gray_light"])
        self.drawString(50, height - 30, "FinAnalyzer Pro")
        self.drawRightString(width - 50, height - 30,
                            f"Portfolio Report · {datetime.now().strftime('%B %Y')}")

        # ── Footer Line ──
        self.setStrokeColor(LUXURY_COLORS["gold"])
        self.setLineWidth(2)
        self.line(50, 50, width - 50, 50)

        # ── Footer Page Number ──
        self.setFont("Helvetica-Bold", 10)
        self.setFillColor(LUXURY_COLORS["primary"])
        self.drawCentredString(width / 2, 35, f"{page_num}")

        # ── Footer Confidential ──
        self.setFont("Helvetica-Oblique", 8)
        self.setFillColor(LUXURY_COLORS["gray_light"])
        self.drawRightString(width - 50, 35, "Confidential")


# ══════════════════════════════════════════════════════════════════════
# 🎨 STYLES
# ══════════════════════════════════════════════════════════════════════

def get_luxury_styles():
    """Restituisce stili luxury per il PDF"""
    styles = getSampleStyleSheet()

    # Cover Title
    styles.add(ParagraphStyle(
        name='CoverTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=48,
        textColor=LUXURY_COLORS["primary"],
        alignment=TA_CENTER,
        spaceAfter=20,
    ))

    # Cover Subtitle
    styles.add(ParagraphStyle(
        name='CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=18,
        textColor=LUXURY_COLORS["gray_dark"],
        alignment=TA_CENTER,
        spaceAfter=10,
    ))

    # Section Title (Gold)
    styles.add(ParagraphStyle(
        name='SectionTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=LUXURY_COLORS["gold"],
        spaceAfter=16,
        spaceBefore=20,
    ))

    # Section Subtitle
    styles.add(ParagraphStyle(
        name='SectionSubtitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=LUXURY_COLORS["primary"],
        spaceAfter=12,
        spaceBefore=16,
    ))

    # Body Text
    styles.add(ParagraphStyle(
        name='BodyLuxury',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        textColor=LUXURY_COLORS["gray_dark"],
        alignment=TA_JUSTIFY,
        spaceAfter=10,
        leading=16,
    ))

    # Metric Value (Large)
    styles.add(ParagraphStyle(
        name='MetricValue',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=32,
        textColor=LUXURY_COLORS["primary"],
        alignment=TA_CENTER,
        spaceAfter=5,
    ))

    # Metric Label
    styles.add(ParagraphStyle(
        name='MetricLabel',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=LUXURY_COLORS["gray_light"],
        alignment=TA_CENTER,
        spaceAfter=10,
    ))

    return styles


# ══════════════════════════════════════════════════════════════════════
# 📊 HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════

def format_currency_eur(value: float, decimals: int = 2) -> str:
    """Formato europeo per valute"""
    if decimals == 0:
        formatted = f"{value:,.0f}".replace(",", ".")
        return f"{formatted}€"
    else:
        formatted = f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{formatted}€"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Formato percentuale europea"""
    formatted = f"{value:.{decimals}f}".replace(".", ",")
    return f"{formatted}%"


def create_metric_table(metrics: List[tuple], ncols: int = 3):
    """
    Crea tabella metriche luxury

    Args:
        metrics: List of (label, value, color_name) tuples
        ncols: Number of columns
    """
    # Organizza in righe
    rows = []
    for i in range(0, len(metrics), ncols):
        row_data = []
        for j in range(ncols):
            if i + j < len(metrics):
                label, value, color_name = metrics[i + j]
                color = LUXURY_COLORS.get(color_name, LUXURY_COLORS["primary"])
                cell = [
                    Paragraph(f'<font size="9" color="{color_name}">{label}</font>',
                             get_luxury_styles()['MetricLabel']),
                    Paragraph(f'<font size="18" color="{color_name}"><b>{value}</b></font>',
                             get_luxury_styles()['BodyLuxury']),
                ]
                row_data.append(cell)
            else:
                row_data.append(['', ''])

        # Flatten row
        flat_row = []
        for cell in row_data:
            flat_row.extend(cell)
        rows.append(flat_row)

    # Create table with proper column structure
    col_widths = []
    for _ in range(ncols):
        col_widths.extend([2.5 * inch, 1.5 * inch])

    table = Table(rows, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, -1), LUXURY_COLORS["bg_light"]),
        ('BOX', (0, 0), (-1, -1), 1, LUXURY_COLORS["gray_light"]),
        ('GRID', (0, 0), (-1, -1), 0.5, LUXURY_COLORS["gray_light"]),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))

    return table


def create_data_table(data: pd.DataFrame, headers: List[str] = None):
    """Crea tabella dati luxury"""
    if headers is None:
        headers = data.columns.tolist()

    # Header
    table_data = [[Paragraph(f'<b>{h}</b>', get_luxury_styles()['BodyLuxury'])
                   for h in headers]]

    # Data rows
    for _, row in data.iterrows():
        table_data.append([Paragraph(str(val), get_luxury_styles()['BodyLuxury'])
                          for val in row])

    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), LUXURY_COLORS["primary"]),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

        # Body
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), LUXURY_COLORS["gray_dark"]),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),

        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, LUXURY_COLORS["gray_light"]),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [colors.white, LUXURY_COLORS["bg_light"]]),

        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))

    return table


# ══════════════════════════════════════════════════════════════════════
# 📄 REPORT GENERATOR
# ══════════════════════════════════════════════════════════════════════

class PortfolioReportGenerator:
    """Generatore report PDF luxury per portfolio"""

    def __init__(self):
        self.styles = get_luxury_styles()
        self.story = []

    def generate(
        self,
        portfolio_name: str,
        symbols: List[str],
        weights: Dict[str, float],
        initial_value: float,
        backtest_results: Optional[Dict] = None,
        prediction_results: Optional[Dict] = None,
    ) -> bytes:
        """
        Genera PDF report completo

        Returns:
            bytes: PDF content
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=1 * inch,
            bottomMargin=1 * inch,
            leftMargin=0.75 * inch,
            rightMargin=0.75 * inch,
        )

        # Build story
        self.story = []

        # 1. Cover Page
        self._add_cover_page(portfolio_name)

        # 2. Executive Summary
        self._add_executive_summary(symbols, weights, initial_value)

        # 3. Portfolio Overview
        self._add_portfolio_overview(symbols, weights, initial_value)

        # 4. Backtest Results (if provided)
        if backtest_results:
            self._add_backtest_section(backtest_results)

        # 5. Predictions (if provided)
        if prediction_results:
            self._add_predictions_section(prediction_results)

        # 6. Risk Analysis
        if backtest_results:
            self._add_risk_analysis(backtest_results)

        # 7. Disclaimer
        self._add_disclaimer()

        # Build PDF
        doc.build(self.story, canvasmaker=LuxuryReportCanvas)

        buffer.seek(0)
        return buffer.getvalue()

    def _add_cover_page(self, portfolio_name: str):
        """Cover page luxury"""
        # Spacer to center
        self.story.append(Spacer(1, 2 * inch))

        # Gold decorative line
        self.story.append(Spacer(1, 0.3 * inch))

        # Title
        title = Paragraph(
            "PORTFOLIO REPORT",
            self.styles['CoverTitle']
        )
        self.story.append(title)

        # Portfolio Name
        subtitle = Paragraph(
            portfolio_name,
            self.styles['CoverSubtitle']
        )
        self.story.append(subtitle)
        self.story.append(Spacer(1, 0.5 * inch))

        # Date
        date_str = datetime.now().strftime("%B %d, %Y")
        date_para = Paragraph(
            f'<font color="{LUXURY_COLORS["gray_light"]}" size="12">{date_str}</font>',
            self.styles['CoverSubtitle']
        )
        self.story.append(date_para)

        # Bottom decorative
        self.story.append(Spacer(1, 2 * inch))

        # FinAnalyzer Pro branding
        branding = Paragraph(
            '<font color="#D4AF37" size="14"><b>FinAnalyzer Pro</b></font><br/>'
            '<font color="#9CA3AF" size="10">Professional Financial Analysis Platform</font>',
            self.styles['CoverSubtitle']
        )
        self.story.append(branding)

        self.story.append(PageBreak())

    def _add_executive_summary(self, symbols: List[str], weights: Dict[str, float], initial_value: float):
        """Executive summary"""
        self.story.append(Paragraph("Executive Summary", self.styles['SectionTitle']))
        self.story.append(Spacer(1, 0.2 * inch))

        summary_text = f"""
        Questo report fornisce un'analisi completa del portafoglio <b>{len(symbols)} strumenti</b>
        con un capitale iniziale di <b>{format_currency_eur(initial_value, 0)}</b>.
        Il portafoglio è stato analizzato attraverso simulazioni Monte Carlo, backtesting storico
        e analisi di rischio avanzate per fornire una visione comprensiva delle performance attese
        e dei rischi associati.
        """
        self.story.append(Paragraph(summary_text, self.styles['BodyLuxury']))
        self.story.append(Spacer(1, 0.3 * inch))

    def _add_portfolio_overview(self, symbols: List[str], weights: Dict[str, float], initial_value: float):
        """Portfolio overview with asset allocation"""
        self.story.append(Paragraph("Portfolio Overview", self.styles['SectionTitle']))
        self.story.append(Spacer(1, 0.2 * inch))

        # Asset allocation table
        data = []
        for symbol in symbols:
            weight = weights.get(symbol, 0)
            allocation = initial_value * weight
            data.append({
                "Strumento": symbol,
                "Peso": format_percentage(weight * 100, 1),
                "Allocazione": format_currency_eur(allocation, 0),
            })

        df = pd.DataFrame(data)
        table = create_data_table(df)
        self.story.append(table)
        self.story.append(Spacer(1, 0.3 * inch))

    def _add_backtest_section(self, backtest_results: Dict):
        """Backtest results section"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("Backtest Analysis", self.styles['SectionTitle']))
        self.story.append(Spacer(1, 0.2 * inch))

        # Metrics
        metrics = [
            ("Rendimento Totale",
             ("+" if backtest_results['total_return'] >= 0 else "") +
             format_percentage(backtest_results['total_return'] * 100, 1),
             "success" if backtest_results['total_return'] >= 0 else "error"),

            ("Rendimento Annuo",
             ("+" if backtest_results['annual_return'] >= 0 else "") +
             format_percentage(backtest_results['annual_return'] * 100, 1),
             "success" if backtest_results['annual_return'] >= 0 else "error"),

            ("Sharpe Ratio",
             f"{backtest_results['sharpe_ratio']:.2f}".replace(".", ","),
             "success" if backtest_results['sharpe_ratio'] >= 1 else "warning"),

            ("Max Drawdown",
             format_percentage(backtest_results['max_drawdown'] * 100, 1),
             "error"),

            ("Volatilità",
             format_percentage(backtest_results['annual_volatility'] * 100, 1),
             "warning"),

            ("Win Rate",
             format_percentage(backtest_results['win_rate'] * 100, 0),
             "success" if backtest_results['win_rate'] >= 0.5 else "warning"),
        ]

        metric_table = create_metric_table(metrics, ncols=3)
        self.story.append(metric_table)
        self.story.append(Spacer(1, 0.3 * inch))

    def _add_predictions_section(self, prediction_results: Dict):
        """Predictions section"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("Predictions & Scenarios", self.styles['SectionTitle']))
        self.story.append(Spacer(1, 0.2 * inch))

        scenarios = prediction_results.get('scenarios', {})

        # Scenario metrics
        scenario_data = []
        for name, key in [("Scenario Migliore", "best_scenario"),
                          ("Scenario Atteso", "normal_scenario"),
                          ("Scenario Peggiore", "worst_scenario")]:
            if key in scenarios:
                s = scenarios[key]
                scenario_data.append({
                    "Scenario": name,
                    "Valore Finale": format_currency_eur(s['final_value'], 0),
                    "Rendimento": ("+" if s['return_percentage'] >= 0 else "") +
                                format_percentage(s['return_percentage'], 1),
                })

        if scenario_data:
            df = pd.DataFrame(scenario_data)
            table = create_data_table(df)
            self.story.append(table)
            self.story.append(Spacer(1, 0.3 * inch))

    def _add_risk_analysis(self, backtest_results: Dict):
        """Risk analysis section"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("Risk Analysis", self.styles['SectionTitle']))
        self.story.append(Spacer(1, 0.2 * inch))

        risk_text = f"""
        L'analisi di rischio valuta la volatilità del portafoglio e i potenziali drawdown.
        Il portafoglio presenta una volatilità annualizzata del
        <b>{format_percentage(backtest_results['annual_volatility'] * 100, 1)}</b>
        con un drawdown massimo osservato del
        <b>{format_percentage(backtest_results['max_drawdown'] * 100, 1)}</b>.
        """
        self.story.append(Paragraph(risk_text, self.styles['BodyLuxury']))
        self.story.append(Spacer(1, 0.3 * inch))

    def _add_disclaimer(self):
        """Disclaimer"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("Important Disclaimer", self.styles['SectionTitle']))
        self.story.append(Spacer(1, 0.2 * inch))

        disclaimer_text = """
        <b>DISCLAIMER LEGALE:</b><br/><br/>

        Questo report è stato generato da FinAnalyzer Pro esclusivamente a scopo informativo
        e educativo. Le informazioni contenute in questo documento non costituiscono una
        consulenza finanziaria, fiscale o legale e non devono essere interpretate come
        raccomandazioni di investimento.<br/><br/>

        Le performance passate non sono garanzia di risultati futuri. Gli investimenti
        comportano rischi, inclusa la possibile perdita del capitale investito.
        Si raccomanda di consultare un consulente finanziario qualificato prima di prendere
        qualsiasi decisione di investimento.<br/><br/>

        Tutte le analisi e proiezioni sono basate su modelli matematici e dati storici,
        che potrebbero non riflettere accuratamente le condizioni di mercato future.
        """

        self.story.append(Paragraph(disclaimer_text, self.styles['BodyLuxury']))


# ══════════════════════════════════════════════════════════════════════
# 🎯 MAIN FUNCTION
# ══════════════════════════════════════════════════════════════════════

def generate_portfolio_report(
    portfolio_name: str,
    symbols: List[str],
    weights: Dict[str, float],
    initial_value: float,
    backtest_results: Optional[Dict] = None,
    prediction_results: Optional[Dict] = None,
) -> bytes:
    """
    Generate comprehensive portfolio PDF report

    Args:
        portfolio_name: Name of the portfolio
        symbols: List of asset symbols
        weights: Dictionary of symbol -> weight
        initial_value: Initial investment value
        backtest_results: Optional backtest results dict
        prediction_results: Optional prediction results dict

    Returns:
        bytes: PDF file content
    """
    generator = PortfolioReportGenerator()
    return generator.generate(
        portfolio_name=portfolio_name,
        symbols=symbols,
        weights=weights,
        initial_value=initial_value,
        backtest_results=backtest_results,
        prediction_results=prediction_results,
    )
