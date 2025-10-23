"""
Test per Portfolio Optimizer
"""
import pytest
import pandas as pd
import numpy as np
from backend.analyzers.portfolio_optimizer import PortfolioOptimizer


def create_sample_prices():
    """Crea dati di test"""
    dates = pd.date_range('2020-01-01', '2023-12-31', freq='D')
    np.random.seed(42)

    data = {
        'AAPL': 100 * np.cumprod(1 + np.random.randn(len(dates)) * 0.01),
        'MSFT': 200 * np.cumprod(1 + np.random.randn(len(dates)) * 0.01),
        'GOOGL': 150 * np.cumprod(1 + np.random.randn(len(dates)) * 0.01),
    }

    return pd.DataFrame(data, index=dates)


def test_portfolio_optimizer_initialization():
    """Test inizializzazione"""
    prices = create_sample_prices()
    optimizer = PortfolioOptimizer(prices)

    assert optimizer.prices is not None
    assert len(optimizer.prices.columns) == 3


def test_calculate_returns():
    """Test calcolo rendimenti"""
    prices = create_sample_prices()
    optimizer = PortfolioOptimizer(prices)

    returns = optimizer.calculate_returns()

    assert returns is not None
    assert len(returns) < len(prices)  # Perde una riga per il calcolo


def test_max_sharpe_optimization():
    """Test ottimizzazione Max Sharpe"""
    prices = create_sample_prices()
    optimizer = PortfolioOptimizer(prices)

    result = optimizer.optimize_max_sharpe()

    assert 'weights' in result
    assert 'expected_return' in result
    assert 'volatility' in result
    assert 'sharpe_ratio' in result

    # I pesi devono sommare a 1
    total_weight = sum(result['weights'].values())
    assert abs(total_weight - 1.0) < 0.01


def test_min_volatility_optimization():
    """Test ottimizzazione Min Volatility"""
    prices = create_sample_prices()
    optimizer = PortfolioOptimizer(prices)

    result = optimizer.optimize_min_volatility()

    assert 'weights' in result
    assert result['volatility'] >= 0


def test_efficient_frontier():
    """Test calcolo frontiera efficiente"""
    prices = create_sample_prices()
    optimizer = PortfolioOptimizer(prices)

    volatilities, returns = optimizer.calculate_efficient_frontier(points=20)

    assert len(volatilities) > 0
    assert len(returns) > 0
    assert len(volatilities) == len(returns)


if __name__ == "__main__":
    pytest.main([__file__])
