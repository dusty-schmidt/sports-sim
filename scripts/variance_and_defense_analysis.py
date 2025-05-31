#!/usr/bin/env python3
"""
Variance and Defense Analysis

Analyzes how variance is applied and how defensive ability is calculated.
"""

import os
import sys
import numpy as np
from pathlib import Path

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sim_models.main_sim.simulator import FantasyTennisSimulator


def analyze_variance_application():
    """Analyze how variance is applied before and during matches."""
    print("🎲 VARIANCE APPLICATION ANALYSIS")
    print("=" * 80)
    
    simulator = FantasyTennisSimulator()
    
    print("📊 STEP 1: PRE-MATCH VARIANCE APPLICATION")
    print("-" * 60)
    
    # Get base stats without variance
    alcaraz_base = simulator.get_player_probabilities("Carlos Alcaraz", "Clay")
    dzumhur_base = simulator.get_player_probabilities("Damir Dzumhur", "Clay")
    
    print("Base surface-weighted stats (no variance):")
    print(f"Carlos Alcaraz:")
    for key, value in alcaraz_base.items():
        print(f"  {key}: {value:.2f}%")
    
    print(f"\nDamir Dzumhur:")
    for key, value in dzumhur_base.items():
        print(f"  {key}: {value:.2f}%")
    
    print(f"\n🎯 STEP 2: MATCH-ADJUSTED VARIANCE SAMPLES")
    print("-" * 60)
    
    print("Showing 10 variance samples for each player:")
    print(f"{'Sample':<8} {'Alcaraz Service':<15} {'Alcaraz Return':<15} {'Dzumhur Service':<15} {'Dzumhur Return':<15}")
    print("-" * 75)
    
    np.random.seed(42)  # For reproducible results
    for i in range(10):
        alcaraz_varied = simulator.get_match_adjusted_probabilities("Carlos Alcaraz", "Clay", use_variance=True)
        dzumhur_varied = simulator.get_match_adjusted_probabilities("Damir Dzumhur", "Clay", use_variance=True)
        
        print(f"{i+1:<8} {alcaraz_varied['service_points_won']:<15.1f} {alcaraz_varied['return_points_won']:<15.1f} "
              f"{dzumhur_varied['service_points_won']:<15.1f} {dzumhur_varied['return_points_won']:<15.1f}")
    
    print(f"\n📈 STEP 3: VARIANCE RANGE ANALYSIS")
    print("-" * 60)
    
    # Collect 100 samples to analyze variance range
    alcaraz_service_samples = []
    alcaraz_return_samples = []
    dzumhur_service_samples = []
    dzumhur_return_samples = []
    
    for _ in range(100):
        alcaraz_varied = simulator.get_match_adjusted_probabilities("Carlos Alcaraz", "Clay", use_variance=True)
        dzumhur_varied = simulator.get_match_adjusted_probabilities("Damir Dzumhur", "Clay", use_variance=True)
        
        alcaraz_service_samples.append(alcaraz_varied['service_points_won'])
        alcaraz_return_samples.append(alcaraz_varied['return_points_won'])
        dzumhur_service_samples.append(dzumhur_varied['service_points_won'])
        dzumhur_return_samples.append(dzumhur_varied['return_points_won'])
    
    print("Variance ranges (100 samples):")
    print(f"Carlos Alcaraz:")
    print(f"  Service: {np.min(alcaraz_service_samples):.1f}% - {np.max(alcaraz_service_samples):.1f}% "
          f"(base: {alcaraz_base['service_points_won']:.1f}%, range: ±{(np.max(alcaraz_service_samples) - np.min(alcaraz_service_samples))/2:.1f}%)")
    print(f"  Return:  {np.min(alcaraz_return_samples):.1f}% - {np.max(alcaraz_return_samples):.1f}% "
          f"(base: {alcaraz_base['return_points_won']:.1f}%, range: ±{(np.max(alcaraz_return_samples) - np.min(alcaraz_return_samples))/2:.1f}%)")
    
    print(f"\nDamir Dzumhur:")
    print(f"  Service: {np.min(dzumhur_service_samples):.1f}% - {np.max(dzumhur_service_samples):.1f}% "
          f"(base: {dzumhur_base['service_points_won']:.1f}%, range: ±{(np.max(dzumhur_service_samples) - np.min(dzumhur_service_samples))/2:.1f}%)")
    print(f"  Return:  {np.min(dzumhur_return_samples):.1f}% - {np.max(dzumhur_return_samples):.1f}% "
          f"(base: {dzumhur_base['return_points_won']:.1f}%, range: ±{(np.max(dzumhur_return_samples) - np.min(dzumhur_return_samples))/2:.1f}%)")


