#!/usr/bin/env python3
"""
Simulation Diagnostics Tool

Comprehensive analysis of tennis simulation behavior to identify specific issues
and calibrate parameters based on real-world data comparisons.
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Any
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sim_models.main_sim.slate_simulator import TennisSlateSimulator
from sim_models.main_sim.simulator import FantasyTennisSimulator


class SimulationDiagnostics:
    """Comprehensive diagnostics for tennis simulation analysis."""

    def __init__(self):
        self.simulator = FantasyTennisSimulator()
        self.slate_sim = TennisSlateSimulator()
        self.results = {}

    def load_slate_data(self, file_path: str) -> Dict[str, Any]:
        """Load and parse slate data from JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data

    def extract_matches_from_slate(self, slate_data: Dict[str, Any]) -> List[Dict]:
        """Extract matches from slate data for analysis"""
        from sim_models.main_sim.slate_simulator import Match

        players = slate_data['players']
        surface = slate_data.get('surface', 'Clay')

        # Track unique matches to avoid duplicates
        unique_matches = {}
        salary_map = {}

        for player in players:
            player_name = player['name']
            opponent_name = player['opponent']
            salary_map[player_name] = player['salary']

            # Create a consistent match key (alphabetical order)
            match_key = tuple(sorted([player_name, opponent_name]))

            if match_key not in unique_matches:
                player1, player2 = match_key
                unique_matches[match_key] = {
                    'player1': player1,
                    'player2': player2,
                    'surface': surface,
                    'player1_salary': salary_map.get(player1, 0),
                    'player2_salary': salary_map.get(player2, 0)
                }

        return list(unique_matches.values())

    def analyze_elo_impact(self, matches: List, num_simulations: int = 100) -> Dict:
        """Analyze how ELO differences translate to win probabilities."""
        print("🔍 Analyzing ELO Impact on Win Probabilities...")

        elo_analysis = {
            'elo_diffs': [],
            'theoretical_probs': [],
            'actual_win_rates': [],
            'player_pairs': []
        }

        for match in matches:
            p1, p2 = match['player1'], match['player2']
            surface = match.get('surface', 'Clay')

            # Get ELO ratings
            p1_elo = self.simulator.analyzer.get_player_elo(p1, surface)
            p2_elo = self.simulator.analyzer.get_player_elo(p2, surface)

            if p1_elo and p2_elo:
                elo_diff = p1_elo - p2_elo
                theoretical_prob = self.simulator.calculate_elo_win_probability(p1, p2, surface)

                # Run simulations to get actual win rate
                p1_wins = 0
                for _ in range(num_simulations):
                    p1_stats, p2_stats, _ = self.simulator.simulate_match_detailed(
                        p1, p2, surface, use_variance=True
                    )
                    if p1_stats.sets_won > p2_stats.sets_won:
                        p1_wins += 1

                actual_win_rate = p1_wins / num_simulations

                elo_analysis['elo_diffs'].append(elo_diff)
                elo_analysis['theoretical_probs'].append(theoretical_prob)
                elo_analysis['actual_win_rates'].append(actual_win_rate)
                elo_analysis['player_pairs'].append(f"{p1} vs {p2}")

                print(f"  {p1} vs {p2}: ELO diff {elo_diff:.0f}, "
                      f"Theoretical {theoretical_prob:.1%}, Actual {actual_win_rate:.1%}")

        return elo_analysis

    def analyze_variance_by_player_tier(self, matches: List, num_simulations: int = 200) -> Dict:
        """Analyze variance patterns by player skill tier."""
        print("🔍 Analyzing Variance by Player Tier...")

        tier_analysis = defaultdict(lambda: {
            'fantasy_points': [],
            'win_rates': [],
            'players': []
        })

        # Define tiers based on salary (proxy for skill)
        salary_tiers = {
            'Elite': (10000, 15000),
            'High': (8000, 9999),
            'Mid': (6000, 7999),
            'Low': (3000, 5999)
        }

        for match in matches:
            for player_key in ['player1', 'player2']:
                player = match[player_key]
                salary = match.get(f'{player_key}_salary', 0)

                # Determine tier
                tier = 'Unknown'
                for tier_name, (min_sal, max_sal) in salary_tiers.items():
                    if min_sal <= salary <= max_sal:
                        tier = tier_name
                        break

                # Run simulations for this player
                fantasy_points = []
                wins = 0

                for _ in range(num_simulations):
                    if player_key == 'player1':
                        p1_stats, p2_stats, _ = self.simulator.simulate_match_detailed(
                            player, match['player2'], match.get('surface', 'Clay')
                        )
                        player_stats = p1_stats
                        won = p1_stats.sets_won > p2_stats.sets_won
                    else:
                        p1_stats, p2_stats, _ = self.simulator.simulate_match_detailed(
                            match['player1'], player, match.get('surface', 'Clay')
                        )
                        player_stats = p2_stats
                        won = p2_stats.sets_won > p1_stats.sets_won

                    fantasy_points.append(player_stats.calculate_fantasy_points(False))
                    if won:
                        wins += 1

                tier_analysis[tier]['fantasy_points'].extend(fantasy_points)
                tier_analysis[tier]['win_rates'].append(wins / num_simulations)
                tier_analysis[tier]['players'].append(player)

        # Calculate statistics for each tier
        tier_stats = {}
        for tier, data in tier_analysis.items():
            if data['fantasy_points']:
                fp_array = np.array(data['fantasy_points'])
                tier_stats[tier] = {
                    'count': len(data['players']),
                    'avg_fantasy': np.mean(fp_array),
                    'fantasy_std': np.std(fp_array),
                    'fantasy_cv': np.std(fp_array) / np.mean(fp_array) * 100,
                    'fantasy_25th': np.percentile(fp_array, 25),
                    'fantasy_75th': np.percentile(fp_array, 75),
                    'avg_win_rate': np.mean(data['win_rates']),
                    'win_rate_std': np.std(data['win_rates'])
                }

                print(f"  {tier} Tier ({tier_stats[tier]['count']} players):")
                print(f"    Fantasy: {tier_stats[tier]['avg_fantasy']:.1f} ± {tier_stats[tier]['fantasy_std']:.1f}")
                print(f"    25th-75th percentile: {tier_stats[tier]['fantasy_25th']:.1f} - {tier_stats[tier]['fantasy_75th']:.1f}")
                print(f"    Win Rate: {tier_stats[tier]['avg_win_rate']:.1%} ± {tier_stats[tier]['win_rate_std']:.1%}")
                print(f"    Coefficient of Variation: {tier_stats[tier]['fantasy_cv']:.1f}%")

        return tier_stats

    def analyze_competitive_balance(self, matches: List, num_simulations: int = 200) -> Dict:
        """Analyze competitive balance in close matchups."""
        print("🔍 Analyzing Competitive Balance...")

        balance_analysis = {
            'close_matches': [],
            'medium_matches': [],
            'lopsided_matches': []
        }

        for match in matches:
            p1, p2 = match['player1'], match['player2']
            p1_salary = match.get('player1_salary', 0)
            p2_salary = match.get('player2_salary', 0)

            # Calculate salary difference as proxy for skill gap
            salary_diff = abs(p1_salary - p2_salary)
            salary_ratio = max(p1_salary, p2_salary) / min(p1_salary, p2_salary) if min(p1_salary, p2_salary) > 0 else 1

            # Run simulations
            p1_wins = 0
            fantasy_points_p1 = []
            fantasy_points_p2 = []

            for _ in range(num_simulations):
                p1_stats, p2_stats, _ = self.simulator.simulate_match_detailed(
                    p1, p2, match.get('surface', 'Clay')
                )

                if p1_stats.sets_won > p2_stats.sets_won:
                    p1_wins += 1

                fantasy_points_p1.append(p1_stats.calculate_fantasy_points(False))
                fantasy_points_p2.append(p2_stats.calculate_fantasy_points(False))

            win_rate = p1_wins / num_simulations
            favorite_win_rate = max(win_rate, 1 - win_rate)

            match_analysis = {
                'players': f"{p1} vs {p2}",
                'salary_diff': salary_diff,
                'salary_ratio': salary_ratio,
                'favorite_win_rate': favorite_win_rate,
                'p1_win_rate': win_rate,
                'p1_avg_fantasy': np.mean(fantasy_points_p1),
                'p2_avg_fantasy': np.mean(fantasy_points_p2),
                'p1_fantasy_std': np.std(fantasy_points_p1),
                'p2_fantasy_std': np.std(fantasy_points_p2)
            }

            # Categorize matches
            if salary_ratio <= 1.3:  # Close match
                balance_analysis['close_matches'].append(match_analysis)
            elif salary_ratio <= 2.0:  # Medium gap
                balance_analysis['medium_matches'].append(match_analysis)
            else:  # Lopsided
                balance_analysis['lopsided_matches'].append(match_analysis)

        # Print summary statistics
        for category, matches in balance_analysis.items():
            if matches:
                avg_favorite_win_rate = np.mean([m['favorite_win_rate'] for m in matches])
                print(f"  {category.replace('_', ' ').title()} ({len(matches)} matches):")
                print(f"    Average favorite win rate: {avg_favorite_win_rate:.1%}")

                for match in matches:
                    print(f"    {match['players']}: {match['favorite_win_rate']:.1%} "
                          f"(salary ratio: {match['salary_ratio']:.2f})")

        return balance_analysis

    def analyze_calibrated_factors_impact(self, matches: List, num_simulations: int = 100) -> Dict:
        """Analyze impact of calibrated factors (clutch, variance, etc.)."""
        print("🔍 Analyzing Calibrated Factors Impact...")

        factor_analysis = {}

        for match in matches:
            p1, p2 = match['player1'], match['player2']

            # Get calibrated factors
            p1_clutch = self.simulator.analyzer.get_player_clutch_factor(p1)
            p2_clutch = self.simulator.analyzer.get_player_clutch_factor(p2)
            p1_variance = self.simulator.analyzer.get_player_variance_factor(p1)
            p2_variance = self.simulator.analyzer.get_player_variance_factor(p2)

            # Run simulations with and without variance
            results_with_variance = []
            results_without_variance = []

            for use_variance in [True, False]:
                p1_wins = 0
                for _ in range(num_simulations):
                    p1_stats, p2_stats, _ = self.simulator.simulate_match_detailed(
                        p1, p2, match.get('surface', 'Clay'), use_variance=use_variance
                    )
                    if p1_stats.sets_won > p2_stats.sets_won:
                        p1_wins += 1

                win_rate = p1_wins / num_simulations
                if use_variance:
                    results_with_variance.append(win_rate)
                else:
                    results_without_variance.append(win_rate)

            factor_analysis[f"{p1} vs {p2}"] = {
                'p1_clutch': p1_clutch,
                'p2_clutch': p2_clutch,
                'p1_variance': p1_variance,
                'p2_variance': p2_variance,
                'win_rate_with_variance': results_with_variance[0],
                'win_rate_without_variance': results_without_variance[0],
                'variance_impact': abs(results_with_variance[0] - results_without_variance[0])
            }

            print(f"  {p1} vs {p2}:")
            print(f"    Clutch factors: {p1_clutch:.3f} vs {p2_clutch:.3f}")
            print(f"    Win rate with variance: {results_with_variance[0]:.1%}")
            print(f"    Win rate without variance: {results_without_variance[0]:.1%}")
            print(f"    Variance impact: {factor_analysis[f'{p1} vs {p2}']['variance_impact']:.1%}")

        return factor_analysis


