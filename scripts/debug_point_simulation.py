#!/usr/bin/env python3
"""
Debug point-level simulation to find why 63.4% probability becomes 100% win rate.
File location: /home/dustys/the net/tennis/scripts/debug_point_simulation.py
"""

import os
import sys
import random

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scripts.enhanced_player_data_filler import EnhancedPlayerDataFiller


def debug_point_simulation():
    """Debug why point simulation creates extreme dominance."""
    print("🔍 DEBUGGING POINT-LEVEL SIMULATION")
    print("=" * 70)
    
    # Create enhanced filler and enhance Gigante
    filler = EnhancedPlayerDataFiller(min_matches_threshold=10)
    surface = 'Clay'
    
    # Enhance Gigante's data
    filler.enhance_player_data("Matteo Gigante", surface)
    
    # Get the probabilities
    shelton_probs = filler.simulator.get_match_adjusted_probabilities("Ben Shelton", surface, True)
    gigante_probs = filler.simulator.get_match_adjusted_probabilities("Matteo Gigante", surface, True)
    
    print("1. MATCH-ADJUSTED PROBABILITIES:")
    print("-" * 40)
    print(f"Ben Shelton:")
    for key, value in shelton_probs.items():
        print(f"  {key}: {value:.1f}%")
    
    print(f"\nMatteo Gigante:")
    for key, value in gigante_probs.items():
        print(f"  {key}: {value:.1f}%")
    
    # Test point simulation directly
    print(f"\n2. TESTING POINT SIMULATION:")
    print("-" * 40)
    
    shelton_point_wins = 0
    total_points = 1000
    
    for i in range(total_points):
        # Create rally context
        rally_context = {
            'server_name': 'Ben Shelton',
            'returner_name': 'Matteo Gigante',
            'current_set': 1,
            'surface': surface
        }
        
        # Simulate point with Shelton serving
        point_result = filler.simulator.simulate_point(
            shelton_probs, gigante_probs, None, rally_context
        )
        
        if point_result['winner'] == 'server':
            shelton_point_wins += 1
    
    point_win_rate = shelton_point_wins / total_points * 100
    
    print(f"Shelton service points won: {shelton_point_wins}/{total_points}")
    print(f"Point win rate: {point_win_rate:.1f}%")
    print(f"Expected from stats: ~{shelton_probs['service_points_won']:.1f}%")
    
    # Test with Gigante serving
    print(f"\n3. TESTING GIGANTE SERVING:")
    print("-" * 40)
    
    gigante_point_wins = 0
    
    for i in range(total_points):
        rally_context = {
            'server_name': 'Matteo Gigante',
            'returner_name': 'Ben Shelton',
            'current_set': 1,
            'surface': surface
        }
        
        point_result = filler.simulator.simulate_point(
            gigante_probs, shelton_probs, None, rally_context
        )
        
        if point_result['winner'] == 'server':
            gigante_point_wins += 1
    
    gigante_point_win_rate = gigante_point_wins / total_points * 100
    
    print(f"Gigante service points won: {gigante_point_wins}/{total_points}")
    print(f"Point win rate: {gigante_point_win_rate:.1f}%")
    print(f"Expected from stats: ~{gigante_probs['service_points_won']:.1f}%")
    
    # Calculate overall match probability from service/return rates
    print(f"\n4. CALCULATING MATCH PROBABILITY:")
    print("-" * 40)
    
    # Approximate match probability from service/return rates
    # In tennis, roughly 50% of points are on each player's serve
    shelton_service_rate = shelton_probs['service_points_won'] / 100
    shelton_return_rate = shelton_probs['return_points_won'] / 100
    gigante_service_rate = gigante_probs['service_points_won'] / 100
    gigante_return_rate = gigante_probs['return_points_won'] / 100
    
    # Shelton's overall point win rate
    shelton_overall = 0.5 * shelton_service_rate + 0.5 * shelton_return_rate
    
    print(f"Shelton service rate: {shelton_service_rate:.3f}")
    print(f"Shelton return rate: {shelton_return_rate:.3f}")
    print(f"Shelton overall point rate: {shelton_overall:.3f}")
    
    print(f"Gigante service rate: {gigante_service_rate:.3f}")
    print(f"Gigante return rate: {gigante_return_rate:.3f}")
    
    # This is a rough approximation - real tennis is more complex
    print(f"Approximate match probability: {shelton_overall:.1%}")
    
    # Test game simulation
    print(f"\n5. TESTING GAME SIMULATION:")
    print("-" * 40)
    
    shelton_games_won = 0
    total_games = 100
    
    for i in range(total_games):
        # Simulate game with Shelton serving
        game_result = filler.simulator.simulate_game(
            shelton_probs, gigante_probs, "Ben Shelton", "Matteo Gigante"
        )
        
        if game_result.winner == "Ben Shelton":
            shelton_games_won += 1
    
    game_win_rate = shelton_games_won / total_games * 100
    
    print(f"Shelton service games won: {shelton_games_won}/{total_games}")
    print(f"Service game win rate: {game_win_rate:.1f}%")
    
    # Test with Gigante serving
    gigante_games_won = 0
    
    for i in range(total_games):
        game_result = filler.simulator.simulate_game(
            gigante_probs, shelton_probs, "Matteo Gigante", "Ben Shelton"
        )
        
        if game_result.winner == "Matteo Gigante":
            gigante_games_won += 1
    
    gigante_game_win_rate = gigante_games_won / total_games * 100
    
    print(f"Gigante service games won: {gigante_games_won}/{total_games}")
    print(f"Gigante service game win rate: {gigante_game_win_rate:.1f}%")
    
    # Calculate break rates
    shelton_break_rate = 100 - gigante_game_win_rate
    gigante_break_rate = 100 - game_win_rate
    
    print(f"\nBreak rates:")
    print(f"Shelton breaks Gigante: {shelton_break_rate:.1f}%")
    print(f"Gigante breaks Shelton: {gigante_break_rate:.1f}%")
    
    # If one player breaks much more often, they'll dominate
    if shelton_break_rate > 20 and gigante_break_rate < 5:
        print(f"\n🚨 ISSUE FOUND: Massive break rate difference!")
        print(f"This explains why Shelton wins 100% of matches")
        print(f"Need to reduce service/return gap or increase variance")
    
    return point_win_rate, game_win_rate, shelton_break_rate, gigante_break_rate


