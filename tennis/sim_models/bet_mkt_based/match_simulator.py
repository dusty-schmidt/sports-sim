"""
Clean Betting Market Tennis Simulator

Simplified, modular implementation for easy integration.
"""

import random
from typing import List, Optional

try:
    from .odds_converter import BettingMarket, OddsConverter
    from .probability_engine import ProbabilityEngine
    from .results_tracker import MatchResult
except ImportError:
    from odds_converter import BettingMarket, OddsConverter
    from probability_engine import ProbabilityEngine
    from results_tracker import MatchResult


class BettingSimulator:
    """
    Clean tennis match simulator using only betting market data.
    
    Usage:
        simulator = BettingSimulator()
        result = simulator.simulate_match(market)
    """

    def __init__(self, seed: Optional[int] = None):
        """Initialize simulator with optional random seed."""
        if seed is not None:
            random.seed(seed)
        
        engine_seed = seed if seed is not None else 42
        self.probability_engine = ProbabilityEngine(engine_seed)

    def simulate_match(self, market: BettingMarket) -> MatchResult:
        """
        Simulate a tennis match from betting market data.
        
        Args:
            market: BettingMarket with odds and player info
            
        Returns:
            MatchResult with complete match statistics
        """
        # Convert odds to match probability
        if not market.player1_ml or not market.player2_ml:
            raise ValueError("Market must have moneyline odds")
        
        odds_analysis = OddsConverter.analyze_moneyline(market.player1_ml, market.player2_ml)
        target_p1_prob = odds_analysis['player1_match_prob']
        
        # Get calibrated service/return parameters
        params = self.probability_engine.derive_match_parameters(target_p1_prob, market.surface)
        
        # Simulate the match
        match_data = self._simulate_tennis_match(params, market.best_of_5)
        
        # Create result object
        result = MatchResult(
            player1=market.player1,
            player2=market.player2,
            surface=market.surface,
            market_win_prob_p1=target_p1_prob
        )
        
        # Fill in match results
        result.sets_won_p1 = match_data['sets_p1']
        result.sets_won_p2 = match_data['sets_p2']
        result.games_won_p1 = match_data['games_p1']
        result.games_won_p2 = match_data['games_p2']
        result.winner = market.player1 if match_data['winner'] == 1 else market.player2
        
        # Service statistics
        result.service_points_won_p1 = match_data['service_won_p1']
        result.service_points_played_p1 = match_data['service_played_p1']
        result.return_points_won_p1 = match_data['return_won_p1']
        result.return_points_played_p1 = match_data['return_played_p1']
        
        result.service_points_won_p2 = match_data['service_won_p2']
        result.service_points_played_p2 = match_data['service_played_p2']
        result.return_points_won_p2 = match_data['return_won_p2']
        result.return_points_played_p2 = match_data['return_played_p2']
        
        # Estimate aces and double faults
        result.aces_p1 = max(0, int(result.service_points_played_p1 * 0.08 * random.uniform(0.7, 1.3)))
        result.aces_p2 = max(0, int(result.service_points_played_p2 * 0.08 * random.uniform(0.7, 1.3)))
        result.double_faults_p1 = max(0, int(result.service_points_played_p1 * 0.04 * random.uniform(0.7, 1.3)))
        result.double_faults_p2 = max(0, int(result.service_points_played_p2 * 0.04 * random.uniform(0.7, 1.3)))
        
        return result

    def _simulate_tennis_match(self, params, best_of_5: bool = False):
        """Simulate a complete tennis match."""
        sets_to_win = 3 if best_of_5 else 2
        sets_p1 = 0
        sets_p2 = 0
        total_games_p1 = 0
        total_games_p2 = 0
        
        # Service tracking
        service_won_p1 = 0
        service_played_p1 = 0
        return_won_p1 = 0
        return_played_p1 = 0
        
        service_won_p2 = 0
        service_played_p2 = 0
        return_won_p2 = 0
        return_played_p2 = 0
        
        # Simulate sets
        while sets_p1 < sets_to_win and sets_p2 < sets_to_win:
            set_result = self._simulate_set(params)
            
            if set_result['winner'] == 1:
                sets_p1 += 1
            else:
                sets_p2 += 1
            
            total_games_p1 += set_result['games_p1']
            total_games_p2 += set_result['games_p2']
            
            # Update service stats
            service_won_p1 += set_result['service_won_p1']
            service_played_p1 += set_result['service_played_p1']
            return_won_p1 += set_result['return_won_p1']
            return_played_p1 += set_result['return_played_p1']
            
            service_won_p2 += set_result['service_won_p2']
            service_played_p2 += set_result['service_played_p2']
            return_won_p2 += set_result['return_won_p2']
            return_played_p2 += set_result['return_played_p2']
        
        return {
            'winner': 1 if sets_p1 > sets_p2 else 2,
            'sets_p1': sets_p1,
            'sets_p2': sets_p2,
            'games_p1': total_games_p1,
            'games_p2': total_games_p2,
            'service_won_p1': service_won_p1,
            'service_played_p1': service_played_p1,
            'return_won_p1': return_won_p1,
            'return_played_p1': return_played_p1,
            'service_won_p2': service_won_p2,
            'service_played_p2': service_played_p2,
            'return_won_p2': return_won_p2,
            'return_played_p2': return_played_p2
        }

    def _simulate_set(self, params):
        """Simulate a single set."""
        games_p1 = 0
        games_p2 = 0
        server = 1  # Player 1 serves first
        
        # Service tracking for this set
        service_won_p1 = 0
        service_played_p1 = 0
        return_won_p1 = 0
        return_played_p1 = 0
        
        service_won_p2 = 0
        service_played_p2 = 0
        return_won_p2 = 0
        return_played_p2 = 0
        
        while True:
            # Simulate game
            if server == 1:
                service_prob = params.p1_serve
                game_won = random.random() < service_prob
                service_played_p1 += 1
                return_played_p2 += 1
                if game_won:
                    games_p1 += 1
                    service_won_p1 += 1
                else:
                    games_p2 += 1
                    return_won_p2 += 1
            else:
                service_prob = params.p2_serve
                game_won = random.random() < service_prob
                service_played_p2 += 1
                return_played_p1 += 1
                if game_won:
                    games_p2 += 1
                    service_won_p2 += 1
                else:
                    games_p1 += 1
                    return_won_p1 += 1
            
            # Check for set win
            if (games_p1 >= 6 and games_p1 - games_p2 >= 2) or games_p1 == 7:
                return {
                    'winner': 1,
                    'games_p1': games_p1,
                    'games_p2': games_p2,
                    'service_won_p1': service_won_p1,
                    'service_played_p1': service_played_p1,
                    'return_won_p1': return_won_p1,
                    'return_played_p1': return_played_p1,
                    'service_won_p2': service_won_p2,
                    'service_played_p2': service_played_p2,
                    'return_won_p2': return_won_p2,
                    'return_played_p2': return_played_p2
                }
            elif (games_p2 >= 6 and games_p2 - games_p1 >= 2) or games_p2 == 7:
                return {
                    'winner': 2,
                    'games_p1': games_p1,
                    'games_p2': games_p2,
                    'service_won_p1': service_won_p1,
                    'service_played_p1': service_played_p1,
                    'return_won_p1': return_won_p1,
                    'return_played_p1': return_played_p1,
                    'service_won_p2': service_won_p2,
                    'service_played_p2': service_played_p2,
                    'return_won_p2': return_won_p2,
                    'return_played_p2': return_played_p2
                }
            
            # Handle tiebreak at 6-6
            if games_p1 == 6 and games_p2 == 6:
                tiebreak_winner = self._simulate_tiebreak(params)
                if tiebreak_winner == 1:
                    games_p1 = 7
                else:
                    games_p2 = 7
                # Add some points for tiebreak
                service_played_p1 += 3
                service_played_p2 += 3
                return_played_p1 += 3
                return_played_p2 += 3
                if tiebreak_winner == 1:
                    service_won_p1 += 2
                    return_won_p1 += 1
                else:
                    service_won_p2 += 2
                    return_won_p2 += 1
            
            # Alternate server
            server = 2 if server == 1 else 1

    def _simulate_tiebreak(self, params):
        """Simulate a tiebreak."""
        points_p1 = 0
        points_p2 = 0
        server = 1
        
        while True:
            if server == 1:
                service_prob = params.p1_serve
            else:
                service_prob = params.p2_serve
            
            if random.random() < service_prob:
                if server == 1:
                    points_p1 += 1
                else:
                    points_p2 += 1
            else:
                if server == 1:
                    points_p2 += 1
                else:
                    points_p1 += 1
            
            # Check for tiebreak win
            total_points = points_p1 + points_p2
            if points_p1 >= 7 and points_p1 - points_p2 >= 2:
                return 1
            elif points_p2 >= 7 and points_p2 - points_p1 >= 2:
                return 2
            
            # Alternate server every 2 points
            if total_points == 1 or (total_points - 1) % 2 == 0:
                server = 2 if server == 1 else 1

    def simulate_multiple_matches(self, market: BettingMarket, 
                                 num_simulations: int = 1000) -> List[MatchResult]:
        """
        Simulate multiple matches for statistical analysis.
        
        Args:
            market: BettingMarket to simulate
            num_simulations: Number of simulations to run
            
        Returns:
            List of MatchResult objects
        """
        results = []
        
        for i in range(num_simulations):
            result = self.simulate_match(market)
            results.append(result)
        
        return results
