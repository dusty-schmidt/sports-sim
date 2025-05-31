#!/usr/bin/env python3
"""
Check ELO data coverage for all players in the player pool.
File location: /home/dustys/the net/tennis/scripts/check_elo_coverage.py
"""

import os
import sys
import json

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sim_models.main_sim.simulator import FantasyTennisSimulator


def check_elo_coverage():
    """Check which players have ELO data and which don't."""
    print("🔍 CHECKING ELO DATA COVERAGE FOR PLAYER POOL")
    print("=" * 80)
    
    simulator = FantasyTennisSimulator()
    
    # Load player pool
    player_pool_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'player_pool.json')
    with open(player_pool_path, 'r') as f:
        player_pool_data = json.load(f)
    
    surface = player_pool_data.get('surface', 'Clay')
    players = player_pool_data['players']
    
    print(f"Surface: {surface}")
    print(f"Total players: {len(players)}")
    
    # Check ELO coverage
    has_elo = []
    missing_elo = []
    
    print(f"\n📊 ELO DATA ANALYSIS")
    print("-" * 60)
    
    for player_data in players:
        player_name = player_data['name']
        salary = player_data['salary']
        
        # Check ELO data
        elo_rating = simulator.analyzer.get_player_elo(player_name, surface)
        
        if elo_rating:
            has_elo.append({
                'name': player_name,
                'salary': salary,
                'elo': elo_rating
            })
            status = f"✅ ELO: {elo_rating:.1f}"
        else:
            missing_elo.append({
                'name': player_name,
                'salary': salary
            })
            status = "❌ NO ELO"
        
        print(f"{player_name:<25} ${salary:<7} {status}")
    
    print(f"\n📈 SUMMARY")
    print("-" * 60)
    print(f"Players with ELO data: {len(has_elo)}/{len(players)} ({len(has_elo)/len(players)*100:.1f}%)")
    print(f"Players missing ELO: {len(missing_elo)}/{len(players)} ({len(missing_elo)/len(players)*100:.1f}%)")
    
    if missing_elo:
        print(f"\n❌ PLAYERS MISSING ELO DATA:")
        print("-" * 40)
        for player in sorted(missing_elo, key=lambda x: x['salary'], reverse=True):
            print(f"  {player['name']:<25} ${player['salary']}")
    
    if has_elo:
        print(f"\n✅ PLAYERS WITH ELO DATA:")
        print("-" * 40)
        for player in sorted(has_elo, key=lambda x: x['elo'], reverse=True):
            print(f"  {player['name']:<25} ${player['salary']:<7} ELO: {player['elo']:.1f}")
    
    print(f"\n🎯 IMPACT ON SIMULATION:")
    print("-" * 60)
    print("Players WITH ELO data:")
    print("  • Use 25% ELO + 75% stats blending")
    print("  • Get proper skill-based win probabilities")
    print("  • Elite players dominate appropriately")
    print()
    print("Players WITHOUT ELO data:")
    print("  • Fall back to pure stats-based simulation")
    print("  • May have less realistic skill gaps")
    print("  • Could over/under-perform vs expectations")
    
    return has_elo, missing_elo


if __name__ == "__main__":
    has_elo, missing_elo = check_elo_coverage()
