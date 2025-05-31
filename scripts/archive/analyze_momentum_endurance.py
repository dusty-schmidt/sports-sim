"""
Analyze momentum and endurance patterns from tennis match data
"""

import pandas as pd
import numpy as np
import json
from collections import defaultdict

def analyze_set_by_set_performance():
    """Analyze how players perform as matches progress."""
    print("ANALYZING SET-BY-SET PERFORMANCE PATTERNS")
    print("="*60)

    endurance_data = {}

    # Load match data to analyze set progression
    for gender, file_suffix in [('M', 'm'), ('W', 'w')]:
        print(f"\n{gender} Set Progression Analysis:")
        print("-" * 40)

        try:
            # Load match overview data
            overview_df = pd.read_csv(f"data/charting-{file_suffix}-stats-Overview.csv")
            print(f"Overview data: {len(overview_df)} records")

            # Analyze set-by-set patterns
            player_set_patterns = defaultdict(lambda: {
                'set1_performance': [],
                'set2_performance': [],
                'set3_performance': [],
                'set4_performance': [],
                'set5_performance': [],
                'total_sets_played': 0,
                'long_matches': 0,
                'quick_matches': 0
            })

            # Look for set-specific columns
            set_columns = [col for col in overview_df.columns if 'set' in col.lower()]
            print(f"Set-related columns: {set_columns[:10]}")  # Show first 10

            # Analyze each player's set patterns
            for _, row in overview_df.head(1000).iterrows():  # Sample for analysis
                player = row.get('player', row.get('Player', ''))
                if not player:
                    continue

                # Look for set-specific performance indicators
                for col in set_columns[:5]:  # Analyze first 5 set columns
                    if not pd.isna(row[col]) and isinstance(row[col], (int, float)):
                        # Determine which set this represents
                        if '1' in col:
                            player_set_patterns[player]['set1_performance'].append(row[col])
                        elif '2' in col:
                            player_set_patterns[player]['set2_performance'].append(row[col])
                        elif '3' in col:
                            player_set_patterns[player]['set3_performance'].append(row[col])
                        elif '4' in col:
                            player_set_patterns[player]['set4_performance'].append(row[col])
                        elif '5' in col:
                            player_set_patterns[player]['set5_performance'].append(row[col])

                player_set_patterns[player]['total_sets_played'] += 1

            # Calculate endurance patterns
            for player, patterns in list(player_set_patterns.items())[:10]:  # Show first 10
                if patterns['total_sets_played'] >= 5:  # Minimum threshold
                    endurance_profile = calculate_endurance_profile(patterns)
                    endurance_data[player] = endurance_profile

                    print(f"  {player}: {endurance_profile['endurance_type']} "
                          f"(Decline: {endurance_profile['performance_decline']:.1f}%)")

        except Exception as e:
            print(f"Error analyzing {gender} set patterns: {e}")

    return endurance_data

