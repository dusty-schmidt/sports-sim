#!/usr/bin/env python3
"""
Debug the hold/break rates being used for Shelton vs Gigante.
File location: /home/dustys/the net/tennis/scripts/debug_shelton_gigante_rates.py
"""

import os
import sys

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scripts.enhanced_full_slate_simulation import EnhancedSlateSimulator


def debug_shelton_gigante_rates():
    """Debug what hold/break rates are actually being used."""
    print("🔍 DEBUGGING SHELTON vs GIGANTE HOLD/BREAK RATES")
    print("=" * 70)
    
    simulator = EnhancedSlateSimulator()
    
    # Enhance all players first
    enhancement_results = simulator.enhance_all_players()
    
    # Get the stats for both players
    shelton_stats = simulator.filler.simulator.analyzer.calculated_stats.get('Ben Shelton', {})
    gigante_stats = simulator.filler.simulator.analyzer.calculated_stats.get('Matteo Gigante', {})
    
    print(f"\n📊 BEN SHELTON STATS:")
    print("-" * 40)
    for key, value in shelton_stats.items():
        print(f"  {key}: {value}")
    
    print(f"\n📊 MATTEO GIGANTE STATS:")
    print("-" * 40)
    for key, value in gigante_stats.items():
        print(f"  {key}: {value}")
    
    # Check what hold/break rates are being used
    print(f"\n🎯 HOLD/BREAK RATES BEING USED:")
    print("-" * 40)
    
    # Ben Shelton
    shelton_hold = shelton_stats.get('hold_rate', simulator._estimate_hold_rate(shelton_stats.get('service_points_won', 60)))
    shelton_break = shelton_stats.get('break_rate', simulator._estimate_break_rate(shelton_stats.get('return_points_won', 35)))
    
    print(f"Ben Shelton:")
    print(f"  Hold Rate: {shelton_hold:.1f}%")
    print(f"  Break Rate: {shelton_break:.1f}%")
    print(f"  Service Points Won: {shelton_stats.get('service_points_won', 'N/A')}")
    print(f"  Return Points Won: {shelton_stats.get('return_points_won', 'N/A')}")
    
    # Matteo Gigante
    gigante_hold = gigante_stats.get('hold_rate', simulator._estimate_hold_rate(gigante_stats.get('service_points_won', 60)))
    gigante_break = gigante_stats.get('break_rate', simulator._estimate_break_rate(gigante_stats.get('return_points_won', 35)))
    
    print(f"\nMatteo Gigante:")
    print(f"  Hold Rate: {gigante_hold:.1f}%")
    print(f"  Break Rate: {gigante_break:.1f}%")
    print(f"  Service Points Won: {gigante_stats.get('service_points_won', 'N/A')}")
    print(f"  Return Points Won: {gigante_stats.get('return_points_won', 'N/A')}")
    
    # Calculate expected match probability
    print(f"\n🎯 MATCH PROBABILITY CALCULATION:")
    print("-" * 40)
    
    shelton_advantage = shelton_hold - gigante_break
    gigante_advantage = gigante_hold - shelton_break
    
    print(f"Shelton service advantage: {shelton_advantage:.1f}%")
    print(f"Gigante service advantage: {gigante_advantage:.1f}%")
    
    # Run a few test simulations
    print(f"\n🎲 TEST SIMULATIONS:")
    print("-" * 40)
    
    shelton_wins = 0
    total_tests = 100
    
    for i in range(total_tests):
        player_won, match_details = simulator.simulate_match_with_hold_break_rates(
            'Ben Shelton', 'Matteo Gigante', 'Clay'
        )
        if player_won:
            shelton_wins += 1
    
    win_rate = shelton_wins / total_tests * 100
    print(f"Ben Shelton win rate: {win_rate:.1f}%")
    print(f"Expected (from our standalone test): ~73%")
    print(f"Vegas implied: 63.6%")
    
    if win_rate > 85:
        print("🚨 PROBLEM: Still too high! Need to investigate further.")
        
        # Check if Tennis Abstract stats are being applied
        if 'tennis_abstract_data' in shelton_stats:
            print("✅ Shelton has Tennis Abstract data")
            ta_data = shelton_stats['tennis_abstract_data']
            print(f"  TA Hold Rate: {ta_data['hold_rate']:.1f}%")
            print(f"  TA Break Rate: {ta_data['break_rate']:.1f}%")
        else:
            print("❌ Shelton missing Tennis Abstract data")
            
        if 'tennis_abstract_data' in gigante_stats:
            print("✅ Gigante has Tennis Abstract data")
        else:
            print("❌ Gigante missing Tennis Abstract data - using estimates")
            print(f"  Estimated from service: {gigante_stats.get('service_points_won', 'N/A')}")
            print(f"  Estimated from return: {gigante_stats.get('return_points_won', 'N/A')}")
    else:
        print("✅ Win rate looks reasonable!")


def test_hold_break_estimation():
    """Test the hold/break rate estimation functions."""
    print(f"\n🧪 TESTING HOLD/BREAK ESTIMATION FUNCTIONS:")
    print("-" * 40)
    
    simulator = EnhancedSlateSimulator()
    
    # Test various service/return percentages
    test_cases = [
        (68.8, 31.8, "Ben Shelton (TA real)"),
        (58.5, 41.5, "Matteo Gigante (estimated)"),
        (70.0, 35.0, "Elite player"),
        (60.0, 35.0, "Average player"),
        (55.0, 40.0, "Weak server, good returner")
    ]
    
    for service_pct, return_pct, description in test_cases:
        estimated_hold = simulator._estimate_hold_rate(service_pct)
        estimated_break = simulator._estimate_break_rate(return_pct)
        
        print(f"{description}:")
        print(f"  Service: {service_pct}% → Hold: {estimated_hold:.1f}%")
        print(f"  Return: {return_pct}% → Break: {estimated_break:.1f}%")
        print()


if __name__ == "__main__":
    debug_shelton_gigante_rates()
    test_hold_break_estimation()
