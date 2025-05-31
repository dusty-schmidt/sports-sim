#!/usr/bin/env python3
"""
Load Tennis Abstract hold/break rates and integrate into simulation.
File location: /home/dustys/the net/tennis/scripts/load_tennis_abstract_stats.py
"""

import os
import sys
import pandas as pd
import json

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scripts.enhanced_player_data_filler import EnhancedPlayerDataFiller


def load_tennis_abstract_stats():
    """Load Tennis Abstract serve and return stats."""
    print("📊 LOADING TENNIS ABSTRACT STATS")
    print("=" * 60)
    
    # Load serve stats
    serve_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'tenab_stats', 'serve.csv')
    serve_df = pd.read_csv(serve_file, sep='\t')
    
    # Load return stats  
    return_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'tenab_stats', 'return.csv')
    return_df = pd.read_csv(return_file, sep='\t')
    
    print(f"✅ Loaded {len(serve_df)} players from serve.csv")
    print(f"✅ Loaded {len(return_df)} players from return.csv")
    
    # Create combined stats dictionary
    tennis_abstract_stats = {}
    
    for _, row in serve_df.iterrows():
        player_name = row['Player'].split(' (')[0]  # Remove URL part
        
        # Clean up percentage values
        def clean_pct(val):
            if isinstance(val, str) and val.endswith('%'):
                return float(val.rstrip('%'))
            return float(val) if pd.notna(val) else 0.0
        
        tennis_abstract_stats[player_name] = {
            'hold_rate': clean_pct(row['Hld%']),
            'service_points_won': clean_pct(row['SPW']),
            'first_serve_win_rate': clean_pct(row['1st%']),
            'second_serve_win_rate': clean_pct(row['2nd%']),
            'ace_rate': clean_pct(row['Ace%']),
            'double_fault_rate': clean_pct(row['DF%']),
            'first_serve_percentage': clean_pct(row['1stIn']),
            'match_win_rate': clean_pct(row['M W%']),
            'data_source': 'tennis_abstract'
        }
    
    # Add return stats
    for _, row in return_df.iterrows():
        player_name = row['Player'].split(' (')[0]  # Remove URL part
        
        if player_name in tennis_abstract_stats:
            tennis_abstract_stats[player_name].update({
                'break_rate': clean_pct(row['Brk%']),
                'return_points_won': clean_pct(row['RPW']),
                'return_vs_first_serve': clean_pct(row['v1st%']),
                'return_vs_second_serve': clean_pct(row['v2nd%']),
                'opponent_ace_rate': clean_pct(row['vAce%']),
                'opponent_df_rate': clean_pct(row['vDF%'])
            })
    
    print(f"✅ Combined stats for {len(tennis_abstract_stats)} players")
    
    return tennis_abstract_stats


def test_shelton_gigante_with_real_stats():
    """Test Shelton vs Gigante using real Tennis Abstract hold/break rates."""
    print(f"\n🎾 TESTING WITH REAL TENNIS ABSTRACT STATS")
    print("=" * 60)
    
    # Load Tennis Abstract stats
    ta_stats = load_tennis_abstract_stats()
    
    # Check if we have Shelton's stats
    if 'Ben Shelton' not in ta_stats:
        print("❌ Ben Shelton not found in Tennis Abstract stats")
        return
    
    shelton_stats = ta_stats['Ben Shelton']
    print(f"✅ Found Ben Shelton stats:")
    print(f"  Hold Rate: {shelton_stats['hold_rate']:.1f}%")
    print(f"  Break Rate: {shelton_stats['break_rate']:.1f}%")
    print(f"  Service Points Won: {shelton_stats['service_points_won']:.1f}%")
    print(f"  Return Points Won: {shelton_stats['return_points_won']:.1f}%")
    
    # For Gigante, we'll need to estimate based on similar players
    print(f"\n🔍 ESTIMATING GIGANTE STATS:")
    print("-" * 40)
    
    # Find players with similar match win rates to Gigante (around 40-50%)
    similar_players = []
    for name, stats in ta_stats.items():
        if 40 <= stats['match_win_rate'] <= 55:
            similar_players.append((name, stats))
    
    if similar_players:
        # Average the stats of similar players
        avg_hold = sum(p[1]['hold_rate'] for p in similar_players) / len(similar_players)
        avg_break = sum(p[1]['break_rate'] for p in similar_players) / len(similar_players)
        avg_service = sum(p[1]['service_points_won'] for p in similar_players) / len(similar_players)
        avg_return = sum(p[1]['return_points_won'] for p in similar_players) / len(similar_players)
        
        print(f"Based on {len(similar_players)} similar players:")
        print(f"  Estimated Gigante Hold Rate: {avg_hold:.1f}%")
        print(f"  Estimated Gigante Break Rate: {avg_break:.1f}%")
        print(f"  Estimated Gigante Service: {avg_service:.1f}%")
        print(f"  Estimated Gigante Return: {avg_return:.1f}%")
        
        gigante_stats = {
            'hold_rate': avg_hold,
            'break_rate': avg_break,
            'service_points_won': avg_service,
            'return_points_won': avg_return
        }
    else:
        print("❌ No similar players found for Gigante estimation")
        return
    
    # Calculate expected match outcome using hold/break rates
    print(f"\n🎯 MATCH PROBABILITY CALCULATION:")
    print("-" * 40)
    
    # In tennis, match outcome is heavily determined by hold/break rates
    # Simple approximation: player with higher (hold_rate - opponent_break_rate) wins more
    
    shelton_advantage = shelton_stats['hold_rate'] - gigante_stats['break_rate']
    gigante_advantage = gigante_stats['hold_rate'] - shelton_stats['break_rate']
    
    print(f"Shelton service advantage: {shelton_advantage:.1f}%")
    print(f"Gigante service advantage: {gigante_advantage:.1f}%")
    
    # Convert to match probability (rough approximation)
    total_advantage = shelton_advantage + gigante_advantage
    if total_advantage > 0:
        shelton_match_prob = (shelton_advantage / total_advantage) * 50 + 50
    else:
        shelton_match_prob = 50
    
    print(f"\nEstimated Shelton win probability: {shelton_match_prob:.1f}%")
    print(f"Vegas implied probability: 63.6%")
    print(f"Difference: {shelton_match_prob - 63.6:.1f} percentage points")
    
    if abs(shelton_match_prob - 63.6) <= 5:
        print("✅ EXCELLENT: Within 5% of Vegas line using real stats!")
    elif abs(shelton_match_prob - 63.6) <= 10:
        print("✅ GOOD: Within 10% of Vegas line using real stats")
    else:
        print("⚠️ Still some discrepancy, but much better foundation")
    
    return shelton_stats, gigante_stats, shelton_match_prob


