#!/usr/bin/env python3
"""
Player Stats Breakdown Tool

Shows the complete pipeline of how player stats are calculated and adjusted
from raw data through all transformations to final simulation probabilities.
"""

import os
import sys
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sim_models.main_sim.simulator import FantasyTennisSimulator


class PlayerStatsBreakdown:
    """Detailed breakdown of player statistics pipeline."""
    
    def __init__(self):
        self.simulator = FantasyTennisSimulator()
        
    def analyze_player_stats_pipeline(self, player_name: str, surface: str = 'Clay') -> Dict[str, Any]:
        """Complete breakdown of how a player's stats are calculated."""
        print(f"\n🔍 COMPLETE STATS BREAKDOWN FOR: {player_name}")
        print(f"Surface: {surface}")
        print("=" * 80)
        
        breakdown = {
            'player_name': player_name,
            'surface': surface,
            'raw_data': {},
            'calculated_stats': {},
            'surface_adjusted': {},
            'match_adjusted': {},
            'calibrated_factors': {},
            'elo_data': {}
        }
        
        # 1. Raw Data from Analyzer
        print("\n📊 STEP 1: RAW DATA FROM ANALYZER")
        print("-" * 40)
        
        raw_stats = self.simulator.analyzer.player_stats.get(player_name, {})
        if raw_stats:
            print(f"Raw player data found:")
            for key, value in raw_stats.items():
                if isinstance(value, (int, float)):
                    print(f"  {key}: {value}")
                breakdown['raw_data'][key] = value
        else:
            print(f"❌ No raw data found for {player_name}")
            breakdown['raw_data'] = "No raw data found"
        
        # 2. Calculated Stats
        print("\n🧮 STEP 2: CALCULATED STATS")
        print("-" * 40)
        
        calculated_stats = self.simulator.analyzer.calculated_stats.get(player_name, {})
        if calculated_stats:
            print(f"Calculated statistics:")
            for key, value in calculated_stats.items():
                if isinstance(value, (int, float)):
                    print(f"  {key}: {value:.2f}")
                else:
                    print(f"  {key}: {value}")
                breakdown['calculated_stats'][key] = value
        else:
            print(f"❌ No calculated stats found for {player_name}")
            # Show default stats that would be used
            default_stats = {
                'ace_rate': 6.0,
                'double_fault_rate': 4.0,
                'first_serve_percentage': 60.0,
                'service_points_won': 60.0,
                'return_points_won': 40.0
            }
            print(f"Using default stats:")
            for key, value in default_stats.items():
                print(f"  {key}: {value}")
            breakdown['calculated_stats'] = default_stats
        
        # 3. Surface Adjustments
        print(f"\n🎾 STEP 3: SURFACE ADJUSTMENTS ({surface})")
        print("-" * 40)
        
        base_probs = self.simulator.get_player_probabilities(player_name, surface)
        surface_adj = self.simulator.surface_adjustments.get(surface, self.simulator.surface_adjustments['Hard'])
        
        print(f"Surface multipliers for {surface}:")
        for key, value in surface_adj.items():
            print(f"  {key}: {value}")
        
        print(f"\nSurface-adjusted probabilities:")
        for key, value in base_probs.items():
            print(f"  {key}: {value:.2f}")
        breakdown['surface_adjusted'] = base_probs
        
        # 4. Match Adjustments (with variance)
        print(f"\n🎲 STEP 4: MATCH ADJUSTMENTS (with variance)")
        print("-" * 40)
        
        match_probs = self.simulator.get_match_adjusted_probabilities(player_name, surface, use_variance=True)
        print(f"Match-adjusted probabilities (with variance):")
        for key, value in match_probs.items():
            print(f"  {key}: {value:.2f}")
            if key in base_probs:
                change = value - base_probs[key]
                print(f"    (change: {change:+.2f})")
        breakdown['match_adjusted'] = match_probs
        
        # 5. Calibrated Factors
        print(f"\n⚙️ STEP 5: CALIBRATED FACTORS")
        print("-" * 40)
        
        clutch_factor = self.simulator.analyzer.get_player_clutch_factor(player_name)
        variance_factor = self.simulator.analyzer.get_player_variance_factor(player_name)
        rally_factor = self.simulator.analyzer.get_player_rally_factor(player_name)
        
        print(f"Calibrated factors:")
        print(f"  clutch_factor: {clutch_factor:.3f}")
        print(f"  variance_factor: {variance_factor:.3f}")
        print(f"  rally_factor: {rally_factor:.3f}")
        
        breakdown['calibrated_factors'] = {
            'clutch_factor': clutch_factor,
            'variance_factor': variance_factor,
            'rally_factor': rally_factor
        }
        
        # 6. ELO Data
        print(f"\n🏆 STEP 6: ELO RATINGS")
        print("-" * 40)
        
        surface_elo = self.simulator.analyzer.get_player_elo(player_name, surface)
        overall_elo = self.simulator.analyzer.get_player_elo(player_name)
        
        print(f"ELO ratings:")
        print(f"  {surface} ELO: {surface_elo}")
        print(f"  Overall ELO: {overall_elo}")
        
        breakdown['elo_data'] = {
            'surface_elo': surface_elo,
            'overall_elo': overall_elo
        }
        
        return breakdown
    
    def compare_players_head_to_head(self, player1: str, player2: str, surface: str = 'Clay') -> Dict[str, Any]:
        """Compare two players head-to-head with complete breakdown."""
        print(f"\n⚔️ HEAD-TO-HEAD COMPARISON")
        print(f"{player1} vs {player2} on {surface}")
        print("=" * 80)
        
        # Get breakdowns for both players
        p1_breakdown = self.analyze_player_stats_pipeline(player1, surface)
        p2_breakdown = self.analyze_player_stats_pipeline(player2, surface)
        
        # Calculate ELO win probability
        print(f"\n🎯 ELO WIN PROBABILITY CALCULATION")
        print("-" * 40)
        
        elo_win_prob = self.simulator.calculate_elo_win_probability(player1, player2, surface)
        p1_elo = self.simulator.analyzer.get_player_elo(player1, surface)
        p2_elo = self.simulator.analyzer.get_player_elo(player2, surface)
        
        if p1_elo and p2_elo:
            elo_diff = p1_elo - p2_elo
            print(f"ELO difference: {elo_diff:.0f} ({player1}: {p1_elo}, {player2}: {p2_elo})")
            print(f"Theoretical win probability for {player1}: {elo_win_prob:.1%}")
        else:
            print(f"Missing ELO data - using 50/50")
        
        # Simulate a point to show the complete calculation
        print(f"\n🎾 POINT SIMULATION BREAKDOWN")
        print("-" * 40)
        
        # Get match-adjusted probabilities
        p1_probs = self.simulator.get_match_adjusted_probabilities(player1, surface, use_variance=True)
        p2_probs = self.simulator.get_match_adjusted_probabilities(player2, surface, use_variance=True)
        
        print(f"\nService strength comparison:")
        print(f"  {player1} service points won: {p1_probs['service_points_won']:.1f}%")
        print(f"  {player2} return points won: {p2_probs['return_points_won']:.1f}%")
        
        # Calculate stats-based probability
        server_strength = p1_probs['service_points_won']
        returner_strength = p2_probs['return_points_won']
        total_strength = server_strength + returner_strength
        stats_server_prob = server_strength / total_strength if total_strength > 0 else 0.5
        
        print(f"\nStats-based probability calculation:")
        print(f"  Total strength: {total_strength:.1f}")
        print(f"  Stats-based {player1} win prob: {stats_server_prob:.1%}")
        
        # Show the final blended calculation
        elo_weight = 0.25
        stats_weight = 0.75
        random_factor = 0.2
        pure_random = 0.5
        adjusted_stats_weight = stats_weight - random_factor
        
        final_prob = (elo_weight * elo_win_prob) + (adjusted_stats_weight * stats_server_prob) + (random_factor * pure_random)
        
        print(f"\nFinal blended probability calculation:")
        print(f"  ELO component (25%): {elo_weight * elo_win_prob:.3f}")
        print(f"  Stats component (55%): {adjusted_stats_weight * stats_server_prob:.3f}")
        print(f"  Random component (20%): {random_factor * pure_random:.3f}")
        print(f"  Final {player1} win probability: {final_prob:.1%}")
        
        return {
            'player1_breakdown': p1_breakdown,
            'player2_breakdown': p2_breakdown,
            'elo_win_prob': elo_win_prob,
            'stats_win_prob': stats_server_prob,
            'final_win_prob': final_prob,
            'probability_components': {
                'elo_component': elo_weight * elo_win_prob,
                'stats_component': adjusted_stats_weight * stats_server_prob,
                'random_component': random_factor * pure_random
            }
        }


