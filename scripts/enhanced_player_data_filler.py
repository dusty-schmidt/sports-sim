#!/usr/bin/env python3
"""
Enhanced player data filler for missing players and small sample sizes.
File location: /home/dustys/the net/tennis/scripts/enhanced_player_data_filler.py
"""

import os
import sys
import json
from typing import Dict, List, Optional, Tuple

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sim_models.main_sim.simulator import FantasyTennisSimulator


class EnhancedPlayerDataFiller:
    """Fill in missing or insufficient player data using ELO-based approximation."""

    def __init__(self, min_matches_threshold: int = 10):
        """
        Initialize the data filler.

        Args:
            min_matches_threshold: Minimum matches required to consider data sufficient
        """
        self.min_matches_threshold = min_matches_threshold
        self.simulator = FantasyTennisSimulator()
        self.all_players_data = self._load_all_players_data()

    def _load_all_players_data(self) -> Dict:
        """Load all player data from the processed stats file."""
        all_players_file = os.path.join(
            os.path.dirname(__file__), '..', 'data', 'processed', 'player_stats.json'
        )
        with open(all_players_file, 'r') as f:
            return json.load(f)

    def identify_players_needing_enhancement(self, player_names: List[str], surface: str = 'Clay') -> Dict[str, str]:
        """
        Identify players who need data enhancement.

        Returns:
            Dict mapping player_name to reason ('missing', 'insufficient', 'ok')
        """
        enhancement_needs = {}

        for player_name in player_names:
            # Check if player has any calculated stats
            if player_name not in self.simulator.analyzer.calculated_stats:
                enhancement_needs[player_name] = 'missing'
                continue

            # Check if player has surface-specific stats
            surface_stats = self.simulator.analyzer.get_player_stats(player_name, surface)
            if not surface_stats:
                enhancement_needs[player_name] = 'missing_surface'
                continue

            # Check sample size
            player_data = self.simulator.analyzer.calculated_stats[player_name]
            surface_matches_key = f'{surface.lower()}_matches'
            surface_matches = player_data.get(surface_matches_key, 0)
            total_matches = player_data.get('matches', 0)

            if surface_matches < self.min_matches_threshold and total_matches < self.min_matches_threshold:
                enhancement_needs[player_name] = 'insufficient'
            else:
                enhancement_needs[player_name] = 'ok'

        return enhancement_needs

    def calculate_elo_based_stats(self, target_elo: float, surface: str = 'Clay',
                                 elo_range: int = 100) -> Tuple[Optional[Dict[str, float]], List[Dict]]:
        """Calculate stats based on average of players with similar ELO ratings."""
        similar_players = []

        # Get players with similar ELO ratings
        for player_name, player_data in self.all_players_data.items():
            if isinstance(player_data, dict):
                player_elo = self.simulator.analyzer.get_player_elo(player_name, surface)

                if player_elo and abs(player_elo - target_elo) <= elo_range:
                    # Check if this player has sufficient data
                    if player_name in self.simulator.analyzer.calculated_stats:
                        calc_data = self.simulator.analyzer.calculated_stats[player_name]
                        surface_matches = calc_data.get(f'{surface.lower()}_matches', 0)
                        total_matches = calc_data.get('matches', 0)

                        # Only use players with sufficient data for approximation
                        if surface_matches >= self.min_matches_threshold or total_matches >= 20:
                            similar_players.append({
                                'name': player_name,
                                'elo': player_elo,
                                'stats': {
                                    'service_points_won': player_data.get('service_points_won', 60.0),
                                    'return_points_won': player_data.get('return_points_won', 40.0),
                                    'ace_rate': player_data.get('ace_rate', 6.0),
                                    'double_fault_rate': player_data.get('double_fault_rate', 4.0),
                                    'first_serve_percentage': player_data.get('first_serve_percentage', 62.0)
                                },
                                'matches': total_matches,
                                'surface_matches': surface_matches
                            })

        # If not enough similar players, expand search range
        if len(similar_players) < 5:
            return self.calculate_elo_based_stats(target_elo, surface, elo_range * 2)

        if similar_players:
            # Calculate weighted average based on ELO proximity and data quality
            total_weight = 0
            weighted_stats = {
                'service_points_won': 0.0,
                'return_points_won': 0.0,
                'ace_rate': 0.0,
                'double_fault_rate': 0.0,
                'first_serve_percentage': 0.0
            }

            for player in similar_players:
                # Weight based on ELO proximity and data quality
                elo_diff = abs(player['elo'] - target_elo)
                elo_weight = 1 / (1 + elo_diff / 50)

                # Bonus weight for more matches
                data_quality_weight = min(2.0, player['matches'] / 20)

                weight = elo_weight * data_quality_weight
                total_weight += weight

                for stat_name in weighted_stats.keys():
                    if stat_name in player['stats']:
                        weighted_stats[stat_name] += player['stats'][stat_name] * weight

            # Normalize by total weight
            if total_weight > 0:
                for stat_name in weighted_stats.keys():
                    weighted_stats[stat_name] /= total_weight

            return weighted_stats, similar_players

        return None, []

    def enhance_player_data(self, player_name: str, surface: str = 'Clay') -> bool:
        """
        Enhance data for a specific player.

        Returns:
            True if enhancement was successful, False otherwise
        """
        player_elo = self.simulator.analyzer.get_player_elo(player_name, surface)
        if not player_elo:
            print(f"❌ No ELO data for {player_name}, cannot enhance")
            return False

        approximated_stats, similar_players = self.calculate_elo_based_stats(player_elo, surface)

        if not approximated_stats:
            print(f"❌ Could not find similar players for {player_name} (ELO {player_elo:.0f})")
            return False

        # Create or update calculated stats entry
        calculated_stats_entry = {
            'service_points_won': approximated_stats['service_points_won'],
            'return_points_won': approximated_stats['return_points_won'],
            'ace_rate': approximated_stats['ace_rate'],
            'double_fault_rate': approximated_stats['double_fault_rate'],
            'first_serve_percentage': approximated_stats['first_serve_percentage'],
            'matches': max(20, len(similar_players)),  # Reasonable number for approximation
            f'{surface.lower()}_matches': max(10, len(similar_players) // 2),
            'data_source': 'elo_approximated',
            'enhancement_info': {
                'target_elo': player_elo,
                'based_on_players': len(similar_players),
                'elo_range': f"{min(p['elo'] for p in similar_players):.0f}-{max(p['elo'] for p in similar_players):.0f}",
                'similar_players': [p['name'] for p in similar_players[:5]],
                'avg_matches_per_similar': sum(p['matches'] for p in similar_players) / len(similar_players)
            }
        }

        # Add to calculated_stats
        self.simulator.analyzer.calculated_stats[player_name] = calculated_stats_entry

        print(f"✅ Enhanced {player_name} (ELO {player_elo:.0f}):")
        print(f"   Service: {approximated_stats['service_points_won']:.1f}%")
        print(f"   Return: {approximated_stats['return_points_won']:.1f}%")
        print(f"   Based on {len(similar_players)} similar players")

        return True

    def enhance_player_pool(self, player_pool_data: Dict, surface: str = 'Clay') -> Dict[str, str]:
        """
        Enhance all players in a player pool that need enhancement.

        Returns:
            Dict mapping player_name to enhancement_result
        """
        player_names = [p['name'] for p in player_pool_data['players']]
        enhancement_needs = self.identify_players_needing_enhancement(player_names, surface)

        print(f"🔍 PLAYER DATA ENHANCEMENT ANALYSIS")
        print("=" * 60)
        print(f"Surface: {surface}")
        print(f"Minimum matches threshold: {self.min_matches_threshold}")
        print()

        # Categorize players
        missing = [name for name, reason in enhancement_needs.items() if reason == 'missing']
        missing_surface = [name for name, reason in enhancement_needs.items() if reason == 'missing_surface']
        insufficient = [name for name, reason in enhancement_needs.items() if reason == 'insufficient']
        ok = [name for name, reason in enhancement_needs.items() if reason == 'ok']

        print(f"📊 PLAYER CATEGORIES:")
        print(f"  ✅ Sufficient data: {len(ok)} players")
        print(f"  ⚠️  Insufficient data: {len(insufficient)} players")
        print(f"  ❌ Missing surface data: {len(missing_surface)} players")
        print(f"  ❌ Completely missing: {len(missing)} players")
        print()

        # Enhance players that need it
        enhancement_results = {}
        players_to_enhance = missing + missing_surface + insufficient

        if players_to_enhance:
            print(f"🔧 ENHANCING {len(players_to_enhance)} PLAYERS:")
            print("-" * 40)

            for player_name in players_to_enhance:
                success = self.enhance_player_data(player_name, surface)
                enhancement_results[player_name] = 'success' if success else 'failed'

        else:
            print("✅ All players have sufficient data!")

        return enhancement_results


def enhance_full_slate():
    """Enhance the full player pool and run simulation."""
    print("🎾 ENHANCED FULL SLATE SIMULATION")
    print("=" * 80)

    # Load player pool
    player_pool_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'player_pool.json')
    with open(player_pool_path, 'r') as f:
        player_pool_data = json.load(f)

    surface = player_pool_data.get('surface', 'Clay')

    # Create data filler with threshold of 10 matches
    filler = EnhancedPlayerDataFiller(min_matches_threshold=10)

    # Enhance the player pool
    enhancement_results = filler.enhance_player_pool(player_pool_data, surface)

    print(f"\n🎯 ENHANCEMENT SUMMARY:")
    print("-" * 40)
    successful = sum(1 for result in enhancement_results.values() if result == 'success')
    failed = sum(1 for result in enhancement_results.values() if result == 'failed')
    print(f"Successfully enhanced: {successful} players")
    print(f"Failed to enhance: {failed} players")

    # Now run the simulation with enhanced data
    print(f"\n🎲 RUNNING ENHANCED SIMULATION...")
    print("-" * 40)

    # Import and run the player pool simulation
    from scripts.player_pool_simulation import simulate_player_pool

    # Run with the enhanced simulator
    results = simulate_player_pool(filler.simulator)

    return results, enhancement_results


if __name__ == "__main__":
    results, enhancements = enhance_full_slate()
