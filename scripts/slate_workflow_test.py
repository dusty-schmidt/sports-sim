#!/usr/bin/env python3
"""
Tennis Slate Workflow Test
Location: tennis/scripts/slate_workflow_test.py

Full workflow test for processing DraftKings slate data and running simulations.
Assumes clay court surface when not specified in data.
"""

import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sim_models'))

from main_sim.slate_simulator import TennisSlateSimulator, Match


def load_slate_data(file_path: str) -> Dict[str, Any]:
    """Load and parse slate data from JSON file"""
    print(f"📂 Loading slate data from: {file_path}")

    with open(file_path, 'r') as f:
        data = json.load(f)

    print(f"✅ Loaded slate with {len(data['players'])} players")
    return data


def extract_matches_from_slate(slate_data: Dict[str, Any]) -> Tuple[List[Match], str]:
    """
    Extract unique matches from slate player data

    Args:
        slate_data: Parsed slate JSON data

    Returns:
        Tuple of (matches_list, surface)
    """
    players = slate_data['players']
    surface = slate_data.get('surface', 'Clay')  # Default to clay as requested

    print(f"🎾 Extracting matches from slate (Surface: {surface})")

    # Track unique matches to avoid duplicates
    unique_matches = {}

    for player in players:
        player_name = player['name']
        opponent_name = player['opponent']

        # Create a consistent match key (alphabetical order)
        match_key = tuple(sorted([player_name, opponent_name]))

        if match_key not in unique_matches:
            # Determine player1 and player2 based on alphabetical order
            player1, player2 = match_key

            match = Match(
                player1=player1,
                player2=player2,
                surface=surface
            )
            unique_matches[match_key] = match
            print(f"   📋 Match: {player1} vs {player2}")

    matches = list(unique_matches.values())
    print(f"✅ Extracted {len(matches)} unique matches")

    return matches, surface


def create_player_salary_map(slate_data: Dict[str, Any]) -> Dict[str, int]:
    """Create mapping of player names to their salaries"""
    salary_map = {}
    for player in slate_data['players']:
        salary_map[player['name']] = player['salary']
    return salary_map


def run_slate_workflow_test(slate_file: str, num_simulations: int = 10):
    """
    Run the complete slate workflow test

    Args:
        slate_file: Path to the slate JSON file
        num_simulations: Number of slate simulations to run
    """
    print("🎾 TENNIS SLATE WORKFLOW TEST")
    print("=" * 60)

    try:
        # Step 1: Load slate data
        slate_data = load_slate_data(slate_file)

        # Step 2: Extract matches and surface
        matches, surface = extract_matches_from_slate(slate_data)

        # Step 3: Create salary mapping for reference
        salary_map = create_player_salary_map(slate_data)

        # Step 4: Initialize slate simulator
        print(f"\n🚀 Initializing slate simulator...")
        slate_simulator = TennisSlateSimulator()

        # Step 5: Run single slate simulation (detailed)
        print(f"\n📊 Running detailed single slate simulation...")
        single_result = slate_simulator.simulate_slate(matches, verbose=True)

        # Step 6: Display single simulation results
        print(f"\n{'='*60}")
        print("SINGLE SIMULATION RESULTS")
        print(f"{'='*60}")

        print(f"Total Fantasy Points Generated: {single_result.total_fantasy_points:.1f}")
        print(f"Simulation Timestamp: {single_result.timestamp}")

        print(f"\nMatch Results:")
        for match_result in single_result.matches:
            winner_salary = salary_map.get(match_result.winner_name, 'N/A')
            loser_salary = salary_map.get(match_result.loser_name, 'N/A')

            print(f"  🏆 {match_result.winner_name} def. {match_result.loser_name}")
            print(f"     Score: {match_result.final_score}")
            print(f"     Fantasy Points: {match_result.winner_name} {match_result.player1_fantasy_points if match_result.winner_name == match_result.player1 else match_result.player2_fantasy_points:.1f}, "
                  f"{match_result.loser_name} {match_result.player2_fantasy_points if match_result.winner_name == match_result.player1 else match_result.player1_fantasy_points:.1f}")
            print(f"     Salaries: {match_result.winner_name} ${winner_salary}, {match_result.loser_name} ${loser_salary}")
            print()

        # Step 7: Run multiple simulations for analysis
        if num_simulations > 1:
            print(f"\n🔄 Running {num_simulations} simulations for statistical analysis...")
            multiple_results = slate_simulator.simulate_multiple_slates(
                matches, num_simulations, verbose=True
            )

            # Step 8: Analyze multiple simulation results
            analyze_multiple_simulations(multiple_results, salary_map)

            # Step 9: Calculate detailed percentile analysis
            calculate_percentile_analysis(multiple_results, salary_map)

        print(f"\n✅ Slate workflow test completed successfully!")

    except Exception as e:
        print(f"❌ Error in slate workflow: {e}")
        import traceback
        traceback.print_exc()


