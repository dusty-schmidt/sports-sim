#!/usr/bin/env python3
"""
Compare different variance levels in tennis simulation.
File location: /home/dustys/the net/tennis/scripts/variance_comparison.py
"""

import os
import sys
import json
import numpy as np
from typing import Dict, List, Tuple

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sim_models.main_sim.simulator import FantasyTennisSimulator


def update_variance_levels(service_variance: float, ace_df_variance: float):
    """Update variance levels in the simulator."""
    simulator_path = os.path.join(os.path.dirname(__file__), '..', 'sim_models', 'main_sim', 'simulator.py')

    # Read the file
    with open(simulator_path, 'r') as f:
        content = f.read()

    # Replace variance levels
    content = content.replace(
        'skill_preserving_variance = 0.10  # ±10% max',
        f'skill_preserving_variance = {service_variance:.2f}  # ±{service_variance*100:.0f}% max'
    )
    content = content.replace(
        'skill_preserving_variance = 0.12  # ±12% max',
        f'skill_preserving_variance = {ace_df_variance:.2f}  # ±{ace_df_variance*100:.0f}% max'
    )

    # Write back
    with open(simulator_path, 'w') as f:
        f.write(content)


def run_simulation_with_variance(service_var: float, ace_df_var: float, num_matches: int = 1000) -> Dict:
    """Run simulation with specific variance levels."""
    print(f"\n🎲 Testing Variance: Service/Return ±{service_var*100:.0f}%, Ace/DF ±{ace_df_var*100:.0f}%")
    print("=" * 80)

    # Update variance levels
    update_variance_levels(service_var, ace_df_var)

    # Reload the simulator to pick up changes
    import importlib
    import sim_models.main_sim.simulator
    importlib.reload(sim_models.main_sim.simulator)
    from sim_models.main_sim.simulator import FantasyTennisSimulator

    # Load player pool
    player_pool_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'player_pool.json')
    with open(player_pool_path, 'r') as f:
        player_pool_data = json.load(f)

    # Create salary mapping and matchups
    salary_map = {}
    matchups = []
    surface = player_pool_data.get('surface', 'Clay')

    # Create matchups from player list
    players = player_pool_data['players']
    processed_pairs = set()

    for player_data in players:
        player_name = player_data['name']
        opponent_name = player_data['opponent']
        salary = player_data['salary']

        salary_map[player_name] = salary

        # Create unique matchup pairs
        pair = tuple(sorted([player_name, opponent_name]))
        if pair not in processed_pairs:
            matchups.append((player_name, opponent_name, surface))
            processed_pairs.add(pair)

    # Initialize simulator
    simulator = FantasyTennisSimulator()

    # Storage for results
    player_performances = {}
    player_wins = {}
    player_matches = {}

    # Initialize storage
    for player in salary_map.keys():
        player_performances[player] = []
        player_wins[player] = 0
        player_matches[player] = 0

    # Run simulations
    print(f"Running {num_matches} simulations...")
    for i in range(num_matches):
        if i % 100 == 0:
            print(f"Progress: {i//10}%", end=" ")

        for player1, player2, surface in matchups:
            # Simulate match
            p1_stats, p2_stats, sets = simulator.simulate_match_detailed(
                player1, player2, surface, best_of_5=False, use_variance=True
            )

            # Calculate fantasy points
            p1_fp = p1_stats.calculate_fantasy_points(False)
            p2_fp = p2_stats.calculate_fantasy_points(False)

            # Track wins and matches
            player_matches[player1] += 1
            player_matches[player2] += 1

            if p1_stats.match_won:
                player_wins[player1] += 1
            else:
                player_wins[player2] += 1

            # Store performances
            player_performances[player1].append(p1_fp)
            player_performances[player2].append(p2_fp)

    print("Complete!")

    # Calculate statistics
    results = {}
    for player, performances in player_performances.items():
        if len(performances) >= 10:  # Only include players with enough data
            salary = salary_map[player]
            total_matches = player_matches.get(player, 0)
            wins = player_wins.get(player, 0)
            win_pct = (wins / total_matches * 100) if total_matches > 0 else 0

            # Calculate percentiles
            percentiles = [1, 25, 50, 75, 99]
            percentile_values = {}
            for p in percentiles:
                percentile_values[p] = np.percentile(performances, p)

            results[player] = {
                'salary': salary,
                'win_pct': win_pct,
                'matches': len(performances),
                'mean': np.mean(performances),
                'std': np.std(performances),
                'percentiles': percentile_values
            }

    return results


def compare_variance_levels():
    """Compare three different variance levels."""
    print("🎾 VARIANCE LEVEL COMPARISON - 1000 MATCHES EACH")
    print("=" * 80)

    # Test three variance levels
    variance_configs = [
        (0.10, 0.12, "Conservative (±10%/±12%)"),
        (0.15, 0.18, "Moderate (±15%/±18%)"),
        (0.20, 0.24, "Aggressive (±20%/±24%)")
    ]

    all_results = {}

    for service_var, ace_df_var, label in variance_configs:
        results = run_simulation_with_variance(service_var, ace_df_var)
        all_results[label] = results

    # Compare results
    print(f"\n📊 VARIANCE COMPARISON SUMMARY")
    print("=" * 80)

    # Get common players across all tests
    common_players = set(all_results[list(all_results.keys())[0]].keys())
    for results in all_results.values():
        common_players &= set(results.keys())

    # Sort by salary for consistent ordering
    sorted_players = sorted(common_players, key=lambda p: all_results[list(all_results.keys())[0]][p]['salary'], reverse=True)

    print(f"\n{'Player':<20} {'Salary':<8} ", end="")
    for label in all_results.keys():
        print(f"{label.split('(')[0].strip():<12} ", end="")
    print()
    print("-" * 80)

    for player in sorted_players[:10]:  # Top 10 by salary
        player_short = player[:19]
        salary = all_results[list(all_results.keys())[0]][player]['salary']
        print(f"{player_short:<20} ${salary:<7} ", end="")

        for label in all_results.keys():
            win_pct = all_results[label][player]['win_pct']
            print(f"{win_pct:>6.1f}%     ", end="")
        print()

    # Summary statistics
    print(f"\n📈 VARIANCE IMPACT ANALYSIS")
    print("-" * 60)

    for label, results in all_results.items():
        win_pcts = [r['win_pct'] for r in results.values()]
        fp_ranges = [r['percentiles'][99] - r['percentiles'][1] for r in results.values()]

        print(f"\n{label}:")
        print(f"  Win % Range: {min(win_pcts):.1f}% - {max(win_pcts):.1f}%")
        print(f"  Win % Spread: {max(win_pcts) - min(win_pcts):.1f}%")
        print(f"  Avg Fantasy Range: {np.mean(fp_ranges):.1f} points")
        print(f"  Fantasy Variance: {np.std(fp_ranges):.1f}")

    # Recommendations
    print(f"\n💡 RECOMMENDATIONS")
    print("-" * 60)
    print("Conservative: More predictable, favorites win more often")
    print("Moderate: Balanced approach, some upsets but skill matters")
    print("Aggressive: High variance, more upsets and chaos")
    print("\nChoose based on desired realism vs. DFS excitement level!")

    return all_results


if __name__ == "__main__":
    results = compare_variance_levels()
