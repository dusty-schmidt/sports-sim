"""
Extract clutch factors from KeyPoints data and integrate into player stats
"""

import pandas as pd
import numpy as np
import json
from collections import defaultdict

def extract_clutch_performance():
    """Extract clutch performance metrics from KeyPoints data."""
    print("EXTRACTING CLUTCH FACTORS FROM KEYPOINTS DATA")
    print("="*60)
    
    clutch_data = {}
    
    # Load KeyPoints files
    for gender, file_suffix in [('M', 'm'), ('W', 'w')]:
        print(f"\n{gender} KeyPoints Clutch Analysis:")
        print("-" * 40)
        
        # Load KeyPointsServe
        try:
            serve_df = pd.read_csv(f"data/charting-{file_suffix}-stats-KeyPointsServe.csv")
            print(f"KeyPointsServe: {len(serve_df)} records")
            
            # Calculate clutch factors for each player
            player_clutch_stats = defaultdict(lambda: {
                'BP': {'pts': 0, 'pts_won': 0, 'aces': 0, 'dfs': 0, 'first_in': 0},
                'GP': {'pts': 0, 'pts_won': 0, 'aces': 0, 'dfs': 0, 'first_in': 0},
                'Deuce': {'pts': 0, 'pts_won': 0, 'aces': 0, 'dfs': 0, 'first_in': 0},
                'STotal': {'pts': 0, 'pts_won': 0, 'aces': 0, 'dfs': 0, 'first_in': 0}
            })
            
            # Aggregate data by player and situation
            for _, row in serve_df.iterrows():
                player = row['player']
                situation = row['row']
                
                if situation in ['BP', 'GP', 'Deuce', 'STotal']:
                    player_clutch_stats[player][situation]['pts'] += row.get('pts', 0)
                    player_clutch_stats[player][situation]['pts_won'] += row.get('pts_won', 0)
                    player_clutch_stats[player][situation]['aces'] += row.get('aces', 0)
                    player_clutch_stats[player][situation]['dfs'] += row.get('dfs', 0)
                    player_clutch_stats[player][situation]['first_in'] += row.get('first_in', 0)
            
            # Calculate clutch factors
            for player, situations in player_clutch_stats.items():
                if situations['STotal']['pts'] >= 20:  # Minimum threshold
                    clutch_factors = calculate_player_clutch_factor(situations)
                    clutch_data[player] = clutch_factors
                    
                    if len(clutch_data) <= 10:  # Show first 10 for analysis
                        print(f"  {player}: {clutch_factors['clutch_level']} "
                              f"(BP: {clutch_factors['bp_performance']:.1f}%, "
                              f"Overall: {clutch_factors['clutch_score']:.3f})")
            
            print(f"Extracted clutch data for {len(clutch_data)} {gender} players")
            
        except Exception as e:
            print(f"Error processing {gender} KeyPointsServe: {e}")
    
    return clutch_data

def calculate_player_clutch_factor(situations):
    """Calculate comprehensive clutch factor for a player."""
    
    # Get totals for comparison
    total_stats = situations['STotal']
    bp_stats = situations['BP']
    gp_stats = situations['GP']
    deuce_stats = situations['Deuce']
    
    if total_stats['pts'] == 0:
        return None
    
    # Calculate base rates
    base_win_rate = (total_stats['pts_won'] / total_stats['pts']) * 100
    base_ace_rate = (total_stats['aces'] / total_stats['pts']) * 100 if total_stats['pts'] > 0 else 0
    base_df_rate = (total_stats['dfs'] / total_stats['pts']) * 100 if total_stats['pts'] > 0 else 0
    
    # Calculate pressure situation performance
    clutch_scores = []
    
    # Break Point Performance (most important)
    if bp_stats['pts'] >= 3:
        bp_win_rate = (bp_stats['pts_won'] / bp_stats['pts']) * 100
        bp_ace_rate = (bp_stats['aces'] / bp_stats['pts']) * 100
        bp_df_rate = (bp_stats['dfs'] / bp_stats['pts']) * 100
        
        # Compare to base rates
        bp_performance = bp_win_rate / base_win_rate if base_win_rate > 0 else 1.0
        bp_ace_performance = (bp_ace_rate / base_ace_rate) if base_ace_rate > 0 else 1.0
        bp_df_performance = (base_df_rate / bp_df_rate) if bp_df_rate > 0 else 1.0
        
        bp_clutch = (bp_performance + bp_ace_performance + bp_df_performance) / 3
        clutch_scores.append(('BP', bp_clutch, bp_stats['pts']))
    
    # Game Point Performance
    if gp_stats['pts'] >= 5:
        gp_win_rate = (gp_stats['pts_won'] / gp_stats['pts']) * 100
        gp_performance = gp_win_rate / base_win_rate if base_win_rate > 0 else 1.0
        clutch_scores.append(('GP', gp_performance, gp_stats['pts']))
    
    # Deuce Performance
    if deuce_stats['pts'] >= 3:
        deuce_win_rate = (deuce_stats['pts_won'] / deuce_stats['pts']) * 100
        deuce_performance = deuce_win_rate / base_win_rate if base_win_rate > 0 else 1.0
        clutch_scores.append(('Deuce', deuce_performance, deuce_stats['pts']))
    
    # Calculate weighted clutch score
    if clutch_scores:
        # Weight by importance: BP (3x), GP (2x), Deuce (1x)
        weights = {'BP': 3.0, 'GP': 2.0, 'Deuce': 1.0}
        total_weight = 0
        weighted_score = 0
        
        for situation, score, pts in clutch_scores:
            weight = weights[situation] * pts  # Also weight by sample size
            weighted_score += score * weight
            total_weight += weight
        
        overall_clutch = weighted_score / total_weight if total_weight > 0 else 1.0
    else:
        overall_clutch = 1.0
    
    # Classify clutch level
    if overall_clutch >= 1.15:
        clutch_level = "Elite Clutch"
        clutch_multiplier = 1.15
    elif overall_clutch >= 1.05:
        clutch_level = "Good Clutch"
        clutch_multiplier = 1.08
    elif overall_clutch >= 0.95:
        clutch_level = "Average"
        clutch_multiplier = 1.0
    elif overall_clutch >= 0.85:
        clutch_level = "Below Average"
        clutch_multiplier = 0.92
    else:
        clutch_level = "Poor Clutch"
        clutch_multiplier = 0.85
    
    return {
        'clutch_score': overall_clutch,
        'clutch_level': clutch_level,
        'clutch_multiplier': clutch_multiplier,
        'bp_performance': (bp_stats['pts_won'] / bp_stats['pts']) * 100 if bp_stats['pts'] > 0 else 0,
        'gp_performance': (gp_stats['pts_won'] / gp_stats['pts']) * 100 if gp_stats['pts'] > 0 else 0,
        'deuce_performance': (deuce_stats['pts_won'] / deuce_stats['pts']) * 100 if deuce_stats['pts'] > 0 else 0,
        'total_pressure_points': sum(s['pts'] for s in [bp_stats, gp_stats, deuce_stats]),
        'sample_size': total_stats['pts']
    }

