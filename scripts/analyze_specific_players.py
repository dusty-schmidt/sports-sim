#!/usr/bin/env python3
"""
Analyze specific players that might be over-performing in simulations.
"""

import os
import sys
import json

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sim_models.main_sim.simulator import FantasyTennisSimulator


def analyze_player_matchups():
    """Analyze Ben Shelton and Elena Rybakina's specific matchups."""
    print("🔍 ANALYZING SPECIFIC PLAYER MATCHUPS")
    print("=" * 80)

    simulator = FantasyTennisSimulator()

    # Analyze Ben Shelton vs Matteo Gigante
    print("📊 BEN SHELTON vs MATTEO GIGANTE")
    print("-" * 60)

    # Get player stats
    shelton_stats = simulator.analyzer.get_player_stats("Ben Shelton", "Clay")
    gigante_stats = simulator.analyzer.get_player_stats("Matteo Gigante", "Clay")

    print("Ben Shelton (Clay-weighted stats):")
    for key, value in shelton_stats.items():
        if isinstance(value, (int, float)):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")

    print(f"\nMatteo Gigante (Clay-weighted stats):")
    for key, value in gigante_stats.items():
        if isinstance(value, (int, float)):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")

    # Get ELO ratings
    shelton_elo = simulator.analyzer.get_player_elo("Ben Shelton", "Clay")
    gigante_elo = simulator.analyzer.get_player_elo("Matteo Gigante", "Clay")

    print(f"\nELO Ratings:")
    print(f"  Ben Shelton Clay ELO: {shelton_elo}")
    print(f"  Matteo Gigante Clay ELO: {gigante_elo}")

    if shelton_elo and gigante_elo:
        elo_diff = shelton_elo - gigante_elo
        elo_prob = simulator.calculate_elo_win_probability("Ben Shelton", "Matteo Gigante", "Clay")
        print(f"  ELO difference: {elo_diff:.1f} points")
        print(f"  ELO-based win probability: {elo_prob:.1%}")

    # Check if either player has unusual stats
    print(f"\nPotential Issues:")
    if not gigante_stats:
        print(f"  🚨 MAJOR ISSUE: Matteo Gigante has NO clay court data!")
        print(f"     This means the simulation is using default/fallback stats")
    else:
        if shelton_stats.get('service_points_won', 0) > 70:
            print(f"  ⚠️  Ben Shelton has very high service rate: {shelton_stats['service_points_won']:.1f}%")
        if gigante_stats.get('service_points_won', 0) < 50:
            print(f"  ⚠️  Matteo Gigante has very low service rate: {gigante_stats['service_points_won']:.1f}%")
        if shelton_stats.get('return_points_won', 0) > 45:
            print(f"  ⚠️  Ben Shelton has very high return rate: {shelton_stats['return_points_won']:.1f}%")
        if gigante_stats.get('return_points_won', 0) < 35:
            print(f"  ⚠️  Matteo Gigante has very low return rate: {gigante_stats['return_points_won']:.1f}%")

    print(f"\n" + "=" * 80)
    print("📊 ELENA RYBAKINA vs JELENA OSTAPENKO")
    print("-" * 60)

    # Get player stats
    rybakina_stats = simulator.analyzer.get_player_stats("Elena Rybakina", "Clay")
    ostapenko_stats = simulator.analyzer.get_player_stats("Jelena Ostapenko", "Clay")

    print("Elena Rybakina (Clay-weighted stats):")
    for key, value in rybakina_stats.items():
        if isinstance(value, (int, float)):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")

    print(f"\nJelena Ostapenko (Clay-weighted stats):")
    for key, value in ostapenko_stats.items():
        if isinstance(value, (int, float)):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")

    # Get ELO ratings
    rybakina_elo = simulator.analyzer.get_player_elo("Elena Rybakina", "Clay")
    ostapenko_elo = simulator.analyzer.get_player_elo("Jelena Ostapenko", "Clay")

    print(f"\nELO Ratings:")
    print(f"  Elena Rybakina Clay ELO: {rybakina_elo}")
    print(f"  Jelena Ostapenko Clay ELO: {ostapenko_elo}")

    if rybakina_elo and ostapenko_elo:
        elo_diff = rybakina_elo - ostapenko_elo
        elo_prob = simulator.calculate_elo_win_probability("Elena Rybakina", "Jelena Ostapenko", "Clay")
        print(f"  ELO difference: {elo_diff:.1f} points")
        print(f"  ELO-based win probability: {elo_prob:.1%}")

    # Check if either player has unusual stats
    print(f"\nPotential Issues:")
    if not ostapenko_stats:
        print(f"  🚨 MAJOR ISSUE: Jelena Ostapenko has NO clay court data!")
        print(f"     This means the simulation is using default/fallback stats")
    else:
        if rybakina_stats.get('service_points_won', 0) > 70:
            print(f"  ⚠️  Elena Rybakina has very high service rate: {rybakina_stats['service_points_won']:.1f}%")
        if ostapenko_stats.get('service_points_won', 0) < 50:
            print(f"  ⚠️  Jelena Ostapenko has very low service rate: {ostapenko_stats['service_points_won']:.1f}%")
        if rybakina_stats.get('return_points_won', 0) > 45:
            print(f"  ⚠️  Elena Rybakina has very high return rate: {rybakina_stats['return_points_won']:.1f}%")
        if ostapenko_stats.get('return_points_won', 0) < 35:
            print(f"  ⚠️  Jelena Ostapenko has very low return rate: {ostapenko_stats['return_points_won']:.1f}%")

    print(f"\n" + "=" * 80)
    print("🔍 SURFACE WEIGHTING ANALYSIS")
    print("-" * 60)

    # Check surface weighting for these players
    players_to_check = ["Ben Shelton", "Matteo Gigante", "Elena Rybakina", "Jelena Ostapenko"]

    for player in players_to_check:
        if player in simulator.analyzer.calculated_stats:
            player_data = simulator.analyzer.calculated_stats[player]
            total_matches = player_data.get('matches', 0)
            clay_matches = player_data.get('clay_matches', 0)
            clay_percentage = (clay_matches / total_matches * 100) if total_matches > 0 else 0

            # Calculate surface weighting
            if clay_percentage >= 30:
                clay_weight = 0.7
            elif clay_percentage >= 15:
                clay_weight = 0.5
            elif clay_percentage >= 5:
                clay_weight = 0.3
            else:
                clay_weight = 0.1

            print(f"{player}:")
            print(f"  Total matches: {total_matches}")
            print(f"  Clay matches: {clay_matches} ({clay_percentage:.1f}%)")
            print(f"  Clay weighting: {clay_weight:.1%}")

            # Check if they have very different clay vs all-surface stats
            if 'clay_service_points_won' in player_data and 'service_points_won' in player_data:
                clay_service = player_data['clay_service_points_won']
                all_service = player_data['service_points_won']
                service_diff = clay_service - all_service
                print(f"  Service difference (clay vs all): {service_diff:+.1f}%")

                if abs(service_diff) > 5:
                    print(f"    ⚠️  Large service difference on clay!")

            print()

    print(f"\n" + "=" * 80)
    print("💡 POTENTIAL SOLUTIONS")
    print("-" * 60)
    print("If Ben Shelton and Elena Rybakina are over-performing:")
    print("1. Check if their clay court stats are inflated vs their general ability")
    print("2. Verify ELO ratings are accurate for clay court performance")
    print("3. Consider if surface weighting is too aggressive for these players")
    print("4. Check if their opponents have unusually poor clay court records")
    print("5. Verify the underlying data quality for these specific players")


if __name__ == "__main__":
    analyze_player_matchups()
