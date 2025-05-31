#!/usr/bin/env python3
"""
Investigate data mismatch between ELO and stats data.
File location: /home/dustys/the net/tennis/scripts/investigate_data_mismatch.py
"""

import os
import sys
import json

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sim_models.main_sim.simulator import FantasyTennisSimulator


def investigate_data_mismatch():
    """Investigate why players have ELO but no stats data."""
    print("🔍 INVESTIGATING DATA MISMATCH")
    print("=" * 80)
    
    simulator = FantasyTennisSimulator()
    
    # Load player pool to check all players
    player_pool_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'player_pool.json')
    with open(player_pool_path, 'r') as f:
        player_pool_data = json.load(f)
    
    players = player_pool_data['players']
    surface = player_pool_data.get('surface', 'Clay')
    
    print(f"Checking {len(players)} players for data consistency...")
    print(f"Surface: {surface}")
    print()
    
    # Check each player for data consistency
    has_elo_no_stats = []
    has_stats_no_elo = []
    has_both = []
    has_neither = []
    
    for player_data in players:
        player_name = player_data['name']
        
        # Check ELO data
        elo_rating = simulator.analyzer.get_player_elo(player_name, surface)
        has_elo = elo_rating is not None
        
        # Check stats data
        stats_data = simulator.analyzer.get_player_stats(player_name, surface)
        has_stats = stats_data is not None and len(stats_data) > 0
        
        # Check calculated stats (the source data)
        in_calculated_stats = player_name in simulator.analyzer.calculated_stats
        
        print(f"{player_name:<25} ELO: {'✅' if has_elo else '❌':<3} Stats: {'✅' if has_stats else '❌':<3} Calculated: {'✅' if in_calculated_stats else '❌'}")
        
        if has_elo and not has_stats:
            has_elo_no_stats.append({
                'name': player_name,
                'elo': elo_rating,
                'in_calculated': in_calculated_stats
            })
        elif has_stats and not has_elo:
            has_stats_no_elo.append(player_name)
        elif has_elo and has_stats:
            has_both.append(player_name)
        else:
            has_neither.append(player_name)
    
    print(f"\n📊 DATA CONSISTENCY SUMMARY:")
    print("-" * 60)
    print(f"Players with both ELO and stats: {len(has_both)}")
    print(f"Players with ELO but no stats: {len(has_elo_no_stats)}")
    print(f"Players with stats but no ELO: {len(has_stats_no_elo)}")
    print(f"Players with neither: {len(has_neither)}")
    
    if has_elo_no_stats:
        print(f"\n🚨 PLAYERS WITH ELO BUT NO STATS:")
        print("-" * 60)
        for player in has_elo_no_stats:
            print(f"  {player['name']:<25} ELO: {player['elo']:.1f} | In calculated_stats: {player['in_calculated']}")
            
            # Try to get their raw calculated stats
            if player['in_calculated']:
                raw_stats = simulator.analyzer.calculated_stats[player['name']]
                print(f"    Raw stats available: {list(raw_stats.keys())}")
                print(f"    Matches: {raw_stats.get('matches', 0)}")
                print(f"    Clay matches: {raw_stats.get('clay_matches', 0)}")
                print(f"    Service points won: {raw_stats.get('service_points_won', 'N/A')}")
            else:
                print(f"    ❌ Not found in calculated_stats!")
    
    if has_stats_no_elo:
        print(f"\n⚠️  PLAYERS WITH STATS BUT NO ELO:")
        print("-" * 60)
        for player in has_stats_no_elo:
            print(f"  {player}")
    
    if has_neither:
        print(f"\n❌ PLAYERS WITH NO DATA:")
        print("-" * 60)
        for player in has_neither:
            print(f"  {player}")
    
    # Special focus on Matteo Gigante
    print(f"\n🔍 DETAILED ANALYSIS: MATTEO GIGANTE")
    print("-" * 60)
    
    gigante_elo = simulator.analyzer.get_player_elo("Matteo Gigante", surface)
    gigante_stats = simulator.analyzer.get_player_stats("Matteo Gigante", surface)
    gigante_in_calculated = "Matteo Gigante" in simulator.analyzer.calculated_stats
    
    print(f"ELO rating: {gigante_elo}")
    print(f"Stats data: {gigante_stats}")
    print(f"In calculated_stats: {gigante_in_calculated}")
    
    if gigante_in_calculated:
        raw_data = simulator.analyzer.calculated_stats["Matteo Gigante"]
        print(f"Raw calculated stats:")
        for key, value in raw_data.items():
            print(f"  {key}: {value}")
    
    # Check if the issue is in the surface weighting
    print(f"\n🔍 SURFACE WEIGHTING ANALYSIS:")
    print("-" * 60)
    
    if gigante_in_calculated:
        raw_data = simulator.analyzer.calculated_stats["Matteo Gigante"]
        clay_matches = raw_data.get('clay_matches', 0)
        total_matches = raw_data.get('matches', 0)
        
        print(f"Total matches: {total_matches}")
        print(f"Clay matches: {clay_matches}")
        print(f"Clay percentage: {clay_matches/total_matches*100 if total_matches > 0 else 0:.1f}%")
        
        # Check if surface weighting is causing the issue
        if clay_matches == 0:
            print(f"🚨 FOUND THE ISSUE: Gigante has 0 clay matches!")
            print(f"   This means surface weighting returns None for clay stats")
            print(f"   But he still has ELO because ELO uses all matches")


if __name__ == "__main__":
    investigate_data_mismatch()
