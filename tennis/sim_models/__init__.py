"""
Tennis Simulation Models - Betting Market Simulator

Clean, production-ready betting market tennis simulation.
No dummy data, no estimates - only real market-derived probabilities.

Quick Start:
    from sim_models import BettingSimulator, BettingMarket

    # Create market and simulate
    market = BettingMarket("Player A", "Player B", -150, +130)
    simulator = BettingSimulator()
    result = simulator.simulate_match(market)
"""

# Import betting market simulator
from .bet_mkt_based.match_simulator import BettingSimulator
from .bet_mkt_based.odds_converter import BettingMarket, SAMPLE_MARKETS
from .bet_mkt_based.results_tracker import MatchResult
from .bet_mkt_based.validator import BettingSimulatorValidator

# Export everything from betting simulator
__all__ = [
    'BettingSimulator',
    'BettingMarket',
    'MatchResult',
    'SAMPLE_MARKETS',
    'BettingSimulatorValidator'
]

# Version info
__version__ = "2.0.0"
__author__ = "Tennis Simulation Engine"
