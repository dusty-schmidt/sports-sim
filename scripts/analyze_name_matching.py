#!/usr/bin/env python3
"""
Analyze name matching between player_pool.json and tenab_stats files
"""

import json
import csv
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple


def clean_player_name(name: str) -> str:
    """Clean player name by removing URLs, brackets, and extra whitespace."""
    # Remove URL parts in parentheses
    name = re.sub(r'\(http[^)]+\)', '', name)

    # Remove country codes in brackets
    name = re.sub(r'\s*\[[A-Z]{2,3}\]', '', name)

    # Clean up whitespace
    name = name.strip()

    return name


def load_player_pool() -> List[str]:
    """Load player names from player_pool.json."""
    pool_file = Path("data/processed/player_pool.json")

    with open(pool_file, 'r') as f:
        data = json.load(f)

    return [player['name'] for player in data['players']]


def load_tenab_stats() -> Dict[str, List[str]]:
    """Load player names from all tenab_stats files."""
    stats_dir = Path("data/raw/tenab_stats")
    files = ['atp.tsv', 'atp2.tsv', 'atp3.tsv', 'wta.tsv', 'wta2.tsv']

    all_players = {}

    for file in files:
        file_path = stats_dir / file
        players = []

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                if 'Player' in row and row['Player']:
                    clean_name = clean_player_name(row['Player'])
                    if clean_name:  # Only add non-empty names
                        players.append(clean_name)

        all_players[file] = players
        print(f"Loaded {len(players)} players from {file}")

    return all_players


def find_exact_matches(pool_players: List[str], stats_players: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Find exact matches between pool and stats players."""
    matches = {}

    for pool_player in pool_players:
        matches[pool_player] = []

        for file, players in stats_players.items():
            if pool_player in players:
                matches[pool_player].append(file)

    return matches


def find_fuzzy_matches(pool_players: List[str], stats_players: Dict[str, List[str]]) -> Dict[str, List[Tuple[str, str]]]:
    """Find potential fuzzy matches for unmatched players."""
    fuzzy_matches = {}

    # Create a flat list of all stats players with their source file
    all_stats_players = []
    for file, players in stats_players.items():
        for player in players:
            all_stats_players.append((player, file))

    for pool_player in pool_players:
        fuzzy_matches[pool_player] = []

        # Split pool player name into parts
        pool_parts = pool_player.lower().split()

        for stats_player, file in all_stats_players:
            stats_parts = stats_player.lower().split()

            # Check if all parts of pool name are in stats name or vice versa
            if (all(part in ' '.join(stats_parts) for part in pool_parts) or
                all(part in ' '.join(pool_parts) for part in stats_parts)):
                fuzzy_matches[pool_player].append((stats_player, file))

    return fuzzy_matches


def main():
    print("🔍 Analyzing name matching between player_pool.json and tenab_stats files")
    print("=" * 80)

    # Load data
    pool_players = load_player_pool()
    stats_players = load_tenab_stats()

    print(f"\n📊 Summary:")
    print(f"   Player pool: {len(pool_players)} players")
    total_stats = sum(len(players) for players in stats_players.values())
    print(f"   Stats files: {total_stats} total players")

    # Find exact matches
    print(f"\n🎯 EXACT MATCHES:")
    print("-" * 40)
    exact_matches = find_exact_matches(pool_players, stats_players)

    matched_players = []
    unmatched_players = []

    for player, files in exact_matches.items():
        if files:
            matched_players.append(player)
            print(f"✅ {player} -> {', '.join(files)}")
        else:
            unmatched_players.append(player)

    print(f"\n📈 Exact match summary:")
    print(f"   Matched: {len(matched_players)}/{len(pool_players)} ({len(matched_players)/len(pool_players)*100:.1f}%)")
    print(f"   Unmatched: {len(unmatched_players)}")

    # Find fuzzy matches for unmatched players
    if unmatched_players:
        print(f"\n🔍 FUZZY MATCHES FOR UNMATCHED PLAYERS:")
        print("-" * 40)

        fuzzy_matches = find_fuzzy_matches(unmatched_players, stats_players)

        for player in unmatched_players:
            matches = fuzzy_matches[player]
            if matches:
                print(f"❓ {player}:")
                for match, file in matches:
                    print(f"     -> {match} ({file})")
            else:
                print(f"❌ {player}: No fuzzy matches found")

    # Show sample of stats file format
    print(f"\n📋 SAMPLE STATS FILE FORMAT:")
    print("-" * 40)
    stats_file = Path("data/raw/tenab_stats/atp.tsv")
    with open(stats_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        headers = reader.fieldnames
        print(f"Headers: {headers}")

        # Show first few rows
        for i, row in enumerate(reader):
            if i < 3:
                player_raw = row.get('Player', '')
                player_clean = clean_player_name(player_raw)
                print(f"Row {i+1}: '{player_raw}' -> '{player_clean}'")
            else:
                break

    print(f"\n🎯 RECOMMENDATIONS:")
    print("-" * 40)
    print("1. Create a name cleaning and standardization script")
    print("2. Combine all 4 TSV files into a single cleaned dataset")
    print("3. Handle name variations (e.g., 'Carlos Alcaraz' vs 'Carlos Alcaraz Garfia')")
    print("4. Consider using fuzzy string matching for remaining unmatched players")
    print("5. Manual review may be needed for some edge cases")


if __name__ == "__main__":
    main()
