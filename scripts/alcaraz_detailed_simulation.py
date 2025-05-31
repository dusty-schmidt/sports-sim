#!/usr/bin/env python3
"""
Detailed Alcaraz Match Simulation

Shows exactly how rate stats are calculated from the dataset and used in simulation.
"""

import os
import sys
import json
import numpy as np
from pathlib import Path

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sim_models.main_sim.simulator import FantasyTennisSimulator


def analyze_alcaraz_dataset_calculation():
    """Show exactly how Alcaraz's stats are calculated from the raw dataset."""
    print("🎾 CARLOS ALCARAZ - SURFACE-WEIGHTED DATASET PIPELINE")
    print("=" * 80)

    # Load the raw dataset to show the calculation
    dataset_file = Path("data/exploratory/calculated_player_stats.json")
    if not dataset_file.exists():
        print(f"❌ Dataset file not found: {dataset_file}")
        return

    with open(dataset_file, 'r') as f:
        dataset = json.load(f)

    if "Carlos Alcaraz" not in dataset:
        print("❌ Carlos Alcaraz not found in dataset")
        return

    alcaraz_data = dataset["Carlos Alcaraz"]

    print("📊 STEP 1: BASELINE DATASET VALUES (ALL SURFACES)")
    print("-" * 40)
    print("These are the calculated stats from ALL 146 matches:")
    print(f"  ace_rate: {alcaraz_data['ace_rate']:.2f}%")
    print(f"  double_fault_rate: {alcaraz_data['double_fault_rate']:.2f}%")
    print(f"  first_serve_percentage: {alcaraz_data['first_serve_percentage']:.1f}%")
    print(f"  service_points_won: {alcaraz_data['service_points_won']:.1f}%")
    print(f"  return_points_won: {alcaraz_data['return_points_won']:.1f}%")
    print(f"  matches: {alcaraz_data['matches']}")

    # Show surface breakdown
    surface_prefs = alcaraz_data.get('surface_preferences', {})
    print(f"\n📈 SURFACE BREAKDOWN:")
    for surface, pct in surface_prefs.items():
        matches = int(alcaraz_data['matches'] * pct)
        print(f"  {surface}: {pct:.1%} ({matches} matches)")

    print("\n🔍 STEP 2: SURFACE WEIGHTING LOGIC")
    print("-" * 40)
    print("For a CLAY COURT match, we should weight clay performance heavily:")
    clay_matches = int(alcaraz_data['matches'] * surface_prefs.get('Clay', 0.33))
    print(f"  • Alcaraz has {clay_matches} clay matches out of {alcaraz_data['matches']} total")
    if clay_matches >= 10:
        surface_weight = 0.7
        print(f"  • High clay experience → 70% clay weighting")
    elif clay_matches >= 5:
        surface_weight = 0.5
        print(f"  • Moderate clay experience → 50% clay weighting")
    else:
        surface_weight = 0.3
        print(f"  • Low clay experience → 30% clay weighting")

    print(f"  • Final formula: {surface_weight:.0%} clay-adjusted + {1-surface_weight:.0%} baseline")

    print("\n🎾 STEP 3: SURFACE-WEIGHTED STATS CALCULATION")
    print("-" * 40)

    simulator = FantasyTennisSimulator()
    surface = 'Clay'

    # Get surface-weighted stats from the analyzer
    surface_weighted_stats = simulator.analyzer.get_player_stats("Carlos Alcaraz", surface)

    print("NEW: Using surface-weighted stats from analyzer:")
    print(f"  Surface weight used: {surface_weighted_stats.get('_surface_weight', 'N/A'):.0%}")
    print(f"  ace_rate: {alcaraz_data['ace_rate']:.2f}% → {surface_weighted_stats['ace_rate']:.2f}%")
    print(f"  double_fault_rate: {alcaraz_data['double_fault_rate']:.2f}% → {surface_weighted_stats['double_fault_rate']:.2f}%")
    print(f"  service_points_won: {alcaraz_data['service_points_won']:.1f}% → {surface_weighted_stats['service_points_won']:.1f}%")
    print(f"  return_points_won: {alcaraz_data['return_points_won']:.1f}% → {surface_weighted_stats['return_points_won']:.1f}%")

    print(f"\nThis combines:")
    print(f"  • {surface_weight:.0%} clay-specific adjustments")
    print(f"  • {1-surface_weight:.0%} baseline all-surface stats")
    print(f"  • Accounts for Alcaraz's {clay_matches} clay matches out of {alcaraz_data['matches']} total")

    print("\n🎲 STEP 4: MATCH VARIANCE APPLICATION")
    print("-" * 40)

    # Show multiple variance samples using surface-weighted stats
    print("Skill-preserving variance (±8% for service stats, ±12% for ace/DF):")
    print("Sample variance applications:")

    np.random.seed(42)  # For reproducible examples
    for i in range(5):
        # Service stats variance (±8%)
        service_variance = np.random.uniform(0.92, 1.08)
        return_variance = np.random.uniform(0.92, 1.08)

        # Ace/DF variance (±12%)
        ace_variance = np.random.uniform(0.88, 1.12)
        df_variance = np.random.uniform(0.88, 1.12)

        # Use surface-weighted stats for variance calculation
        varied_service = surface_weighted_stats['service_points_won'] * service_variance
        varied_return = surface_weighted_stats['return_points_won'] * return_variance
        varied_ace = surface_weighted_stats['ace_rate'] * ace_variance
        varied_df = surface_weighted_stats['double_fault_rate'] * df_variance

        print(f"\n  Sample {i+1}:")
        print(f"    service_points_won: {surface_weighted_stats['service_points_won']:.1f}% × {service_variance:.3f} = {varied_service:.1f}%")
        print(f"    return_points_won: {surface_weighted_stats['return_points_won']:.1f}% × {return_variance:.3f} = {varied_return:.1f}%")
        print(f"    ace_rate: {surface_weighted_stats['ace_rate']:.2f}% × {ace_variance:.3f} = {varied_ace:.2f}%")
        print(f"    double_fault_rate: {surface_weighted_stats['double_fault_rate']:.2f}% × {df_variance:.3f} = {varied_df:.2f}%")

    print("\n⚙️ STEP 5: ELO INTEGRATION")
    print("-" * 40)

    # Get ELO data
    alcaraz_elo = simulator.analyzer.get_player_elo("Carlos Alcaraz", surface)
    dzumhur_elo = simulator.analyzer.get_player_elo("Damir Dzumhur", surface)

    print(f"Carlos Alcaraz Clay ELO: {alcaraz_elo}")
    print(f"Damir Dzumhur Clay ELO: {dzumhur_elo}")
    print(f"ELO difference: {alcaraz_elo - dzumhur_elo:.1f}")

    elo_win_prob = simulator.calculate_elo_win_probability("Carlos Alcaraz", "Damir Dzumhur", surface)
    print(f"ELO-based win probability: {elo_win_prob:.1%}")

    print("\n🎯 STEP 6: FINAL PROBABILITY CALCULATION")
    print("-" * 40)

    # Get actual match probabilities
    alcaraz_probs = simulator.get_match_adjusted_probabilities("Carlos Alcaraz", surface, use_variance=True)
    dzumhur_probs = simulator.get_match_adjusted_probabilities("Damir Dzumhur", surface, use_variance=True)

    print("Final match-adjusted probabilities:")
    print(f"Carlos Alcaraz:")
    for key, value in alcaraz_probs.items():
        print(f"  {key}: {value:.2f}%")

    print(f"\nDamir Dzumhur:")
    for key, value in dzumhur_probs.items():
        print(f"  {key}: {value:.2f}%")

    # Show point probability calculation
    server_strength = alcaraz_probs['service_points_won']
    returner_strength = dzumhur_probs['return_points_won']
    total_strength = server_strength + returner_strength
    stats_server_prob = server_strength / total_strength

    print(f"\nPoint-by-point probability calculation:")
    print(f"  Alcaraz service strength: {server_strength:.1f}%")
    print(f"  Dzumhur return strength: {returner_strength:.1f}%")
    print(f"  Total strength: {total_strength:.1f}")
    print(f"  Stats-based Alcaraz win prob: {stats_server_prob:.1%}")

    # Final blended probability
    elo_weight = 0.25
    stats_weight = 0.55  # 75% - 20% random
    random_weight = 0.20

    final_prob = (elo_weight * elo_win_prob) + (stats_weight * stats_server_prob) + (random_weight * 0.5)

    print(f"\nFinal blended probability:")
    print(f"  ELO component (25%): {elo_weight * elo_win_prob:.3f}")
    print(f"  Stats component (55%): {stats_weight * stats_server_prob:.3f}")
    print(f"  Random component (20%): {random_weight * 0.5:.3f}")
    print(f"  Final Alcaraz win probability: {final_prob:.1%}")

    return alcaraz_probs, dzumhur_probs