def analyze_rally_length_fatigue():
    """Analyze how rally length performance changes with fatigue."""
    print(f"\n" + "="*60)
    print("ANALYZING RALLY LENGTH FATIGUE PATTERNS")
    print("="*60)

    rally_fatigue_data = {}

    for gender, file_suffix in [('M', 'm'), ('W', 'w')]:
        print(f"\n{gender} Rally Fatigue Analysis:")
        print("-" * 40)

        try:
            # Load rally data
            rally_df = pd.read_csv(f"data/charting-{file_suffix}-stats-Rally.csv")
            print(f"Rally data: {len(rally_df)} records")

            # Analyze rally length patterns by player
            player_rally_patterns = defaultdict(lambda: {
                'short_rallies_won': 0,    # 1-3 shots won
                'short_rallies_total': 0,  # 1-3 shots total
                'medium_rallies_won': 0,   # 4-6 shots won
                'medium_rallies_total': 0, # 4-6 shots total
                'long_rallies_won': 0,     # 7-9 shots won
                'long_rallies_total': 0,   # 7-9 shots total
                'very_long_rallies_won': 0,   # 10+ shots won
                'very_long_rallies_total': 0, # 10+ shots total
                'total_points': 0
            })

            # Analyze rally performance patterns
            for _, row in rally_df.iterrows():
                server = row.get('server', '')
                returner = row.get('returner', '')
                rally_type = row.get('row', '')

                if not server or not returner or not rally_type:
                    continue

                # Extract rally statistics
                pts = row.get('pts', 0)
                pl1_won = row.get('pl1_won', 0)
                pl2_won = row.get('pl2_won', 0)

                if pts == 0:
                    continue

                # Determine rally length category
                if rally_type == '1-3':
                    # Short rallies
                    player_rally_patterns[server]['short_rallies_total'] += pts
                    player_rally_patterns[server]['short_rallies_won'] += pl1_won
                    player_rally_patterns[returner]['short_rallies_total'] += pts
                    player_rally_patterns[returner]['short_rallies_won'] += pl2_won
                elif rally_type == '4-6':
                    # Medium rallies
                    player_rally_patterns[server]['medium_rallies_total'] += pts
                    player_rally_patterns[server]['medium_rallies_won'] += pl1_won
                    player_rally_patterns[returner]['medium_rallies_total'] += pts
                    player_rally_patterns[returner]['medium_rallies_won'] += pl2_won
                elif rally_type == '7-9':
                    # Long rallies
                    player_rally_patterns[server]['long_rallies_total'] += pts
                    player_rally_patterns[server]['long_rallies_won'] += pl1_won
                    player_rally_patterns[returner]['long_rallies_total'] += pts
                    player_rally_patterns[returner]['long_rallies_won'] += pl2_won
                elif rally_type == '10':
                    # Very long rallies
                    player_rally_patterns[server]['very_long_rallies_total'] += pts
                    player_rally_patterns[server]['very_long_rallies_won'] += pl1_won
                    player_rally_patterns[returner]['very_long_rallies_total'] += pts
                    player_rally_patterns[returner]['very_long_rallies_won'] += pl2_won

                # Track total points for each player
                player_rally_patterns[server]['total_points'] += pts
                player_rally_patterns[returner]['total_points'] += pts

            # Calculate rally endurance for each player
            for player, patterns in list(player_rally_patterns.items())[:15]:
                if patterns['total_points'] >= 50:  # Minimum threshold
                    rally_endurance = calculate_rally_endurance(patterns)
                    rally_fatigue_data[player] = rally_endurance

                    print(f"  {player}: {rally_endurance['rally_type']} "
                          f"(Long rally win rate: {rally_endurance['long_rally_win_rate']:.1f}%)")

        except Exception as e:
            print(f"Error analyzing {gender} rally fatigue: {e}")

    return rally_fatigue_data

def analyze_service_endurance():
    """Analyze how serving performance degrades with fatigue."""
    print(f"\n" + "="*60)
    print("ANALYZING SERVICE ENDURANCE PATTERNS")
    print("="*60)

    service_endurance_data = {}

    for gender, file_suffix in [('M', 'm'), ('W', 'w')]:
        print(f"\n{gender} Service Endurance Analysis:")
        print("-" * 40)

        try:
            # Load serve basics data
            serve_df = pd.read_csv(f"data/charting-{file_suffix}-stats-ServeBasics.csv")
            print(f"Serve data: {len(serve_df)} records")

            # Analyze serving patterns by match progression
            player_serve_patterns = defaultdict(lambda: {
                'early_ace_rate': [],
                'late_ace_rate': [],
                'early_df_rate': [],
                'late_df_rate': [],
                'early_first_serve': [],
                'late_first_serve': [],
                'service_endurance': 0
            })

            # Look for time/set-based serving data
            serve_cols = [col for col in serve_df.columns if any(x in col.lower() for x in ['ace', 'df', 'first', 'serve'])]
            print(f"Service columns: {serve_cols[:10]}")

            # Analyze serving endurance patterns
            for _, row in serve_df.head(500).iterrows():
                player = row.get('player', row.get('Player', ''))
                if not player:
                    continue

                # Extract serving performance by match stage
                for col in serve_cols[:8]:  # Analyze first 8 serve columns
                    if not pd.isna(row[col]) and isinstance(row[col], (int, float)):
                        value = row[col]

                        # Categorize by match stage (if column indicates timing)
                        if any(x in col.lower() for x in ['early', 'first', 'start', '1st']):
                            if 'ace' in col.lower():
                                player_serve_patterns[player]['early_ace_rate'].append(value)
                            elif 'df' in col.lower():
                                player_serve_patterns[player]['early_df_rate'].append(value)
                            elif 'first' in col.lower():
                                player_serve_patterns[player]['early_first_serve'].append(value)
                        elif any(x in col.lower() for x in ['late', 'final', 'end', 'last']):
                            if 'ace' in col.lower():
                                player_serve_patterns[player]['late_ace_rate'].append(value)
                            elif 'df' in col.lower():
                                player_serve_patterns[player]['late_df_rate'].append(value)
                            elif 'first' in col.lower():
                                player_serve_patterns[player]['late_first_serve'].append(value)

            # Calculate service endurance
            for player, patterns in list(player_serve_patterns.items())[:10]:
                if any(patterns[key] for key in patterns.keys() if isinstance(patterns[key], list)):
                    service_endurance = calculate_service_endurance(patterns)
                    service_endurance_data[player] = service_endurance

                    print(f"  {player}: {service_endurance['endurance_type']} "
                          f"(Late-match serving: {service_endurance['late_match_performance']:.1f}%)")

        except Exception as e:
            print(f"Error analyzing {gender} service endurance: {e}")

    return service_endurance_data