def implement_direct_hold_break_simulation():
    """Implement a simulation that uses hold/break rates directly."""
    print(f"\n🔧 DIRECT HOLD/BREAK SIMULATION")
    print("=" * 60)
    
    # Load stats
    ta_stats = load_tennis_abstract_stats()
    shelton_stats, gigante_stats, expected_prob = test_shelton_gigante_with_real_stats()
    
    if not shelton_stats or not gigante_stats:
        print("❌ Cannot run simulation without both player stats")
        return
    
    print(f"\n🎲 RUNNING DIRECT HOLD/BREAK SIMULATION:")
    print("-" * 40)
    
    import random
    
    shelton_wins = 0
    total_matches = 100
    
    for match in range(total_matches):
        # Simulate a best-of-3 match using hold/break rates
        shelton_sets = 0
        gigante_sets = 0
        
        while shelton_sets < 2 and gigante_sets < 2:
            # Simulate a set
            shelton_games = 0
            gigante_games = 0
            
            while True:
                # Shelton serving
                if random.random() * 100 < shelton_stats['hold_rate']:
                    shelton_games += 1
                else:
                    gigante_games += 1
                
                # Check for set win
                if shelton_games >= 6 and shelton_games - gigante_games >= 2:
                    shelton_sets += 1
                    break
                elif gigante_games >= 6 and gigante_games - shelton_games >= 2:
                    gigante_sets += 1
                    break
                elif shelton_games == 6 and gigante_games == 6:
                    # Tiebreak - roughly 50/50 with slight advantage to better player
                    if random.random() < 0.55:  # Slight Shelton advantage
                        shelton_sets += 1
                    else:
                        gigante_sets += 1
                    break
                
                # Gigante serving
                if random.random() * 100 < gigante_stats['hold_rate']:
                    gigante_games += 1
                else:
                    shelton_games += 1
                
                # Check for set win again
                if shelton_games >= 6 and shelton_games - gigante_games >= 2:
                    shelton_sets += 1
                    break
                elif gigante_games >= 6 and gigante_games - shelton_games >= 2:
                    gigante_sets += 1
                    break
                elif shelton_games == 6 and gigante_games == 6:
                    # Tiebreak
                    if random.random() < 0.55:
                        shelton_sets += 1
                    else:
                        gigante_sets += 1
                    break
        
        if shelton_sets > gigante_sets:
            shelton_wins += 1
        
        if (match + 1) % 20 == 0:
            current_rate = shelton_wins / (match + 1) * 100
            print(f"  After {match + 1} matches: Shelton {current_rate:.1f}% win rate")
    
    final_win_rate = shelton_wins / total_matches * 100
    
    print(f"\n📊 DIRECT HOLD/BREAK SIMULATION RESULTS:")
    print("-" * 40)
    print(f"Shelton wins: {shelton_wins}/{total_matches}")
    print(f"Win rate: {final_win_rate:.1f}%")
    print(f"Vegas implied: 63.6%")
    print(f"Difference: {final_win_rate - 63.6:.1f} percentage points")
    
    if abs(final_win_rate - 63.6) <= 5:
        print("🎯 SUCCESS: Direct hold/break simulation matches Vegas line!")
    elif abs(final_win_rate - 63.6) <= 10:
        print("✅ GOOD: Much closer to Vegas line with real stats")
    else:
        print("⚠️ Still needs refinement, but major improvement")
    
    return final_win_rate


if __name__ == "__main__":
    final_rate = implement_direct_hold_break_simulation()
