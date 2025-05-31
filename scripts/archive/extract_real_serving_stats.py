"""
Extract actual serving statistics from Overview and ServeBasics data
Replace our calculated stats with real measured data
"""

import pandas as pd
import numpy as np
import json
from collections import defaultdict

def extract_overview_serving_stats():
    """Extract ace rates and double fault rates from Overview data."""
    print("EXTRACTING REAL SERVING STATISTICS FROM OVERVIEW DATA")
    print("="*70)
    
    real_stats = {}
    
    for gender, file_suffix in [('M', 'm'), ('W', 'w')]:
        try:
            df = pd.read_csv(f"data/charting-{file_suffix}-stats-Overview.csv")
            print(f"\n{gender} Overview: {len(df)} records")
            
            # Filter for 'Total' set data (complete match stats)
            total_df = df[df['set'] == 'Total'].copy()
            print(f"Total match records: {len(total_df)}")
            
            # Calculate actual rates for each player
            player_stats = defaultdict(lambda: {'serve_pts': 0, 'aces': 0, 'dfs': 0, 'matches': 0})
            
            for _, row in total_df.iterrows():
                player = row['player']
                serve_pts = row.get('serve_pts', 0)
                aces = row.get('aces', 0)
                dfs = row.get('dfs', 0)
                
                if serve_pts > 0:  # Valid serving data
                    player_stats[player]['serve_pts'] += serve_pts
                    player_stats[player]['aces'] += aces
                    player_stats[player]['dfs'] += dfs
                    player_stats[player]['matches'] += 1
            
            # Calculate rates
            for player, stats in player_stats.items():
                if stats['serve_pts'] >= 50 and stats['matches'] >= 2:  # Minimum thresholds
                    ace_rate = (stats['aces'] / stats['serve_pts']) * 100
                    df_rate = (stats['dfs'] / stats['serve_pts']) * 100
                    
                    real_stats[player] = {
                        'ace_rate': round(ace_rate, 2),
                        'double_fault_rate': round(df_rate, 2),
                        'total_serve_pts': stats['serve_pts'],
                        'total_aces': stats['aces'],
                        'total_dfs': stats['dfs'],
                        'matches': stats['matches'],
                        'gender': gender
                    }
            
            print(f"Extracted stats for {len([p for p in real_stats if real_stats[p]['gender'] == gender])} {gender} players")
            
        except Exception as e:
            print(f"Error processing {gender} overview: {e}")
    
    return real_stats

def extract_rally_length_distributions():
    """Extract rally length patterns from Rally data."""
    print("\n\nEXTRACTING RALLY LENGTH DISTRIBUTIONS")
    print("="*70)
    
    rally_distributions = {}
    
    for gender, file_suffix in [('M', 'm'), ('W', 'w')]:
        try:
            df = pd.read_csv(f"data/charting-{file_suffix}-stats-Rally.csv")
            print(f"\n{gender} Rally: {len(df)} records")
            
            # Look at rally length categories in 'row' column
            rally_categories = df['row'].value_counts()
            print(f"Rally categories: {rally_categories.head(10).to_dict()}")
            
            # Extract rally length distributions
            rally_data = defaultdict(int)
            total_points = 0
            
            for _, row in df.iterrows():
                category = row['row']
                points = row.get('pts', 0)
                
                if points > 0:
                    rally_data[category] += points
                    total_points += points
            
            # Convert to percentages
            rally_percentages = {}
            for category, count in rally_data.items():
                rally_percentages[category] = (count / total_points) * 100
            
            rally_distributions[gender] = {
                'raw_counts': dict(rally_data),
                'percentages': rally_percentages,
                'total_points': total_points
            }
            
            print(f"Rally distribution for {gender}:")
            for category, pct in sorted(rally_percentages.items(), key=lambda x: x[1], reverse=True)[:8]:
                print(f"  {category}: {pct:.1f}%")
                
        except Exception as e:
            print(f"Error processing {gender} rally: {e}")
    
    return rally_distributions