def analyze_multiple_simulations(simulations: List, salary_map: Dict[str, int]):
    """Analyze results from multiple slate simulations"""
    print(f"\n{'='*60}")
    print("MULTIPLE SIMULATION ANALYSIS")
    print(f"{'='*60}")

    # Collect statistics
    total_fantasy_points = [sim.total_fantasy_points for sim in simulations]
    avg_total_points = sum(total_fantasy_points) / len(total_fantasy_points)
    min_total_points = min(total_fantasy_points)
    max_total_points = max(total_fantasy_points)

    print(f"Total Fantasy Points Across Slate:")
    print(f"  Average: {avg_total_points:.1f}")
    print(f"  Range: {min_total_points:.1f} - {max_total_points:.1f}")

    # Player win rates
    player_wins = {}
    player_fantasy_totals = {}

    for sim in simulations:
        for match_result in sim.matches:
            winner = match_result.winner_name
            loser = match_result.loser_name

            # Track wins
            player_wins[winner] = player_wins.get(winner, 0) + 1
            player_wins[loser] = player_wins.get(loser, 0)  # Ensure loser is in dict

            # Track fantasy points
            if match_result.winner_name == match_result.player1:
                winner_points = match_result.player1_fantasy_points
                loser_points = match_result.player2_fantasy_points
            else:
                winner_points = match_result.player2_fantasy_points
                loser_points = match_result.player1_fantasy_points

            player_fantasy_totals[winner] = player_fantasy_totals.get(winner, []) + [winner_points]
            player_fantasy_totals[loser] = player_fantasy_totals.get(loser, []) + [loser_points]

    # Display player statistics sorted by salary (descending)
    print(f"\nPlayer Performance Summary (sorted by salary):")
    print(f"{'Player':<20} {'Win Rate':<10} {'Avg Fantasy':<12} {'Salary':<8}")
    print("-" * 55)

    # Sort players by salary in descending order
    players_by_salary = sorted(player_wins.keys(),
                               key=lambda p: salary_map.get(p, 0),
                               reverse=True)

    for player in players_by_salary:
        win_rate = (player_wins[player] / len(simulations)) * 100
        avg_fantasy = (sum(player_fantasy_totals[player]) /
                       len(player_fantasy_totals[player]))
        salary = salary_map.get(player, 'N/A')

        print(f"{player:<20} {win_rate:>7.1f}%   {avg_fantasy:>9.1f}    "
              f"${salary}")


def calculate_percentile_analysis(simulations: List, salary_map: Dict[str, int]):
    """Calculate detailed percentile analysis for each player's fantasy points"""
    import numpy as np

    print(f"\n{'='*80}")
    print("DETAILED PERCENTILE ANALYSIS")
    print(f"{'='*80}")

    # Collect all fantasy points for each player
    player_fantasy_totals = {}

    for sim in simulations:
        for match_result in sim.matches:
            winner = match_result.winner_name
            loser = match_result.loser_name

            # Get fantasy points for winner and loser
            if match_result.winner_name == match_result.player1:
                winner_points = match_result.player1_fantasy_points
                loser_points = match_result.player2_fantasy_points
            else:
                winner_points = match_result.player2_fantasy_points
                loser_points = match_result.player1_fantasy_points

            player_fantasy_totals[winner] = player_fantasy_totals.get(winner, []) + [winner_points]
            player_fantasy_totals[loser] = player_fantasy_totals.get(loser, []) + [loser_points]

    # Calculate percentiles for each player
    percentiles = [25, 50, 75, 85, 95, 99]

    print(f"Fantasy Points Percentiles (based on {len(simulations)} simulations):")
    print(f"{'Player':<20} {'Salary':<8} {'25th':<6} {'50th':<6} {'75th':<6} {'85th':<6} {'95th':<6} {'99th':<6}")
    print("-" * 80)

    # Sort players by salary (descending)
    players_by_salary = sorted(player_fantasy_totals.keys(),
                               key=lambda p: salary_map.get(p, 0),
                               reverse=True)

    for player in players_by_salary:
        fantasy_points = player_fantasy_totals[player]
        salary = salary_map.get(player, 'N/A')

        # Calculate percentiles
        player_percentiles = np.percentile(fantasy_points, percentiles)

        print(f"{player:<20} ${salary:<7} {player_percentiles[0]:<5.1f} {player_percentiles[1]:<5.1f} "
              f"{player_percentiles[2]:<5.1f} {player_percentiles[3]:<5.1f} {player_percentiles[4]:<5.1f} "
              f"{player_percentiles[5]:<5.1f}")

    # Additional statistics
    print(f"\n{'='*80}")
    print("ADDITIONAL STATISTICS")
    print(f"{'='*80}")

    print(f"{'Player':<20} {'Salary':<8} {'Min':<6} {'Max':<6} {'Std':<6} {'CV':<6}")
    print("-" * 60)

    for player in players_by_salary:
        fantasy_points = player_fantasy_totals[player]
        salary = salary_map.get(player, 'N/A')

        min_pts = min(fantasy_points)
        max_pts = max(fantasy_points)
        std_pts = np.std(fantasy_points)
        mean_pts = np.mean(fantasy_points)
        cv = (std_pts / mean_pts) * 100 if mean_pts > 0 else 0  # Coefficient of variation

        print(f"{player:<20} ${salary:<7} {min_pts:<5.1f} {max_pts:<5.1f} {std_pts:<5.1f} {cv:<5.1f}%")


if __name__ == "__main__":
    # Default to the cleaned slate file
    slate_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'draftgroup_128447_clean.json')

    # Check if file exists
    if not os.path.exists(slate_file):
        print(f"❌ Slate file not found: {slate_file}")
        print("Please ensure the cleaned slate file exists.")
        sys.exit(1)

    # Run the workflow test with 1000 simulations for detailed analysis
    run_slate_workflow_test(slate_file, num_simulations=1000)
