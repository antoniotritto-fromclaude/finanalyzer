"""
Componenti grafici riutilizzabili - stile professionale
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import List, Dict, Optional

CHART_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(255,255,255,0.85)",
    font=dict(family="Inter, sans-serif", size=12, color="#374151"),
    margin=dict(l=10, r=10, t=40, b=30),
    xaxis=dict(showgrid=True, gridcolor="#e5eef8", gridwidth=1, zeroline=False, linecolor="#c8daea"),
    yaxis=dict(showgrid=True, gridcolor="#e5eef8", gridwidth=1, zeroline=False, linecolor="#c8daea"),
    legend=dict(bgcolor="rgba(255,255,255,0.8)", bordercolor="#e2eaf4", borderwidth=1, font=dict(size=11)),
    hovermode="x unified",
)

COLORS = ["#2471c8","#22c55e","#f59e0b","#ef4444","#8b5cf6","#0ea5c9","#f97316","#ec4899"]


def line_chart(
    df: pd.DataFrame,
    title: str = "",
    y_title: str = "",
    normalize: bool = False,
    filled: bool = False,
    height: int = 340,
) -> go.Figure:
    """Grafico a linee multi-serie"""
    fig = go.Figure()
    data = (df / df.iloc[0] * 100) if normalize else df
    for i, col in enumerate(data.columns):
        color = COLORS[i % len(COLORS)]
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data[col],
            name=col,
            line=dict(color=color, width=2.2),
            fill="tonexty" if (filled and i == 0) else "none",
            fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.08)",
            hovertemplate=f"<b>{col}</b><br>%{{y:.2f}}<extra></extra>",
        ))
    fig.update_layout(**CHART_THEME, title=dict(text=title, font=dict(size=14, weight=700), x=0), height=height, yaxis_title=y_title)
    return fig


def candle_chart(df: pd.DataFrame, title: str = "", height: int = 380) -> go.Figure:
    """Candlestick chart"""
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        increasing_line_color="#22c55e", decreasing_line_color="#ef4444",
        increasing_fillcolor="#22c55e", decreasing_fillcolor="#ef4444",
    )])
    fig.update_layout(**CHART_THEME, title=dict(text=title, font=dict(size=14, weight=700), x=0), height=height)
    fig.update_xaxes(rangeslider_visible=False)
    return fig


def pie_chart(labels: List[str], values: List[float], title: str = "", height: int = 300) -> go.Figure:
    """Pie chart moderno"""
    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values,
        hole=0.4,
        marker=dict(colors=COLORS[:len(labels)], line=dict(color="white", width=2)),
        textfont=dict(size=11, family="Inter"),
        hovertemplate="<b>%{label}</b><br>%{value:.1f}%<extra></extra>",
    )])
    fig.update_layout(
        **{k: v for k, v in CHART_THEME.items() if k not in ["xaxis","yaxis","hovermode"]},
        title=dict(text=title, font=dict(size=13, weight=700), x=0),
        height=height,
        showlegend=True,
        legend=dict(orientation="v", x=1.05),
    )
    return fig


def bar_chart(
    x: List,
    y: List,
    title: str = "",
    colors: Optional[List[str]] = None,
    horizontal: bool = False,
    height: int = 300,
) -> go.Figure:
    """Bar chart"""
    clrs = colors if colors else [COLORS[0]] * len(x)
    if horizontal:
        fig = go.Figure(go.Bar(y=x, x=y, orientation="h", marker_color=clrs,
                               hovertemplate="%{x:.2f}<extra></extra>"))
    else:
        fig = go.Figure(go.Bar(x=x, y=y, marker_color=clrs,
                               hovertemplate="%{y:.2f}<extra></extra>"))
    fig.update_layout(**CHART_THEME, title=dict(text=title, font=dict(size=13, weight=700), x=0), height=height)
    return fig


def efficient_frontier_chart(
    volatilities: List[float],
    returns: List[float],
    optimal_vol: float,
    optimal_ret: float,
    symbols: List[str],
    asset_vols: List[float],
    asset_rets: List[float],
    height: int = 420,
) -> go.Figure:
    """Frontiera efficiente di Markowitz"""
    fig = go.Figure()

    # Frontiera efficiente
    fig.add_trace(go.Scatter(
        x=volatilities, y=returns,
        mode="lines",
        name="Frontiera Efficiente",
        line=dict(color="#2471c8", width=3),
        hovertemplate="Vol: %{x:.1%}<br>Ret: %{y:.1%}<extra></extra>",
    ))

    # Asset individuali
    for sym, vol, ret in zip(symbols, asset_vols, asset_rets):
        fig.add_trace(go.Scatter(
            x=[vol], y=[ret],
            mode="markers+text",
            name=sym,
            text=[sym],
            textposition="top center",
            textfont=dict(size=10, weight=600),
            marker=dict(size=10, color=COLORS[symbols.index(sym) % len(COLORS)], line=dict(color="white", width=2)),
            hovertemplate=f"<b>{sym}</b><br>Vol: %{{x:.1%}}<br>Ret: %{{y:.1%}}<extra></extra>",
        ))

    # Portafoglio ottimale
    fig.add_trace(go.Scatter(
        x=[optimal_vol], y=[optimal_ret],
        mode="markers",
        name="Portafoglio Ottimale",
        marker=dict(size=18, color="#ef4444", symbol="star", line=dict(color="white", width=2)),
        hovertemplate=f"<b>Ottimale</b><br>Vol: %{{x:.1%}}<br>Ret: %{{y:.1%}}<extra></extra>",
    ))

    fig.update_layout(
        **CHART_THEME,
        title=dict(text="Frontiera Efficiente di Markowitz", font=dict(size=14, weight=700), x=0),
        xaxis=dict(**CHART_THEME["xaxis"], title="Volatilità (Rischio)", tickformat=".0%"),
        yaxis=dict(**CHART_THEME["yaxis"], title="Rendimento Atteso", tickformat=".0%"),
        height=height,
    )
    return fig


def prediction_chart(
    dates: List[str],
    normal: List[float],
    best: List[float],
    worst: List[float],
    initial_value: float,
    height: int = 380,
) -> go.Figure:
    """Grafico scenari predittivi"""
    fig = go.Figure()

    # Area tra worst e best
    fig.add_trace(go.Scatter(
        x=dates + dates[::-1],
        y=best + worst[::-1],
        fill="toself",
        fillcolor="rgba(36,113,200,0.08)",
        line=dict(color="rgba(255,255,255,0)"),
        name="Range Scenari",
        showlegend=True,
        hoverinfo="skip",
    ))

    # Scenario peggiore
    fig.add_trace(go.Scatter(
        x=dates, y=worst,
        mode="lines",
        name="Scenario Peggiore",
        line=dict(color="#ef4444", width=1.8, dash="dash"),
        hovertemplate="Peggiore: €%{y:,.0f}<extra></extra>",
    ))

    # Scenario migliore
    fig.add_trace(go.Scatter(
        x=dates, y=best,
        mode="lines",
        name="Scenario Migliore",
        line=dict(color="#22c55e", width=1.8, dash="dash"),
        hovertemplate="Migliore: €%{y:,.0f}<extra></extra>",
    ))

    # Scenario normale
    fig.add_trace(go.Scatter(
        x=dates, y=normal,
        mode="lines",
        name="Scenario Atteso",
        line=dict(color="#2471c8", width=2.5),
        hovertemplate="Atteso: €%{y:,.0f}<extra></extra>",
    ))

    # Linea valore iniziale
    fig.add_hline(y=initial_value, line_dash="dot", line_color="#6b7280",
                  annotation_text=f"Valore iniziale: €{initial_value:,.0f}",
                  annotation_position="bottom right")

    fig.update_layout(
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["plot_bgcolor"],
        font=CHART_THEME["font"],
        margin=CHART_THEME["margin"],
        xaxis=CHART_THEME["xaxis"],
        legend=CHART_THEME["legend"],
        hovermode=CHART_THEME["hovermode"],
        title=dict(text="Scenari Predittivi a 6 Mesi", font=dict(size=14, weight=700), x=0),
        height=height,
    )

    # Aggiorna yaxis separatamente per evitare conflitti
    fig.update_yaxes(
        title="Valore Portafoglio (€)",
        tickformat=",.0f",
        showgrid=True,
        gridcolor="#e5eef8",
        gridwidth=1,
        zeroline=False,
        linecolor="#c8daea"
    )
    return fig


def drawdown_chart(portfolio_value: pd.Series, height: int = 220) -> go.Figure:
    """Grafico drawdown"""
    running_max = portfolio_value.cummax()
    drawdown = ((portfolio_value - running_max) / running_max) * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=drawdown.index, y=drawdown.values,
        mode="lines",
        fill="tozeroy",
        fillcolor="rgba(239,68,68,0.15)",
        line=dict(color="#ef4444", width=1.5),
        name="Drawdown",
        hovertemplate="%{y:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        **CHART_THEME,
        title=dict(text="Drawdown", font=dict(size=12, weight=700), x=0),
        yaxis=dict(**CHART_THEME["yaxis"], title="%", ticksuffix="%"),
        height=height,
    )
    return fig


def heatmap_correlation(corr_matrix: pd.DataFrame, height: int = 320) -> go.Figure:
    """Heatmap di correlazione"""
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns.tolist(),
        y=corr_matrix.columns.tolist(),
        colorscale=[[0,"#ef4444"],[0.5,"#f3f4f6"],[1,"#2471c8"]],
        zmid=0,
        zmin=-1, zmax=1,
        text=[[f"{v:.2f}" for v in row] for row in corr_matrix.values],
        texttemplate="%{text}",
        textfont=dict(size=11, weight=600),
        hovertemplate="%{x} / %{y}: %{z:.2f}<extra></extra>",
    ))
    fig.update_layout(
        **{k: v for k, v in CHART_THEME.items() if k not in ["xaxis","yaxis"]},
        title=dict(text="Matrice di Correlazione", font=dict(size=13, weight=700), x=0),
        height=height,
    )
    return fig


def seasonality_bar(monthly_returns: Dict[str, float], height: int = 250) -> go.Figure:
    """Bar chart stagionalità mensile"""
    months = list(monthly_returns.keys())
    values = list(monthly_returns.values())
    colors = ["#22c55e" if v >= 0 else "#ef4444" for v in values]

    fig = go.Figure(go.Bar(
        x=months, y=values,
        marker_color=colors,
        text=[f"{v:+.1f}%" for v in values],
        textposition="outside",
        textfont=dict(size=10, weight=600),
        hovertemplate="%{x}: %{y:.2f}%<extra></extra>",
    ))

    # Crea una copia del theme senza yaxis per evitare conflitti
    theme_copy = {k: v for k, v in CHART_THEME.items() if k != "yaxis"}

    fig.update_layout(
        **theme_copy,
        title=dict(text="Stagionalità Mensile", font=dict(size=13, weight=700), x=0),
        yaxis=dict(**CHART_THEME["yaxis"], title="%", ticksuffix="%"),
        height=height,
    )
    fig.add_hline(y=0, line_color="#9ca3af", line_width=1)
    return fig
