#!/usr/bin/env python3
"""
Full Slate Tennis Simulation - 1000 Matches
Shows fantasy points percentile outcomes for all players.
"""

import os
import sys
import numpy as np
import random
from pathlib import Path

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sim_models.main_sim.simulator import FantasyTennisSimulator


def create_full_slate_matchups():
    """Create realistic tennis matchups from available players."""
    simulator = FantasyTennisSimulator()

    # Get all players with real data
    all_players = list(simulator.analyzer.calculated_stats.keys())

    # Filter to players with sufficient data (at least 10 matches)
    quality_players = []
    for player in all_players:
        stats = simulator.analyzer.calculated_stats[player]
        if stats.get('matches', 0) >= 10:
            quality_players.append(player)

    print(f"Found {len(quality_players)} players with sufficient match data")

    # Create realistic matchups based on ranking tiers
    matchups = []
    surfaces = ['Hard', 'Clay', 'Grass']

    # Group players by rank tier for realistic matchups
    tier_players = {1: [], 2: [], 3: [], 4: [], 5: []}
    for player in quality_players:
        stats = simulator.analyzer.calculated_stats[player]
        tier = stats.get('rank_tier', 5)
        tier_players[tier].append(player)

    print(f"Player distribution by tier:")
    for tier, players in tier_players.items():
        print(f"  Tier {tier}: {len(players)} players")

    # Create 1000 matchups ensuring all players get multiple matches
    # First, ensure each player gets at least 3 matches
    for player in quality_players:
        for _ in range(3):
            # Pick a random opponent
            opponent = random.choice([p for p in quality_players if p != player])
            surface = random.choice(surfaces)
            matchups.append((player, opponent, surface))

    # Fill remaining slots with random matchups
    remaining_matches = 1000 - len(matchups)
    for i in range(remaining_matches):
        players = random.sample(quality_players, 2)
        surface = random.choice(surfaces)
        matchups.append((players[0], players[1], surface))

    return matchups


def simulate_full_slate():
    """Simulate 1000 matches and analyze fantasy points percentiles."""
    print("🎾 FULL SLATE TENNIS SIMULATION - 1000 MATCHES")
    print("=" * 80)

    simulator = FantasyTennisSimulator()
    matchups = create_full_slate_matchups()

    # Storage for all player performances
    player_performances = {}

    print("Running 1000 simulations...")
    print("Progress: ", end="", flush=True)

    for i, (player1, player2, surface) in enumerate(matchups):
        if i % 100 == 0:
            print(f"{i//10}%", end=" ", flush=True)

        try:
            p1_stats, p2_stats, sets = simulator.simulate_match_detailed(
                player1, player2, surface, verbose=False
            )

            # Calculate fantasy points
            p1_fp = p1_stats.calculate_fantasy_points(False)
            p2_fp = p2_stats.calculate_fantasy_points(False)

            # Store performances
            if player1 not in player_performances:
                player_performances[player1] = []
            if player2 not in player_performances:
                player_performances[player2] = []

            player_performances[player1].append(p1_fp)
            player_performances[player2].append(p2_fp)

        except Exception as e:
            # Skip problematic matchups
            continue

    print("100% Complete!")

    # Calculate percentiles for each player
    print(f"\n📊 FANTASY POINTS PERCENTILE ANALYSIS")
    print("=" * 80)

    # Filter to players with at least 5 simulated matches
    qualified_players = {
        player: performances for player, performances in player_performances.items()
        if len(performances) >= 5
    }

    print(f"Analyzing {len(qualified_players)} players with 5+ simulated matches")

    # Calculate percentiles
    percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
    player_stats = []

    for player, performances in qualified_players.items():
        performances = np.array(performances)

        # Get player info
        player_info = simulator.analyzer.calculated_stats.get(player, {})
        rank = player_info.get('rank', 999)
        tier = player_info.get('rank_tier', 5)
        matches_simulated = len(performances)

        # Calculate percentiles
        percentile_values = {}
        for p in percentiles:
            percentile_values[p] = np.percentile(performances, p)

        # Calculate salary based on tier and rank
        if tier == 1:  # Elite
            salary = 10500 + (50 - min(rank, 50)) * 20  # $10,500-$11,500
        elif tier == 2:  # Top
            salary = 8500 + (100 - min(rank, 100)) * 20  # $8,500-$10,500
        elif tier == 3:  # High
            salary = 6500 + (200 - min(rank, 200)) * 10  # $6,500-$8,500
        elif tier == 4:  # Mid
            salary = 4500 + (500 - min(rank, 500)) * 4   # $4,500-$6,500
        else:  # Low
            salary = 3000 + min(rank, 1000) * 1.5        # $3,000-$4,500

        player_stats.append({
            'player': player,
            'rank': rank,
            'tier': tier,
            'salary': int(salary),
            'matches': matches_simulated,
            'mean': np.mean(performances),
            'std': np.std(performances),
            'percentiles': percentile_values
        })

    # Sort by salary (descending)
    player_stats.sort(key=lambda x: x['salary'], reverse=True)

    # Display results
    print(f"\n{'Player':<25} {'Salary':<8} ", end="")
    for p in [1, 25, 50, 75, 99]:
        print(f"{p}th%{'':<4}", end="")
    print()
    print("-" * 80)

    for stats in player_stats[:30]:  # Show top 30 players
        player = stats['player'][:24]  # Truncate long names
        salary = stats['salary']

        print(f"{player:<25} ${salary:<7} ", end="")

        for p in [1, 25, 50, 75, 99]:
            value = stats['percentiles'][p]
            print(f"{value:>6.1f}  ", end="")
        print()

    # Summary statistics
    print(f"\n📈 SUMMARY STATISTICS")
    print("-" * 60)

    all_performances = []
    for performances in qualified_players.values():
        all_performances.extend(performances)

    all_performances = np.array(all_performances)

    print(f"Total simulated matches: {len(matchups)}")
    print(f"Total player performances: {len(all_performances)}")
    print(f"Overall fantasy points range: {np.min(all_performances):.1f} - {np.max(all_performances):.1f}")
    print(f"Overall mean: {np.mean(all_performances):.1f} ± {np.std(all_performances):.1f}")

    # Tier analysis
    print(f"\nFantasy points by tier:")
    for tier in [1, 2, 3, 4, 5]:
        tier_performances = []
        for stats in player_stats:
            if stats['tier'] == tier:
                tier_performances.append(stats['mean'])

        if tier_performances:
            tier_mean = np.mean(tier_performances)
            print(f"  Tier {tier}: {tier_mean:.1f} avg fantasy points ({len(tier_performances)} players)")


if __name__ == "__main__":
    simulate_full_slate()
