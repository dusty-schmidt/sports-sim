"""
Calculate individual player variance from match-to-match performance
"""

import pandas as pd
import numpy as np
import json
from collections import defaultdict

def calculate_player_specific_variance():
    """Calculate variance for each player based on their actual match-to-match performance."""
    
    # Load matches and points
    matches_m = pd.read_csv("data/charting-m-matches(1).csv")
    
    # Load points data to analyze serving patterns by match
    points_files = [
        "charting-m-points-2020s.csv",
        "charting-m-points-2010s.csv"
    ]
    
    all_points = []
    for file in points_files:
        try:
            df = pd.read_csv(f"data/{file}")
            all_points.append(df)
        except:
            continue
    
    if not all_points:
        print("No points data available")
        return {}
    
    points_df = pd.concat(all_points, ignore_index=True)
    
    # Merge with match surface data
    points_with_surface = points_df.merge(
        matches_m[['match_id', 'Surface', 'Player 1', 'Player 2']], 
        on='match_id', 
        how='inner'
    )
    
    print(f"Analyzing {len(points_with_surface)} points across {points_with_surface['match_id'].nunique()} matches")
    
    # Calculate match-level statistics for each player
    player_match_stats = defaultdict(list)
    
    # Group by match and calculate stats
    for match_id, match_points in points_with_surface.groupby('match_id'):
        if len(match_points) < 20:  # Skip very short matches
            continue
            
        match_info = match_points.iloc[0]
        player1, player2 = match_info['Player 1'], match_info['Player 2']
        
        # Calculate serving stats for each player in this match
        for player in [player1, player2]:
            # Get points where this player is serving
            serving_points = match_points[
                ((match_points['Svr'] == 1) & (player == player1)) |
                ((match_points['Svr'] == 2) & (player == player2))
            ]
            
            if len(serving_points) < 10:  # Need minimum serving points
                continue
            
            # Analyze serving patterns (simplified)
            notes = serving_points['Notes'].dropna().astype(str)
            total_serves = len(notes)
            
            if total_serves == 0:
                continue
            
            # Count aces and faults (simplified pattern matching)
            aces = sum(1 for note in notes if '*' in note or '#' in note)
            faults = sum(1 for note in notes if 'n' in note or 'w' in note)
            double_faults = sum(1 for note in notes if note.count('n') + note.count('w') >= 2)
            
            # Calculate rates for this match
            ace_rate = (aces / total_serves) * 100
            df_rate = (double_faults / total_serves) * 100
            
            # Store match-level stats
            player_match_stats[player].append({
                'match_id': match_id,
                'ace_rate': ace_rate,
                'double_fault_rate': df_rate,
                'total_serves': total_serves
            })
    
    # Calculate variance for each player
    player_variances = {}
    
    for player, match_stats in player_match_stats.items():
        if len(match_stats) < 3:  # Need minimum matches for variance calculation
            continue
        
        # Extract rates
        ace_rates = [m['ace_rate'] for m in match_stats]
        df_rates = [m['double_fault_rate'] for m in match_stats]
        
        # Calculate variance metrics
        ace_variance = np.std(ace_rates) / (np.mean(ace_rates) + 0.1)  # Coefficient of variation
        df_variance = np.std(df_rates) / (np.mean(df_rates) + 0.1)
        
        # Overall variance score (higher = more variable)
        overall_variance = (ace_variance + df_variance) / 2
        
        # Classify variance level
        if overall_variance < 0.3:
            variance_level = 'low'
            variance_multiplier = 0.08  # ±8% variance
        elif overall_variance < 0.6:
            variance_level = 'medium'
            variance_multiplier = 0.12  # ±12% variance
        elif overall_variance < 1.0:
            variance_level = 'high'
            variance_multiplier = 0.18  # ±18% variance
        else:
            variance_level = 'very_high'
            variance_multiplier = 0.25  # ±25% variance
        
        player_variances[player] = {
            'matches_analyzed': len(match_stats),
            'ace_variance': round(ace_variance, 3),
            'df_variance': round(df_variance, 3),
            'overall_variance': round(overall_variance, 3),
            'variance_level': variance_level,
            'variance_multiplier': variance_multiplier,
            'mean_ace_rate': round(np.mean(ace_rates), 2),
            'mean_df_rate': round(np.mean(df_rates), 2)
        }
    
    # Save variance data
    with open('data/player_variance_profiles.json', 'w') as f:
        json.dump(player_variances, f, indent=2)
    
    print(f"Calculated variance profiles for {len(player_variances)} players")
    
    # Print summary
    variance_counts = defaultdict(int)
    for player, data in player_variances.items():
        variance_counts[data['variance_level']] += 1
    
    print("Variance distribution:")
    for level, count in variance_counts.items():
        print(f"  {level}: {count} players")
    
    return player_variances

if __name__ == "__main__":
    calculate_player_specific_variance()
