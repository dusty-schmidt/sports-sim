"""
Betting Market-Based Tennis Simulation Engine

A clean, modular tennis simulation system that derives all parameters
from betting market data with zero dummy values or estimates.

Easy Integration:
    from sim_models.bet_mkt_based import BettingSimulator, BettingMarket

    market = BettingMarket("Player A", "Player B", -150, +130)
    simulator = BettingSimulator()
    result = simulator.simulate_match(market)
"""

# Core public interface
from .odds_converter import BettingMarket, OddsConverter, SAMPLE_MARKETS
from .probability_engine import ProbabilityEngine, PlayerParams
from .match_simulator import BettingSimulator
from .results_tracker import MatchResult, SimulationResults
from .validator import BettingSimulatorValidator

# Main classes for external use
__all__ = [
    # Primary interface
    'BettingSimulator',
    'BettingMarket',
    'MatchResult',

    # Advanced usage
    'OddsConverter',
    'ProbabilityEngine',
    'PlayerParams',
    'SimulationResults',
    'BettingSimulatorValidator',

    # Sample data
    'SAMPLE_MARKETS'
]

# Version info
__version__ = "2.0.0"
__author__ = "Tennis Simulation Engine"

# Convenience functions
def create_simulator(seed=None):
    """Create a betting simulator instance."""
    return BettingSimulator(seed=seed)

def validate_simulator(seed=42):
    """Run validation on the betting simulator."""
    validator = BettingSimulatorValidator(seed=seed)
    return validator.run_full_validation()

def get_sample_markets():
    """Get sample betting markets for testing."""
    return SAMPLE_MARKETS