def run_comprehensive_diagnostics():
    """Run comprehensive simulation diagnostics."""
    print("🎾 TENNIS SIMULATION DIAGNOSTICS")
    print("=" * 60)

    # Load slate data
    slate_file = Path("data/draftgroup_128447_clean.json")
    if not slate_file.exists():
        print(f"❌ Slate file not found: {slate_file}")
        return

    diagnostics = SimulationDiagnostics()

    # Load and extract matches
    slate_data = diagnostics.load_slate_data(str(slate_file))
    matches = diagnostics.extract_matches_from_slate(slate_data)

    print(f"📊 Analyzing {len(matches)} matches from slate...")

    # Run diagnostic analyses
    results = {}

    # 1. ELO Impact Analysis
    results['elo_analysis'] = diagnostics.analyze_elo_impact(matches, 50)

    # 2. Variance by Player Tier
    results['tier_analysis'] = diagnostics.analyze_variance_by_player_tier(matches, 100)

    # 3. Competitive Balance
    results['balance_analysis'] = diagnostics.analyze_competitive_balance(matches, 100)

    # 4. Calibrated Factors Impact
    results['factor_analysis'] = diagnostics.analyze_calibrated_factors_impact(matches, 50)

    # Save results
    output_file = "simulation_diagnostics_results.json"
    with open(output_file, 'w') as f:
        # Convert numpy arrays to lists for JSON serialization
        json_results = {}
        for key, value in results.items():
            if key == 'elo_analysis':
                json_results[key] = {
                    'elo_diffs': [float(x) for x in value['elo_diffs']],
                    'theoretical_probs': [float(x) for x in value['theoretical_probs']],
                    'actual_win_rates': [float(x) for x in value['actual_win_rates']],
                    'player_pairs': value['player_pairs']
                }
            else:
                json_results[key] = value

        json.dump(json_results, f, indent=2)

    print(f"\n✅ Diagnostics complete! Results saved to {output_file}")

    return results


if __name__ == "__main__":
    run_comprehensive_diagnostics()