def compare_with_calculated_stats(real_stats):
    """Compare real stats with our calculated stats."""
    print("\n\nCOMPARING REAL VS CALCULATED STATISTICS")
    print("="*70)
    
    try:
        with open('data/calculated_player_stats.json', 'r') as f:
            calculated_stats = json.load(f)
        
        comparisons = []
        print(f"{'Player':<25} {'Calc Ace':<10} {'Real Ace':<10} {'Ace Diff':<10} {'Calc DF':<10} {'Real DF':<10} {'DF Diff':<10}")
        print("-" * 90)
        
        for player, real_data in list(real_stats.items())[:15]:
            if player in calculated_stats:
                calc_ace = calculated_stats[player]['ace_rate']
                calc_df = calculated_stats[player]['double_fault_rate']
                real_ace = real_data['ace_rate']
                real_df = real_data['double_fault_rate']
                
                ace_diff = abs(calc_ace - real_ace)
                df_diff = abs(calc_df - real_df)
                
                comparisons.append({'ace_diff': ace_diff, 'df_diff': df_diff})
                
                print(f"{player:<25} {calc_ace:<10.2f} {real_ace:<10.2f} {ace_diff:<10.2f} {calc_df:<10.2f} {real_df:<10.2f} {df_diff:<10.2f}")
        
        if comparisons:
            avg_ace_diff = np.mean([c['ace_diff'] for c in comparisons])
            avg_df_diff = np.mean([c['df_diff'] for c in comparisons])
            
            print(f"\nAverage differences:")
            print(f"  Ace rate: {avg_ace_diff:.2f} percentage points")
            print(f"  Double fault rate: {avg_df_diff:.2f} percentage points")
            
            if avg_ace_diff < 2.0 and avg_df_diff < 1.0:
                print("✅ Our calculated stats are very accurate!")
            elif avg_ace_diff < 4.0 and avg_df_diff < 2.0:
                print("⚠️  Moderate differences - worth updating with real data")
            else:
                print("❌ Significant differences - should replace with real data")
        
    except Exception as e:
        print(f"Could not load calculated stats for comparison: {e}")

def create_updated_player_stats(real_stats):
    """Create updated player stats file with real serving data."""
    print("\n\nCREATING UPDATED PLAYER STATISTICS")
    print("="*70)
    
    try:
        # Load current calculated stats
        with open('data/calculated_player_stats.json', 'r') as f:
            current_stats = json.load(f)
        
        updated_stats = current_stats.copy()
        updates_made = 0
        
        # Update with real data where available
        for player, real_data in real_stats.items():
            if player in updated_stats:
                # Update ace and double fault rates with real data
                updated_stats[player]['ace_rate'] = real_data['ace_rate']
                updated_stats[player]['double_fault_rate'] = real_data['double_fault_rate']
                updated_stats[player]['data_source'] = 'real_measured'
                updated_stats[player]['serve_points_analyzed'] = real_data['total_serve_pts']
                updates_made += 1
            else:
                # Add new player with real data
                updated_stats[player] = {
                    'ace_rate': real_data['ace_rate'],
                    'double_fault_rate': real_data['double_fault_rate'],
                    'first_serve_percentage': 62.0,  # Default
                    'service_points_won': 60.0,  # Default
                    'return_points_won': 40.0,  # Default
                    'gender': real_data['gender'],
                    'matches': real_data['matches'],
                    'data_source': 'real_measured',
                    'serve_points_analyzed': real_data['total_serve_pts']
                }
                updates_made += 1
        
        # Save updated stats
        with open('data/updated_player_stats_with_real_data.json', 'w') as f:
            json.dump(updated_stats, f, indent=2)
        
        print(f"✅ Updated {updates_made} players with real serving data")
        print(f"📁 Saved to: data/updated_player_stats_with_real_data.json")
        print(f"📊 Total players in updated file: {len(updated_stats)}")
        
        # Show sample of updated players
        print(f"\nSample updated players:")
        real_data_players = [p for p in updated_stats if updated_stats[p].get('data_source') == 'real_measured']
        for player in real_data_players[:5]:
            stats = updated_stats[player]
            print(f"  {player}: Ace {stats['ace_rate']:.2f}%, DF {stats['double_fault_rate']:.2f}% (from {stats['serve_points_analyzed']} serve points)")
        
        return updated_stats
        
    except Exception as e:
        print(f"Error creating updated stats: {e}")
        return None

def main():
    """Extract and integrate real serving statistics."""
    print("EXTRACTING REAL TENNIS STATISTICS FROM NEW DATA")
    print("="*80)
    
    # Extract real serving stats
    real_stats = extract_overview_serving_stats()
    
    # Extract rally patterns
    rally_distributions = extract_rally_length_distributions()
    
    # Compare with calculated stats
    compare_with_calculated_stats(real_stats)
    
    # Create updated stats file
    updated_stats = create_updated_player_stats(real_stats)
    
    # Save all analysis
    analysis_results = {
        'real_serving_stats': real_stats,
        'rally_distributions': rally_distributions,
        'summary': {
            'players_with_real_data': len(real_stats),
            'men_players': len([p for p in real_stats if real_stats[p]['gender'] == 'M']),
            'women_players': len([p for p in real_stats if real_stats[p]['gender'] == 'W'])
        }
    }
    
    with open('data/real_stats_extraction_results.json', 'w') as f:
        json.dump(analysis_results, f, indent=2, default=str)
    
    print(f"\n✅ EXTRACTION COMPLETE!")
    print(f"📊 Extracted real data for {len(real_stats)} players")
    print(f"📁 Analysis saved to: data/real_stats_extraction_results.json")

if __name__ == "__main__":
    main()
