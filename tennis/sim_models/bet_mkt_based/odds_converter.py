"""
Betting Odds Conversion Utilities

Handles conversion between different odds formats and probability calculations.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple


@dataclass
class BettingMarket:
    """Represents betting market data for a tennis match."""
    
    # Player names
    player1: str
    player2: str
    
    # Moneyline odds (American format: +150, -200, etc.)
    player1_ml: Optional[int] = None
    player2_ml: Optional[int] = None
    
    # Set spread (e.g., player1 -1.5 sets)
    set_spread: Optional[float] = None
    set_spread_odds: Optional[int] = None
    
    # Games spread (e.g., player1 -3.5 games)
    games_spread: Optional[float] = None
    games_spread_odds: Optional[int] = None
    
    # Additional metadata
    surface: str = "Hard"
    tournament: Optional[str] = None
    best_of_5: bool = False


class OddsConverter:
    """Utility class for converting betting odds to probabilities."""
    
    @staticmethod
    def american_to_probability(odds: int) -> float:
        """
        Convert American odds to implied probability.
        
        Args:
            odds: American odds (e.g., +150, -200)
            
        Returns:
            Implied probability as decimal (0.0 to 1.0)
        """
        if odds > 0:
            # Positive odds: probability = 100 / (odds + 100)
            return 100 / (odds + 100)
        else:
            # Negative odds: probability = abs(odds) / (abs(odds) + 100)
            return abs(odds) / (abs(odds) + 100)
    
    @staticmethod
    def probability_to_american(probability: float) -> int:
        """
        Convert probability to American odds.
        
        Args:
            probability: Probability as decimal (0.0 to 1.0)
            
        Returns:
            American odds
        """
        if probability >= 0.5:
            # Favorite: negative odds
            return int(-100 * probability / (1 - probability))
        else:
            # Underdog: positive odds
            return int(100 * (1 - probability) / probability)
    
    @staticmethod
    def remove_vig(prob1: float, prob2: float) -> Tuple[float, float]:
        """
        Remove vigorish (bookmaker margin) from probabilities.
        
        Args:
            prob1: Implied probability for player 1
            prob2: Implied probability for player 2
            
        Returns:
            Tuple of true probabilities (prob1, prob2)
        """
        total = prob1 + prob2
        if total <= 1.0:
            # No vig detected, return as-is
            return prob1, prob2
        
        # Remove vig proportionally
        true_prob1 = prob1 / total
        true_prob2 = prob2 / total
        
        return true_prob1, true_prob2
    
    @staticmethod
    def analyze_moneyline(ml1: int, ml2: int) -> Dict[str, float]:
        """
        Analyze moneyline odds to get match win probabilities.
        
        Args:
            ml1: Player 1 moneyline odds
            ml2: Player 2 moneyline odds
            
        Returns:
            Dictionary with probability analysis
        """
        # Convert to implied probabilities
        prob1_implied = OddsConverter.american_to_probability(ml1)
        prob2_implied = OddsConverter.american_to_probability(ml2)
        
        # Remove vig
        prob1_true, prob2_true = OddsConverter.remove_vig(prob1_implied, prob2_implied)
        
        return {
            'player1_match_prob': prob1_true,
            'player2_match_prob': prob2_true,
            'player1_ml_implied': prob1_implied,
            'player2_ml_implied': prob2_implied,
            'vig_amount': (prob1_implied + prob2_implied) - 1.0
        }
    
    @staticmethod
    def analyze_spread(spread: float, spread_odds: int) -> Dict[str, float]:
        """
        Analyze spread betting line.
        
        Args:
            spread: Point/set/games spread
            spread_odds: Odds for the spread bet
            
        Returns:
            Dictionary with spread analysis
        """
        spread_prob = OddsConverter.american_to_probability(spread_odds)
        
        return {
            'spread_value': spread,
            'spread_probability': spread_prob,
            'spread_odds': spread_odds,
            'implied_dominance': abs(spread) * 0.1  # Simple dominance estimate
        }


# Dummy data for testing and development
SAMPLE_MARKETS = [
    BettingMarket(
        player1="Carlos Alcaraz",
        player2="Damir Dzumhur", 
        player1_ml=-2000,  # Heavy favorite
        player2_ml=+1200,  # Big underdog
        set_spread=-2.5,
        set_spread_odds=-110,
        games_spread=-8.5,
        games_spread_odds=-105,
        surface="Clay"
    ),
    BettingMarket(
        player1="Ben Shelton",
        player2="Matteo Gigante",
        player1_ml=-180,   # Moderate favorite
        player2_ml=+155,   # Moderate underdog
        set_spread=-1.5,
        set_spread_odds=-115,
        games_spread=-3.5,
        games_spread_odds=-110,
        surface="Clay"
    ),
    BettingMarket(
        player1="Elena Rybakina",
        player2="Jelena Ostapenko",
        player1_ml=-125,   # Slight favorite
        player2_ml=+105,   # Slight underdog
        set_spread=-1.5,
        set_spread_odds=-105,
        games_spread=-2.5,
        games_spread_odds=-108,
        surface="Clay"
    )
]
