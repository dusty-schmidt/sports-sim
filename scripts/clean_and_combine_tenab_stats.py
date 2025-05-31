#!/usr/bin/env python3
"""
Clean and combine tenab_stats files into a single dataset
"""

import json
import csv
import re
import pandas as pd
from pathlib import Path
from typing import Dict, List, Set


def clean_player_name(name: str) -> str:
    """Clean player name by removing URLs, brackets, and extra whitespace."""
    # Remove URL parts in parentheses
    name = re.sub(r'\(http[^)]+\)', '', name)
    
    # Remove country codes in brackets
    name = re.sub(r'\s*\[[A-Z]{2,3}\]', '', name)
    
    # Clean up whitespace
    name = name.strip()
    
    return name


def extract_country_code(name: str) -> str:
    """Extract country code from player name."""
    match = re.search(r'\[([A-Z]{2,3})\]', name)
    return match.group(1) if match else ''


def determine_gender(filename: str) -> str:
    """Determine gender based on filename."""
    return 'W' if 'wta' in filename.lower() else 'M'


def clean_numeric_value(value: str) -> float:
    """Clean and convert numeric values, handling percentages."""
    if not value or value == '':
        return None
    
    # Remove percentage signs
    value = value.replace('%', '')
    
    try:
        return float(value)
    except ValueError:
        return None


def process_stats_file(file_path: Path) -> List[Dict]:
    """Process a single stats file and return cleaned data."""
    print(f"Processing {file_path.name}...")
    
    gender = determine_gender(file_path.name)
    players = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        
        for row in reader:
            if not row.get('Player'):
                continue
                
            # Clean player name and extract country
            raw_name = row['Player']
            clean_name = clean_player_name(raw_name)
            country = extract_country_code(raw_name)
            
            if not clean_name:
                continue
            
            # Create cleaned player record
            player_data = {
                'name': clean_name,
                'country': country,
                'gender': gender,
                'source_file': file_path.name,
                'rank': int(row.get('Rk', 0)) if row.get('Rk', '').isdigit() else None,
                
                # Match statistics
                'matches': int(row.get('M', 0)) if row.get('M', '').isdigit() else None,
                'match_win_pct': clean_numeric_value(row.get('M W%', '')),
                
                # Service statistics
                'service_points_won_pct': clean_numeric_value(row.get('SPW', '')),
                'aces': int(row.get('Aces', 0)) if row.get('Aces', '').isdigit() else None,
                'ace_pct': clean_numeric_value(row.get('Ace%', '')),
                'double_faults': int(row.get('DFs', 0)) if row.get('DFs', '').isdigit() else None,
                'double_fault_pct': clean_numeric_value(row.get('DF%', '')),
                'first_serve_in_pct': clean_numeric_value(row.get('1stIn', '')),
                'first_serve_win_pct': clean_numeric_value(row.get('1st%', '')),
                'second_serve_win_pct': clean_numeric_value(row.get('2nd%', '')),
                'hold_pct': clean_numeric_value(row.get('Hld%', '')),
                
                # Additional stats
                'points_per_service_game': clean_numeric_value(row.get('Pts/SG', '')),
                'points_lost_per_service_game': clean_numeric_value(row.get('PtsL/SG', ''))
            }
            
            players.append(player_data)
    
    print(f"   Processed {len(players)} players from {file_path.name}")
    return players


def combine_duplicate_players(all_players: List[Dict]) -> List[Dict]:
    """Combine data for players that appear in multiple files."""
    player_dict = {}
    
    for player in all_players:
        name = player['name']
        
        if name not in player_dict:
            player_dict[name] = player.copy()
            player_dict[name]['source_files'] = [player['source_file']]
        else:
            # Player exists, combine data
            existing = player_dict[name]
            
            # Add source file
            existing['source_files'].append(player['source_file'])
            
            # For numeric fields, take the average if both exist
            numeric_fields = [
                'matches', 'match_win_pct', 'service_points_won_pct', 'aces', 'ace_pct',
                'double_faults', 'double_fault_pct', 'first_serve_in_pct', 
                'first_serve_win_pct', 'second_serve_win_pct', 'hold_pct',
                'points_per_service_game', 'points_lost_per_service_game'
            ]
            
            for field in numeric_fields:
                existing_val = existing.get(field)
                new_val = player.get(field)
                
                if existing_val is not None and new_val is not None:
                    # Average the values
                    existing[field] = (existing_val + new_val) / 2
                elif new_val is not None and existing_val is None:
                    # Use new value if existing is None
                    existing[field] = new_val
            
            # Take the better rank (lower number)
            if player.get('rank') and existing.get('rank'):
                existing['rank'] = min(existing['rank'], player['rank'])
            elif player.get('rank') and not existing.get('rank'):
                existing['rank'] = player['rank']
    
    # Convert back to list and clean up
    combined_players = []
    for name, player in player_dict.items():
        # Convert source_files list to string
        player['source_files'] = ', '.join(player['source_files'])
        combined_players.append(player)
    
    return combined_players


def main():
    print("🧹 Cleaning and combining tenab_stats files")
    print("=" * 60)
    
    # Process all stats files
    stats_dir = Path("data/raw/tenab_stats")
    files = ['atp.tsv', 'atp2.tsv', 'wta.tsv', 'wta2.tsv']
    
    all_players = []
    for file in files:
        file_path = stats_dir / file
        if file_path.exists():
            players = process_stats_file(file_path)
            all_players.extend(players)
    
    print(f"\n📊 Initial totals:")
    print(f"   Total player records: {len(all_players)}")
    
    # Combine duplicate players
    print(f"\n🔄 Combining duplicate players...")
    combined_players = combine_duplicate_players(all_players)
    
    print(f"   Unique players after combining: {len(combined_players)}")
    
    # Sort by rank (nulls last)
    combined_players.sort(key=lambda x: (x['rank'] is None, x['rank'] or 999, x['name']))
    
    # Save to JSON
    output_file = Path("data/processed/tenab_combined_stats.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(combined_players, f, indent=2)
    
    print(f"✅ Saved combined stats to: {output_file}")
    
    # Save to CSV as well
    csv_file = Path("data/processed/tenab_combined_stats.csv")
    df = pd.DataFrame(combined_players)
    df.to_csv(csv_file, index=False)
    
    print(f"✅ Saved combined stats to: {csv_file}")
    
    # Show summary statistics
    print(f"\n📈 Summary:")
    print(f"   Total unique players: {len(combined_players)}")
    print(f"   Men (ATP): {len([p for p in combined_players if p['gender'] == 'M'])}")
    print(f"   Women (WTA): {len([p for p in combined_players if p['gender'] == 'W'])}")
    
    # Show top 10 players by rank
    print(f"\n🏆 Top 10 players by rank:")
    for i, player in enumerate(combined_players[:10]):
        rank = player.get('rank', 'N/A')
        name = player['name']
        gender = player['gender']
        win_pct = player.get('match_win_pct', 0)
        print(f"   {i+1:2d}. #{rank:3} {name} ({gender}) - {win_pct:.1f}% wins")


if __name__ == "__main__":
    main()