def test_variance_impact():
    """Test how variance affects the extreme dominance."""
    print(f"\n🎲 TESTING VARIANCE IMPACT")
    print("=" * 70)
    
    filler = EnhancedPlayerDataFiller(min_matches_threshold=10)
    surface = 'Clay'
    filler.enhance_player_data("Matteo Gigante", surface)
    
    variance_levels = [0.1, 0.2, 0.3, 0.4, 0.5]
    
    for variance in variance_levels:
        # Get probabilities with specific variance
        shelton_probs = filler.simulator.get_match_adjusted_probabilities(
            "Ben Shelton", surface, True, variance
        )
        gigante_probs = filler.simulator.get_match_adjusted_probabilities(
            "Matteo Gigante", surface, True, variance
        )
        
        # Test a few matches
        shelton_wins = 0
        total_matches = 20
        
        for i in range(total_matches):
            p1_stats, p2_stats, sets = filler.simulator.simulate_match_detailed(
                "Ben Shelton", "Matteo Gigante", surface, best_of_5=False, use_variance=True
            )
            
            if p1_stats.match_won:
                shelton_wins += 1
        
        win_rate = shelton_wins / total_matches * 100
        
        print(f"Variance {variance:.1f}: {win_rate:>5.1f}% win rate")
        print(f"  Shelton service: {shelton_probs['service_points_won']:>5.1f}%")
        print(f"  Gigante service: {gigante_probs['service_points_won']:>5.1f}%")


if __name__ == "__main__":
    point_rate, game_rate, shelton_breaks, gigante_breaks = debug_point_simulation()
    test_variance_impact()
