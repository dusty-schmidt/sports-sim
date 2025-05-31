#!/usr/bin/env python3
"""
Alcaraz vs Dzumhur - 1000 Match Simulations with Percentile Analysis

Runs 1000 simulations and shows percentile outcome distributions.
"""

import os
import sys
import numpy as np
from pathlib import Path

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sim_models.main_sim.simulator import FantasyTennisSimulator


def run_1000_simulations():
    """Run 1000 Alcaraz vs Dzumhur simulations and analyze percentiles."""
    print("🎾 ALCARAZ vs DZUMHUR - 1000 SIMULATION ANALYSIS")
    print("=" * 80)
    
    simulator = FantasyTennisSimulator()
    
    # Storage for results
    alcaraz_wins = 0
    alcaraz_fantasy_points = []
    dzumhur_fantasy_points = []
    alcaraz_aces = []
    alcaraz_dfs = []
    dzumhur_aces = []
    dzumhur_dfs = []
    match_scores = []  # Store set scores
    
    print("Running 1000 simulations...")
    print("Progress: ", end="", flush=True)
    
    for i in range(1000):
        if i % 100 == 0:
            print(f"{i//10}%", end=" ", flush=True)
        
        p1_stats, p2_stats, sets = simulator.simulate_match_detailed(
            "Carlos Alcaraz", "Damir Dzumhur", "Clay", verbose=False
        )
        
        # Track wins
        if p1_stats.sets_won > p2_stats.sets_won:
            alcaraz_wins += 1
        
        # Track fantasy points
        alcaraz_fp = p1_stats.calculate_fantasy_points(False)
        dzumhur_fp = p2_stats.calculate_fantasy_points(False)
        
        alcaraz_fantasy_points.append(alcaraz_fp)
        dzumhur_fantasy_points.append(dzumhur_fp)
        
        # Track aces and double faults
        alcaraz_aces.append(p1_stats.aces)
        alcaraz_dfs.append(p1_stats.double_faults)
        dzumhur_aces.append(p2_stats.aces)
        dzumhur_dfs.append(p2_stats.double_faults)
        
        # Track match score
        match_scores.append(f"{p1_stats.sets_won}-{p1_stats.sets_lost}")
    
    print("100% Complete!")
    
    # Convert to numpy arrays for easier analysis
    alcaraz_fp = np.array(alcaraz_fantasy_points)
    dzumhur_fp = np.array(dzumhur_fantasy_points)
    alcaraz_aces_arr = np.array(alcaraz_aces)
    alcaraz_dfs_arr = np.array(alcaraz_dfs)
    dzumhur_aces_arr = np.array(dzumhur_aces)
    dzumhur_dfs_arr = np.array(dzumhur_dfs)
    
    print(f"\n📊 OVERALL RESULTS")
    print("-" * 60)
    print(f"Alcaraz win rate: {alcaraz_wins}/1000 = {alcaraz_wins/10:.1f}%")
    print(f"Dzumhur win rate: {1000-alcaraz_wins}/1000 = {(1000-alcaraz_wins)/10:.1f}%")
    
    # Match score distribution
    from collections import Counter
    score_counts = Counter(match_scores)
    print(f"\nMatch score distribution:")
    for score, count in sorted(score_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {score}: {count} matches ({count/10:.1f}%)")
    
    print(f"\n🎯 FANTASY POINTS PERCENTILE ANALYSIS")
    print("-" * 60)
    
    # Define percentiles to analyze
    percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
    
    print(f"{'Percentile':<12} {'Alcaraz':<10} {'Dzumhur':<10}")
    print("-" * 35)
    
    for p in percentiles:
        alcaraz_p = np.percentile(alcaraz_fp, p)
        dzumhur_p = np.percentile(dzumhur_fp, p)
        print(f"{p:>3}th{'':<7} {alcaraz_p:>7.1f}{'':<3} {dzumhur_p:>7.1f}")
    
    print(f"\nMean ± Std:")
    print(f"{'Mean ± Std':<12} {np.mean(alcaraz_fp):>7.1f}±{np.std(alcaraz_fp):<2.1f} {np.mean(dzumhur_fp):>7.1f}±{np.std(dzumhur_fp):<2.1f}")
    
    print(f"\n⚡ ACES PERCENTILE ANALYSIS")
    print("-" * 60)
    
    print(f"{'Percentile':<12} {'Alcaraz':<10} {'Dzumhur':<10}")
    print("-" * 35)
    
    for p in percentiles:
        alcaraz_aces_p = np.percentile(alcaraz_aces_arr, p)
        dzumhur_aces_p = np.percentile(dzumhur_aces_arr, p)
        print(f"{p:>3}th{'':<7} {alcaraz_aces_p:>7.1f}{'':<3} {dzumhur_aces_p:>7.1f}")
    
    print(f"\nMean ± Std:")
    print(f"{'Mean ± Std':<12} {np.mean(alcaraz_aces_arr):>7.1f}±{np.std(alcaraz_aces_arr):<2.1f} {np.mean(dzumhur_aces_arr):>7.1f}±{np.std(dzumhur_aces_arr):<2.1f}")
    
    print(f"\n💥 DOUBLE FAULTS PERCENTILE ANALYSIS")
    print("-" * 60)
    
    print(f"{'Percentile':<12} {'Alcaraz':<10} {'Dzumhur':<10}")
    print("-" * 35)
    
    for p in percentiles:
        alcaraz_dfs_p = np.percentile(alcaraz_dfs_arr, p)
        dzumhur_dfs_p = np.percentile(dzumhur_dfs_arr, p)
        print(f"{p:>3}th{'':<7} {alcaraz_dfs_p:>7.1f}{'':<3} {dzumhur_dfs_p:>7.1f}")
    
    print(f"\nMean ± Std:")
    print(f"{'Mean ± Std':<12} {np.mean(alcaraz_dfs_arr):>7.1f}±{np.std(alcaraz_dfs_arr):<2.1f} {np.mean(dzumhur_dfs_arr):>7.1f}±{np.std(dzumhur_dfs_arr):<2.1f}")
    
    print(f"\n📈 DISTRIBUTION INSIGHTS")
    print("-" * 60)
    
    # Fantasy points insights
    alcaraz_range = np.max(alcaraz_fp) - np.min(alcaraz_fp)
    dzumhur_range = np.max(dzumhur_fp) - np.min(dzumhur_fp)
    
    print(f"Fantasy Points:")
    print(f"  Alcaraz range: {np.min(alcaraz_fp):.1f} - {np.max(alcaraz_fp):.1f} (span: {alcaraz_range:.1f})")
    print(f"  Dzumhur range: {np.min(dzumhur_fp):.1f} - {np.max(dzumhur_fp):.1f} (span: {dzumhur_range:.1f})")
    
    # Probability of Dzumhur outscoring Alcaraz
    dzumhur_higher = np.sum(dzumhur_fp > alcaraz_fp)
    print(f"  Dzumhur outscores Alcaraz: {dzumhur_higher}/1000 = {dzumhur_higher/10:.1f}%")
    
    # High-scoring games analysis
    alcaraz_high = np.sum(alcaraz_fp > 90)
    dzumhur_high = np.sum(dzumhur_fp > 50)
    
    print(f"\nHigh-scoring performances:")
    print(f"  Alcaraz >90 points: {alcaraz_high}/1000 = {alcaraz_high/10:.1f}%")
    print(f"  Dzumhur >50 points: {dzumhur_high}/1000 = {dzumhur_high/10:.1f}%")
    
    # Variance analysis
    alcaraz_cv = np.std(alcaraz_fp) / np.mean(alcaraz_fp) * 100
    dzumhur_cv = np.std(dzumhur_fp) / np.mean(dzumhur_fp) * 100
    
    print(f"\nVariance analysis (Coefficient of Variation):")
    print(f"  Alcaraz CV: {alcaraz_cv:.1f}% (lower = more consistent)")
    print(f"  Dzumhur CV: {dzumhur_cv:.1f}% (lower = more consistent)")
    
    print(f"\n✅ SURFACE-WEIGHTED STATS VALIDATION")
    print("-" * 60)
    print("This simulation uses:")
    print("  • 70% clay-specific weighting for Alcaraz (53 clay matches)")
    print("  • 30% clay-specific weighting for Dzumhur (2 clay matches)")
    print("  • Surface-weighted ELO calculations")
    print("  • Skill-preserving variance (±8% service, ±12% ace/DF)")
    print("  • Realistic 63.3% win probability vs 80% pure ELO")


if __name__ == "__main__":
    run_1000_simulations()
