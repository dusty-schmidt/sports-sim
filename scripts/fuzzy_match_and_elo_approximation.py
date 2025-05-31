#!/usr/bin/env python3
"""
Fuzzy matching and ELO-based stat approximation for missing players.
File location: /home/dustys/the net/tennis/scripts/fuzzy_match_and_elo_approximation.py
"""

import os
import sys
import json
import csv
import pandas as pd
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple, Union

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sim_models.main_sim.simulator import FantasyTennisSimulator


def similarity(a: str, b: str) -> float:
    """Calculate similarity between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def fuzzy_match_player(target_name: str, candidate_names: List[str], threshold: float = 0.7) -> Optional[str]:
    """Find the best fuzzy match for a player name."""
    best_match = None
    best_score = 0.0

    for candidate in candidate_names:
        score = similarity(target_name, candidate)
        if score > best_score and score >= threshold:
            best_score = score
            best_match = candidate

    return best_match if best_score >= threshold else None


def load_tmcp_player_names() -> Dict[str, List[str]]:
    """Load all player names from TMCP CSV files."""
    tmcp_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'tmcp')
    player_names = {'men': set(), 'women': set()}

    # Key files that contain player names
    key_files = [
        'charting-m-stats-Overview.csv',
        'charting-w-stats-Overview.csv',
        'charting-m-matches.csv',
        'charting-w-matches.csv'
    ]

    for filename in key_files:
        filepath = os.path.join(tmcp_dir, filename)
        if os.path.exists(filepath):
            try:
                df = pd.read_csv(filepath)

                # Look for player name columns
                name_columns = [col for col in df.columns if 'player' in col.lower() or 'name' in col.lower()]

                if not name_columns:
                    # Try common column names
                    possible_cols = ['Player', 'player', 'Name', 'name', 'Player1', 'Player2']
                    name_columns = [col for col in possible_cols if col in df.columns]

                names_found = set()
                for col in name_columns:
                    unique_names = df[col].dropna().unique()
                    names_found.update([name.strip() for name in unique_names if isinstance(name, str) and name.strip()])

                if 'w-' in filename:  # Women's file
                    player_names['women'].update(names_found)
                else:  # Men's file
                    player_names['men'].update(names_found)

                print(f"✅ Loaded {len(names_found)} names from {filename}")

            except Exception as e:
                print(f"❌ Error reading {filename}: {e}")

    # Convert sets to sorted lists
    return {
        'men': sorted(list(player_names['men'])),
        'women': sorted(list(player_names['women']))
    }


def calculate_elo_based_stats(target_elo: float, all_players_data: Dict, surface: str = 'Clay', simulator=None) -> Tuple[Optional[Dict[str, float]], List[Dict]]:
    """Calculate stats based on average of players with similar ELO ratings."""
    if not simulator:
        return None, []

    elo_range = 100  # ±100 ELO points
    similar_players = []

    # Get players with similar ELO ratings
    for player_name, player_data in all_players_data.items():
        if isinstance(player_data, dict):
            # Get ELO rating for this player
            player_elo = simulator.analyzer.get_player_elo(player_name, surface)

            if player_elo and abs(player_elo - target_elo) <= elo_range:
                # Use the stats directly from player_data
                similar_players.append({
                    'name': player_name,
                    'elo': player_elo,
                    'stats': {
                        'service_points_won': player_data.get('service_points_won', 60.0),
                        'return_points_won': player_data.get('return_points_won', 40.0),
                        'ace_rate': player_data.get('ace_rate', 6.0),
                        'double_fault_rate': player_data.get('double_fault_rate', 4.0),
                        'first_serve_percentage': player_data.get('first_serve_percentage', 62.0)
                    }
                })

    if not similar_players:
        # Expand search range if no similar players found
        elo_range = 200
        for player_name, player_data in all_players_data.items():
            if isinstance(player_data, dict):
                player_elo = simulator.analyzer.get_player_elo(player_name, surface)

                if player_elo and abs(player_elo - target_elo) <= elo_range:
                    similar_players.append({
                        'name': player_name,
                        'elo': player_elo,
                        'stats': {
                            'service_points_won': player_data.get('service_points_won', 60.0),
                            'return_points_won': player_data.get('return_points_won', 40.0),
                            'ace_rate': player_data.get('ace_rate', 6.0),
                            'double_fault_rate': player_data.get('double_fault_rate', 4.0),
                            'first_serve_percentage': player_data.get('first_serve_percentage', 62.0)
                        }
                    })

    if similar_players:
        # Calculate weighted average based on ELO proximity
        total_weight = 0
        weighted_stats = {
            'service_points_won': 0.0,
            'return_points_won': 0.0,
            'ace_rate': 0.0,
            'double_fault_rate': 0.0,
            'first_serve_percentage': 0.0
        }

        for player in similar_players:
            # Weight inversely proportional to ELO difference
            elo_diff = abs(player['elo'] - target_elo)
            weight = 1 / (1 + elo_diff / 50)  # Closer ELO = higher weight
            total_weight += weight

            for stat_name in weighted_stats.keys():
                if stat_name in player['stats']:
                    weighted_stats[stat_name] += player['stats'][stat_name] * weight

        # Normalize by total weight
        if total_weight > 0:
            for stat_name in weighted_stats.keys():
                weighted_stats[stat_name] /= total_weight

        return weighted_stats, similar_players

    return None, []


def analyze_missing_players():
    """Analyze missing players and attempt fuzzy matching and ELO approximation."""
    print("🔍 ANALYZING MISSING PLAYERS WITH FUZZY MATCHING & ELO APPROXIMATION")
    print("=" * 80)

    simulator = FantasyTennisSimulator()

    # Load player pool
    player_pool_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'player_pool.json')
    with open(player_pool_path, 'r') as f:
        player_pool_data = json.load(f)

    surface = player_pool_data.get('surface', 'Clay')
    players = player_pool_data['players']

    # Load TMCP player names
    print("📂 Loading TMCP player names...")
    tmcp_names = load_tmcp_player_names()
    print(f"Found {len(tmcp_names['men'])} men's names and {len(tmcp_names['women'])} women's names in TMCP data")

    # Find missing players
    missing_players = []
    for player_data in players:
        player_name = player_data['name']

        # Check if player has stats
        stats_data = simulator.analyzer.get_player_stats(player_name, surface)
        in_calculated_stats = player_name in simulator.analyzer.calculated_stats

        if not stats_data or not in_calculated_stats:
            missing_players.append({
                'name': player_name,
                'salary': player_data['salary'],
                'elo': simulator.analyzer.get_player_elo(player_name, surface)
            })

    print(f"\n🚨 Found {len(missing_players)} players missing stats data:")
    for player in missing_players:
        print(f"  {player['name']:<25} ${player['salary']:<7} ELO: {player['elo']:.1f}")

    print(f"\n🔍 ATTEMPTING FUZZY MATCHING...")
    print("-" * 60)

    fuzzy_matches = {}
    for player in missing_players:
        player_name = player['name']

        # Try both men's and women's names
        all_tmcp_names = tmcp_names['men'] + tmcp_names['women']

        # Try different similarity thresholds
        for threshold in [0.8, 0.7, 0.6]:
            match = fuzzy_match_player(player_name, all_tmcp_names, threshold)
            if match:
                fuzzy_matches[player_name] = {
                    'match': match,
                    'similarity': similarity(player_name, match),
                    'threshold': threshold
                }
                print(f"  {player_name:<25} → {match:<25} (similarity: {similarity(player_name, match):.2f})")
                break

        if player_name not in fuzzy_matches:
            print(f"  {player_name:<25} → No fuzzy match found")

    print(f"\n🎯 ELO-BASED STAT APPROXIMATION...")
    print("-" * 60)

    # Load all player data for ELO approximation
    all_players_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'player_stats.json')
    with open(all_players_file, 'r') as f:
        all_players_data = json.load(f)

    elo_approximations = {}
    for player in missing_players:
        player_name = player['name']
        player_elo = player['elo']

        if player_elo:
            approximated_stats, similar_players = calculate_elo_based_stats(player_elo, all_players_data, surface, simulator)

            if approximated_stats:
                elo_approximations[player_name] = {
                    'stats': approximated_stats,
                    'similar_players': [p['name'] for p in similar_players[:5]],  # Top 5 similar
                    'elo_range': f"{min(p['elo'] for p in similar_players):.0f}-{max(p['elo'] for p in similar_players):.0f}"
                }

                print(f"  {player_name} (ELO {player_elo:.0f}):")
                print(f"    Service: {approximated_stats['service_points_won']:.1f}%")
                print(f"    Return: {approximated_stats['return_points_won']:.1f}%")
                print(f"    Based on {len(similar_players)} players (ELO {elo_approximations[player_name]['elo_range']})")
                print(f"    Similar players: {', '.join(elo_approximations[player_name]['similar_players'])}")
                print()

    print(f"\n📊 SUMMARY:")
    print("-" * 60)
    print(f"Missing players: {len(missing_players)}")
    print(f"Fuzzy matches found: {len(fuzzy_matches)}")
    print(f"ELO approximations created: {len(elo_approximations)}")

    return missing_players, fuzzy_matches, elo_approximations


if __name__ == "__main__":
    missing_players, fuzzy_matches, elo_approximations = analyze_missing_players()
