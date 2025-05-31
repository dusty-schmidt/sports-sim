#!/usr/bin/env python3
"""
Use fuzzy matching to find potential matches for Matteo Gigante
"""

import csv
import re
from pathlib import Path
from typing import List, Tuple
from difflib import SequenceMatcher


def clean_player_name(name: str) -> str:
    """Clean player name by removing URLs, brackets, and extra whitespace."""
    # Remove URL parts in parentheses
    name = re.sub(r'\(http[^)]+\)', '', name)
    
    # Remove country codes in brackets
    name = re.sub(r'\s*\[[A-Z]{2,3}\]', '', name)
    
    # Clean up whitespace
    name = name.strip()
    
    return name


def similarity_score(a: str, b: str) -> float:
    """Calculate similarity score between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def contains_name_parts(target: str, candidate: str) -> bool:
    """Check if candidate contains parts of target name."""
    target_parts = target.lower().split()
    candidate_lower = candidate.lower()
    
    # Check if all parts of target are in candidate
    all_parts_found = all(part in candidate_lower for part in target_parts)
    
    # Check if any significant part is found
    significant_parts = [part for part in target_parts if len(part) > 2]
    any_significant_found = any(part in candidate_lower for part in significant_parts)
    
    return all_parts_found or any_significant_found


def load_all_players_from_stats() -> List[Tuple[str, str]]:
    """Load all player names from stats files with their source file."""
    stats_dir = Path("data/raw/tenab_stats")
    files = ['atp.tsv', 'atp2.tsv', 'atp3.tsv', 'wta.tsv', 'wta2.tsv']
    
    all_players = []
    
    for file in files:
        file_path = stats_dir / file
        if not file_path.exists():
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                if 'Player' in row and row['Player']:
                    raw_name = row['Player']
                    clean_name = clean_player_name(raw_name)
                    if clean_name:
                        all_players.append((clean_name, file))
    
    return all_players


def find_fuzzy_matches(target: str, all_players: List[Tuple[str, str]], 
                      min_similarity: float = 0.3) -> List[Tuple[str, str, float]]:
    """Find fuzzy matches for target name."""
    matches = []
    
    for player_name, source_file in all_players:
        # Calculate similarity score
        sim_score = similarity_score(target, player_name)
        
        # Check if name parts are contained
        contains_parts = contains_name_parts(target, player_name)
        
        # Include if similarity is high enough or contains name parts
        if sim_score >= min_similarity or contains_parts:
            matches.append((player_name, source_file, sim_score))
    
    # Sort by similarity score (descending)
    matches.sort(key=lambda x: x[2], reverse=True)
    
    return matches


def search_by_parts(target: str, all_players: List[Tuple[str, str]]) -> List[Tuple[str, str, str]]:
    """Search for players containing individual parts of the target name."""
    target_parts = target.lower().split()
    part_matches = []
    
    for part in target_parts:
        if len(part) < 3:  # Skip very short parts
            continue
            
        for player_name, source_file in all_players:
            if part in player_name.lower():
                part_matches.append((player_name, source_file, part))
    
    return part_matches


def main():
    print("🔍 Fuzzy matching search for 'Matteo Gigante'")
    print("=" * 60)
    
    target_name = "Matteo Gigante"
    
    # Load all players
    print("Loading all players from stats files...")
    all_players = load_all_players_from_stats()
    print(f"Loaded {len(all_players)} total player records")
    
    # Find fuzzy matches
    print(f"\n🎯 FUZZY MATCHES for '{target_name}':")
    print("-" * 40)
    
    fuzzy_matches = find_fuzzy_matches(target_name, all_players, min_similarity=0.2)
    
    if fuzzy_matches:
        print(f"Found {len(fuzzy_matches)} potential matches:")
        for i, (player, file, score) in enumerate(fuzzy_matches[:20]):  # Show top 20
            print(f"{i+1:2d}. {player:<30} ({file}) - {score:.3f}")
    else:
        print("No fuzzy matches found")
    
    # Search by individual name parts
    print(f"\n🔍 SEARCHING BY NAME PARTS:")
    print("-" * 40)
    
    part_matches = search_by_parts(target_name, all_players)
    
    if part_matches:
        print("Players containing name parts:")
        matteo_matches = [m for m in part_matches if m[2] == 'matteo']
        gigante_matches = [m for m in part_matches if m[2] == 'gigante']
        
        if matteo_matches:
            print(f"\nPlayers with 'Matteo':")
            for player, file, part in matteo_matches:
                print(f"  - {player} ({file})")
        
        if gigante_matches:
            print(f"\nPlayers with 'Gigante':")
            for player, file, part in gigante_matches:
                print(f"  - {player} ({file})")
        
        if not matteo_matches and not gigante_matches:
            print("No players found with 'Matteo' or 'Gigante'")
    else:
        print("No matches found for individual name parts")
    
    # Search for similar Italian names
    print(f"\n🇮🇹 SEARCHING FOR ITALIAN PLAYERS (similar patterns):")
    print("-" * 40)
    
    italian_patterns = ['matteo', 'gigante', 'giga', 'matt']
    italian_matches = []
    
    for player_name, source_file in all_players:
        player_lower = player_name.lower()
        for pattern in italian_patterns:
            if pattern in player_lower:
                italian_matches.append((player_name, source_file, pattern))
    
    if italian_matches:
        print("Players matching Italian name patterns:")
        for player, file, pattern in italian_matches:
            print(f"  - {player} ({file}) - matches '{pattern}'")
    else:
        print("No Italian name patterns found")
    
    # Manual search suggestions
    print(f"\n💡 MANUAL SEARCH SUGGESTIONS:")
    print("-" * 40)
    print("Try searching for these variations:")
    print("  - Matteo (first name only)")
    print("  - Gigante (last name only)")
    print("  - M. Gigante")
    print("  - Matteo G.")
    print("  - Different spellings: Matheo, Mateo")
    print("  - Check if he might be listed under a different tournament category")
    print("  - He might not be in the top rankings covered by these files")


if __name__ == "__main__":
    main()
