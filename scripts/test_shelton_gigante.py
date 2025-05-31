#!/usr/bin/env python3
"""
Quick test of Shelton vs Gigante win rates.
File location: /home/dustys/the net/tennis/scripts/test_shelton_gigante.py
"""

import os
import sys

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sim_models.main_sim.simulator import FantasyTennisSimulator


def test_shelton_gigante():
    """Test Shelton vs Gigante win rates."""
    print("🎾 TESTING SHELTON vs GIGANTE WIN RATES")
    print("=" * 60)
    
    simulator = FantasyTennisSimulator()
    
    # Run 100 quick simulations
    shelton_wins = 0
    total_matches = 100
    
    print(f"Running {total_matches} simulations...")
    
    for i in range(total_matches):
        p1_stats, p2_stats, sets = simulator.simulate_match_detailed(
            "Ben Shelton", "Matteo Gigante", "Clay", best_of_5=False, use_variance=True
        )
        
        if p1_stats.match_won:
            shelton_wins += 1
        
        if (i + 1) % 20 == 0:
            current_rate = shelton_wins / (i + 1) * 100
            print(f"  After {i+1} matches: Shelton {current_rate:.1f}% win rate")
    
    final_win_rate = shelton_wins / total_matches * 100
    
    print(f"\n📊 FINAL RESULTS:")
    print(f"  Ben Shelton wins: {shelton_wins}/{total_matches}")
    print(f"  Win rate: {final_win_rate:.1f}%")
    print(f"  Vegas implied: 63.6%")
    print(f"  Difference: {final_win_rate - 63.6:.1f} percentage points")
    
    # Show the probability calculations
    print(f"\n🔍 PROBABILITY BREAKDOWN:")
    
    # Get ELO probability
    elo_prob = simulator.calculate_elo_win_probability("Ben Shelton", "Matteo Gigante", "Clay")
    print(f"  ELO-based probability: {elo_prob:.1%}")
    
    # Get stats-based probability
    shelton_probs = simulator.get_match_adjusted_probabilities("Ben Shelton", "Clay", use_variance=False)
    gigante_probs = simulator.get_match_adjusted_probabilities("Matteo Gigante", "Clay", use_variance=False)
    
    print(f"  Shelton service: {shelton_probs['service_points_won']:.1f}%")
    print(f"  Gigante service: {gigante_probs['service_points_won']:.1f}%")
    print(f"  Shelton return: {shelton_probs['return_points_won']:.1f}%")
    print(f"  Gigante return: {gigante_probs['return_points_won']:.1f}%")
    
    # Calculate stats-based probability correctly
    server_strength = shelton_probs['service_points_won']
    returner_strength = gigante_probs['return_points_won']
    total_strength = server_strength + returner_strength
    stats_prob = server_strength / total_strength
    
    print(f"  Stats-based probability: {stats_prob:.1%}")
    
    # Final blended probability
    elo_weight = 0.25
    stats_weight = 0.75
    final_prob = (elo_weight * elo_prob) + (stats_weight * stats_prob)
    
    print(f"  Final blended probability: {final_prob:.1%}")
    
    if final_win_rate > 80:
        print(f"\n🚨 ISSUE CONFIRMED:")
        print(f"  Simulation shows {final_win_rate:.1f}% but should be closer to 63.6%")
        print(f"  The ELO + stats blending is creating too much dominance")
    else:
        print(f"\n✅ LOOKS REASONABLE:")
        print(f"  Simulation shows {final_win_rate:.1f}% vs Vegas 63.6%")


if __name__ == "__main__":
    test_shelton_gigante()
