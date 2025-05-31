#!/usr/bin/env python3
"""
Surface-Weighted Player Stats Calculator

Calculates surface-specific player stats by heavily weighting matches on the target surface.
For clay court matches, this will weight clay court performance much more heavily than overall stats.
"""

import os
import sys
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Any
from collections import defaultdict

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


class SurfaceWeightedStatsCalculator:
    """Calculate surface-weighted player statistics."""
    
    def __init__(self):
        self.raw_matches = None
        self.baseline_stats = None
        self.load_data()
    
    def load_data(self):
        """Load raw match data and baseline stats."""
        # Load baseline calculated stats
        baseline_file = Path("data/exploratory/calculated_player_stats.json")
        if baseline_file.exists():
            with open(baseline_file, 'r') as f:
                self.baseline_stats = json.load(f)
            print(f"✅ Loaded baseline stats for {len(self.baseline_stats)} players")
        
        # Load raw match data
        matches_file = Path("data/tmcp/charting-m-matches.csv")
        if matches_file.exists():
            self.raw_matches = pd.read_csv(matches_file)
            print(f"✅ Loaded {len(self.raw_matches)} raw matches")
        else:
            print("❌ Raw match data not found")
    
    def get_player_surface_matches(self, player_name: str, surface: str) -> List[str]:
        """Get all match IDs for a player on a specific surface."""
        if self.raw_matches is None:
            return []
        
        # Find matches where player appears and surface matches
        player_matches = self.raw_matches[
            ((self.raw_matches['Player 1'] == player_name) | 
             (self.raw_matches['Player 2'] == player_name)) &
            (self.raw_matches['Surface'] == surface)
        ]
        
        return player_matches['match_id'].tolist()
    
    def calculate_surface_weighted_stats(self, player_name: str, target_surface: str, 
                                       surface_weight: float = 0.7) -> Dict[str, float]:
        """
        Calculate surface-weighted stats for a player.
        
        Args:
            player_name: Name of the player
            target_surface: Surface for the upcoming match (Clay, Hard, Grass)
            surface_weight: Weight given to surface-specific performance (0.7 = 70% surface, 30% overall)
        
        Returns:
            Dictionary of weighted stats
        """
        print(f"\n🎾 CALCULATING SURFACE-WEIGHTED STATS")
        print(f"Player: {player_name}")
        print(f"Target Surface: {target_surface}")
        print(f"Surface Weight: {surface_weight:.1%}")
        print("-" * 60)
        
        # Get baseline stats (all surfaces)
        if player_name not in self.baseline_stats:
            print(f"❌ No baseline stats found for {player_name}")
            return self._get_default_stats()
        
        baseline = self.baseline_stats[player_name]
        
        # Get surface-specific match count
        surface_matches = self.get_player_surface_matches(player_name, target_surface)
        total_matches = baseline['matches']
        surface_match_count = len(surface_matches)
        
        print(f"📊 Match Distribution:")
        print(f"  Total matches: {total_matches}")
        print(f"  {target_surface} matches: {surface_match_count}")
        print(f"  {target_surface} percentage: {surface_match_count/total_matches:.1%}")
        
        # Calculate surface preferences from baseline data
        surface_prefs = baseline.get('surface_preferences', {})
        surface_pref_pct = surface_prefs.get(target_surface, 0.33)  # Default to 33% if missing
        
        print(f"  Expected {target_surface} percentage: {surface_pref_pct:.1%}")
        
        # If we have very few surface matches, reduce surface weighting
        if surface_match_count < 5:
            adjusted_surface_weight = min(surface_weight, 0.3)  # Cap at 30% if <5 matches
            print(f"⚠️  Low surface match count, reducing weight to {adjusted_surface_weight:.1%}")
        elif surface_match_count < 10:
            adjusted_surface_weight = min(surface_weight, 0.5)  # Cap at 50% if <10 matches
            print(f"⚠️  Moderate surface match count, reducing weight to {adjusted_surface_weight:.1%}")
        else:
            adjusted_surface_weight = surface_weight
        
        # For now, we'll use the baseline stats with surface adjustments
        # In a full implementation, we'd calculate actual surface-specific stats from raw data
        weighted_stats = self._apply_surface_weighting(
            baseline, target_surface, adjusted_surface_weight, surface_match_count, total_matches
        )
        
        print(f"\n📈 SURFACE-WEIGHTED RESULTS:")
        for key, value in weighted_stats.items():
            if key in ['ace_rate', 'double_fault_rate', 'service_points_won', 'return_points_won']:
                baseline_val = baseline[key]
                change = value - baseline_val
                print(f"  {key}: {baseline_val:.1f}% → {value:.1f}% ({change:+.1f}%)")
        
        return weighted_stats
    
    def _apply_surface_weighting(self, baseline: Dict, surface: str, surface_weight: float,
                               surface_matches: int, total_matches: int) -> Dict[str, float]:
        """Apply surface-specific adjustments to baseline stats."""
        
        # Surface-specific adjustments based on tennis knowledge
        surface_adjustments = {
            'Clay': {
                'ace_rate_multiplier': 0.85,      # Fewer aces on clay
                'double_fault_multiplier': 1.1,   # Slightly more DFs on clay
                'service_points_multiplier': 0.98, # Slightly lower service dominance
                'return_points_multiplier': 1.02,  # Slightly better return opportunities
            },
            'Hard': {
                'ace_rate_multiplier': 1.0,       # Baseline
                'double_fault_multiplier': 1.0,   # Baseline
                'service_points_multiplier': 1.0, # Baseline
                'return_points_multiplier': 1.0,  # Baseline
            },
            'Grass': {
                'ace_rate_multiplier': 1.15,      # More aces on grass
                'double_fault_multiplier': 0.9,   # Fewer DFs on grass
                'service_points_multiplier': 1.05, # Higher service dominance
                'return_points_multiplier': 0.95,  # Harder to return
            }
        }
        
        adjustments = surface_adjustments.get(surface, surface_adjustments['Hard'])
        
        # Calculate weighted stats
        weighted_stats = baseline.copy()
        
        # Apply surface weighting: surface_weight * surface_adjusted + (1-surface_weight) * baseline
        for stat in ['ace_rate', 'double_fault_rate', 'service_points_won', 'return_points_won']:
            baseline_val = baseline[stat]
            
            # Get the appropriate multiplier
            if stat == 'ace_rate':
                multiplier = adjustments['ace_rate_multiplier']
            elif stat == 'double_fault_rate':
                multiplier = adjustments['double_fault_multiplier']
            elif stat == 'service_points_won':
                multiplier = adjustments['service_points_multiplier']
            elif stat == 'return_points_won':
                multiplier = adjustments['return_points_multiplier']
            else:
                multiplier = 1.0
            
            # Calculate surface-adjusted value
            surface_adjusted_val = baseline_val * multiplier
            
            # Apply weighting: surface_weight * surface_specific + (1-surface_weight) * baseline
            weighted_val = (surface_weight * surface_adjusted_val) + ((1 - surface_weight) * baseline_val)
            
            weighted_stats[stat] = weighted_val
        
        return weighted_stats
    
    def _get_default_stats(self) -> Dict[str, float]:
        """Return default stats if player not found."""
        return {
            'ace_rate': 6.0,
            'double_fault_rate': 4.0,
            'first_serve_percentage': 60.0,
            'service_points_won': 60.0,
            'return_points_won': 40.0,
            'matches': 0,
            'rank': 500,
            'gender': 'M',
            'rank_tier': 5
        }
    
    def compare_baseline_vs_surface_weighted(self, player_name: str, surface: str) -> None:
        """Compare baseline stats vs surface-weighted stats."""
        print(f"\n🔍 BASELINE vs SURFACE-WEIGHTED COMPARISON")
        print(f"Player: {player_name}, Surface: {surface}")
        print("=" * 80)
        
        # Get baseline stats
        baseline = self.baseline_stats.get(player_name, self._get_default_stats())
        
        # Get surface-weighted stats
        surface_weighted = self.calculate_surface_weighted_stats(player_name, surface, 0.7)
        
        print(f"\n📊 COMPARISON TABLE:")
        print(f"{'Stat':<25} {'Baseline':<12} {'Surface-Weighted':<18} {'Change':<10}")
        print("-" * 70)
        
        for stat in ['ace_rate', 'double_fault_rate', 'service_points_won', 'return_points_won']:
            baseline_val = baseline[stat]
            weighted_val = surface_weighted[stat]
            change = weighted_val - baseline_val
            
            print(f"{stat:<25} {baseline_val:<12.1f} {weighted_val:<18.1f} {change:+.1f}")


def analyze_alcaraz_surface_weighting():
    """Analyze Carlos Alcaraz with surface weighting for clay court match."""
    calculator = SurfaceWeightedStatsCalculator()
    
    print("🎾 CARLOS ALCARAZ SURFACE-WEIGHTED ANALYSIS")
    print("=" * 80)
    
    # Compare different surface weightings
    surface_weights = [0.5, 0.7, 0.9]  # 50%, 70%, 90% surface weighting
    
    for weight in surface_weights:
        print(f"\n{'='*20} SURFACE WEIGHT: {weight:.0%} {'='*20}")
        stats = calculator.calculate_surface_weighted_stats("Carlos Alcaraz", "Clay", weight)
    
    # Show detailed comparison
    calculator.compare_baseline_vs_surface_weighted("Carlos Alcaraz", "Clay")
    
    # Also analyze Damir Dzumhur for comparison
    print(f"\n\n🎾 DAMIR DZUMHUR SURFACE-WEIGHTED ANALYSIS")
    print("=" * 80)
    calculator.compare_baseline_vs_surface_weighted("Damir Dzumhur", "Clay")


if __name__ == "__main__":
    analyze_alcaraz_surface_weighting()
