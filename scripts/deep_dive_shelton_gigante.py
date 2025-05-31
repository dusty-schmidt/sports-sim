#!/usr/bin/env python3
"""
Deep dive analysis of Ben Shelton vs Matteo Gigante matchup.
File location: /home/dustys/the net/tennis/scripts/deep_dive_shelton_gigante.py
"""

import os
import sys
import json

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sim_models.main_sim.simulator import FantasyTennisSimulator


def analyze_shelton_gigante_deep():
    """Deep dive into why Shelton vs Gigante is so skewed."""
    print("🔍 DEEP DIVE: BEN SHELTON vs MATTEO GIGANTE")
    print("=" * 80)
    print("Vegas Line: Shelton -175 (≈63.6% implied probability)")
    print("Our Simulation: 97.6% win rate")
    print("DISCREPANCY: 34 percentage points!")
    print()
    
    simulator = FantasyTennisSimulator()
    
    # Get detailed stats for both players
    print("📊 DETAILED PLAYER ANALYSIS")
    print("-" * 60)
    
    # Ben Shelton analysis
    shelton_stats = simulator.analyzer.get_player_stats("Ben Shelton", "Clay")
    shelton_elo = simulator.analyzer.get_player_elo("Ben Shelton", "Clay")
    
    print("BEN SHELTON:")
    print(f"  Clay ELO: {shelton_elo:.1f}")
    print(f"  Service Points Won: {shelton_stats.get('service_points_won', 'N/A'):.1f}%")
    print(f"  Return Points Won: {shelton_stats.get('return_points_won', 'N/A'):.1f}%")
    print(f"  Ace Rate: {shelton_stats.get('ace_rate', 'N/A'):.1f}%")
    print(f"  Double Fault Rate: {shelton_stats.get('double_fault_rate', 'N/A'):.1f}%")
    print(f"  First Serve %: {shelton_stats.get('first_serve_percentage', 'N/A'):.1f}%")
    print(f"  Rank: {shelton_stats.get('rank', 'N/A')}")
    print(f"  Surface Weight: {shelton_stats.get('_surface_weight', 'N/A')}")
    
    # Matteo Gigante analysis
    gigante_stats = simulator.analyzer.get_player_stats("Matteo Gigante", "Clay")
    gigante_elo = simulator.analyzer.get_player_elo("Matteo Gigante", "Clay")
    
    print(f"\nMATTEO GIGANTE:")
    print(f"  Clay ELO: {gigante_elo:.1f}")
    if gigante_stats:
        print(f"  Service Points Won: {gigante_stats.get('service_points_won', 'N/A'):.1f}%")
        print(f"  Return Points Won: {gigante_stats.get('return_points_won', 'N/A'):.1f}%")
        print(f"  Ace Rate: {gigante_stats.get('ace_rate', 'N/A'):.1f}%")
        print(f"  Double Fault Rate: {gigante_stats.get('double_fault_rate', 'N/A'):.1f}%")
        print(f"  First Serve %: {gigante_stats.get('first_serve_percentage', 'N/A'):.1f}%")
        print(f"  Rank: {gigante_stats.get('rank', 'N/A')}")
        print(f"  Surface Weight: {gigante_stats.get('_surface_weight', 'N/A')}")
    else:
        print("  ❌ NO CLAY COURT STATS - Using fallback!")
        
        # Check if he has any stats at all
        all_surface_stats = simulator.analyzer.get_player_stats("Matteo Gigante", None)
        if all_surface_stats:
            print(f"  ALL-SURFACE Service Points Won: {all_surface_stats.get('service_points_won', 'N/A'):.1f}%")
            print(f"  ALL-SURFACE Return Points Won: {all_surface_stats.get('return_points_won', 'N/A'):.1f}%")
            print(f"  ALL-SURFACE Rank: {all_surface_stats.get('rank', 'N/A')}")
        else:
            print("  ❌ NO STATS AT ALL - Using defaults!")
    
    # ELO-based probability
    elo_prob = simulator.calculate_elo_win_probability("Ben Shelton", "Matteo Gigante", "Clay")
    print(f"\n🎯 ELO-BASED WIN PROBABILITY:")
    print(f"  ELO difference: {shelton_elo - gigante_elo:.1f} points")
    print(f"  ELO win probability: {elo_prob:.1%}")
    print(f"  Vegas implied: 63.6%")
    print(f"  ELO vs Vegas difference: {elo_prob - 0.636:.1%}")
    
    # Simulate a few matches to see what's happening
    print(f"\n🎲 SAMPLE MATCH SIMULATIONS:")
    print("-" * 60)
    
    for i in range(5):
        p1_stats, p2_stats, sets = simulator.simulate_match_detailed(
            "Ben Shelton", "Matteo Gigante", "Clay", best_of_5=False, use_variance=True
        )
        
        winner = "Shelton" if p1_stats.match_won else "Gigante"
        score = f"{p1_stats.sets_won}-{p2_stats.sets_won}"
        p1_fp = p1_stats.calculate_fantasy_points(False)
        p2_fp = p2_stats.calculate_fantasy_points(False)
        
        print(f"  Match {i+1}: {winner} wins {score} | FP: {p1_fp:.1f} - {p2_fp:.1f}")
    
    # Check what default stats are being used
    print(f"\n🔍 INVESTIGATING DEFAULT STATS:")
    print("-" * 60)
    
    # Check if Gigante is getting default stats
    if not gigante_stats:
        print("Gigante has no clay stats, checking fallback mechanism...")
        
        # Check the analyzer's fallback logic
        if hasattr(simulator.analyzer, 'calculated_stats'):
            if "Matteo Gigante" in simulator.analyzer.calculated_stats:
                raw_data = simulator.analyzer.calculated_stats["Matteo Gigante"]
                print(f"Raw data available: {list(raw_data.keys())}")
                print(f"Total matches: {raw_data.get('matches', 0)}")
                print(f"Clay matches: {raw_data.get('clay_matches', 0)}")
            else:
                print("❌ Matteo Gigante not found in calculated_stats!")
    
    # Check what the actual point-by-point probabilities look like
    print(f"\n⚡ POINT-BY-POINT PROBABILITY ANALYSIS:")
    print("-" * 60)
    
    # Get match-adjusted probabilities
    shelton_probs = simulator.get_match_adjusted_probabilities("Ben Shelton", "Clay", use_variance=False)
    gigante_probs = simulator.get_match_adjusted_probabilities("Matteo Gigante", "Clay", use_variance=False)
    
    print("Ben Shelton serving probabilities:")
    for key, value in shelton_probs.items():
        print(f"  {key}: {value:.3f}")
    
    print(f"\nMatteo Gigante serving probabilities:")
    for key, value in gigante_probs.items():
        print(f"  {key}: {value:.3f}")
    
    # Calculate theoretical service hold rates
    shelton_hold = shelton_probs['service_points_won']
    gigante_hold = gigante_probs['service_points_won']
    shelton_break = 1 - gigante_probs['service_points_won']
    gigante_break = 1 - shelton_probs['service_points_won']
    
    print(f"\n📈 THEORETICAL HOLD/BREAK RATES:")
    print(f"  Shelton hold rate: {shelton_hold:.1%}")
    print(f"  Gigante hold rate: {gigante_hold:.1%}")
    print(f"  Shelton break rate: {shelton_break:.1%}")
    print(f"  Gigante break rate: {gigante_break:.1%}")
    
    # This should give us insight into why the simulation is so skewed
    if shelton_hold > 0.8 and gigante_hold < 0.5:
        print(f"\n🚨 FOUND THE ISSUE!")
        print(f"  Shelton holds serve {shelton_hold:.1%} of the time")
        print(f"  Gigante only holds serve {gigante_hold:.1%} of the time")
        print(f"  This creates a massive advantage for Shelton!")
    
    print(f"\n💡 POTENTIAL FIXES:")
    print("-" * 60)
    print("1. Check if Gigante's default stats are too weak")
    print("2. Verify ELO ratings are accurate for both players")
    print("3. Consider if 25% ELO weight is too low")
    print("4. Check if surface weighting is creating unrealistic gaps")


if __name__ == "__main__":
    analyze_shelton_gigante_deep()