def simulate_alcaraz_match():
    """Simulate the Alcaraz vs Dzumhur match with detailed output."""
    print("\n" + "=" * 80)
    print("🎾 MATCH SIMULATION: Carlos Alcaraz vs Damir Dzumhur")
    print("=" * 80)

    simulator = FantasyTennisSimulator()

    # Run multiple simulations to show variance
    print("\nRunning 10 simulations to show realistic variance:")
    print("-" * 60)

    alcaraz_wins = 0
    alcaraz_fantasy_points = []
    dzumhur_fantasy_points = []

    for i in range(10):
        p1_stats, p2_stats, sets = simulator.simulate_match_detailed(
            "Carlos Alcaraz", "Damir Dzumhur", "Clay", verbose=False
        )

        if p1_stats.sets_won > p2_stats.sets_won:
            alcaraz_wins += 1
            winner = "Alcaraz"
        else:
            winner = "Dzumhur"

        alcaraz_fp = p1_stats.calculate_fantasy_points(False)
        dzumhur_fp = p2_stats.calculate_fantasy_points(False)

        alcaraz_fantasy_points.append(alcaraz_fp)
        dzumhur_fantasy_points.append(dzumhur_fp)

        print(f"Sim {i+1:2d}: {winner:8s} wins | "
              f"Alcaraz: {alcaraz_fp:5.1f} pts | "
              f"Dzumhur: {dzumhur_fp:5.1f} pts | "
              f"Score: {p1_stats.sets_won}-{p1_stats.sets_lost}")

    print(f"\nResults Summary:")
    print(f"  Alcaraz win rate: {alcaraz_wins}/10 = {alcaraz_wins/10:.1%}")
    print(f"  Alcaraz fantasy points: {np.mean(alcaraz_fantasy_points):.1f} ± {np.std(alcaraz_fantasy_points):.1f}")
    print(f"  Dzumhur fantasy points: {np.mean(dzumhur_fantasy_points):.1f} ± {np.std(dzumhur_fantasy_points):.1f}")
    print(f"  Alcaraz range: {min(alcaraz_fantasy_points):.1f} - {max(alcaraz_fantasy_points):.1f}")
    print(f"  Dzumhur range: {min(dzumhur_fantasy_points):.1f} - {max(dzumhur_fantasy_points):.1f}")

    print("\n✅ This shows realistic variance while preserving skill differences!")


if __name__ == "__main__":
    # First show the detailed calculation pipeline
    analyze_alcaraz_dataset_calculation()

    # Then simulate the actual match
    simulate_alcaraz_match()
