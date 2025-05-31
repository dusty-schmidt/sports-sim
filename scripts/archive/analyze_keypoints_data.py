"""
Analyze KeyPoints data to extract clutch factor and pressure situation performance
"""

import pandas as pd
import numpy as np
import json
from collections import defaultdict

def analyze_keypoints_files():
    """Analyze KeyPointsServe and KeyPointsReturn files."""
    print("ANALYZING KEYPOINTS DATA FOR CLUTCH FACTOR")
    print("="*60)

    keypoints_data = {}

    # Load KeyPoints files
    for gender, file_suffix in [('M', 'm'), ('W', 'w')]:
        print(f"\n{gender} KeyPoints Analysis:")
        print("-" * 30)

        # Load KeyPointsServe
        try:
            serve_df = pd.read_csv(f"data/charting-{file_suffix}-stats-KeyPointsServe.csv")
            print(f"KeyPointsServe: {len(serve_df)} records")
            print(f"Columns: {list(serve_df.columns)}")

            # Show sample data
            if len(serve_df) > 0:
                print("Sample KeyPointsServe data:")
                for col in serve_df.columns[:6]:
                    sample_vals = serve_df[col].dropna().head(3).tolist()
                    print(f"  {col}: {sample_vals}")

            keypoints_data[f'{gender}_serve'] = serve_df

        except Exception as e:
            print(f"Error loading {gender} KeyPointsServe: {e}")

        # Load KeyPointsReturn
        try:
            return_df = pd.read_csv(f"data/charting-{file_suffix}-stats-KeyPointsReturn.csv")
            print(f"\nKeyPointsReturn: {len(return_df)} records")
            print(f"Columns: {list(return_df.columns)}")

            # Show sample data
            if len(return_df) > 0:
                print("Sample KeyPointsReturn data:")
                for col in return_df.columns[:6]:
                    sample_vals = return_df[col].dropna().head(3).tolist()
                    print(f"  {col}: {sample_vals}")

            keypoints_data[f'{gender}_return'] = return_df

        except Exception as e:
            print(f"Error loading {gender} KeyPointsReturn: {e}")

    return keypoints_data

def extract_clutch_performance_metrics(keypoints_data):
    """Extract clutch performance metrics from KeyPoints data."""
    print(f"\n" + "="*60)
    print("EXTRACTING CLUTCH PERFORMANCE METRICS")
    print("="*60)

    clutch_metrics = {}

    for data_key, df in keypoints_data.items():
        if df is None or len(df) == 0:
            continue

        gender = data_key.split('_')[0]
        data_type = data_key.split('_')[1]

        print(f"\n{gender} {data_type.upper()} Clutch Analysis:")
        print("-" * 40)

        # Look for pressure situation columns
        pressure_cols = []
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['break', 'bp', 'deuce', 'game', 'set', 'match']):
                pressure_cols.append(col)

        print(f"Pressure situation columns found: {pressure_cols}")

        if 'Player' in df.columns and pressure_cols:
            # Extract clutch stats for each player
            player_clutch_stats = defaultdict(dict)

            for _, row in df.head(20).iterrows():  # Sample first 20 for analysis
                player = row['Player']

                for col in pressure_cols:
                    if not pd.isna(row[col]):
                        player_clutch_stats[player][col] = row[col]

                if player_clutch_stats[player]:
                    print(f"  {player}: {dict(player_clutch_stats[player])}")

            clutch_metrics[data_key] = dict(player_clutch_stats)

    return clutch_metrics

def identify_key_pressure_situations(keypoints_data):
    """Identify the most important pressure situations in the data."""
    print(f"\n" + "="*60)
    print("IDENTIFYING KEY PRESSURE SITUATIONS")
    print("="*60)

    pressure_situations = {}

    for data_key, df in keypoints_data.items():
        if df is None or len(df) == 0:
            continue

        print(f"\n{data_key.upper()} Pressure Situations:")
        print("-" * 40)

        # Analyze column names to understand pressure situations
        situation_types = {
            'break_points': [],
            'game_points': [],
            'set_points': [],
            'match_points': [],
            'deuce_situations': [],
            'other_pressure': []
        }

        for col in df.columns:
            col_lower = col.lower()

            if 'break' in col_lower or 'bp' in col_lower:
                situation_types['break_points'].append(col)
            elif 'game' in col_lower and ('point' in col_lower or 'pts' in col_lower):
                situation_types['game_points'].append(col)
            elif 'set' in col_lower and ('point' in col_lower or 'pts' in col_lower):
                situation_types['set_points'].append(col)
            elif 'match' in col_lower and ('point' in col_lower or 'pts' in col_lower):
                situation_types['match_points'].append(col)
            elif 'deuce' in col_lower:
                situation_types['deuce_situations'].append(col)
            elif any(keyword in col_lower for keyword in ['pressure', 'clutch', 'important', 'key']):
                situation_types['other_pressure'].append(col)

        # Report findings
        for situation, cols in situation_types.items():
            if cols:
                print(f"  {situation}: {cols}")

        pressure_situations[data_key] = situation_types

    return pressure_situations

