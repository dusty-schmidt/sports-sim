"""
Fantasy Tennis Statistics Classes
Handles fantasy point calculation and match statistics tracking
"""

class FantasyStats:
    """Tracks fantasy-relevant statistics for a tennis player in a match."""

    def __init__(self, player_name: str):
        self.player_name = player_name

        # Match outcome
        self.match_won = False
        self.sets_won = 0
        self.sets_lost = 0
        self.games_won = 0
        self.games_lost = 0

        # Point-level stats
        self.aces = 0
        self.double_faults = 0
        self.breaks = 0  # Break points converted

        # Bonus qualifiers
        self.clean_sets = 0  # Sets won 6-0, 6-1, 6-2
        self.straight_sets = False  # Won without losing a set
        self.no_double_faults = True  # No double faults in match
        self.ten_plus_aces = False  # 10+ aces in match

    def calculate_fantasy_points(self, best_of_5: bool = False) -> float:
        """Calculate total fantasy points using official DraftKings scoring system."""
        points = 0.0

        # Base scoring - Official DraftKings
        points += 30.0  # Match played

        if self.match_won:
            points += 5.0 if best_of_5 else 6.0  # Match won

        # Sets - Official DraftKings
        set_win_points = 5.0 if best_of_5 else 6.0
        set_loss_points = -2.5 if best_of_5 else -3.0
        points += set_win_points * self.sets_won
        points += set_loss_points * self.sets_lost

        # Games - Official DraftKings
        game_win_points = 2.0 if best_of_5 else 2.5
        game_loss_points = -1.6 if best_of_5 else -2.0
        points += game_win_points * self.games_won
        points += game_loss_points * self.games_lost

        # Point-level scoring - Official DraftKings
        ace_points = 0.25 if best_of_5 else 0.4
        points += ace_points * self.aces
        points -= 1.0 * self.double_faults  # -1 per double fault

        break_points = 0.5 if best_of_5 else 0.75
        points += break_points * self.breaks

        # Bonuses - Official DraftKings
        if self.clean_sets > 0:
            clean_set_bonus = 2.5 if best_of_5 else 4.0
            points += clean_set_bonus * self.clean_sets

        if self.straight_sets:
            points += 5.0 if best_of_5 else 6.0

        if self.no_double_faults:
            points += 5.0 if best_of_5 else 2.5

        # Ace bonus - Official DraftKings
        if (best_of_5 and self.aces >= 15) or (not best_of_5 and self.aces >= 10):
            points += 2.0

        return points

    def add_ace(self):
        """Record an ace."""
        self.aces += 1
        if self.aces >= 10:
            self.ten_plus_aces = True

    def add_double_fault(self):
        """Record a double fault."""
        self.double_faults += 1
        self.no_double_faults = False

    def add_break(self):
        """Record a break of serve."""
        self.breaks += 1

    def add_game_won(self):
        """Record a game won."""
        self.games_won += 1

    def add_game_lost(self):
        """Record a game lost."""
        self.games_lost += 1

    def add_set_won(self, opponent_games: int):
        """Record a set won."""
        self.sets_won += 1

        # Check for clean set (6-0, 6-1, 6-2)
        if opponent_games <= 2:
            self.clean_sets += 1

    def add_set_lost(self):
        """Record a set lost."""
        self.sets_lost += 1

    def finalize_match(self, won_match: bool):
        """Finalize match statistics."""
        self.match_won = won_match

        # Check for straight sets
        if won_match and self.sets_lost == 0:
            self.straight_sets = True

    def __str__(self):
        return (f"{self.player_name}: {self.sets_won}-{self.sets_lost} sets, "
                f"{self.games_won}-{self.games_lost} games, "
                f"{self.aces} aces, {self.double_faults} DFs, {self.breaks} breaks")


class SetResult:
    """Represents the result of a tennis set."""

    def __init__(self, winner: str, loser: str, winner_games: int, loser_games: int,
                 tiebreak: bool = False, tiebreak_score: tuple = None):
        self.winner = winner
        self.loser = loser
        self.winner_games = winner_games
        self.loser_games = loser_games
        self.tiebreak = tiebreak
        self.tiebreak_score = tiebreak_score  # (winner_points, loser_points)

    def __str__(self):
        if self.tiebreak and self.tiebreak_score:
            return f"{self.winner_games}-{self.loser_games}({self.tiebreak_score[0]}-{self.tiebreak_score[1]})"
        else:
            return f"{self.winner_games}-{self.loser_games}"


class GameResult:
    """Represents the result of a tennis game."""

    def __init__(self, winner: str, loser: str, points_played: int,
                 aces: int = 0, double_faults: int = 0, break_point: bool = False):
        self.winner = winner
        self.loser = loser
        self.points_played = points_played
        self.aces = aces
        self.double_faults = double_faults
        self.break_point = break_point  # Was this a break of serve?


class MatchResult:
    """Complete match result with all statistics."""

    def __init__(self, player1_stats: FantasyStats, player2_stats: FantasyStats, sets: list):
        self.player1_stats = player1_stats
        self.player2_stats = player2_stats
        self.sets = sets
        self.winner = player1_stats.player_name if player1_stats.match_won else player2_stats.player_name
        self.loser = player2_stats.player_name if player1_stats.match_won else player1_stats.player_name
