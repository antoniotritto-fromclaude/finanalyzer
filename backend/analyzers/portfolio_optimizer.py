"""
Portfolio Optimizer usando la teoria di Markowitz
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from pypfopt import EfficientFrontier, risk_models, expected_returns
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PortfolioOptimizer:
    """Ottimizzatore di portafoglio basato su teoria di Markowitz"""

    def __init__(self, prices_df: pd.DataFrame):
        """
        Inizializza l'ottimizzatore

        Args:
            prices_df: DataFrame con prezzi storici (colonne = simboli, righe = date)
        """
        self.prices = prices_df
        self.returns = None
        self.mu = None  # Expected returns
        self.S = None   # Covariance matrix

    def calculate_returns(self) -> pd.DataFrame:
        """
        Calcola i rendimenti giornalieri

        Returns:
            DataFrame con rendimenti
        """
        self.returns = self.prices.pct_change().dropna()
        return self.returns

    def calculate_expected_returns(self, method: str = "mean_historical_return") -> pd.Series:
        """
        Calcola i rendimenti attesi

        Args:
            method: Metodo di calcolo (mean_historical_return, ema_historical_return, capm_return)

        Returns:
            Serie con rendimenti attesi per ogni asset
        """
        if method == "mean_historical_return":
            self.mu = expected_returns.mean_historical_return(self.prices)
        elif method == "ema_historical_return":
            self.mu = expected_returns.ema_historical_return(self.prices)
        elif method == "capm_return":
            self.mu = expected_returns.capm_return(self.prices)
        else:
            self.mu = expected_returns.mean_historical_return(self.prices)

        return self.mu

    def calculate_covariance_matrix(self, method: str = "sample_cov") -> pd.DataFrame:
        """
        Calcola la matrice di covarianza

        Args:
            method: Metodo di calcolo (sample_cov, semicovariance, exp_cov, ledoit_wolf, oracle_approximating)

        Returns:
            Matrice di covarianza
        """
        if method == "sample_cov":
            self.S = risk_models.sample_cov(self.prices)
        elif method == "semicovariance":
            self.S = risk_models.semicovariance(self.prices)
        elif method == "exp_cov":
            self.S = risk_models.exp_cov(self.prices)
        elif method == "ledoit_wolf":
            self.S = risk_models.CovarianceShrinkage(self.prices).ledoit_wolf()
        elif method == "oracle_approximating":
            self.S = risk_models.CovarianceShrinkage(self.prices).oracle_approximating()
        else:
            self.S = risk_models.sample_cov(self.prices)

        return self.S

    def optimize_max_sharpe(self, risk_free_rate: float = 0.02) -> Dict:
        """
        Ottimizza per massimizzare lo Sharpe Ratio

        Args:
            risk_free_rate: Tasso risk-free (default 2%)

        Returns:
            Dizionario con pesi ottimali e performance
        """
        if self.mu is None:
            self.calculate_expected_returns()
        if self.S is None:
            self.calculate_covariance_matrix()

        ef = EfficientFrontier(self.mu, self.S)
        weights = ef.max_sharpe(risk_free_rate=risk_free_rate)
        cleaned_weights = ef.clean_weights()

        performance = ef.portfolio_performance(risk_free_rate=risk_free_rate)

        return {
            'weights': cleaned_weights,
            'expected_return': performance[0],
            'volatility': performance[1],
            'sharpe_ratio': performance[2]
        }

    def optimize_min_volatility(self) -> Dict:
        """
        Ottimizza per minimizzare la volatilità

        Returns:
            Dizionario con pesi ottimali e performance
        """
        if self.mu is None:
            self.calculate_expected_returns()
        if self.S is None:
            self.calculate_covariance_matrix()

        ef = EfficientFrontier(self.mu, self.S)
        weights = ef.min_volatility()
        cleaned_weights = ef.clean_weights()

        performance = ef.portfolio_performance()

        return {
            'weights': cleaned_weights,
            'expected_return': performance[0],
            'volatility': performance[1],
            'sharpe_ratio': performance[2]
        }

    def optimize_efficient_risk(self, target_volatility: float) -> Dict:
        """
        Ottimizza per un target di volatilità

        Args:
            target_volatility: Volatilità target (es. 0.15 per 15%)

        Returns:
            Dizionario con pesi ottimali e performance
        """
        if self.mu is None:
            self.calculate_expected_returns()
        if self.S is None:
            self.calculate_covariance_matrix()

        ef = EfficientFrontier(self.mu, self.S)
        weights = ef.efficient_risk(target_volatility)
        cleaned_weights = ef.clean_weights()

        performance = ef.portfolio_performance()

        return {
            'weights': cleaned_weights,
            'expected_return': performance[0],
            'volatility': performance[1],
            'sharpe_ratio': performance[2]
        }

    def optimize_efficient_return(self, target_return: float) -> Dict:
        """
        Ottimizza per un target di rendimento

        Args:
            target_return: Rendimento target (es. 0.20 per 20%)

        Returns:
            Dizionario con pesi ottimali e performance
        """
        if self.mu is None:
            self.calculate_expected_returns()
        if self.S is None:
            self.calculate_covariance_matrix()

        ef = EfficientFrontier(self.mu, self.S)
        weights = ef.efficient_return(target_return)
        cleaned_weights = ef.clean_weights()

        performance = ef.portfolio_performance()

        return {
            'weights': cleaned_weights,
            'expected_return': performance[0],
            'volatility': performance[1],
            'sharpe_ratio': performance[2]
        }

    def calculate_efficient_frontier(self, points: int = 100) -> Tuple[List[float], List[float]]:
        """
        Calcola la frontiera efficiente

        Args:
            points: Numero di punti sulla frontiera

        Returns:
            Tuple (lista volatilità, lista rendimenti)
        """
        if self.mu is None:
            self.calculate_expected_returns()
        if self.S is None:
            self.calculate_covariance_matrix()

        # Trova il range di rendimenti
        min_vol_result = self.optimize_min_volatility()
        max_sharpe_result = self.optimize_max_sharpe()

        min_return = min_vol_result['expected_return']
        max_return = max_sharpe_result['expected_return'] * 1.5  # Un po' oltre il max sharpe

        target_returns = np.linspace(min_return, max_return, points)

        volatilities = []
        returns = []

        for target_return in target_returns:
            try:
                ef = EfficientFrontier(self.mu, self.S)
                ef.efficient_return(target_return)
                performance = ef.portfolio_performance()

                returns.append(performance[0])
                volatilities.append(performance[1])
            except Exception as e:
                # Se non può raggiungere quel rendimento, salta
                continue

        return volatilities, returns

    def calculate_portfolio_stats(self, weights: Dict[str, float]) -> Dict:
        """
        Calcola statistiche per un portafoglio con pesi specificati

        Args:
            weights: Dizionario {symbol: weight}

        Returns:
            Dizionario con statistiche
        """
        if self.returns is None:
            self.calculate_returns()

        # Converti weights in array nell'ordine corretto
        weight_array = np.array([weights.get(symbol, 0) for symbol in self.prices.columns])

        # Calcola rendimento del portafoglio
        portfolio_returns = (self.returns * weight_array).sum(axis=1)

        # Calcola statistiche
        annual_return = portfolio_returns.mean() * 252  # 252 trading days
        annual_volatility = portfolio_returns.std() * np.sqrt(252)
        sharpe_ratio = annual_return / annual_volatility if annual_volatility > 0 else 0

        # Calcola drawdown
        cumulative_returns = (1 + portfolio_returns).cumprod()
        running_max = cumulative_returns.cummax()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()

        return {
            'annual_return': annual_return,
            'annual_volatility': annual_volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'cumulative_return': cumulative_returns.iloc[-1] - 1 if len(cumulative_returns) > 0 else 0
        }

    def discrete_allocation(
        self,
        weights: Dict[str, float],
        total_portfolio_value: float
    ) -> Tuple[Dict[str, int], float]:
        """
        Calcola l'allocazione discreta (numero di azioni da comprare)

        Args:
            weights: Pesi ottimali
            total_portfolio_value: Valore totale del portafoglio

        Returns:
            Tuple (dizionario {symbol: num_shares}, leftover_cash)
        """
        latest_prices = get_latest_prices(self.prices)

        da = DiscreteAllocation(
            weights,
            latest_prices,
            total_portfolio_value=total_portfolio_value
        )

        allocation, leftover = da.greedy_portfolio()

        return allocation, leftover
