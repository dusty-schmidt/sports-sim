"""
Fantasy Tennis Simulator
Main simulation engine for point-by-point tennis match simulation
Enhanced with ML insights and advanced analytics
"""

import random
import math
from typing import Dict, Any, Tuple, List, Optional
from .stats import FantasyStats, SetResult, GameResult
from .analyzer import TennisStatsAnalyzer
from .enhanced_data_engine import EnhancedDataEngine
from .enhanced_profiles import EnhancedPlayerProfile
from .enhanced_analytics import (
    EnhancedMatchResult, EnhancedAnalyticsEngine,
    MLInsights, TacticalAnalysis, BettingAnalysis
)


class FantasyTennisSimulator:
    """Main tennis match simulator with fantasy scoring."""

    def __init__(self, data_source: Optional[str] = None):
        self.analyzer = TennisStatsAnalyzer(data_source)
        self.player_stats = self.analyzer.player_stats
        self.calculated_stats = self.analyzer.calculated_stats

        # Surface adjustments based on our data analysis
        self.surface_adjustments = {
            'Hard': {
                'ace_multiplier': 1.0,
                'fault_multiplier': 1.0,
                'rally_multiplier': 1.0,
                'variance_multiplier': 0.35  # ±35% variance (increased for more randomness)
            },
            'Clay': {
                'ace_multiplier': 0.7,  # Fewer aces on clay
                'fault_multiplier': 1.8,  # More faults on clay (from our analysis)
                'rally_multiplier': 1.2,   # Longer rallies on clay
                'variance_multiplier': 0.30  # ±30% variance (increased)
            },
            'Grass': {
                'ace_multiplier': 1.3,  # More aces on grass
                'fault_multiplier': 3.2,  # Much more faults on grass (from our analysis)
                'rally_multiplier': 1.5,   # Surprisingly longer rallies (from our data)
                'variance_multiplier': 0.25  # ±25% variance (increased)
            }
        }

    def calculate_elo_win_probability(self, player1: str, player2: str, surface: str = 'Hard') -> float:
        """Calculate win probability for player1 based on surface-specific ELO ratings."""
        elo1 = self.analyzer.get_player_elo(player1, surface)
        elo2 = self.analyzer.get_player_elo(player2, surface)

        # If either player doesn't have surface-specific ELO, try overall ELO
        if elo1 is None:
            elo1 = self.analyzer.get_player_elo(player1)
        if elo2 is None:
            elo2 = self.analyzer.get_player_elo(player2)

        # If either player still doesn't have ELO, use default 50/50
        if elo1 is None or elo2 is None:
            return 0.5

        # Standard ELO win probability formula with dampening for more realistic variance
        # P(A beats B) = 1 / (1 + 10^((ELO_B - ELO_A) / K))
        # Use K=600 instead of 400 to reduce the impact of ELO differences
        # This makes upsets more likely and reduces extreme win probabilities
        elo_diff = elo2 - elo1
        k_factor = 1000  # Higher K = more variance, lower dominance (increased from 600)
        win_prob = 1 / (1 + math.pow(10, elo_diff / k_factor))

        # Ensure win probability is never too extreme (min 20%, max 80%)
        # Further tighten the range to reduce favorite dominance
        win_prob = max(0.20, min(0.80, win_prob))

        return win_prob

    def get_player_probabilities(self, player_name: str, surface: str = 'Hard') -> Dict[str, float]:
        """Get surface-weighted probabilities for a player."""
        # Use surface-weighted stats from analyzer
        surface_weighted_stats = self.analyzer.get_player_stats(player_name, surface)

        if not surface_weighted_stats:
            # Generate ELO-appropriate default stats for missing players
            elo_rating = self.analyzer.get_player_elo(player_name, surface)

            if elo_rating:
                # Scale stats based on ELO rating (1500 = average, 2000 = elite)
                # Lower ELO = weaker stats, Higher ELO = stronger stats
                elo_factor = (elo_rating - 1500) / 500  # -1.0 to +1.0 range
                elo_factor = max(-0.8, min(0.8, elo_factor))  # Cap the range

                # Base stats for average player (ELO 1500)
                base_service = 62.0
                base_return = 38.0

                # Adjust based on ELO
                service_adjustment = elo_factor * 8.0  # ±8% range
                return_adjustment = elo_factor * 6.0   # ±6% range

                surface_weighted_stats = {
                    'ace_rate': 6.0 + (elo_factor * 2.0),  # 4-8% range
                    'double_fault_rate': 4.0 - (elo_factor * 1.0),  # 3-5% range
                    'first_serve_percentage': 62.0 + (elo_factor * 4.0),  # 58-66% range
                    'service_points_won': base_service + service_adjustment,
                    'return_points_won': base_return + return_adjustment
                }
            else:
                # Fallback if no ELO data either
                surface_weighted_stats = {
                    'ace_rate': 6.0,
                    'double_fault_rate': 4.0,
                    'first_serve_percentage': 62.0,
                    'service_points_won': 62.0,
                    'return_points_won': 38.0
                }

        return {
            'ace_rate': surface_weighted_stats.get('ace_rate', 6.0),
            'double_fault_rate': surface_weighted_stats.get('double_fault_rate', 4.0),
            'first_serve_percentage': surface_weighted_stats.get('first_serve_percentage', 60.0),
            'service_points_won': surface_weighted_stats.get('service_points_won', 60.0),
            'return_points_won': surface_weighted_stats.get('return_points_won', 40.0)
        }

    def get_match_adjusted_probabilities(self, player_name: str, surface: str = 'Hard',
                                       use_variance: bool = True, variance_level: Optional[float] = None,
                                       pressure_situation: Optional[str] = None) -> Dict[str, float]:
        """Get match-specific probabilities with optional surface-specific variance and clutch factor."""
        probs = self.get_player_probabilities(player_name, surface)

        if use_variance:
            # Use surface-specific variance if not overridden
            if variance_level is None:
                surface_adj = self.surface_adjustments.get(surface, self.surface_adjustments['Hard'])
                variance_level = surface_adj['variance_multiplier']

            # Apply skill-preserving match-to-match variance
            # Instead of pure random multipliers, use smaller variance that preserves skill gaps
            for key, value in probs.items():
                if key in ['ace_rate', 'double_fault_rate', 'service_points_won', 'return_points_won']:
                    # Use moderate variance that preserves skill differences
                    if key in ['service_points_won', 'return_points_won']:
                        # Moderate service/return variance
                        skill_preserving_variance = 0.10  # ±10% max
                    else:
                        # Ace/DF rates can have slightly more variance
                        skill_preserving_variance = 0.12  # ±12% max

                    # Apply Gaussian-like variance centered on the player's true skill
                    variance_factor = random.uniform(1 - skill_preserving_variance, 1 + skill_preserving_variance)
                    probs[key] = max(0.1, min(99.9, value * variance_factor))

        # Apply clutch factor for pressure situations
        if pressure_situation:
            clutch_multiplier = self._get_clutch_multiplier(player_name, pressure_situation)

            # Apply clutch factor to key stats
            if pressure_situation in ['BP', 'GP', 'SP', 'MP']:  # Break/Game/Set/Match points
                probs['service_points_won'] *= clutch_multiplier
                probs['return_points_won'] *= clutch_multiplier

                # Clutch players hit more aces, fewer double faults under pressure
                if clutch_multiplier > 1.0:  # Good clutch
                    probs['ace_rate'] *= min(1.2, clutch_multiplier)
                    probs['double_fault_rate'] *= max(0.8, 2.0 - clutch_multiplier)
                else:  # Poor clutch
                    probs['ace_rate'] *= max(0.8, clutch_multiplier)
                    probs['double_fault_rate'] *= min(1.3, 2.0 - clutch_multiplier)

                # Ensure bounds
                probs['service_points_won'] = max(30.0, min(85.0, probs['service_points_won']))
                probs['return_points_won'] = max(15.0, min(70.0, probs['return_points_won']))
                probs['ace_rate'] = max(0.5, min(20.0, probs['ace_rate']))
                probs['double_fault_rate'] = max(0.5, min(12.0, probs['double_fault_rate']))

        return probs

    def _get_clutch_multiplier(self, player_name: str, pressure_situation: str) -> float:
        """Get clutch multiplier for a player in a pressure situation."""
        player_stats = self.analyzer.calculated_stats.get(player_name, {})
        base_clutch = player_stats.get('clutch_factor', 1.0)

        # Adjust clutch factor based on pressure level
        pressure_multipliers = {
            'BP': 1.0,    # Break points - full clutch factor
            'GP': 0.7,    # Game points - moderate pressure
            'SP': 1.2,    # Set points - high pressure
            'MP': 1.5,    # Match points - maximum pressure
            'Deuce': 0.5  # Deuce - mild pressure
        }

        pressure_mult = pressure_multipliers.get(pressure_situation, 0.5)

        # Calculate final multiplier
        # Formula: 1.0 + (base_clutch - 1.0) * pressure_multiplier
        final_multiplier = 1.0 + (base_clutch - 1.0) * pressure_mult

        return max(0.7, min(1.3, final_multiplier))  # Bound between 0.7 and 1.3

    def _get_rally_multiplier(self, player_name: str, rally_length: int) -> float:
        """Get rally length multiplier for a player."""
        player_stats = self.analyzer.calculated_stats.get(player_name, {})
        rally_type = player_stats.get('rally_type', 'Consistent')
        base_multiplier = player_stats.get('rally_multiplier', 1.0)

        # Apply rally length effects
        if rally_length <= 3:  # Short rallies (1-3 shots)
            if rally_type == 'Quick Points':
                return base_multiplier * 1.1  # Boost for quick point players
            elif rally_type == 'Grinder':
                return base_multiplier * 0.95  # Slight penalty for grinders
            else:
                return base_multiplier
        elif rally_length <= 6:  # Medium rallies (4-6 shots)
            return base_multiplier  # Neutral for all player types
        else:  # Long rallies (7+ shots)
            if rally_type == 'Grinder':
                return base_multiplier * 1.15  # Big boost for grinders
            elif rally_type == 'Balanced Fighter':
                return base_multiplier * 1.05  # Moderate boost
            elif rally_type == 'Quick Points':
                return base_multiplier * 0.85  # Penalty for quick point players
            else:
                return base_multiplier

    def _get_fatigue_multiplier(self, player_name: str, current_set: int) -> float:
        """Get fatigue multiplier based on set progression."""
        if current_set <= 2:
            return 1.0  # No fatigue in early sets

        player_stats = self.analyzer.calculated_stats.get(player_name, {})
        fatigue_resistance = player_stats.get('fatigue_resistance', 1.0)
        momentum_factor = player_stats.get('momentum_factor', 1.0)

        # Calculate fatigue effect
        set_fatigue = 1.0 - ((current_set - 2) * 0.05 * fatigue_resistance)

        # Apply momentum (positive momentum counters fatigue)
        final_multiplier = set_fatigue * momentum_factor

        return max(0.8, min(1.2, final_multiplier))  # Bound between 0.8 and 1.2

    def _get_pressure_situation(self, server_points: int, returner_points: int,
                               game_situation: Optional[Dict] = None) -> Optional[str]:
        """Determine if current point is a pressure situation."""
        if game_situation is None:
            game_situation = {}

        # Break point situations
        if returner_points >= 3 and returner_points > server_points:
            if returner_points >= 4 or (returner_points == 3 and server_points < 3):
                return 'BP'  # Break point

        # Game point situations
        if server_points >= 3 and server_points > returner_points:
            if server_points >= 4 or (server_points == 3 and returner_points < 3):
                return 'GP'  # Game point

        # Deuce situations
        if server_points >= 3 and returner_points >= 3 and abs(server_points - returner_points) <= 1:
            return 'Deuce'

        # Set/Match points (would need to be passed in game_situation)
        if game_situation.get('set_point', False):
            return 'SP'  # Set point
        if game_situation.get('match_point', False):
            return 'MP'  # Match point

        return None  # No pressure situation

    def _generate_realistic_rally_length(self):
        """Generate rally length based on real tennis data patterns."""
        # Based on real rally data: 1-3 shots (~19%), 4-6 shots (~7%), 7-9 shots (~3%)
        rand = random.random()

        if rand < 0.19:  # 1-3 shots (short rallies)
            return random.randint(1, 3)
        elif rand < 0.26:  # 4-6 shots
            return random.randint(4, 6)
        elif rand < 0.29:  # 7-9 shots
            return random.randint(7, 9)
        elif rand < 0.32:  # 10-12 shots
            return random.randint(10, 12)
        else:  # Longer rallies (rare)
            return random.randint(13, 25)

    def simulate_point(self, server_probs: Dict[str, float], returner_probs: Dict[str, float],
                      pressure_situation: Optional[str] = None, rally_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Simulate a single point with optional pressure situation and rally context."""
        result = {
            'winner': 'server',
            'ace': False,
            'double_fault': False,
            'shots': 1,
            'pressure_situation': pressure_situation,
            'rally_context': rally_context
        }

        # Determine serve type (first serve vs second serve)
        first_serve_percentage = server_probs['first_serve_percentage']
        is_first_serve = random.random() * 100 < first_serve_percentage

        # Check for double fault (only on second serve)
        if not is_first_serve and random.random() * 100 < server_probs['double_fault_rate']:
            result['winner'] = 'returner'
            result['double_fault'] = True
            return result

        # Check for ace (more likely on first serve)
        ace_rate = server_probs['ace_rate']
        if is_first_serve:
            ace_rate *= 1.3  # 30% more aces on first serve
        else:
            ace_rate *= 0.4  # Much fewer aces on second serve

        if random.random() * 100 < ace_rate:
            result['ace'] = True
            return result

        # Calculate serve-specific win rates
        # First serve: typically 75% win rate for elite, 70% for good players
        # Second serve: typically 55% win rate for elite, 50% for good players
        overall_service_rate = server_probs['service_points_won']

        if is_first_serve:
            # First serve is stronger - add 12-15% to overall rate
            server_strength = min(85.0, overall_service_rate + 14.0)
        else:
            # Second serve is weaker - subtract 8-12% from overall rate
            server_strength = max(35.0, overall_service_rate - 10.0)

        returner_strength = returner_probs['return_points_won']

        # Estimate rally length using real tennis data patterns
        rally_length = self._generate_realistic_rally_length()
        result['shots'] = rally_length

        # Apply endurance/momentum effects based on rally length
        if rally_context:
            server_name = rally_context.get('server_name', '')
            returner_name = rally_context.get('returner_name', '')
            current_set = rally_context.get('current_set', 1)

            # Apply rally length multipliers
            server_rally_mult = self._get_rally_multiplier(server_name, rally_length)
            returner_rally_mult = self._get_rally_multiplier(returner_name, rally_length)

            # Apply fatigue effects for later sets
            server_fatigue_mult = self._get_fatigue_multiplier(server_name, current_set)
            returner_fatigue_mult = self._get_fatigue_multiplier(returner_name, current_set)

            # Combine all multipliers
            server_strength *= server_rally_mult * server_fatigue_mult
            returner_strength *= returner_rally_mult * returner_fatigue_mult

            # Apply ELO-based skill adjustment (get surface from rally context)
            surface = rally_context.get('surface', 'Hard')
            elo_win_prob = self.calculate_elo_win_probability(server_name, returner_name, surface)

            # Normalize stats-based probability
            total_strength = server_strength + returner_strength
            stats_server_prob = server_strength / total_strength if total_strength > 0 else 0.5

            # Only apply ELO blending if we have valid ELO data for both players
            server_elo = self.analyzer.get_player_elo(server_name, surface)
            returner_elo = self.analyzer.get_player_elo(returner_name, surface)

            if server_elo and returner_elo:
                # Calculate ELO difference to determine appropriate weighting
                elo_diff = abs(server_elo - returner_elo)

                # Account for ELO overvaluation at the top end
                # Studies show ELO ratings overestimate elite player dominance
                # Use calibrated ELO weights based on testing with real betting lines

                if elo_diff >= 400:  # Massive skill gap (like Carlos vs low-ranked)
                    elo_weight = 0.20  # Reduced - ELO overvalues extreme dominance
                    stats_weight = 0.65
                    random_weight = 0.15
                elif elo_diff >= 300:  # Large skill gap (like Shelton vs Gigante)
                    elo_weight = 0.15  # Much lower - tennis simulation heavily amplifies advantages
                    stats_weight = 0.50
                    random_weight = 0.35  # Much higher randomness to prevent extreme dominance
                elif elo_diff >= 200:  # Moderate-large skill gap
                    elo_weight = 0.35  # Moderate ELO influence
                    stats_weight = 0.55
                    random_weight = 0.10
                elif elo_diff >= 100:  # Moderate skill gap
                    elo_weight = 0.30  # Keep moderate influence for mid-tier gaps
                    stats_weight = 0.60
                    random_weight = 0.10
                else:  # Small skill gap
                    elo_weight = 0.35  # Higher weight for close matches where ELO is more accurate
                    stats_weight = 0.55
                    random_weight = 0.10

                # Combine ELO, stats, and randomness with corrected weighting
                server_win_prob = (elo_weight * elo_win_prob) + (stats_weight * stats_server_prob) + (random_weight * 0.5)
            else:
                # Fall back to pure stats if ELO data missing
                server_win_prob = stats_server_prob
        else:
            # Fallback to stats-only if no rally context
            total_strength = server_strength + returner_strength
            server_win_prob = server_strength / total_strength if total_strength > 0 else 0.5

        if random.random() < server_win_prob:
            result['winner'] = 'server'
        else:
            result['winner'] = 'returner'

        return result

    def simulate_game(self, server_probs: Dict[str, float], returner_probs: Dict[str, float],
                     server_name: str, returner_name: str, game_situation: Optional[Dict] = None) -> GameResult:
        """Simulate a tennis game with pressure situation awareness."""
        server_points = 0
        returner_points = 0
        points_played = 0
        aces = 0
        double_faults = 0

        while True:
            # Determine pressure situation
            pressure_situation = self._get_pressure_situation(
                server_points, returner_points, game_situation
            )

            # Get pressure-adjusted probabilities if needed
            if pressure_situation:
                server_probs_adj = self.get_match_adjusted_probabilities(
                    server_name, 'Hard', True, pressure_situation=pressure_situation
                )
                returner_probs_adj = self.get_match_adjusted_probabilities(
                    returner_name, 'Hard', True, pressure_situation=pressure_situation
                )
            else:
                server_probs_adj = server_probs
                returner_probs_adj = returner_probs

            # Create rally context for momentum/endurance effects
            rally_context = {
                'server_name': server_name,
                'returner_name': returner_name,
                'current_set': game_situation.get('current_set', 1) if game_situation else 1,
                'surface': game_situation.get('surface', 'Hard') if game_situation else 'Hard'
            }

            point_result = self.simulate_point(server_probs_adj, returner_probs_adj, pressure_situation, rally_context)
            points_played += 1

            if point_result['ace']:
                aces += 1
            if point_result['double_fault']:
                double_faults += 1

            if point_result['winner'] == 'server':
                server_points += 1
            else:
                returner_points += 1

            # Check for game win
            if server_points >= 4 and server_points - returner_points >= 2:
                return GameResult(server_name, returner_name, points_played, aces, double_faults, False)
            elif returner_points >= 4 and returner_points - server_points >= 2:
                return GameResult(returner_name, server_name, points_played, aces, double_faults, True)

    def simulate_tiebreak(self, p1_probs: Dict[str, float], p2_probs: Dict[str, float],
                         p1_name: str, p2_name: str) -> Tuple[str, int, int]:
        """Simulate a tiebreak."""
        p1_points = 0
        p2_points = 0
        points_played = 0

        while True:
            # Determine server (alternates every 2 points after first point)
            if points_played == 0 or (points_played - 1) // 2 % 2 == 0:
                server_probs, returner_probs = p1_probs, p2_probs
                server_name, returner_name = p1_name, p2_name
            else:
                server_probs, returner_probs = p2_probs, p1_probs
                server_name, returner_name = p2_name, p1_name

            point_result = self.simulate_point(server_probs, returner_probs)
            points_played += 1

            if point_result['winner'] == 'server':
                if server_name == p1_name:
                    p1_points += 1
                else:
                    p2_points += 1
            else:
                if returner_name == p1_name:
                    p1_points += 1
                else:
                    p2_points += 1

            # Check for tiebreak win
            if p1_points >= 7 and p1_points - p2_points >= 2:
                return p1_name, p1_points, p2_points
            elif p2_points >= 7 and p2_points - p1_points >= 2:
                return p2_name, p2_points, p1_points

    def simulate_set(self, p1_probs: Dict[str, float], p2_probs: Dict[str, float],
                    p1_name: str, p2_name: str) -> SetResult:
        """Simulate a tennis set."""
        p1_games = 0
        p2_games = 0

        while True:
            # Determine server (alternates each game)
            if (p1_games + p2_games) % 2 == 0:
                server_probs, returner_probs = p1_probs, p2_probs
                server_name, returner_name = p1_name, p2_name
            else:
                server_probs, returner_probs = p2_probs, p1_probs
                server_name, returner_name = p2_name, p1_name

            game_result = self.simulate_game(server_probs, returner_probs, server_name, returner_name)

            if game_result.winner == p1_name:
                p1_games += 1
            else:
                p2_games += 1

            # Check for set win
            if p1_games >= 6 and p1_games - p2_games >= 2:
                return SetResult(p1_name, p2_name, p1_games, p2_games)
            elif p2_games >= 6 and p2_games - p1_games >= 2:
                return SetResult(p2_name, p1_name, p2_games, p1_games)
            elif p1_games == 6 and p2_games == 6:
                # Tiebreak
                tb_winner, tb_p1_pts, tb_p2_pts = self.simulate_tiebreak(p1_probs, p2_probs, p1_name, p2_name)
                if tb_winner == p1_name:
                    return SetResult(p1_name, p2_name, 7, 6, True, (tb_p1_pts, tb_p2_pts))
                else:
                    return SetResult(p2_name, p1_name, 7, 6, True, (tb_p2_pts, tb_p1_pts))

    def calculate_match_stats(self, sets: List[SetResult], p1_name: str, p2_name: str) -> Tuple[FantasyStats, FantasyStats]:
        """Calculate comprehensive match statistics."""
        p1_stats = FantasyStats(p1_name)
        p2_stats = FantasyStats(p2_name)

        # Count sets and games
        for set_result in sets:
            if set_result.winner == p1_name:
                p1_stats.add_set_won(set_result.loser_games)
                p2_stats.add_set_lost()
                p1_stats.games_won += set_result.winner_games
                p1_stats.games_lost += set_result.loser_games
                p2_stats.games_won += set_result.loser_games
                p2_stats.games_lost += set_result.winner_games
            else:
                p2_stats.add_set_won(set_result.loser_games)
                p1_stats.add_set_lost()
                p2_stats.games_won += set_result.winner_games
                p2_stats.games_lost += set_result.loser_games
                p1_stats.games_won += set_result.loser_games
                p1_stats.games_lost += set_result.winner_games

        # Estimate point-level stats based on games and player probabilities
        p1_probs = self.get_player_probabilities(p1_name)
        p2_probs = self.get_player_probabilities(p2_name)

        # Rough estimation of aces and double faults based on games served
        total_games = sum(s.winner_games + s.loser_games for s in sets)
        p1_service_games = total_games // 2 + (1 if total_games % 2 == 1 else 0)
        p2_service_games = total_games // 2

        # Estimate aces (roughly 4 points per service game)
        p1_stats.aces = max(0, int(p1_service_games * 4 * p1_probs['ace_rate'] / 100))
        p2_stats.aces = max(0, int(p2_service_games * 4 * p2_probs['ace_rate'] / 100))

        # Estimate double faults
        p1_stats.double_faults = max(0, int(p1_service_games * 4 * p1_probs['double_fault_rate'] / 100))
        p2_stats.double_faults = max(0, int(p2_service_games * 4 * p2_probs['double_fault_rate'] / 100))

        # Update no double faults bonus
        if p1_stats.double_faults == 0:
            p1_stats.no_double_faults = True
        else:
            p1_stats.no_double_faults = False

        if p2_stats.double_faults == 0:
            p2_stats.no_double_faults = True
        else:
            p2_stats.no_double_faults = False

        # Estimate breaks (simplified)
        p1_stats.breaks = max(0, p2_service_games - p2_stats.games_won // 2)
        p2_stats.breaks = max(0, p1_service_games - p1_stats.games_won // 2)

        # Finalize match
        p1_won = p1_stats.sets_won > p2_stats.sets_won
        p1_stats.finalize_match(p1_won)
        p2_stats.finalize_match(not p1_won)

        return p1_stats, p2_stats

    def simulate_match_detailed(self, player1: str, player2: str, surface: str = 'Hard',
                              best_of_5: bool = False, use_variance: bool = True, verbose: bool = False) -> Tuple[FantasyStats, FantasyStats, List[SetResult]]:
        """Simulate a complete tennis match with detailed statistics."""
        if verbose:
            print(f"\n🎾 Simulating: {player1} vs {player2} on {surface}")
            print(f"Format: Best of {'5' if best_of_5 else '3'}")

        # Standard match simulation

        # Get match-specific probabilities
        p1_probs = self.get_match_adjusted_probabilities(player1, surface, use_variance)
        p2_probs = self.get_match_adjusted_probabilities(player2, surface, use_variance)

        if verbose:
            print(f"\n{player1} probabilities: Ace {p1_probs['ace_rate']:.1f}%, DF {p1_probs['double_fault_rate']:.1f}%")
            print(f"{player2} probabilities: Ace {p2_probs['ace_rate']:.1f}%, DF {p2_probs['double_fault_rate']:.1f}%")

        sets_needed = 3 if best_of_5 else 2
        sets = []
        p1_sets = 0
        p2_sets = 0

        while p1_sets < sets_needed and p2_sets < sets_needed:
            set_result = self.simulate_set(p1_probs, p2_probs, player1, player2)
            sets.append(set_result)

            if set_result.winner == player1:
                p1_sets += 1
            else:
                p2_sets += 1

            if verbose:
                print(f"Set {len(sets)}: {set_result}")

        # Calculate final statistics
        p1_stats, p2_stats = self.calculate_match_stats(sets, player1, player2)

        if verbose:
            print(f"\nMatch Result: {p1_stats.player_name} {p1_stats.sets_won}-{p1_stats.sets_lost} {p2_stats.player_name}")
            print(f"Fantasy Points: {p1_stats.player_name} {p1_stats.calculate_fantasy_points(best_of_5):.1f}, {p2_stats.player_name} {p2_stats.calculate_fantasy_points(best_of_5):.1f}")

        return p1_stats, p2_stats, sets

    def simulate_match_enhanced(self, player1: str, player2: str, surface: str = 'Hard',
                              best_of_5: bool = False, use_variance: bool = True,
                              analysis_depth: str = "standard", verbose: bool = False) -> EnhancedMatchResult:
        """
        Enhanced match simulation with ML insights and comprehensive analytics

        Args:
            player1: First player name
            player2: Second player name
            surface: Court surface (Hard, Clay, Grass)
            best_of_5: Whether to play best of 5 sets
            use_variance: Whether to apply match variance
            analysis_depth: Level of analysis (quick, standard, comprehensive)
            verbose: Whether to print detailed output

        Returns:
            EnhancedMatchResult with comprehensive analytics
        """
        # Initialize enhanced data engine if not already done
        if not hasattr(self, 'enhanced_engine'):
            self.enhanced_engine = EnhancedDataEngine()
            self.analytics_engine = EnhancedAnalyticsEngine()

        if verbose:
            print(f"\n🎾 Enhanced Simulation: {player1} vs {player2} on {surface}")
            print(f"Analysis Depth: {analysis_depth}")

        # Create enhanced player profiles
        p1_profile = self.enhanced_engine.create_enhanced_player_profile(player1, surface)
        p2_profile = self.enhanced_engine.create_enhanced_player_profile(player2, surface)

        if verbose:
            print(f"\n📊 Player Profiles:")
            print(f"   {player1}: {p1_profile.ml_archetype.primary_type} (confidence: {p1_profile.confidence_score:.2f})")
            print(f"   {player2}: {p2_profile.ml_archetype.primary_type} (confidence: {p2_profile.confidence_score:.2f})")

        # Run the standard simulation
        p1_stats, p2_stats, sets = self.simulate_match_detailed(
            player1, player2, surface, best_of_5, use_variance, verbose
        )

        # Determine winner and create basic result
        winner = 0 if p1_stats.sets_won > p2_stats.sets_won else 1
        final_score = [(s.winner_games, s.loser_games) for s in sets]

        # Calculate match duration (rough estimate)
        total_games = sum(s.winner_games + s.loser_games for s in sets)
        total_time_minutes = total_games * 8.5  # Average 8.5 minutes per game

        # Create enhanced result
        result = EnhancedMatchResult(
            player1_name=player1,
            player2_name=player2,
            surface=surface,
            winner=winner,
            final_score=final_score,
            sets=sets,
            total_time_minutes=total_time_minutes,
            fantasy_stats=(p1_stats, p2_stats),
            analysis_depth=analysis_depth
        )

        # Add enhanced analytics based on depth
        if analysis_depth in ["standard", "comprehensive"]:
            result.ml_insights = self.analytics_engine.generate_ml_insights(
                p1_profile, p2_profile, result
            )

            result.tactical_analysis = self.analytics_engine.generate_tactical_analysis(sets)

        if analysis_depth == "comprehensive":
            result.betting_analysis = self.analytics_engine.generate_betting_opportunities(result)

        if verbose:
            result.display_complete_analysis()

        return result