def analyze_defensive_ability():
    """Analyze how defensive ability (return game) is calculated."""
    print(f"\n🛡️ DEFENSIVE ABILITY ANALYSIS")
    print("=" * 80)
    
    simulator = FantasyTennisSimulator()
    
    print("📊 STEP 1: RETURN GAME STATS")
    print("-" * 60)
    
    # Get surface-weighted stats
    alcaraz_stats = simulator.analyzer.get_player_stats("Carlos Alcaraz", "Clay")
    dzumhur_stats = simulator.analyzer.get_player_stats("Damir Dzumhur", "Clay")
    
    print("Surface-weighted return abilities:")
    print(f"Carlos Alcaraz return_points_won: {alcaraz_stats['return_points_won']:.1f}%")
    print(f"Damir Dzumhur return_points_won: {dzumhur_stats['return_points_won']:.1f}%")
    
    print(f"\n🎾 STEP 2: POINT-BY-POINT INTERACTION")
    print("-" * 60)
    
    # Show how service vs return works in point simulation
    alcaraz_probs = simulator.get_match_adjusted_probabilities("Carlos Alcaraz", "Clay", use_variance=False)
    dzumhur_probs = simulator.get_match_adjusted_probabilities("Damir Dzumhur", "Clay", use_variance=False)
    
    print("When Alcaraz serves vs Dzumhur returns:")
    server_strength = alcaraz_probs['service_points_won']
    returner_strength = dzumhur_probs['return_points_won']
    total_strength = server_strength + returner_strength
    alcaraz_win_prob = server_strength / total_strength
    
    print(f"  Alcaraz service strength: {server_strength:.1f}%")
    print(f"  Dzumhur return strength: {returner_strength:.1f}%")
    print(f"  Total strength: {total_strength:.1f}")
    print(f"  Alcaraz point win probability: {alcaraz_win_prob:.1%}")
    
    print(f"\nWhen Dzumhur serves vs Alcaraz returns:")
    server_strength = dzumhur_probs['service_points_won']
    returner_strength = alcaraz_probs['return_points_won']
    total_strength = server_strength + returner_strength
    dzumhur_win_prob = server_strength / total_strength
    
    print(f"  Dzumhur service strength: {server_strength:.1f}%")
    print(f"  Alcaraz return strength: {returner_strength:.1f}%")
    print(f"  Total strength: {total_strength:.1f}")
    print(f"  Dzumhur point win probability: {dzumhur_win_prob:.1%}")
    
    print(f"\n⚖️ STEP 3: DEFENSIVE IMPACT ANALYSIS")
    print("-" * 60)
    
    # Calculate how much defense matters
    alcaraz_return_advantage = alcaraz_stats['return_points_won'] - dzumhur_stats['return_points_won']
    print(f"Alcaraz return advantage: +{alcaraz_return_advantage:.1f} percentage points")
    
    # Show impact on break chances
    print(f"\nBreak point scenarios:")
    print(f"  Alcaraz breaking Dzumhur: {1 - dzumhur_win_prob:.1%} chance per point")
    print(f"  Dzumhur breaking Alcaraz: {1 - alcaraz_win_prob:.1%} chance per point")
    
    break_differential = (1 - dzumhur_win_prob) - (1 - alcaraz_win_prob)
    print(f"  Break advantage for Alcaraz: +{break_differential:.1%} per point")


def analyze_in_match_variance():
    """Analyze how variance is applied during the match."""
    print(f"\n🔄 IN-MATCH VARIANCE ANALYSIS")
    print("=" * 80)
    
    simulator = FantasyTennisSimulator()
    
    print("📊 STEP 1: VARIANCE TIMING")
    print("-" * 60)
    print("Current variance application:")
    print("  1. PRE-MATCH: Variance applied once at match start")
    print("  2. DURING MATCH: Same varied stats used throughout")
    print("  3. NO POINT-BY-POINT: No additional variance per point")
    print("  4. NO SET-BY-SET: No variance changes between sets")
    
    print(f"\n⚠️ STEP 2: POTENTIAL ISSUES")
    print("-" * 60)
    print("Current system may be too predictable because:")
    print("  • Variance is 'locked in' at match start")
    print("  • No momentum swings during match")
    print("  • No fatigue/pressure effects on variance")
    print("  • Elite players get consistent 'good day' advantage")
    
    print(f"\n💡 STEP 3: IMPROVEMENT SUGGESTIONS")
    print("-" * 60)
    print("To make Alcaraz less dominant:")
    print("  1. INCREASE VARIANCE: ±12-15% instead of ±8%")
    print("  2. SET-BY-SET VARIANCE: Re-roll variance each set")
    print("  3. MOMENTUM EFFECTS: Losing player gets variance boost")
    print("  4. PRESSURE VARIANCE: Higher variance in crucial moments")
    print("  5. DEFENSIVE BOOST: Increase return game impact")


if __name__ == "__main__":
    analyze_variance_application()
    analyze_defensive_ability()
    analyze_in_match_variance()
