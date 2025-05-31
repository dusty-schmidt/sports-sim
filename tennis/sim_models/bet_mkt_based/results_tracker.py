"""
Results Tracking for Betting Market Tennis Simulator

Clean, modular result tracking designed for easy integration.
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class MatchResult:
    """Statistics for a match simulated using betting market data."""

    # Match info
    player1: str = ""
    player2: str = ""
    winner: str = ""
    surface: str = "Hard"

    # Score
    sets_won_p1: int = 0
    sets_won_p2: int = 0
    games_won_p1: int = 0
    games_won_p2: int = 0
    total_points_p1: int = 0
    total_points_p2: int = 0

    # Service statistics (estimated from simulation)
    service_points_won_p1: int = 0
    service_points_played_p1: int = 0
    return_points_won_p1: int = 0
    return_points_played_p1: int = 0

    service_points_won_p2: int = 0
    service_points_played_p2: int = 0
    return_points_won_p2: int = 0
    return_points_played_p2: int = 0

    # Derived statistics
    aces_p1: int = 0
    aces_p2: int = 0
    double_faults_p1: int = 0
    double_faults_p2: int = 0

    # Match characteristics
    total_games: int = 0
    match_duration_minutes: int = 0

    # Betting market validation
    market_win_prob_p1: float = 0.5
    actual_winner_was_favorite: bool = True

    # Simulation metadata
    simulation_method: str = "betting_market"
    confidence_score: float = 1.0

    def __post_init__(self):
        """Calculate derived statistics after initialization."""
        self.total_games = self.games_won_p1 + self.games_won_p2

        # Estimate match duration based on total games
        # Average: ~4 minutes per game
        self.match_duration_minutes = max(60, self.total_games * 4)

        # Determine if favorite won
        if self.market_win_prob_p1 > 0.5:
            self.actual_winner_was_favorite = (self.winner == self.player1)
        else:
            self.actual_winner_was_favorite = (self.winner == self.player2)

    @property
    def service_pct_p1(self) -> float:
        """Service points won percentage for player 1."""
        if self.service_points_played_p1 == 0:
            return 0.0
        return (self.service_points_won_p1 / self.service_points_played_p1) * 100

    @property
    def service_pct_p2(self) -> float:
        """Service points won percentage for player 2."""
        if self.service_points_played_p2 == 0:
            return 0.0
        return (self.service_points_won_p2 / self.service_points_played_p2) * 100

    @property
    def return_pct_p1(self) -> float:
        """Return points won percentage for player 1."""
        if self.return_points_played_p1 == 0:
            return 0.0
        return (self.return_points_won_p1 / self.return_points_played_p1) * 100

    @property
    def return_pct_p2(self) -> float:
        """Return points won percentage for player 2."""
        if self.return_points_played_p2 == 0:
            return 0.0
        return (self.return_points_won_p2 / self.return_points_played_p2) * 100

    @property
    def final_score(self) -> str:
        """Final score string."""
        return f"{self.sets_won_p1}-{self.sets_won_p2}"

    @property
    def games_score(self) -> str:
        """Games score string."""
        return f"{self.games_won_p1}-{self.games_won_p2}"

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'match_info': {
                'player1': self.player1,
                'player2': self.player2,
                'winner': self.winner,
                'surface': self.surface,
                'final_score': self.final_score,
                'games_score': self.games_score
            },
            'statistics': {
                'total_points': {
                    'player1': self.total_points_p1,
                    'player2': self.total_points_p2
                },
                'service': {
                    'player1': {
                        'points_won': self.service_points_won_p1,
                        'points_played': self.service_points_played_p1,
                        'percentage': self.service_pct_p1,
                        'aces': self.aces_p1,
                        'double_faults': self.double_faults_p1
                    },
                    'player2': {
                        'points_won': self.service_points_won_p2,
                        'points_played': self.service_points_played_p2,
                        'percentage': self.service_pct_p2,
                        'aces': self.aces_p2,
                        'double_faults': self.double_faults_p2
                    }
                },
                'return': {
                    'player1': {
                        'points_won': self.return_points_won_p1,
                        'points_played': self.return_points_played_p1,
                        'percentage': self.return_pct_p1
                    },
                    'player2': {
                        'points_won': self.return_points_won_p2,
                        'points_played': self.return_points_played_p2,
                        'percentage': self.return_pct_p2
                    }
                }
            },
            'market_validation': {
                'market_win_prob_p1': self.market_win_prob_p1,
                'actual_winner_was_favorite': self.actual_winner_was_favorite,
                'confidence_score': self.confidence_score
            },
            'metadata': {
                'simulation_method': self.simulation_method,
                'total_games': self.total_games,
                'duration_minutes': self.match_duration_minutes
            }
        }

    def get_fantasy_points(self, scoring_system: str = "draftkings") -> Dict[str, float]:
        """
        Calculate fantasy points for both players.

        Args:
            scoring_system: Fantasy scoring system to use

        Returns:
            Dictionary with fantasy points for each player
        """
        if scoring_system.lower() == "draftkings":
            return self._calculate_draftkings_points()
        else:
            raise ValueError(f"Unsupported scoring system: {scoring_system}")

    def _calculate_draftkings_points(self) -> Dict[str, float]:
        """Calculate DraftKings fantasy points."""

        def calc_player_points(
            winner: bool, sets_won: int, games_won: int,
            aces: int, double_faults: int
        ) -> float:
            points = 0.0

            # Win bonus
            if winner:
                points += 3.0

            # Sets won
            points += sets_won * 1.0

            # Games won
            points += games_won * 0.25

            # Aces
            points += aces * 0.25

            # Double fault penalty
            points -= double_faults * 0.25

            return max(0.0, points)  # No negative scores

        p1_points = calc_player_points(
            winner=(self.winner == self.player1),
            sets_won=self.sets_won_p1,
            games_won=self.games_won_p1,
            aces=self.aces_p1,
            double_faults=self.double_faults_p1
        )

        p2_points = calc_player_points(
            winner=(self.winner == self.player2),
            sets_won=self.sets_won_p2,
            games_won=self.games_won_p2,
            aces=self.aces_p2,
            double_faults=self.double_faults_p2
        )

        return {
            self.player1: p1_points,
            self.player2: p2_points
        }


@dataclass
class SimulationResults:
    """Results from multiple betting-based simulations."""

    matches: List[MatchResult] = field(default_factory=list)
    total_simulations: int = 0

    def add_match(self, match_stats: MatchResult):
        """Add a match result to the collection."""
        self.matches.append(match_stats)
        self.total_simulations += 1

    def get_win_percentage(self, player_name: str) -> float:
        """Get win percentage for a specific player."""
        if not self.matches:
            return 0.0

        wins = sum(1 for match in self.matches if match.winner == player_name)
        return (wins / len(self.matches)) * 100

    def get_average_fantasy_points(self, player_name: str, scoring_system: str = "draftkings") -> float:
        """Get average fantasy points for a player."""
        if not self.matches:
            return 0.0

        total_points = 0.0
        count = 0

        for match in self.matches:
            fantasy_points = match.get_fantasy_points(scoring_system)
            if player_name in fantasy_points:
                total_points += fantasy_points[player_name]
                count += 1

        return total_points / count if count > 0 else 0.0

    def get_market_accuracy(self) -> Dict[str, float]:
        """Analyze how well betting markets predicted outcomes."""
        if not self.matches:
            return {'accuracy': 0.0, 'favorite_win_rate': 0.0}

        correct_predictions = sum(1 for match in self.matches if match.actual_winner_was_favorite)
        accuracy = (correct_predictions / len(self.matches)) * 100

        return {
            'accuracy': accuracy,
            'favorite_win_rate': accuracy,  # Same thing in this context
            'total_matches': len(self.matches)
        }

    def to_summary_dict(self) -> Dict:
        """Create summary dictionary of all results."""
        if not self.matches:
            return {'error': 'No matches simulated'}

        # Get unique players
        players = set()
        for match in self.matches:
            players.add(match.player1)
            players.add(match.player2)

        # Calculate stats for each player
        player_stats = {}
        for player in players:
            player_stats[player] = {
                'win_percentage': self.get_win_percentage(player),
                'avg_fantasy_points': self.get_average_fantasy_points(player),
                'matches_played': sum(1 for m in self.matches if player in [m.player1, m.player2])
            }

        market_accuracy = self.get_market_accuracy()

        return {
            'simulation_summary': {
                'total_simulations': self.total_simulations,
                'unique_players': len(players),
                'simulation_method': 'betting_market_based'
            },
            'player_statistics': player_stats,
            'market_validation': market_accuracy
        }
