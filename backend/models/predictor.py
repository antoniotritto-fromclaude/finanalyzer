"""
Predictive Models
Modelli predittivi per analisi finanziaria
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PortfolioPredictor:
    """Modello predittivo per portafogli finanziari"""

    def __init__(self, prices_df: pd.DataFrame):
        """
        Inizializza il predittore

        Args:
            prices_df: DataFrame con prezzi storici
        """
        self.prices = prices_df
        self.returns = prices_df.pct_change().dropna()

    def predict_portfolio_scenarios(
        self,
        weights: Dict[str, float],
        months: int = 6,
        initial_value: float = 10000.0,
        num_simulations: int = 10000
    ) -> Dict:
        """
        Predice scenari futuri per un portafoglio (normale, peggiore, migliore)

        Args:
            weights: Pesi del portafoglio
            months: Mesi di predizione (default 6)
            initial_value: Valore iniziale
            num_simulations: Numero di simulazioni Monte Carlo

        Returns:
            Dizionario con scenari predittivi
        """
        # Converti weights in array
        weight_array = np.array([weights.get(symbol, 0) for symbol in self.prices.columns])
        weight_array = weight_array / weight_array.sum()

        # Calcola statistiche dai dati storici
        mean_returns = self.returns.mean().values
        cov_matrix = self.returns.cov().values

        # Numero di giorni di trading (circa 21 giorni per mese)
        num_days = months * 21

        # Esegui simulazioni Monte Carlo
        simulations = self._run_monte_carlo(
            mean_returns,
            cov_matrix,
            weight_array,
            num_days,
            initial_value,
            num_simulations
        )

        # Calcola scenari
        scenarios = self._calculate_scenarios(simulations, initial_value)

        # Aggiungi predizioni dettagliate
        scenarios['predictions'] = self._generate_prediction_paths(
            mean_returns,
            cov_matrix,
            weight_array,
            num_days,
            initial_value
        )

        return scenarios

    def _run_monte_carlo(
        self,
        mean_returns: np.ndarray,
        cov_matrix: np.ndarray,
        weights: np.ndarray,
        num_days: int,
        initial_value: float,
        num_simulations: int
    ) -> np.ndarray:
        """
        Esegue simulazione Monte Carlo

        Returns:
            Array di simulazioni (num_simulations, num_days)
        """
        simulations = np.zeros((num_simulations, num_days))

        for i in range(num_simulations):
            # Genera rendimenti casuali basati su distribuzione storica
            random_returns = np.random.multivariate_normal(
                mean_returns,
                cov_matrix,
                num_days
            )

            # Calcola rendimenti del portafoglio
            portfolio_returns = np.dot(random_returns, weights)

            # Calcola valore del portafoglio nel tempo
            portfolio_values = initial_value * np.cumprod(1 + portfolio_returns)
            simulations[i] = portfolio_values

        return simulations

    def _calculate_scenarios(
        self,
        simulations: np.ndarray,
        initial_value: float
    ) -> Dict:
        """
        Calcola scenari da simulazioni Monte Carlo

        Args:
            simulations: Array di simulazioni
            initial_value: Valore iniziale

        Returns:
            Dizionario con scenari
        """
        final_values = simulations[:, -1]

        # Scenario Normale (mediana/50° percentile)
        normal_value = np.median(final_values)
        normal_return = (normal_value - initial_value) / initial_value

        # Scenario Peggiore (5° percentile - VaR 95%)
        worst_value = np.percentile(final_values, 5)
        worst_return = (worst_value - initial_value) / initial_value

        # Scenario Migliore (95° percentile)
        best_value = np.percentile(final_values, 95)
        best_return = (best_value - initial_value) / initial_value

        # Calcola anche altri percentili utili
        percentile_25 = np.percentile(final_values, 25)
        percentile_75 = np.percentile(final_values, 75)

        # Calcola probabilità di perdita
        probability_of_loss = (final_values < initial_value).sum() / len(final_values)

        return {
            'normal_scenario': {
                'final_value': normal_value,
                'total_return': normal_return,
                'return_percentage': normal_return * 100
            },
            'worst_scenario': {
                'final_value': worst_value,
                'total_return': worst_return,
                'return_percentage': worst_return * 100
            },
            'best_scenario': {
                'final_value': best_value,
                'total_return': best_return,
                'return_percentage': best_return * 100
            },
            'statistics': {
                'mean_value': np.mean(final_values),
                'std_value': np.std(final_values),
                'percentile_25': percentile_25,
                'percentile_75': percentile_75,
                'probability_of_loss': probability_of_loss,
                'expected_return': (np.mean(final_values) - initial_value) / initial_value
            }
        }

    def _generate_prediction_paths(
        self,
        mean_returns: np.ndarray,
        cov_matrix: np.ndarray,
        weights: np.ndarray,
        num_days: int,
        initial_value: float
    ) -> Dict:
        """
        Genera percorsi di predizione per i tre scenari

        Returns:
            Dizionario con percorsi temporali
        """
        # Genera molte simulazioni per avere distribuzioni robuste
        num_sims = 5000
        simulations = np.zeros((num_sims, num_days))

        for i in range(num_sims):
            random_returns = np.random.multivariate_normal(mean_returns, cov_matrix, num_days)
            portfolio_returns = np.dot(random_returns, weights)
            simulations[i] = initial_value * np.cumprod(1 + portfolio_returns)

        # Per ogni giorno, calcola percentili
        normal_path = []
        worst_path = []
        best_path = []

        for day in range(num_days):
            day_values = simulations[:, day]
            normal_path.append(np.percentile(day_values, 50))
            worst_path.append(np.percentile(day_values, 5))
            best_path.append(np.percentile(day_values, 95))

        # Crea date per l'asse X
        start_date = datetime.now()
        dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(num_days)]

        return {
            'dates': dates,
            'normal_path': normal_path,
            'worst_path': worst_path,
            'best_path': best_path
        }

    def calculate_value_at_risk(
        self,
        weights: Dict[str, float],
        confidence_level: float = 0.95,
        time_horizon_days: int = 1,
        initial_value: float = 10000.0
    ) -> Dict:
        """
        Calcola Value at Risk (VaR)

        Args:
            weights: Pesi del portafoglio
            confidence_level: Livello di confidenza (0.95 = 95%)
            time_horizon_days: Orizzonte temporale in giorni
            initial_value: Valore iniziale

        Returns:
            Dizionario con VaR e CVaR
        """
        # Converti weights
        weight_array = np.array([weights.get(symbol, 0) for symbol in self.prices.columns])
        weight_array = weight_array / weight_array.sum()

        # Calcola rendimenti del portafoglio
        portfolio_returns = (self.returns * weight_array).sum(axis=1)

        # VaR parametrico (assumendo distribuzione normale)
        mean_return = portfolio_returns.mean()
        std_return = portfolio_returns.std()

        # Scala per time horizon
        scaled_mean = mean_return * time_horizon_days
        scaled_std = std_return * np.sqrt(time_horizon_days)

        # Calcola VaR
        from scipy import stats
        z_score = stats.norm.ppf(1 - confidence_level)
        var_return = scaled_mean + z_score * scaled_std
        var_value = initial_value * var_return

        # Calcola CVaR (Conditional VaR / Expected Shortfall)
        # CVaR è la perdita attesa oltre il VaR
        sorted_returns = np.sort(portfolio_returns)
        var_threshold_idx = int((1 - confidence_level) * len(sorted_returns))
        cvar_returns = sorted_returns[:var_threshold_idx]
        cvar_return = cvar_returns.mean() * time_horizon_days
        cvar_value = initial_value * cvar_return

        return {
            'var_percentage': var_return * 100,
            'var_value': var_value,
            'cvar_percentage': cvar_return * 100,
            'cvar_value': cvar_value,
            'confidence_level': confidence_level,
            'time_horizon_days': time_horizon_days
        }

    def calculate_expected_performance(
        self,
        weights: Dict[str, float],
        months: int = 6
    ) -> Dict:
        """
        Calcola performance attesa basata su dati storici

        Args:
            weights: Pesi del portafoglio
            months: Periodo di predizione

        Returns:
            Dizionario con metriche predittive
        """
        # Converti weights
        weight_array = np.array([weights.get(symbol, 0) for symbol in self.prices.columns])
        weight_array = weight_array / weight_array.sum()

        # Calcola statistiche storiche
        mean_returns = self.returns.mean()
        cov_matrix = self.returns.cov()

        # Rendimento atteso del portafoglio
        expected_return = np.dot(weight_array, mean_returns) * 252  # Annualizzato

        # Volatilità del portafoglio
        portfolio_variance = np.dot(weight_array, np.dot(cov_matrix, weight_array))
        portfolio_volatility = np.sqrt(portfolio_variance) * np.sqrt(252)  # Annualizzata

        # Sharpe Ratio atteso
        risk_free_rate = 0.02
        expected_sharpe = (expected_return - risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0

        # Scala per il periodo richiesto
        period_return = expected_return * (months / 12)
        period_volatility = portfolio_volatility * np.sqrt(months / 12)

        return {
            'expected_return_annual': expected_return,
            'expected_return_period': period_return,
            'expected_volatility_annual': portfolio_volatility,
            'expected_volatility_period': period_volatility,
            'expected_sharpe_ratio': expected_sharpe,
            'period_months': months
        }


class AssetPredictor:
    """Predittore per singoli asset"""

    def __init__(self, prices_series: pd.Series):
        """
        Inizializza il predittore per un asset

        Args:
            prices_series: Serie di prezzi storici
        """
        self.prices = prices_series
        self.returns = prices_series.pct_change().dropna()

    def predict_price_scenarios(
        self,
        months: int = 6,
        num_simulations: int = 5000
    ) -> Dict:
        """
        Predice scenari di prezzo per un singolo asset

        Args:
            months: Mesi di predizione
            num_simulations: Numero di simulazioni

        Returns:
            Dizionario con scenari
        """
        current_price = self.prices.iloc[-1]
        mean_return = self.returns.mean()
        std_return = self.returns.std()

        num_days = months * 21

        # Simulazioni
        simulations = np.zeros((num_simulations, num_days))

        for i in range(num_simulations):
            # Geometric Brownian Motion
            daily_returns = np.random.normal(mean_return, std_return, num_days)
            price_path = current_price * np.cumprod(1 + daily_returns)
            simulations[i] = price_path

        final_prices = simulations[:, -1]

        return {
            'current_price': current_price,
            'normal_scenario': np.percentile(final_prices, 50),
            'worst_scenario': np.percentile(final_prices, 5),
            'best_scenario': np.percentile(final_prices, 95),
            'expected_price': np.mean(final_prices),
            'price_std': np.std(final_prices)
        }