def calculate_clutch_factors(keypoints_data):
    """Calculate clutch factors for players based on pressure situation performance."""
    print(f"\n" + "="*60)
    print("CALCULATING PLAYER CLUTCH FACTORS")
    print("="*60)

    player_clutch_factors = {}

    for data_key, df in keypoints_data.items():
        if df is None or len(df) == 0 or 'Player' not in df.columns:
            continue

        print(f"\n{data_key.upper()} Clutch Factor Calculation:")
        print("-" * 50)

        # Look for win/loss or success/failure columns in pressure situations
        performance_cols = []
        total_cols = []

        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['won', 'win', 'made', 'success']):
                performance_cols.append(col)
            elif any(keyword in col_lower for keyword in ['total', 'played', 'faced', 'pts']):
                total_cols.append(col)

        print(f"Performance columns: {performance_cols[:5]}")  # Show first 5
        print(f"Total columns: {total_cols[:5]}")  # Show first 5

        # Calculate clutch factors for sample players
        sample_players = df['Player'].unique()[:10]

        for player in sample_players:
            player_data = df[df['Player'] == player]

            if len(player_data) == 0:
                continue

            clutch_scores = []

            # Try to calculate success rates in pressure situations
            for _, row in player_data.iterrows():
                for perf_col in performance_cols[:3]:  # Limit to first 3 for analysis
                    # Look for corresponding total column
                    for total_col in total_cols[:3]:
                        if (perf_col in row and total_col in row and
                            not pd.isna(row[perf_col]) and not pd.isna(row[total_col]) and
                            row[total_col] > 0):

                            success_rate = row[perf_col] / row[total_col]
                            clutch_scores.append(success_rate)

            if clutch_scores:
                avg_clutch = sum(clutch_scores) / len(clutch_scores)

                # Classify clutch factor
                if avg_clutch >= 0.7:
                    clutch_level = "Elite Clutch"
                elif avg_clutch >= 0.6:
                    clutch_level = "Good Clutch"
                elif avg_clutch >= 0.5:
                    clutch_level = "Average Clutch"
                elif avg_clutch >= 0.4:
                    clutch_level = "Below Average"
                else:
                    clutch_level = "Poor Clutch"

                player_clutch_factors[player] = {
                    'clutch_score': avg_clutch,
                    'clutch_level': clutch_level,
                    'data_points': len(clutch_scores)
                }

                print(f"  {player}: {avg_clutch:.3f} ({clutch_level}) - {len(clutch_scores)} situations")

    return player_clutch_factors

def create_clutch_integration_plan(pressure_situations, clutch_factors):
    """Create a plan for integrating clutch factors into the simulator."""
    print(f"\n" + "="*60)
    print("CLUTCH FACTOR INTEGRATION PLAN")
    print("="*60)

    print("🎯 IDENTIFIED PRESSURE SITUATIONS:")

    # Count total pressure situations across all data
    all_situations = set()
    for data_key, situations in pressure_situations.items():
        for situation_type, cols in situations.items():
            if cols:
                all_situations.add(situation_type)
                print(f"  ✅ {situation_type}: {len(cols)} metrics available")

    print(f"\n🎾 CLUTCH FACTOR DISTRIBUTION:")
    if clutch_factors:
        clutch_levels = defaultdict(int)
        for player, data in clutch_factors.items():
            clutch_levels[data['clutch_level']] += 1

        for level, count in clutch_levels.items():
            print(f"  {level}: {count} players")

    print(f"\n📊 INTEGRATION RECOMMENDATIONS:")
    print("1. ✅ Break Point Situations:")
    print("   - Apply clutch multiplier to service/return point win rates")
    print("   - Elite clutch: +15% performance, Poor clutch: -15% performance")

    print("\n2. ✅ Game Point Situations:")
    print("   - Adjust ace rate and double fault rate based on clutch factor")
    print("   - Clutch players: fewer double faults under pressure")

    print("\n3. ✅ Set/Match Point Situations:")
    print("   - Maximum clutch factor application")
    print("   - Can swing match outcomes for close contests")

    print("\n4. ✅ Implementation Strategy:")
    print("   - Add clutch_factor to player stats (0.8-1.2 multiplier)")
    print("   - Apply in simulate_point() based on game situation")
    print("   - Track break points, game points, set points in match state")

def main():
    """Analyze KeyPoints data for clutch factor integration."""
    print("KEYPOINTS DATA ANALYSIS FOR CLUTCH FACTOR")
    print("="*80)
    print("Analyzing pressure situation performance to add clutch factor to simulator")
    print("="*80)

    # Load and analyze KeyPoints data
    keypoints_data = analyze_keypoints_files()

    # Extract clutch metrics
    clutch_metrics = extract_clutch_performance_metrics(keypoints_data)

    # Identify pressure situations
    pressure_situations = identify_key_pressure_situations(keypoints_data)

    # Calculate clutch factors
    clutch_factors = calculate_clutch_factors(keypoints_data)

    # Create integration plan
    create_clutch_integration_plan(pressure_situations, clutch_factors)

    # Save analysis results
    analysis_results = {
        'clutch_metrics': clutch_metrics,
        'pressure_situations': pressure_situations,
        'clutch_factors': clutch_factors
    }

    with open('data/keypoints_clutch_analysis.json', 'w') as f:
        json.dump(analysis_results, f, indent=2, default=str)

    print(f"\n✅ KEYPOINTS ANALYSIS COMPLETE!")
    print(f"📁 Results saved to: data/keypoints_clutch_analysis.json")
    print(f"🎾 Ready to integrate clutch factor into tennis simulator!")

if __name__ == "__main__":
    main()
