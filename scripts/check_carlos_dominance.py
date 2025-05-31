#!/usr/bin/env python3
"""
Check Carlos Alcaraz dominance levels and adjust ELO weighting.
File location: /home/dustys/the net/tennis/scripts/check_carlos_dominance.py
"""

import os
import sys
import json

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scripts.enhanced_player_data_filler import EnhancedPlayerDataFiller


def analyze_carlos_matchups():
    """Analyze Carlos Alcaraz's expected dominance vs his opponent."""
    print("🔍 ANALYZING CARLOS ALCARAZ DOMINANCE")
    print("=" * 60)
    
    # Load player pool to find Carlos's opponent
    player_pool_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'player_pool.json')
    with open(player_pool_path, 'r') as f:
        player_pool_data = json.load(f)
    
    surface = player_pool_data.get('surface', 'Clay')
    players = player_pool_data['players']
    
    # Find Carlos and his opponent
    carlos_data = None
    opponent_data = None
    
    for player in players:
        if 'Carlos Alcaraz' in player['name']:
            carlos_data = player
            # Find his opponent
            for p in players:
                if p['name'] == player['opponent']:
                    opponent_data = p
                    break
            break
    
    if not carlos_data or not opponent_data:
        print("❌ Could not find Carlos Alcaraz or his opponent in player pool")
        return
    
    print(f"Carlos Alcaraz (${carlos_data['salary']}) vs {opponent_data['name']} (${opponent_data['salary']})")
    print(f"Surface: {surface}")
    print()
    
    # Create enhanced filler and get ELO data
    filler = EnhancedPlayerDataFiller(min_matches_threshold=10)
    
    # Get ELO ratings
    carlos_elo = filler.simulator.analyzer.get_player_elo("Carlos Alcaraz", surface)
    opponent_elo = filler.simulator.analyzer.get_player_elo(opponent_data['name'], surface)
    
    print(f"📊 ELO ANALYSIS:")
    print(f"  Carlos Alcaraz ELO: {carlos_elo:.1f}")
    print(f"  {opponent_data['name']} ELO: {opponent_elo:.1f}")
    print(f"  ELO difference: {carlos_elo - opponent_elo:.1f} points")
    print()
    
    # Calculate ELO-based probability
    elo_prob = filler.simulator.calculate_elo_win_probability("Carlos Alcaraz", opponent_data['name'], surface)
    print(f"🎯 ELO-BASED WIN PROBABILITY:")
    print(f"  Carlos win probability: {elo_prob:.1%}")
    print(f"  DraftKings implied (-100000): 99.99%")
    print(f"  Difference: {elo_prob - 0.9999:.1%}")
    print()
    
    # Get actual stats being used
    carlos_stats = filler.simulator.analyzer.get_player_stats("Carlos Alcaraz", surface)
    opponent_stats = filler.simulator.analyzer.get_player_stats(opponent_data['name'], surface)
    
    print(f"📈 ACTUAL STATS:")
    print(f"  Carlos - Service: {carlos_stats.get('service_points_won', 'N/A'):.1f}%, Return: {carlos_stats.get('return_points_won', 'N/A'):.1f}%")
    print(f"  {opponent_data['name']} - Service: {opponent_stats.get('service_points_won', 'N/A'):.1f}%, Return: {opponent_stats.get('return_points_won', 'N/A'):.1f}%")
    print()
    
    # Test different ELO weights
    print(f"🔧 TESTING DIFFERENT ELO WEIGHTS:")
    print("-" * 40)
    
    elo_weights = [0.05, 0.15, 0.25, 0.35, 0.50, 0.75]
    
    for weight in elo_weights:
        # Calculate blended probability
        server_strength = carlos_stats.get('service_points_won', 65.0)
        returner_strength = opponent_stats.get('return_points_won', 35.0)
        total_strength = server_strength + returner_strength
        stats_prob = server_strength / total_strength if total_strength > 0 else 0.5
        
        blended_prob = (weight * elo_prob) + ((1 - weight) * stats_prob)
        
        print(f"  ELO weight {weight:.0%}: {blended_prob:.1%} win probability")
    
    print()
    
    # Run actual simulations with current settings
    print(f"🎾 CURRENT SIMULATION RESULTS:")
    print("-" * 40)
    
    carlos_wins = 0
    total_matches = 100
    
    for i in range(total_matches):
        p1_stats, p2_stats, sets = filler.simulator.simulate_match_detailed(
            "Carlos Alcaraz", opponent_data['name'], surface, best_of_5=False, use_variance=True
        )
        
        if p1_stats.match_won:
            carlos_wins += 1
    
    actual_win_rate = carlos_wins / total_matches * 100
    
    print(f"  Current simulation: {actual_win_rate:.1f}% win rate")
    print(f"  DraftKings line: 99.99% win rate")
    print(f"  Gap: {99.99 - actual_win_rate:.1f} percentage points")
    
    if actual_win_rate < 85:
        print(f"\n🚨 ISSUE: Carlos should be 85%+ favorite, showing {actual_win_rate:.1f}%")
        print("Need to increase ELO weight or adjust skill gap calculation")
    elif actual_win_rate < 95:
        print(f"\n⚠️  MODERATE: Carlos at {actual_win_rate:.1f}% is reasonable but could be higher")
    else:
        print(f"\n✅ GOOD: Carlos at {actual_win_rate:.1f}% shows proper dominance")
    
    return carlos_data, opponent_data, actual_win_rate


def suggest_elo_weight_adjustment():
    """Suggest optimal ELO weight for realistic tennis dominance."""
    print(f"\n💡 ELO WEIGHT RECOMMENDATIONS:")
    print("-" * 60)
    print("Current ELO weight: 5% (too low for elite dominance)")
    print()
    print("Recommended adjustments:")
    print("  • 25-35% ELO weight: For realistic elite player dominance")
    print("  • 50%+ ELO weight: For extreme favorites like Carlos vs low-ranked players")
    print("  • Keep variance low: Elite players should be consistent")
    print()
    print("This would create:")
    print("  • 85-95% win rates for elite vs mid-tier")
    print("  • 95-99% win rates for elite vs low-tier")
    print("  • Proper salary tier separation")


if __name__ == "__main__":
    carlos_data, opponent_data, win_rate = analyze_carlos_matchups()
    suggest_elo_weight_adjustment()
