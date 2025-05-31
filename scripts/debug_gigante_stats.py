#!/usr/bin/env python3
"""
Debug Matteo Gigante's missing stats issue.
File location: /home/dustys/the net/tennis/scripts/debug_gigante_stats.py
"""

import os
import sys
import json

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scripts.enhanced_player_data_filler import EnhancedPlayerDataFiller


def debug_gigante_stats():
    """Debug why Gigante's stats aren't loading."""
    print("🔍 DEBUGGING MATTEO GIGANTE STATS")
    print("=" * 60)
    
    # Create enhanced filler
    filler = EnhancedPlayerDataFiller(min_matches_threshold=10)
    surface = 'Clay'
    
    print("1. CHECKING CALCULATED STATS:")
    print("-" * 40)
    
    if "Matteo Gigante" in filler.simulator.analyzer.calculated_stats:
        gigante_calc = filler.simulator.analyzer.calculated_stats["Matteo Gigante"]
        print("✅ Matteo Gigante found in calculated_stats:")
        for key, value in gigante_calc.items():
            print(f"  {key}: {value}")
    else:
        print("❌ Matteo Gigante NOT found in calculated_stats")
    
    print("\n2. CHECKING RAW PLAYER DATA:")
    print("-" * 40)
    
    if "Matteo Gigante" in filler.all_players_data:
        gigante_raw = filler.all_players_data["Matteo Gigante"]
        print("✅ Matteo Gigante found in raw player data:")
        for key, value in gigante_raw.items():
            print(f"  {key}: {value}")
    else:
        print("❌ Matteo Gigante NOT found in raw player data")
    
    print("\n3. CHECKING GET_PLAYER_STATS:")
    print("-" * 40)
    
    stats = filler.simulator.analyzer.get_player_stats("Matteo Gigante", surface)
    if stats:
        print("✅ get_player_stats returned:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    else:
        print("❌ get_player_stats returned None")
    
    print("\n4. CHECKING ELO RATING:")
    print("-" * 40)
    
    elo = filler.simulator.analyzer.get_player_elo("Matteo Gigante", surface)
    print(f"ELO rating: {elo}")
    
    print("\n5. RUNNING ENHANCEMENT MANUALLY:")
    print("-" * 40)
    
    # Try to enhance manually
    success = filler.enhance_player_data("Matteo Gigante", surface)
    print(f"Enhancement result: {success}")
    
    if success:
        print("\n6. CHECKING STATS AFTER ENHANCEMENT:")
        print("-" * 40)
        
        stats_after = filler.simulator.analyzer.get_player_stats("Matteo Gigante", surface)
        if stats_after:
            print("✅ Stats after enhancement:")
            for key, value in stats_after.items():
                print(f"  {key}: {value}")
        else:
            print("❌ Still no stats after enhancement")
    
    print("\n7. TESTING SIMULATION WITH ENHANCED STATS:")
    print("-" * 40)
    
    # Test a few simulations
    wins = 0
    total = 20
    
    for i in range(total):
        p1_stats, p2_stats, sets = filler.simulator.simulate_match_detailed(
            "Ben Shelton", "Matteo Gigante", surface, best_of_5=False, use_variance=True
        )
        
        if p1_stats.match_won:
            wins += 1
    
    win_rate = wins / total * 100
    print(f"Shelton win rate after enhancement: {win_rate:.1f}%")
    
    return filler


def test_different_enhancement_approaches():
    """Test different ways to enhance Gigante's data."""
    print(f"\n🔧 TESTING DIFFERENT ENHANCEMENT APPROACHES")
    print("=" * 60)
    
    filler = EnhancedPlayerDataFiller(min_matches_threshold=10)
    surface = 'Clay'
    
    # Approach 1: Direct stat injection
    print("1. DIRECT STAT INJECTION:")
    print("-" * 40)
    
    gigante_elo = filler.simulator.analyzer.get_player_elo("Matteo Gigante", surface)
    print(f"Gigante ELO: {gigante_elo}")
    
    # Manually create reasonable stats for his ELO level
    enhanced_stats = {
        'service_points_won': 55.0,  # Appropriate for ELO 1580
        'return_points_won': 45.0,
        'ace_rate': 5.0,
        'double_fault_rate': 4.5,
        'first_serve_percentage': 60.0,
        'matches': 25,
        'clay_matches': 15,
        'data_source': 'manual_enhancement',
        'enhancement_info': {
            'target_elo': gigante_elo,
            'method': 'direct_injection'
        }
    }
    
    # Inject directly
    filler.simulator.analyzer.calculated_stats["Matteo Gigante"] = enhanced_stats
    
    # Test
    stats_check = filler.simulator.analyzer.get_player_stats("Matteo Gigante", surface)
    if stats_check:
        print("✅ Direct injection successful:")
        print(f"  Service: {stats_check.get('service_points_won', 'N/A'):.1f}%")
        print(f"  Return: {stats_check.get('return_points_won', 'N/A'):.1f}%")
    else:
        print("❌ Direct injection failed")
    
    # Test simulation
    wins = 0
    total = 50
    
    for i in range(total):
        p1_stats, p2_stats, sets = filler.simulator.simulate_match_detailed(
            "Ben Shelton", "Matteo Gigante", surface, best_of_5=False, use_variance=True
        )
        
        if p1_stats.match_won:
            wins += 1
    
    win_rate = wins / total * 100
    print(f"Shelton win rate with direct injection: {win_rate:.1f}%")
    print(f"Gap from Vegas (63.6%): {win_rate - 63.6:.1f} percentage points")
    
    # Approach 2: Adjust ELO weighting for this specific matchup
    print(f"\n2. TESTING DIFFERENT ELO WEIGHTS:")
    print("-" * 40)
    
    # Test with different ELO weights by temporarily modifying the simulator
    original_method = filler.simulator.simulate_match_detailed
    
    def test_with_elo_weight(weight):
        """Test simulation with specific ELO weight."""
        wins = 0
        total = 30
        
        for i in range(total):
            # Calculate probabilities manually with specific weight
            shelton_elo = filler.simulator.analyzer.get_player_elo("Ben Shelton", surface)
            gigante_elo = filler.simulator.analyzer.get_player_elo("Matteo Gigante", surface)
            
            elo_prob = filler.simulator.calculate_elo_win_probability("Ben Shelton", "Matteo Gigante", surface)
            
            # Get stats
            shelton_stats = filler.simulator.analyzer.get_player_stats("Ben Shelton", surface)
            gigante_stats = filler.simulator.analyzer.get_player_stats("Matteo Gigante", surface)
            
            shelton_service = shelton_stats.get('service_points_won', 60.0)
            gigante_return = gigante_stats.get('return_points_won', 40.0)
            total_strength = shelton_service + gigante_return
            stats_prob = shelton_service / total_strength if total_strength > 0 else 0.5
            
            # Blend with specific weight
            blended_prob = (weight * elo_prob) + ((1 - weight) * stats_prob)
            
            # Simple win/loss based on probability
            import random
            if random.random() < blended_prob:
                wins += 1
        
        return wins / total * 100
    
    elo_weights = [0.1, 0.2, 0.3, 0.4, 0.5]
    
    for weight in elo_weights:
        win_rate = test_with_elo_weight(weight)
        gap = win_rate - 63.6
        print(f"  ELO weight {weight:.1f}: {win_rate:>5.1f}% (gap: {gap:>+5.1f})")


if __name__ == "__main__":
    filler = debug_gigante_stats()
    test_different_enhancement_approaches()
