"""
Portfolio Optimizer semplificato - Senza dipendenze da PyPortfolioOpt
Implementazione diretta della teoria di Markowitz
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy.optimize import minimize
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
        self.symbols = list(prices_df.columns)

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
            method: Metodo di calcolo

        Returns:
            Serie con rendimenti attesi per ogni asset
        """
        if self.returns is None:
            self.calculate_returns()

        # Rendimenti medi annualizzati
        self.mu = self.returns.mean() * 252
        return self.mu

    def calculate_covariance_matrix(self, method: str = "sample_cov") -> pd.DataFrame:
        """
        Calcola la matrice di covarianza

        Args:
            method: Metodo di calcolo

        Returns:
            Matrice di covarianza
        """
        if self.returns is None:
            self.calculate_returns()

        # Covarianza annualizzata
        self.S = self.returns.cov() * 252
        return self.S

    def _portfolio_stats(self, weights: np.ndarray) -> Tuple[float, float, float]:
        """
        Calcola statistiche del portafoglio

        Args:
            weights: Array dei pesi

        Returns:
            Tuple (rendimento, volatilità, sharpe ratio)
        """
        portfolio_return = np.dot(weights, self.mu)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(self.S, weights)))
        sharpe_ratio = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0
        return portfolio_return, portfolio_volatility, sharpe_ratio

    def _neg_sharpe_ratio(self, weights: np.ndarray, risk_free_rate: float = 0.02) -> float:
        """
        Calcola lo Sharpe Ratio negativo (per minimizzazione)

        Args:
            weights: Array dei pesi
            risk_free_rate: Tasso risk-free

        Returns:
            Sharpe ratio negativo
        """
        portfolio_return, portfolio_volatility, _ = self._portfolio_stats(weights)
        return -(portfolio_return - risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0

    def _portfolio_volatility(self, weights: np.ndarray) -> float:
        """
        Calcola la volatilità del portafoglio

        Args:
            weights: Array dei pesi

        Returns:
            Volatilità
        """
        return np.sqrt(np.dot(weights.T, np.dot(self.S, weights)))

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

        n_assets = len(self.symbols)

        # Vincoli e bounds
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})  # Pesi sommano a 1
        bounds = tuple((0, 1) for _ in range(n_assets))  # Pesi tra 0 e 1
        initial_weights = np.array([1/n_assets] * n_assets)  # Pesi uguali iniziali

        # Ottimizzazione
        result = minimize(
            self._neg_sharpe_ratio,
            initial_weights,
            args=(risk_free_rate,),
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        if not result.success:
            logger.warning(f"Ottimizzazione non convergente: {result.message}")

        # Calcola performance
        weights = result.x
        portfolio_return, portfolio_volatility, sharpe_ratio = self._portfolio_stats(weights)

        # Pulisci pesi (rimuovi molto piccoli)
        cleaned_weights = {}
        for symbol, weight in zip(self.symbols, weights):
            if weight > 0.01:  # Solo pesi > 1%
                cleaned_weights[symbol] = round(weight, 4)

        return {
            'weights': cleaned_weights,
            'expected_return': portfolio_return,
            'volatility': portfolio_volatility,
            'sharpe_ratio': sharpe_ratio
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

        n_assets = len(self.symbols)

        # Vincoli e bounds
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for _ in range(n_assets))
        initial_weights = np.array([1/n_assets] * n_assets)

        # Ottimizzazione
        result = minimize(
            self._portfolio_volatility,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        weights = result.x
        portfolio_return, portfolio_volatility, sharpe_ratio = self._portfolio_stats(weights)

        # Pulisci pesi
        cleaned_weights = {}
        for symbol, weight in zip(self.symbols, weights):
            if weight > 0.01:
                cleaned_weights[symbol] = round(weight, 4)

        return {
            'weights': cleaned_weights,
            'expected_return': portfolio_return,
            'volatility': portfolio_volatility,
            'sharpe_ratio': sharpe_ratio
        }

    def optimize_efficient_return(self, target_return: float) -> Dict:
        """
        Ottimizza per un target di rendimento

        Args:
            target_return: Rendimento target

        Returns:
            Dizionario con pesi ottimali e performance
        """
        if self.mu is None:
            self.calculate_expected_returns()
        if self.S is None:
            self.calculate_covariance_matrix()

        n_assets = len(self.symbols)

        # Vincoli
        constraints = (
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
            {'type': 'eq', 'fun': lambda x: np.dot(x, self.mu) - target_return}
        )
        bounds = tuple((0, 1) for _ in range(n_assets))
        initial_weights = np.array([1/n_assets] * n_assets)

        # Ottimizzazione
        result = minimize(
            self._portfolio_volatility,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        if not result.success:
            logger.warning(f"Ottimizzazione non convergente: {result.message}")

        weights = result.x
        portfolio_return, portfolio_volatility, sharpe_ratio = self._portfolio_stats(weights)

        cleaned_weights = {}
        for symbol, weight in zip(self.symbols, weights):
            if weight > 0.01:
                cleaned_weights[symbol] = round(weight, 4)

        return {
            'weights': cleaned_weights,
            'expected_return': portfolio_return,
            'volatility': portfolio_volatility,
            'sharpe_ratio': sharpe_ratio
        }

    def optimize_efficient_risk(self, target_volatility: float) -> Dict:
        """
        Ottimizza per un target di volatilità

        Args:
            target_volatility: Volatilità target

        Returns:
            Dizionario con pesi ottimali e performance
        """
        if self.mu is None:
            self.calculate_expected_returns()
        if self.S is None:
            self.calculate_covariance_matrix()

        n_assets = len(self.symbols)

        def neg_return(weights):
            return -np.dot(weights, self.mu)

        # Vincoli
        constraints = (
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
            {'type': 'eq', 'fun': lambda x: self._portfolio_volatility(x) - target_volatility}
        )
        bounds = tuple((0, 1) for _ in range(n_assets))
        initial_weights = np.array([1/n_assets] * n_assets)

        # Ottimizzazione
        result = minimize(
            neg_return,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        if not result.success:
            logger.warning(f"Ottimizzazione non convergente: {result.message}")

        weights = result.x
        portfolio_return, portfolio_volatility, sharpe_ratio = self._portfolio_stats(weights)

        cleaned_weights = {}
        for symbol, weight in zip(self.symbols, weights):
            if weight > 0.01:
                cleaned_weights[symbol] = round(weight, 4)

        return {
            'weights': cleaned_weights,
            'expected_return': portfolio_return,
            'volatility': portfolio_volatility,
            'sharpe_ratio': sharpe_ratio
        }

    def calculate_efficient_frontier(self, points: int = 50) -> Tuple[List[float], List[float]]:
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
        max_return = max(self.mu) * 0.95  # Un po' sotto il massimo teorico

        target_returns = np.linspace(min_return, max_return, points)

        volatilities = []
        returns = []

        for target_return in target_returns:
            try:
                result = self.optimize_efficient_return(target_return)
                returns.append(result['expected_return'])
                volatilities.append(result['volatility'])
            except Exception as e:
                logger.debug(f"Skip return {target_return}: {e}")
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
        annual_return = portfolio_returns.mean() * 252
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
        latest_prices = self.prices.iloc[-1]

        allocation = {}
        leftover = total_portfolio_value

        # Ordina per peso decrescente
        sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)

        for symbol, weight in sorted_weights:
            if symbol not in latest_prices.index:
                continue

            price = latest_prices[symbol]
            target_value = total_portfolio_value * weight
            num_shares = int(target_value / price)

            if num_shares > 0:
                allocation[symbol] = num_shares
                leftover -= num_shares * price

        return allocation, leftover