def calculate_endurance_profile(patterns):
    """Calculate a player's endurance profile from set patterns."""
    set1_avg = np.mean(patterns['set1_performance']) if patterns['set1_performance'] else 50
    set3_avg = np.mean(patterns['set3_performance']) if patterns['set3_performance'] else 50
    set5_avg = np.mean(patterns['set5_performance']) if patterns['set5_performance'] else 50

    # Calculate performance decline
    if set1_avg > 0:
        decline_set3 = ((set1_avg - set3_avg) / set1_avg) * 100
        decline_set5 = ((set1_avg - set5_avg) / set1_avg) * 100 if set5_avg > 0 else decline_set3
    else:
        decline_set3 = decline_set5 = 0

    avg_decline = (decline_set3 + decline_set5) / 2

    # Classify endurance type
    if avg_decline <= -5:  # Performance improves
        endurance_type = "Strong Finisher"
        endurance_multiplier = 1.1
    elif avg_decline <= 5:  # Stable performance
        endurance_type = "Consistent"
        endurance_multiplier = 1.0
    elif avg_decline <= 15:  # Moderate decline
        endurance_type = "Average Endurance"
        endurance_multiplier = 0.95
    else:  # Significant decline
        endurance_type = "Poor Endurance"
        endurance_multiplier = 0.85

    return {
        'endurance_type': endurance_type,
        'endurance_multiplier': endurance_multiplier,
        'performance_decline': avg_decline,
        'set1_performance': set1_avg,
        'set3_performance': set3_avg,
        'set5_performance': set5_avg,
        'total_sets_analyzed': patterns['total_sets_played']
    }