def analyze_slate_players():
    """Analyze all players from the slate."""
    print("🎾 TENNIS PLAYER STATS BREAKDOWN")
    print("=" * 80)
    
    # Load slate data
    slate_file = Path("data/draftgroup_128447_clean.json")
    if not slate_file.exists():
        print(f"❌ Slate file not found: {slate_file}")
        return
    
    with open(slate_file, 'r') as f:
        slate_data = json.load(f)
    
    analyzer = PlayerStatsBreakdown()
    
    # Get unique players
    players = list(set([p['name'] for p in slate_data['players']]))
    surface = slate_data.get('surface', 'Clay')
    
    print(f"📊 Analyzing {len(players)} players on {surface}")
    
    # Analyze a few key players in detail
    key_players = ['Carlos Alcaraz', 'Damir Dzumhur', 'Frances Tiafoe', 'Sebastian Korda']
    
    for player in key_players:
        if player in players:
            analyzer.analyze_player_stats_pipeline(player, surface)
    
    # Show head-to-head comparison
    print(f"\n" + "=" * 80)
    analyzer.compare_players_head_to_head('Carlos Alcaraz', 'Damir Dzumhur', surface)
    
    print(f"\n" + "=" * 80)
    analyzer.compare_players_head_to_head('Frances Tiafoe', 'Sebastian Korda', surface)


if __name__ == "__main__":
    analyze_slate_players()
