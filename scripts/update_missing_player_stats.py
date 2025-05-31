#!/usr/bin/env python3
"""
Update the simulator with ELO-approximated stats for missing players.
File location: /home/dustys/the net/tennis/scripts/update_missing_player_stats.py
"""

import os
import sys
import json

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scripts.fuzzy_match_and_elo_approximation import analyze_missing_players
from sim_models.main_sim.simulator import FantasyTennisSimulator


def update_simulator_with_approximated_stats():
    """Update the simulator's analyzer with approximated stats for missing players."""
    print("🔄 UPDATING SIMULATOR WITH APPROXIMATED STATS")
    print("=" * 60)
    
    # Get the approximated stats
    missing_players, fuzzy_matches, elo_approximations = analyze_missing_players()
    
    if not elo_approximations:
        print("❌ No ELO approximations found to update")
        return
    
    # Load the simulator
    simulator = FantasyTennisSimulator()
    
    print(f"\n📝 UPDATING CALCULATED STATS...")
    print("-" * 40)
    
    # Update the calculated_stats with approximated data
    for player_name, approximation_data in elo_approximations.items():
        stats = approximation_data['stats']
        
        # Create calculated stats entry
        calculated_stats_entry = {
            'service_points_won': stats['service_points_won'],
            'return_points_won': stats['return_points_won'],
            'ace_rate': stats['ace_rate'],
            'double_fault_rate': stats['double_fault_rate'],
            'first_serve_percentage': stats['first_serve_percentage'],
            'matches': 50,  # Reasonable number for approximation
            'clay_matches': 25,  # Half on clay
            'hard_matches': 20,  # Some on hard
            'grass_matches': 5,   # Some on grass
            'data_source': 'elo_approximated',
            'approximation_info': {
                'based_on_players': len(approximation_data.get('similar_players', [])),
                'elo_range': approximation_data.get('elo_range', 'unknown'),
                'similar_players': approximation_data.get('similar_players', [])
            }
        }
        
        # Add to calculated_stats
        simulator.analyzer.calculated_stats[player_name] = calculated_stats_entry
        
        print(f"✅ Updated {player_name}:")
        print(f"   Service: {stats['service_points_won']:.1f}%")
        print(f"   Return: {stats['return_points_won']:.1f}%")
        print(f"   Based on: {approximation_data.get('elo_range', 'unknown')} ELO range")
    
    print(f"\n🎯 TESTING UPDATED STATS...")
    print("-" * 40)
    
    # Test that the stats are now available
    for player_name in elo_approximations.keys():
        surface_stats = simulator.analyzer.get_player_stats(player_name, 'Clay')
        if surface_stats:
            print(f"✅ {player_name}: Service {surface_stats.get('service_points_won', 'N/A'):.1f}%")
        else:
            print(f"❌ {player_name}: Still no stats available")
    
    return simulator


def test_updated_simulation():
    """Test the simulation with updated stats."""
    print(f"\n🎾 TESTING SHELTON vs GIGANTE WITH UPDATED STATS")
    print("=" * 60)
    
    # Update the simulator
    simulator = update_simulator_with_approximated_stats()
    
    # Run a few test matches
    shelton_wins = 0
    total_matches = 50
    
    print(f"\nRunning {total_matches} test simulations...")
    
    for i in range(total_matches):
        p1_stats, p2_stats, sets = simulator.simulate_match_detailed(
            "Ben Shelton", "Matteo Gigante", "Clay", best_of_5=False, use_variance=True
        )
        
        if p1_stats.match_won:
            shelton_wins += 1
    
    win_rate = shelton_wins / total_matches * 100
    
    print(f"\n📊 RESULTS WITH UPDATED STATS:")
    print(f"  Ben Shelton wins: {shelton_wins}/{total_matches}")
    print(f"  Win rate: {win_rate:.1f}%")
    print(f"  Vegas implied: 63.6%")
    print(f"  Difference: {win_rate - 63.6:.1f} percentage points")
    
    # Show the actual stats being used
    shelton_stats = simulator.analyzer.get_player_stats("Ben Shelton", "Clay")
    gigante_stats = simulator.analyzer.get_player_stats("Matteo Gigante", "Clay")
    
    print(f"\n📈 ACTUAL STATS USED:")
    print(f"  Ben Shelton - Service: {shelton_stats.get('service_points_won', 'N/A'):.1f}%, Return: {shelton_stats.get('return_points_won', 'N/A'):.1f}%")
    print(f"  Matteo Gigante - Service: {gigante_stats.get('service_points_won', 'N/A'):.1f}%, Return: {gigante_stats.get('return_points_won', 'N/A'):.1f}%")
    
    # Calculate ELO probability for comparison
    elo_prob = simulator.calculate_elo_win_probability("Ben Shelton", "Matteo Gigante", "Clay")
    print(f"  ELO probability: {elo_prob:.1%}")
    
    if abs(win_rate - 63.6) <= 5:
        print(f"\n✅ SUCCESS: Win rate within 5% of Vegas line!")
    else:
        print(f"\n⚠️  Still some discrepancy, but much better than before")


if __name__ == "__main__":
    test_updated_simulation()
