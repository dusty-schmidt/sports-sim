#!/usr/bin/env python3
"""
Test Shelton vs Gigante with enhanced player data.
File location: /home/dustys/the net/tennis/scripts/test_shelton_gigante_enhanced.py
"""

import os
import sys

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scripts.enhanced_player_data_filler import EnhancedPlayerDataFiller


def test_shelton_gigante_enhanced():
    """Test Shelton vs Gigante with enhanced data filling."""
    print("🎾 TESTING SHELTON vs GIGANTE WITH ENHANCED DATA")
    print("=" * 70)
    
    # Create enhanced filler and enhance missing players
    filler = EnhancedPlayerDataFiller(min_matches_threshold=10)
    surface = 'Clay'
    
    # Enhance Gigante's data first
    print("1. ENHANCING GIGANTE'S DATA:")
    print("-" * 40)
    
    success = filler.enhance_player_data("Matteo Gigante", surface)
    if not success:
        print("❌ Failed to enhance Gigante's data")
        return
    
    # Verify the enhanced stats
    gigante_stats = filler.simulator.analyzer.get_player_stats("Matteo Gigante", surface)
    shelton_stats = filler.simulator.analyzer.get_player_stats("Ben Shelton", surface)
    
    print(f"\n2. VERIFIED ENHANCED STATS:")
    print("-" * 40)
    print(f"Ben Shelton:")
    print(f"  Service: {shelton_stats.get('service_points_won', 'N/A'):.1f}%")
    print(f"  Return: {shelton_stats.get('return_points_won', 'N/A'):.1f}%")
    print()
    print(f"Matteo Gigante:")
    print(f"  Service: {gigante_stats.get('service_points_won', 'N/A'):.1f}%")
    print(f"  Return: {gigante_stats.get('return_points_won', 'N/A'):.1f}%")
    
    # Get ELO data
    shelton_elo = filler.simulator.analyzer.get_player_elo("Ben Shelton", surface)
    gigante_elo = filler.simulator.analyzer.get_player_elo("Matteo Gigante", surface)
    
    print(f"\n3. ELO ANALYSIS:")
    print("-" * 40)
    print(f"Ben Shelton ELO: {shelton_elo:.1f}")
    print(f"Matteo Gigante ELO: {gigante_elo:.1f}")
    print(f"ELO difference: {shelton_elo - gigante_elo:.1f} points")
    
    # Calculate probabilities
    elo_prob = filler.simulator.calculate_elo_win_probability("Ben Shelton", "Matteo Gigante", surface)
    
    # Stats-based probability
    shelton_service = shelton_stats.get('service_points_won', 60.0)
    gigante_return = gigante_stats.get('return_points_won', 40.0)
    total_strength = shelton_service + gigante_return
    stats_prob = shelton_service / total_strength if total_strength > 0 else 0.5
    
    print(f"\n4. PROBABILITY COMPONENTS:")
    print("-" * 40)
    print(f"ELO-based probability: {elo_prob:.1%}")
    print(f"Stats-based probability: {stats_prob:.1%}")
    print(f"Vegas implied: 63.6%")
    
    # Test simulation with enhanced data
    print(f"\n5. SIMULATION WITH ENHANCED DATA:")
    print("-" * 40)
    
    shelton_wins = 0
    total_matches = 100
    
    print(f"Running {total_matches} simulations...")
    
    for i in range(total_matches):
        if (i + 1) % 20 == 0:
            current_rate = shelton_wins / (i + 1) * 100
            print(f"  After {i + 1} matches: Shelton {current_rate:.1f}% win rate")
        
        p1_stats, p2_stats, sets = filler.simulator.simulate_match_detailed(
            "Ben Shelton", "Matteo Gigante", surface, best_of_5=False, use_variance=True
        )
        
        if p1_stats.match_won:
            shelton_wins += 1
    
    win_rate = shelton_wins / total_matches * 100
    gap = win_rate - 63.6
    
    print(f"\n📊 ENHANCED SIMULATION RESULTS:")
    print("-" * 40)
    print(f"Ben Shelton wins: {shelton_wins}/{total_matches}")
    print(f"Win rate: {win_rate:.1f}%")
    print(f"Vegas implied: 63.6%")
    print(f"Difference: {gap:+.1f} percentage points")
    
    # Analyze the result
    if abs(gap) <= 5:
        print(f"\n✅ EXCELLENT: Within 5% of Vegas line!")
    elif abs(gap) <= 10:
        print(f"\n✅ GOOD: Within 10% of Vegas line")
    elif abs(gap) <= 15:
        print(f"\n⚠️  MODERATE: Within 15% of Vegas line")
    else:
        print(f"\n🚨 ISSUE: More than 15% off Vegas line")
    
    # Show what ELO weight was used
    elo_diff = shelton_elo - gigante_elo
    if elo_diff >= 400:
        elo_weight = 0.20
    elif elo_diff >= 300:
        elo_weight = 0.45
    elif elo_diff >= 200:
        elo_weight = 0.35
    elif elo_diff >= 100:
        elo_weight = 0.30
    else:
        elo_weight = 0.35
    
    print(f"\n🔧 TECHNICAL DETAILS:")
    print("-" * 40)
    print(f"ELO difference: {elo_diff:.1f} points")
    print(f"ELO weight used: {elo_weight:.0%}")
    print(f"Stats weight used: {1-elo_weight-0.10:.0%}")
    print(f"Random weight used: 10%")
    
    # Calculate expected blended probability
    expected_prob = (elo_weight * elo_prob) + ((1-elo_weight-0.10) * stats_prob) + (0.10 * 0.5)
    print(f"Expected blended probability: {expected_prob:.1%}")
    print(f"Actual simulation result: {win_rate:.1%}")
    
    return win_rate, gap


if __name__ == "__main__":
    win_rate, gap = test_shelton_gigante_enhanced()
