"""
Backtest Engine
Sistema di backtesting per portafogli
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BacktestEngine:
    """Engine per backtesting di portafogli"""

    def __init__(self, prices_df: pd.DataFrame):
        """
        Inizializza il backtest engine

        Args:
            prices_df: DataFrame con prezzi storici (colonne = simboli, righe = date)
        """
        self.prices = prices_df
        self.returns = prices_df.pct_change().dropna()

    def backtest_portfolio(
        self,
        weights: Dict[str, float],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        initial_value: float = 10000.0,
        rebalance_frequency: Optional[str] = None
    ) -> Dict:
        """
        Esegue backtest di un portafoglio

        Args:
            weights: Pesi del portafoglio {symbol: weight}
            start_date: Data inizio backtest (YYYY-MM-DD)
            end_date: Data fine backtest (YYYY-MM-DD)
            initial_value: Valore iniziale del portafoglio
            rebalance_frequency: Frequenza di ribilanciamento (None, 'monthly', 'quarterly', 'yearly')

        Returns:
            Dizionario con risultati del backtest
        """
        # Filtra date
        prices = self.prices.copy()
        if start_date:
            prices = prices[prices.index >= start_date]
        if end_date:
            prices = prices[prices.index <= end_date]

        if prices.empty:
            raise ValueError("Nessun dato disponibile per il periodo selezionato")

        # Calcola rendimenti
        returns = prices.pct_change().dropna()

        # Converti weights in array
        weight_array = np.array([weights.get(symbol, 0) for symbol in prices.columns])

        # Normalizza i pesi
        weight_array = weight_array / weight_array.sum()

        # Calcola rendimenti del portafoglio
        if rebalance_frequency is None:
            # Buy and hold
            portfolio_returns = (returns * weight_array).sum(axis=1)
        else:
            # Con ribilanciamento
            portfolio_returns = self._calculate_returns_with_rebalancing(
                prices, weight_array, rebalance_frequency
            )

        # Calcola valore del portafoglio nel tempo
        portfolio_value = initial_value * (1 + portfolio_returns).cumprod()
        portfolio_value.iloc[0] = initial_value  # Set initial value

        # Calcola metriche
        metrics = self._calculate_backtest_metrics(portfolio_returns, portfolio_value, initial_value)

        # Aggiungi dati temporali
        metrics['portfolio_value_over_time'] = portfolio_value.to_dict()
        metrics['daily_returns'] = portfolio_returns.to_dict()

        return metrics

    def _calculate_returns_with_rebalancing(
        self,
        prices: pd.DataFrame,
        weights: np.ndarray,
        frequency: str
    ) -> pd.Series:
        """
        Calcola rendimenti con ribilanciamento periodico

        Args:
            prices: DataFrame prezzi
            weights: Array dei pesi
            frequency: Frequenza ('monthly', 'quarterly', 'yearly')

        Returns:
            Serie di rendimenti
        """
        returns = prices.pct_change().dropna()
        portfolio_returns = pd.Series(index=returns.index, dtype=float)

        # Determina date di ribilanciamento
        if frequency == 'monthly':
            rebalance_dates = returns.resample('M').last().index
        elif frequency == 'quarterly':
            rebalance_dates = returns.resample('Q').last().index
        elif frequency == 'yearly':
            rebalance_dates = returns.resample('Y').last().index
        else:
            rebalance_dates = [returns.index[-1]]

        current_weights = weights.copy()

        for i in range(len(returns)):
            date = returns.index[i]

            # Calcola rendimento giornaliero
            daily_returns = returns.iloc[i].values
            portfolio_return = np.dot(current_weights, daily_returns)
            portfolio_returns.iloc[i] = portfolio_return

            # Aggiorna pesi in base ai rendimenti (drift)
            current_weights = current_weights * (1 + daily_returns)
            current_weights = current_weights / current_weights.sum()

            # Ribilancia se necessario
            if date in rebalance_dates:
                current_weights = weights.copy()

        return portfolio_returns

    def _calculate_backtest_metrics(
        self,
        returns: pd.Series,
        portfolio_value: pd.Series,
        initial_value: float
    ) -> Dict:
        """
        Calcola metriche di performance del backtest

        Args:
            returns: Serie di rendimenti giornalieri
            portfolio_value: Serie del valore del portafoglio
            initial_value: Valore iniziale

        Returns:
            Dizionario con metriche
        """
        # Rendimenti
        total_return = (portfolio_value.iloc[-1] - initial_value) / initial_value
        annual_return = returns.mean() * 252

        # Volatilità
        annual_volatility = returns.std() * np.sqrt(252)

        # Sharpe Ratio (assumendo risk-free rate = 2%)
        risk_free_rate = 0.02
        sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility if annual_volatility > 0 else 0

        # Sortino Ratio (usa solo downside volatility)
        downside_returns = returns[returns < 0]
        downside_volatility = downside_returns.std() * np.sqrt(252)
        sortino_ratio = (annual_return - risk_free_rate) / downside_volatility if downside_volatility > 0 else 0

        # Maximum Drawdown
        running_max = portfolio_value.cummax()
        drawdown = (portfolio_value - running_max) / running_max
        max_drawdown = drawdown.min()

        # Calmar Ratio
        calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0

        # Win Rate
        win_rate = (returns > 0).sum() / len(returns)

        # Best/Worst Day
        best_day = returns.max()
        worst_day = returns.min()

        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'annual_volatility': annual_volatility,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'calmar_ratio': calmar_ratio,
            'win_rate': win_rate,
            'best_day': best_day,
            'worst_day': worst_day,
            'final_value': portfolio_value.iloc[-1],
            'initial_value': initial_value
        }

    def backtest_multiple_periods(
        self,
        weights: Dict[str, float],
        periods: List[int] = [1, 3, 5, 7],
        initial_value: float = 10000.0
    ) -> Dict[int, Dict]:
        """
        Esegue backtest su multipli periodi

        Args:
            weights: Pesi del portafoglio
            periods: Lista di anni da testare [1, 3, 5, 7]
            initial_value: Valore iniziale

        Returns:
            Dizionario {years: metrics}
        """
        results = {}

        today = self.prices.index[-1]

        for years in periods:
            start_date = today - timedelta(days=years * 365)

            # Verifica che ci siano dati sufficienti
            if start_date < self.prices.index[0]:
                logger.warning(f"Dati insufficienti per backtest a {years} anni")
                continue

            try:
                result = self.backtest_portfolio(
                    weights=weights,
                    start_date=start_date.strftime('%Y-%m-%d'),
                    end_date=today.strftime('%Y-%m-%d'),
                    initial_value=initial_value
                )
                results[years] = result
            except Exception as e:
                logger.error(f"Errore nel backtest a {years} anni: {e}")

        return results

    def compare_portfolios(
        self,
        portfolios: Dict[str, Dict[str, float]],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        initial_value: float = 10000.0
    ) -> Dict[str, Dict]:
        """
        Confronta multipli portafogli

        Args:
            portfolios: Dizionario {portfolio_name: weights}
            start_date: Data inizio
            end_date: Data fine
            initial_value: Valore iniziale

        Returns:
            Dizionario {portfolio_name: metrics}
        """
        results = {}

        for name, weights in portfolios.items():
            try:
                result = self.backtest_portfolio(
                    weights=weights,
                    start_date=start_date,
                    end_date=end_date,
                    initial_value=initial_value
                )
                results[name] = result
            except Exception as e:
                logger.error(f"Errore nel backtest di {name}: {e}")

        return results

    def monte_carlo_simulation(
        self,
        weights: Dict[str, float],
        num_simulations: int = 1000,
        num_days: int = 252,
        initial_value: float = 10000.0
    ) -> Dict:
        """
        Esegue simulazione Monte Carlo

        Args:
            weights: Pesi del portafoglio
            num_simulations: Numero di simulazioni
            num_days: Numero di giorni da simulare
            initial_value: Valore iniziale

        Returns:
            Dizionario con risultati della simulazione
        """
        # Calcola media e covarianza dai rendimenti storici
        weight_array = np.array([weights.get(symbol, 0) for symbol in self.prices.columns])
        weight_array = weight_array / weight_array.sum()

        mean_returns = self.returns.mean().values
        cov_matrix = self.returns.cov().values

        # Esegui simulazioni
        simulations = np.zeros((num_simulations, num_days))

        for i in range(num_simulations):
            # Genera rendimenti casuali
            random_returns = np.random.multivariate_normal(mean_returns, cov_matrix, num_days)

            # Calcola rendimenti del portafoglio
            portfolio_returns = np.dot(random_returns, weight_array)

            # Calcola valore del portafoglio
            portfolio_values = initial_value * np.cumprod(1 + portfolio_returns)
            simulations[i] = portfolio_values

        # Calcola statistiche
        final_values = simulations[:, -1]

        return {
            'mean_final_value': np.mean(final_values),
            'median_final_value': np.median(final_values),
            'std_final_value': np.std(final_values),
            'percentile_5': np.percentile(final_values, 5),
            'percentile_25': np.percentile(final_values, 25),
            'percentile_75': np.percentile(final_values, 75),
            'percentile_95': np.percentile(final_values, 95),
            'simulations': simulations.tolist()
        }
