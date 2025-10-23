"""
FastAPI Main Application
API per la piattaforma FinAnalyzer
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging

from backend.data_collectors.unified_collector import UnifiedDataCollector
from backend.analyzers.portfolio_optimizer import PortfolioOptimizer
from backend.analyzers.backtest import BacktestEngine
from backend.models.predictor import PortfolioPredictor, AssetPredictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="FinAnalyzer API",
    description="API per analisi finanziaria completa",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize data collector
collector = UnifiedDataCollector()


# Pydantic Models
class SearchRequest(BaseModel):
    query: str
    asset_type: Optional[str] = None


class PortfolioRequest(BaseModel):
    symbols: List[str]
    period: str = "1y"


class OptimizationRequest(BaseModel):
    symbols: List[str]
    period: str = "1y"
    optimization_type: str = "max_sharpe"  # max_sharpe, min_volatility
    target_return: Optional[float] = None
    target_volatility: Optional[float] = None


class BacktestRequest(BaseModel):
    symbols: List[str]
    weights: Dict[str, float]
    periods: List[int] = [1, 3, 5, 7]
    initial_value: float = 10000.0


class PredictionRequest(BaseModel):
    symbols: List[str]
    weights: Dict[str, float]
    months: int = 6
    initial_value: float = 10000.0


# Endpoints
@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "name": "FinAnalyzer API",
        "version": "1.0.0",
        "status": "active"
    }


@app.post("/search")
def search_instruments(request: SearchRequest):
    """
    Cerca strumenti finanziari

    - **query**: Termine di ricerca (simbolo o nome)
    - **asset_type**: Tipo di asset (opzionale)
    """
    try:
        results = collector.search_all_sources(request.query, request.asset_type)
        return {
            "success": True,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Errore nella ricerca: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/asset/info")
def get_asset_info(symbol: str):
    """
    Ottiene informazioni dettagliate su un asset

    - **symbol**: Simbolo dell'asset
    """
    try:
        info = collector.get_asset_info(symbol)
        if not info:
            raise HTTPException(status_code=404, detail=f"Asset {symbol} non trovato")

        return {
            "success": True,
            "data": info
        }
    except Exception as e:
        logger.error(f"Errore nel recupero info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/portfolio/data")
def get_portfolio_data(request: PortfolioRequest):
    """
    Ottiene dati storici per un portafoglio

    - **symbols**: Lista di simboli
    - **period**: Periodo (1y, 3y, 5y, 7y)
    """
    try:
        prices_df = collector.get_historical_prices(
            request.symbols,
            period=request.period
        )

        if prices_df.empty:
            raise HTTPException(status_code=404, detail="Nessun dato disponibile")

        return {
            "success": True,
            "symbols": request.symbols,
            "data": prices_df.to_dict(orient='index')
        }
    except Exception as e:
        logger.error(f"Errore nel recupero dati portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/portfolio/optimize")
def optimize_portfolio(request: OptimizationRequest):
    """
    Ottimizza un portafoglio secondo Markowitz

    - **symbols**: Lista di simboli
    - **period**: Periodo storico per analisi
    - **optimization_type**: Tipo di ottimizzazione (max_sharpe, min_volatility, efficient_return, efficient_risk)
    """
    try:
        # Ottieni dati
        prices_df = collector.get_historical_prices(
            request.symbols,
            period=request.period
        )

        if prices_df.empty:
            raise HTTPException(status_code=404, detail="Nessun dato disponibile")

        # Ottimizza
        optimizer = PortfolioOptimizer(prices_df)
        optimizer.calculate_expected_returns()
        optimizer.calculate_covariance_matrix()

        if request.optimization_type == "max_sharpe":
            result = optimizer.optimize_max_sharpe()
        elif request.optimization_type == "min_volatility":
            result = optimizer.optimize_min_volatility()
        elif request.optimization_type == "efficient_return" and request.target_return:
            result = optimizer.optimize_efficient_return(request.target_return)
        elif request.optimization_type == "efficient_risk" and request.target_volatility:
            result = optimizer.optimize_efficient_risk(request.target_volatility)
        else:
            result = optimizer.optimize_max_sharpe()

        # Calcola frontiera efficiente
        volatilities, returns = optimizer.calculate_efficient_frontier()

        return {
            "success": True,
            "optimization_type": request.optimization_type,
            "optimal_weights": result['weights'],
            "expected_return": result['expected_return'],
            "volatility": result['volatility'],
            "sharpe_ratio": result['sharpe_ratio'],
            "efficient_frontier": {
                "volatilities": volatilities,
                "returns": returns
            }
        }
    except Exception as e:
        logger.error(f"Errore nell'ottimizzazione: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/portfolio/backtest")
def backtest_portfolio(request: BacktestRequest):
    """
    Esegue backtest di un portafoglio

    - **symbols**: Lista di simboli
    - **weights**: Pesi del portafoglio
    - **periods**: Lista di anni da testare [1, 3, 5, 7]
    - **initial_value**: Valore iniziale del portafoglio
    """
    try:
        # Ottieni dati per il periodo più lungo
        max_period = max(request.periods)
        prices_df = collector.get_historical_prices(
            request.symbols,
            period=f"{max_period}y"
        )

        if prices_df.empty:
            raise HTTPException(status_code=404, detail="Nessun dato disponibile")

        # Backtest
        backtest_engine = BacktestEngine(prices_df)
        results = backtest_engine.backtest_multiple_periods(
            weights=request.weights,
            periods=request.periods,
            initial_value=request.initial_value
        )

        return {
            "success": True,
            "results": results
        }
    except Exception as e:
        logger.error(f"Errore nel backtest: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/portfolio/predict")
def predict_portfolio(request: PredictionRequest):
    """
    Predice scenari futuri per un portafoglio (6 mesi)

    - **symbols**: Lista di simboli
    - **weights**: Pesi del portafoglio
    - **months**: Mesi di predizione (default 6)
    - **initial_value**: Valore iniziale
    """
    try:
        # Ottieni dati storici
        prices_df = collector.get_historical_prices(
            request.symbols,
            period="3y"  # Usa 3 anni di dati per predizioni
        )

        if prices_df.empty:
            raise HTTPException(status_code=404, detail="Nessun dato disponibile")

        # Predici
        predictor = PortfolioPredictor(prices_df)
        scenarios = predictor.predict_portfolio_scenarios(
            weights=request.weights,
            months=request.months,
            initial_value=request.initial_value
        )

        # Calcola anche performance attesa
        expected_perf = predictor.calculate_expected_performance(
            weights=request.weights,
            months=request.months
        )

        # Calcola VaR
        var_result = predictor.calculate_value_at_risk(
            weights=request.weights,
            initial_value=request.initial_value
        )

        return {
            "success": True,
            "scenarios": scenarios,
            "expected_performance": expected_perf,
            "value_at_risk": var_result
        }
    except Exception as e:
        logger.error(f"Errore nella predizione: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/lists/bonds")
def get_bonds(country: str = "italy"):
    """Ottiene lista di obbligazioni"""
    try:
        bonds = collector.get_bonds(country)
        return {"success": True, "count": len(bonds), "bonds": bonds}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/lists/commodities")
def get_commodities():
    """Ottiene lista di commodities"""
    try:
        commodities = collector.get_commodities()
        return {"success": True, "count": len(commodities), "commodities": commodities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/lists/etfs")
def get_etfs(country: str = "italy"):
    """Ottiene lista di ETF"""
    try:
        etfs = collector.get_etfs(country)
        return {"success": True, "count": len(etfs), "etfs": etfs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