def calculate_rally_endurance(patterns):
    """Calculate rally endurance from rally length patterns."""
    # Calculate win rates for different rally lengths
    short_win_rate = (patterns['short_rallies_won'] / patterns['short_rallies_total'] * 100) if patterns['short_rallies_total'] > 0 else 0
    medium_win_rate = (patterns['medium_rallies_won'] / patterns['medium_rallies_total'] * 100) if patterns['medium_rallies_total'] > 0 else 0
    long_win_rate = (patterns['long_rallies_won'] / patterns['long_rallies_total'] * 100) if patterns['long_rallies_total'] > 0 else 0
    very_long_win_rate = (patterns['very_long_rallies_won'] / patterns['very_long_rallies_total'] * 100) if patterns['very_long_rallies_total'] > 0 else 0

    # Calculate endurance factor (how well they perform in long rallies vs short)
    if short_win_rate > 0:
        endurance_factor = long_win_rate / short_win_rate
    else:
        endurance_factor = 1.0

    # Calculate overall long rally performance (7-9 + 10+)
    total_long_won = patterns['long_rallies_won'] + patterns['very_long_rallies_won']
    total_long_played = patterns['long_rallies_total'] + patterns['very_long_rallies_total']
    overall_long_win_rate = (total_long_won / total_long_played * 100) if total_long_played > 0 else 0

    # Classify rally type and endurance
    if endurance_factor >= 1.1 and overall_long_win_rate >= 55:
        rally_type = "Grinder"
        rally_multiplier = 1.15
        endurance_type = "High Endurance"
    elif endurance_factor >= 1.05 or overall_long_win_rate >= 50:
        rally_type = "Balanced Fighter"
        rally_multiplier = 1.05
        endurance_type = "Good Endurance"
    elif endurance_factor >= 0.95:
        rally_type = "Consistent"
        rally_multiplier = 1.0
        endurance_type = "Average Endurance"
    else:
        rally_type = "Quick Points"
        rally_multiplier = 0.9
        endurance_type = "Poor Endurance"

    return {
        'rally_type': rally_type,
        'endurance_type': endurance_type,
        'rally_multiplier': rally_multiplier,
        'endurance_factor': endurance_factor,
        'short_rally_win_rate': short_win_rate,
        'medium_rally_win_rate': medium_win_rate,
        'long_rally_win_rate': long_win_rate,
        'very_long_rally_win_rate': very_long_win_rate,
        'overall_long_win_rate': overall_long_win_rate,
        'total_points_analyzed': patterns['total_points']
    }

def calculate_service_endurance(patterns):
    """Calculate service endurance from serving patterns."""
    early_ace = np.mean(patterns['early_ace_rate']) if patterns['early_ace_rate'] else 5
    late_ace = np.mean(patterns['late_ace_rate']) if patterns['late_ace_rate'] else 5
    early_df = np.mean(patterns['early_df_rate']) if patterns['early_df_rate'] else 3
    late_df = np.mean(patterns['late_df_rate']) if patterns['late_df_rate'] else 3

    # Calculate late match performance
    if early_ace > 0 and early_df > 0:
        ace_decline = ((early_ace - late_ace) / early_ace) * 100
        df_increase = ((late_df - early_df) / early_df) * 100
        overall_decline = (ace_decline + df_increase) / 2
    else:
        overall_decline = 0

    late_performance = max(0, 100 - overall_decline)

    # Classify endurance type
    if overall_decline <= 5:
        endurance_type = "Strong Server"
        serve_multiplier = 1.05
    elif overall_decline <= 15:
        endurance_type = "Average Server"
        serve_multiplier = 1.0
    else:
        endurance_type = "Fading Server"
        serve_multiplier = 0.9

    return {
        'endurance_type': endurance_type,
        'serve_multiplier': serve_multiplier,
        'late_match_performance': late_performance,
        'ace_decline': ace_decline if 'ace_decline' in locals() else 0,
        'df_increase': df_increase if 'df_increase' in locals() else 0
    }

def main():
    """Analyze momentum and endurance patterns."""
    print("MOMENTUM AND ENDURANCE ANALYSIS")
    print("="*80)
    print("Analyzing how player performance changes as matches progress")
    print("="*80)

    # Analyze different aspects of endurance
    endurance_data = analyze_set_by_set_performance()
    rally_fatigue_data = analyze_rally_length_fatigue()
    service_endurance_data = analyze_service_endurance()

    # Combine all endurance data
    combined_endurance = {
        'endurance_patterns': endurance_data,
        'rally_fatigue': rally_fatigue_data,
        'service_endurance': service_endurance_data
    }

    # Save analysis
    with open('data/momentum_endurance_analysis.json', 'w') as f:
        json.dump(combined_endurance, f, indent=2, default=str)

    print(f"\n✅ MOMENTUM AND ENDURANCE ANALYSIS COMPLETE!")
    print(f"📊 Analyzed endurance patterns for multiple players")
    print(f"📁 Results saved to: data/momentum_endurance_analysis.json")
    print(f"🎾 Ready to integrate momentum and endurance into simulator!")

if __name__ == "__main__":
    main()