def integrate_clutch_into_player_stats(clutch_data):
    """Integrate clutch factors into existing player stats."""
    print(f"\n" + "="*60)
    print("INTEGRATING CLUTCH FACTORS INTO PLAYER STATS")
    print("="*60)
    
    try:
        # Load current player stats
        with open('data/updated_player_stats_with_real_data.json', 'r') as f:
            player_stats = json.load(f)
        
        updates_made = 0
        clutch_distribution = defaultdict(int)
        
        # Add clutch factors to player stats
        for player, clutch_info in clutch_data.items():
            if player in player_stats:
                player_stats[player]['clutch_factor'] = clutch_info['clutch_multiplier']
                player_stats[player]['clutch_level'] = clutch_info['clutch_level']
                player_stats[player]['clutch_score'] = clutch_info['clutch_score']
                player_stats[player]['bp_performance'] = clutch_info['bp_performance']
                player_stats[player]['pressure_points_analyzed'] = clutch_info['total_pressure_points']
                updates_made += 1
                clutch_distribution[clutch_info['clutch_level']] += 1
        
        # Add default clutch factor for players without data
        for player, stats in player_stats.items():
            if 'clutch_factor' not in stats:
                # Default based on tier/ranking
                if stats.get('rank', 999) <= 50:
                    stats['clutch_factor'] = 1.05  # Top players slightly clutch
                    stats['clutch_level'] = "Good Clutch"
                else:
                    stats['clutch_factor'] = 1.0   # Average for others
                    stats['clutch_level'] = "Average"
                stats['clutch_score'] = stats['clutch_factor']
        
        # Save updated stats
        with open('data/player_stats_with_clutch_factors.json', 'w') as f:
            json.dump(player_stats, f, indent=2)
        
        print(f"✅ Updated {updates_made} players with real clutch data")
        print(f"📁 Saved to: data/player_stats_with_clutch_factors.json")
        print(f"📊 Total players in file: {len(player_stats)}")
        
        print(f"\nClutch Level Distribution:")
        for level, count in clutch_distribution.items():
            print(f"  {level}: {count} players")
        
        # Show sample clutch players
        print(f"\nSample Elite Clutch Players:")
        elite_clutch = [(p, d) for p, d in clutch_data.items() if d['clutch_level'] == 'Elite Clutch']
        for player, data in elite_clutch[:5]:
            print(f"  {player}: {data['clutch_score']:.3f} (BP: {data['bp_performance']:.1f}%)")
        
        print(f"\nSample Poor Clutch Players:")
        poor_clutch = [(p, d) for p, d in clutch_data.items() if d['clutch_level'] == 'Poor Clutch']
        for player, data in poor_clutch[:5]:
            print(f"  {player}: {data['clutch_score']:.3f} (BP: {data['bp_performance']:.1f}%)")
        
        return player_stats
        
    except Exception as e:
        print(f"Error integrating clutch factors: {e}")
        return None

def main():
    """Extract clutch factors and integrate into player stats."""
    print("CLUTCH FACTOR EXTRACTION AND INTEGRATION")
    print("="*80)
    print("Analyzing KeyPoints data to add realistic clutch performance to simulator")
    print("="*80)
    
    # Extract clutch performance from KeyPoints data
    clutch_data = extract_clutch_performance()
    
    # Integrate into player stats
    updated_stats = integrate_clutch_into_player_stats(clutch_data)
    
    # Save clutch analysis
    with open('data/clutch_factor_analysis.json', 'w') as f:
        json.dump(clutch_data, f, indent=2, default=str)
    
    print(f"\n✅ CLUTCH FACTOR INTEGRATION COMPLETE!")
    print(f"📊 Analyzed {len(clutch_data)} players with pressure situation data")
    print(f"📁 Clutch analysis saved to: data/clutch_factor_analysis.json")
    print(f"🎾 Ready to add clutch factor to tennis simulator!")

if __name__ == "__main__":
    main()
