"""
Analyze variance patterns by surface to see if different surfaces have different variance levels
"""

import pandas as pd
import numpy as np
import json
from collections import defaultdict

def analyze_surface_specific_variance():
    """Analyze if variance differs by surface type."""
    
    # Load matches and points
    matches_m = pd.read_csv("data/charting-m-matches(1).csv")
    
    # Load points data
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
    
    print(f"Analyzing variance across surfaces...")
    
    # Calculate match-level statistics by surface
    surface_variance_data = defaultdict(lambda: defaultdict(list))
    
    # Group by surface and match
    for surface in ['Hard', 'Clay', 'Grass']:
        surface_points = points_with_surface[points_with_surface['Surface'] == surface]
        
        if len(surface_points) < 1000:
            continue
            
        print(f"\n{surface} Court Analysis:")
        print(f"  Total points: {len(surface_points):,}")
        print(f"  Unique matches: {surface_points['match_id'].nunique():,}")
        
        # Calculate match-level stats for each player on this surface
        player_match_stats = defaultdict(list)
        
        for match_id, match_points in surface_points.groupby('match_id'):
            if len(match_points) < 20:
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
                
                if len(serving_points) < 10:
                    continue
                
                # Analyze serving patterns
                notes = serving_points['Notes'].dropna().astype(str)
                total_serves = len(notes)
                
                if total_serves == 0:
                    continue
                
                # Count aces and faults
                aces = sum(1 for note in notes if '*' in note or '#' in note)
                faults = sum(1 for note in notes if 'n' in note or 'w' in note)
                double_faults = sum(1 for note in notes if note.count('n') + note.count('w') >= 2)
                
                # Calculate rates for this match
                ace_rate = (aces / total_serves) * 100
                df_rate = (double_faults / total_serves) * 100
                
                player_match_stats[player].append({
                    'ace_rate': ace_rate,
                    'double_fault_rate': df_rate,
                    'total_serves': total_serves
                })
        
        # Calculate variance metrics for this surface
        surface_ace_variances = []
        surface_df_variances = []
        
        for player, match_stats in player_match_stats.items():
            if len(match_stats) < 3:
                continue
            
            ace_rates = [m['ace_rate'] for m in match_stats]
            df_rates = [m['double_fault_rate'] for m in match_stats]
            
            if np.mean(ace_rates) > 0:
                ace_cv = np.std(ace_rates) / np.mean(ace_rates)
                surface_ace_variances.append(ace_cv)
            
            if np.mean(df_rates) > 0:
                df_cv = np.std(df_rates) / np.mean(df_rates)
                surface_df_variances.append(df_cv)
        
        # Surface-level variance summary
        if surface_ace_variances and surface_df_variances:
            surface_variance_data[surface] = {
                'players_analyzed': len(surface_ace_variances),
                'ace_variance_mean': np.mean(surface_ace_variances),
                'ace_variance_std': np.std(surface_ace_variances),
                'df_variance_mean': np.mean(surface_df_variances),
                'df_variance_std': np.std(surface_df_variances),
                'overall_variance': (np.mean(surface_ace_variances) + np.mean(surface_df_variances)) / 2
            }
            
            print(f"  Players analyzed: {len(surface_ace_variances)}")
            print(f"  Ace variance (CV): {np.mean(surface_ace_variances):.3f} ± {np.std(surface_ace_variances):.3f}")
            print(f"  DF variance (CV): {np.mean(surface_df_variances):.3f} ± {np.std(surface_df_variances):.3f}")
            print(f"  Overall variance: {surface_variance_data[surface]['overall_variance']:.3f}")
    
    # Compare surfaces
    print(f"\n" + "="*60)
    print("SURFACE VARIANCE COMPARISON")
    print("="*60)
    
    surfaces_sorted = sorted(surface_variance_data.items(), key=lambda x: x[1]['overall_variance'], reverse=True)
    
    for surface, data in surfaces_sorted:
        variance_level = "HIGH" if data['overall_variance'] > 0.8 else "MEDIUM" if data['overall_variance'] > 0.5 else "LOW"
        print(f"{surface:5s}: Overall Variance = {data['overall_variance']:.3f} ({variance_level})")
        print(f"       Ace CV = {data['ace_variance_mean']:.3f}, DF CV = {data['df_variance_mean']:.3f}")
    
    # Recommendations
    print(f"\n" + "="*60)
    print("VARIANCE CALIBRATION RECOMMENDATIONS")
    print("="*60)
    
    if len(surfaces_sorted) >= 2:
        highest_var = surfaces_sorted[0]
        lowest_var = surfaces_sorted[-1]
        
        variance_diff = highest_var[1]['overall_variance'] - lowest_var[1]['overall_variance']
        
        if variance_diff > 0.2:
            print(f"✅ SIGNIFICANT surface variance differences detected:")
            print(f"   {highest_var[0]} has {variance_diff:.3f} higher variance than {lowest_var[0]}")
            print(f"   Recommend surface-specific variance multipliers:")
            
            for surface, data in surfaces_sorted:
                base_multiplier = 0.12  # Base 12% variance
                surface_multiplier = base_multiplier * (1 + (data['overall_variance'] - 0.6) * 0.5)
                surface_multiplier = max(0.08, min(0.25, surface_multiplier))
                print(f"   {surface}: {surface_multiplier:.3f} (±{surface_multiplier*100:.1f}%)")
        else:
            print(f"❌ No significant surface variance differences detected")
            print(f"   Variance difference: {variance_diff:.3f} (threshold: 0.2)")
            print(f"   Current uniform variance approach is appropriate")
    
    # Save results
    with open('data/surface_variance_analysis.json', 'w') as f:
        json.dump(dict(surface_variance_data), f, indent=2)
    
    return dict(surface_variance_data)

if __name__ == "__main__":
    analyze_surface_specific_variance()
