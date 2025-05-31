#!/usr/bin/env python3
"""
Player Pool Tennis Simulation - 1000 Matches
Uses actual player pool with real salaries and matchups.
"""

import os
import sys
import json
import numpy as np

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sim_models.main_sim.simulator import FantasyTennisSimulator


def load_player_pool():
    """Load the actual player pool with real salaries and matchups."""
    with open('data/processed/player_pool.json', 'r') as f:
        data = json.load(f)

    surface = data['surface']
    players = data['players']

    # Create matchups from the player pool
    matchups = []
    salary_map = {}

    # Store salaries
    for player in players:
        salary_map[player['name']] = player['salary']

    # Create matchups (each player vs their opponent)
    processed_pairs = set()
    for player in players:
        player_name = player['name']
        opponent_name = player['opponent']

        # Avoid duplicate matchups
        pair = tuple(sorted([player_name, opponent_name]))
        if pair not in processed_pairs:
            matchups.append((player_name, opponent_name, surface))
            processed_pairs.add(pair)

    return matchups, salary_map, surface


def simulate_player_pool(custom_simulator=None):
    """Simulate 1000 matches using the actual player pool."""
    print("🎾 PLAYER POOL TENNIS SIMULATION - 1000 MATCHES")
    print("=" * 80)

    simulator = custom_simulator if custom_simulator else FantasyTennisSimulator()
    matchups, salary_map, surface = load_player_pool()

    print(f"Surface: {surface}")
    print(f"Unique matchups: {len(matchups)}")
    print(f"Total players: {len(salary_map)}")

    # Storage for all player performances and wins
    player_performances = {}
    player_wins = {}
    player_matches = {}

    # Initialize performance storage for all players
    for player in salary_map.keys():
        player_performances[player] = []
        player_wins[player] = 0
        player_matches[player] = 0

    print("\nRunning 1000 simulations...")
    print("Progress: ", end="", flush=True)

    # Run 1000 simulations by cycling through matchups
    for i in range(1000):
        if i % 100 == 0:
            print(f"{i//10}%", end=" ", flush=True)

        # Cycle through matchups
        matchup_idx = i % len(matchups)
        player1, player2, match_surface = matchups[matchup_idx]

        try:
            p1_stats, p2_stats, _ = simulator.simulate_match_detailed(
                player1, player2, match_surface, verbose=False
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

        except Exception as e:
            # Skip problematic matchups
            continue

    print("100% Complete!")

    # Calculate percentiles for each player
    print(f"\n📊 FANTASY POINTS PERCENTILE ANALYSIS")
    print("=" * 80)

    # Filter to players with at least 10 simulated matches
    qualified_players = {
        player: performances for player, performances in player_performances.items()
        if len(performances) >= 10
    }

    print(f"Analyzing {len(qualified_players)} players with 10+ simulated matches")

    # Calculate percentiles
    percentiles = [1, 25, 50, 75, 99]
    player_stats = []

    for player, performances in qualified_players.items():
        performances = np.array(performances)
        salary = salary_map.get(player, 0)

        # Calculate percentiles
        percentile_values = {}
        for p in percentiles:
            percentile_values[p] = np.percentile(performances, p)

        # Calculate win percentage
        total_matches = player_matches.get(player, 0)
        wins = player_wins.get(player, 0)
        win_pct = (wins / total_matches * 100) if total_matches > 0 else 0

        player_stats.append({
            'player': player,
            'salary': salary,
            'matches': len(performances),
            'win_pct': win_pct,
            'percentiles': percentile_values
        })

    # Sort by salary (descending)
    player_stats.sort(key=lambda x: x['salary'], reverse=True)

    # Display results
    print(f"\n{'Player':<25} {'Salary':<8} {'Win%':<6} ", end="")
    for p in percentiles:
        print(f"{p}th%{'':<4}", end="")
    print()
    print("-" * 90)

    for stats in player_stats:
        player = stats['player'][:24]  # Truncate long names
        salary = stats['salary']
        win_pct = stats['win_pct']

        print(f"{player:<25} ${salary:<7} {win_pct:>5.1f}% ", end="")

        for p in percentiles:
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

    print(f"Total simulated matches: 1000")
    print(f"Total player performances: {len(all_performances)}")
    print(f"Overall fantasy points range: {np.min(all_performances):.1f} - {np.max(all_performances):.1f}")
    print(f"Overall mean: {np.mean(all_performances):.1f} ± {np.std(all_performances):.1f}")

    # Salary tier analysis
    print(f"\nFantasy points by salary tier:")
    salary_tiers = [
        ("Elite ($10,000+)", 10000, 15000),
        ("High ($8,000-$9,999)", 8000, 9999),
        ("Mid ($6,000-$7,999)", 6000, 7999),
        ("Low ($3,000-$5,999)", 3000, 5999)
    ]

    for tier_name, min_sal, max_sal in salary_tiers:
        tier_performances = []
        tier_count = 0
        for stats in player_stats:
            salary = stats['salary']
            if min_sal <= salary <= max_sal:
                tier_count += 1
                # Get all performances for this player
                player_perfs = qualified_players[stats['player']]
                tier_performances.extend(player_perfs)

        if tier_performances:
            tier_mean = np.mean(tier_performances)
            print(f"  {tier_name}: {tier_mean:.1f} avg fantasy points ({tier_count} players)")


if __name__ == "__main__":
    simulate_player_pool()
