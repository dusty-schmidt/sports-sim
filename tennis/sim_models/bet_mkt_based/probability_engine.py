"""
Probability Engine for Betting Market Tennis Simulator

Calibrates service/return probabilities to match target match probabilities.
Ensures simulated win rates match betting market expectations.
"""

import random
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class PlayerParams:
    """Service and return parameters for both players."""
    p1_serve: float
    p1_return: float
    p2_serve: float
    p2_return: float


class ProbabilityEngine:
    """
    Calibrates tennis match probabilities to match betting market expectations.

    This is the core component that ensures simulated win rates match
    the probabilities implied by betting odds.
    """

    def __init__(self, seed: int = 42):
        """Initialize engine with random seed for reproducible results."""
        random.seed(seed)

    def derive_match_parameters(self, target_p1_prob: float, surface: str = "Hard") -> PlayerParams:
        """
        Derive service/return parameters that produce target match probability.

        This is the main method that ensures betting market accuracy.

        Args:
            target_p1_prob: Target match win probability for player 1
            surface: Court surface (affects baseline probabilities)

        Returns:
            PlayerParams with calibrated probabilities
        """
        # Use binary search to find parameters that match target probability
        return self._calibrate_parameters(target_p1_prob, surface)

    def _calibrate_parameters(self, target_prob: float, surface: str,
                            tolerance: float = 0.015, max_iterations: int = 75) -> PlayerParams:
        """
        Find service/return probabilities that produce target match probability.

        Args:
            target_prob: Target match win probability for player 1
            surface: Court surface
            tolerance: Acceptable error in match probability
            max_iterations: Maximum calibration iterations

        Returns:
            PlayerParams with calibrated probabilities
        """
        # Surface-specific baselines
        surface_baselines = {
            'Hard': {'serve': 0.62, 'return': 0.38},
            'Clay': {'serve': 0.60, 'return': 0.40},  # Less service-dependent
            'Grass': {'serve': 0.65, 'return': 0.35}  # More service-dependent
        }

        baseline = surface_baselines.get(surface, surface_baselines['Hard'])
        base_serve = baseline['serve']
        base_return = baseline['return']

        # For 50-50 matches, use baseline for both players
        if abs(target_prob - 0.5) < 0.01:
            return PlayerParams(
                p1_serve=base_serve,
                p1_return=base_return,
                p2_serve=base_serve,
                p2_return=base_return
            )

        # Binary search for correct advantage with tighter calibration
        low_advantage = -0.20  # Wider search range
        high_advantage = 0.20

        best_params = None
        best_error = float('inf')

        for iteration in range(max_iterations):
            # Try middle point
            advantage = (low_advantage + high_advantage) / 2

            # Calculate service/return probabilities with adaptive scaling
            # Use different scaling based on target probability range
            if abs(target_prob - 0.5) < 0.08:  # Very close matches (42%-58%)
                serve_scaling = 2.0  # Most aggressive for close matches
                return_scaling = 1.6
            elif abs(target_prob - 0.5) < 0.15:  # Moderate matches (35%-65%)
                serve_scaling = 1.7  # Increased for better calibration
                return_scaling = 1.3
            elif abs(target_prob - 0.5) < 0.25:  # Moderate favorites (25%-75%)
                serve_scaling = 1.4  # Fine-tuned for 60-70% range
                return_scaling = 1.0
            else:  # Heavy favorites/underdogs
                serve_scaling = 1.1
                return_scaling = 0.8

            p1_serve = base_serve + (advantage * serve_scaling)
            p1_return = base_return + (advantage * return_scaling)

            # Opponent gets inverse advantage
            p2_serve = base_serve - (advantage * serve_scaling)
            p2_return = base_return - (advantage * return_scaling)

            # Ensure realistic bounds
            p1_serve = max(0.40, min(0.90, p1_serve))
            p1_return = max(0.10, min(0.60, p1_return))
            p2_serve = max(0.40, min(0.90, p2_serve))
            p2_return = max(0.10, min(0.60, p2_return))

            # Test these probabilities with more simulations for accuracy
            params = PlayerParams(p1_serve, p1_return, p2_serve, p2_return)
            simulated_prob = self._estimate_match_probability(params, num_simulations=500)

            error = abs(simulated_prob - target_prob)

            # Track best result
            if error < best_error:
                best_error = error
                best_params = params

            # Check if we're close enough (tighter tolerance)
            if error < tolerance:
                return params

            # Adjust search range
            if simulated_prob < target_prob:
                # Need more advantage for P1
                low_advantage = advantage
            else:
                # Need less advantage for P1
                high_advantage = advantage

            # Prevent infinite loops with tighter convergence
            if abs(high_advantage - low_advantage) < 0.0005:
                break

        # Return best result found
        return best_params if best_params else PlayerParams(base_serve, base_return, base_serve, base_return)

    def _estimate_match_probability(self, params: PlayerParams, num_simulations: int = 200) -> float:
        """
        Estimate match probability by running quick simulations.

        Args:
            params: Service/return parameters to test
            num_simulations: Number of simulations to run

        Returns:
            Estimated match win probability for player 1
        """
        p1_wins = 0

        for _ in range(num_simulations):
            winner = self._simulate_quick_match(params)
            if winner == 1:
                p1_wins += 1

        return p1_wins / num_simulations

    def _simulate_quick_match(self, params: PlayerParams, best_of_5: bool = False) -> int:
        """Quick match simulation for calibration purposes."""
        sets_to_win = 3 if best_of_5 else 2
        sets_p1 = 0
        sets_p2 = 0

        while sets_p1 < sets_to_win and sets_p2 < sets_to_win:
            set_winner = self._simulate_quick_set(params)
            if set_winner == 1:
                sets_p1 += 1
            else:
                sets_p2 += 1

        return 1 if sets_p1 > sets_p2 else 2

    def _simulate_quick_set(self, params: PlayerParams) -> int:
        """Quick set simulation for calibration."""
        games_p1 = 0
        games_p2 = 0
        server = 1  # Player 1 serves first

        while True:
            # Simulate game
            game_winner = self._simulate_quick_game(params, server)

            if game_winner == 1:
                games_p1 += 1
            else:
                games_p2 += 1

            # Check for set win
            if (games_p1 >= 6 and games_p1 - games_p2 >= 2) or games_p1 == 7:
                return 1
            elif (games_p2 >= 6 and games_p2 - games_p1 >= 2) or games_p2 == 7:
                return 2

            # Handle tiebreak at 6-6
            if games_p1 == 6 and games_p2 == 6:
                tiebreak_winner = self._simulate_quick_tiebreak(params)
                return tiebreak_winner

            # Alternate server
            server = 2 if server == 1 else 1

    def _simulate_quick_game(self, params: PlayerParams, server: int) -> int:
        """Quick game simulation using service probability."""
        if server == 1:
            service_prob = params.p1_serve
        else:
            service_prob = params.p2_serve

        # Simplified: just use service probability to determine game winner
        if random.random() < service_prob:
            return server
        else:
            return 2 if server == 1 else 1

    def _simulate_quick_tiebreak(self, params: PlayerParams) -> int:
        """Quick tiebreak simulation."""
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

    def validate_accuracy(self, params: PlayerParams, target_prob: float,
                         num_simulations: int = 1000) -> Dict[str, float]:
        """
        Validate calibration accuracy with extensive simulations.

        Args:
            params: Calibrated parameters
            target_prob: Target match probability
            num_simulations: Number of validation simulations

        Returns:
            Validation results
        """
        actual_prob = self._estimate_match_probability(params, num_simulations)
        error = abs(actual_prob - target_prob)

        return {
            'target_probability': target_prob,
            'actual_probability': actual_prob,
            'error': error,
            'error_percentage': error * 100,
            'within_tolerance': error < 0.03,  # 3% tolerance
            'p1_serve': params.p1_serve,
            'p1_return': params.p1_return,
            'p2_serve': params.p2_serve,
            'p2_return': params.p2_return
        }
