#!/usr/bin/env python3
"""
Test high variance solution to create realistic tennis outcomes.
File location: /home/dustys/the net/tennis/scripts/test_high_variance_solution.py
"""

import os
import sys

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scripts.enhanced_player_data_filler import EnhancedPlayerDataFiller


def test_high_variance_solution():
    """Test if high variance can create realistic outcomes."""
    print("🎲 TESTING HIGH VARIANCE SOLUTION")
    print("=" * 70)
    
    # Create enhanced filler
    filler = EnhancedPlayerDataFiller(min_matches_threshold=10)
    surface = 'Clay'
    
    # Enhance Gigante's data
    filler.enhance_player_data("Matteo Gigante", surface)
    
    # Set conservative stats
    if "Ben Shelton" in filler.simulator.analyzer.calculated_stats:
        filler.simulator.analyzer.calculated_stats["Ben Shelton"]['service_points_won'] = 61.0
        filler.simulator.analyzer.calculated_stats["Ben Shelton"]['return_points_won'] = 38.0
    
    if "Matteo Gigante" in filler.simulator.analyzer.calculated_stats:
        filler.simulator.analyzer.calculated_stats["Matteo Gigante"]['service_points_won'] = 59.0
        filler.simulator.analyzer.calculated_stats["Matteo Gigante"]['return_points_won'] = 40.0
    
    print("1. CONSERVATIVE STATS:")
    print("-" * 40)
    print("Ben Shelton: Service 61.0%, Return 38.0%")
    print("Matteo Gigante: Service 59.0%, Return 40.0%")
    print("Total skill gap: 4.0%")
    
    # Test different variance levels
    print(f"\n2. TESTING EXTREME VARIANCE LEVELS:")
    print("-" * 40)
    
    variance_levels = [0.3, 0.5, 0.7, 0.9, 1.2, 1.5]
    
    for variance in variance_levels:
        # Temporarily modify surface variance
        original_variance = filler.simulator.surface_adjustments[surface]['variance_multiplier']
        filler.simulator.surface_adjustments[surface]['variance_multiplier'] = variance
        
        # Test simulation
        wins = 0
        total = 50
        
        for i in range(total):
            p1_stats, p2_stats, sets = filler.simulator.simulate_match_detailed(
                "Ben Shelton", "Matteo Gigante", surface, best_of_5=False, use_variance=True
            )
            
            if p1_stats.match_won:
                wins += 1
        
        win_rate = wins / total * 100
        gap = win_rate - 63.6
        
        print(f"Variance {variance:>4.1f}: {win_rate:>5.1f}% (gap: {gap:>+5.1f})")
        
        # Restore original variance
        filler.simulator.surface_adjustments[surface]['variance_multiplier'] = original_variance
    
    # Test with even smaller skill gaps
    print(f"\n3. TESTING MINIMAL SKILL GAPS:")
    print("-" * 40)
    
    minimal_cases = [
        {"name": "Tiny gap", "shelton_service": 60.5, "shelton_return": 39.0, 
         "gigante_service": 59.5, "gigante_return": 40.0},
        {"name": "Micro gap", "shelton_service": 60.2, "shelton_return": 39.5, 
         "gigante_service": 59.8, "gigante_return": 39.5},
        {"name": "Equal", "shelton_service": 60.0, "shelton_return": 39.0, 
         "gigante_service": 60.0, "gigante_return": 39.0},
    ]
    
    for case in minimal_cases:
        # Apply stats
        if "Ben Shelton" in filler.simulator.analyzer.calculated_stats:
            filler.simulator.analyzer.calculated_stats["Ben Shelton"]['service_points_won'] = case['shelton_service']
            filler.simulator.analyzer.calculated_stats["Ben Shelton"]['return_points_won'] = case['shelton_return']
        
        if "Matteo Gigante" in filler.simulator.analyzer.calculated_stats:
            filler.simulator.analyzer.calculated_stats["Matteo Gigante"]['service_points_won'] = case['gigante_service']
            filler.simulator.analyzer.calculated_stats["Matteo Gigante"]['return_points_won'] = case['gigante_return']
        
        # Test with high variance
        filler.simulator.surface_adjustments[surface]['variance_multiplier'] = 0.8
        
        wins = 0
        total = 50
        
        for i in range(total):
            p1_stats, p2_stats, sets = filler.simulator.simulate_match_detailed(
                "Ben Shelton", "Matteo Gigante", surface, best_of_5=False, use_variance=True
            )
            
            if p1_stats.match_won:
                wins += 1
        
        win_rate = wins / total * 100
        gap = win_rate - 63.6
        
        service_gap = case['shelton_service'] - case['gigante_service']
        return_gap = case['shelton_return'] - case['gigante_return']
        total_gap = service_gap - return_gap
        
        print(f"{case['name']:<10}: {win_rate:>5.1f}% (gap: {gap:>+5.1f}) | Skill gap: {total_gap:>4.1f}%")
    
    # Test pure ELO-based approach
    print(f"\n4. TESTING PURE ELO APPROACH:")
    print("-" * 40)
    
    # Reset to equal stats, let ELO do the work
    if "Ben Shelton" in filler.simulator.analyzer.calculated_stats:
        filler.simulator.analyzer.calculated_stats["Ben Shelton"]['service_points_won'] = 60.0
        filler.simulator.analyzer.calculated_stats["Ben Shelton"]['return_points_won'] = 40.0
    
    if "Matteo Gigante" in filler.simulator.analyzer.calculated_stats:
        filler.simulator.analyzer.calculated_stats["Matteo Gigante"]['service_points_won'] = 60.0
        filler.simulator.analyzer.calculated_stats["Matteo Gigante"]['return_points_won'] = 40.0
    
    print("Equal stats: Both players 60% service, 40% return")
    print("Let ELO create the skill difference")
    
    # Test with different ELO weights
    elo_weights = [0.3, 0.4, 0.5, 0.6, 0.7]
    
    for elo_weight in elo_weights:
        # Temporarily modify ELO weight in simulator
        # This is a hack - we'd need to modify the simulator code properly
        wins = 0
        total = 30
        
        for i in range(total):
            # Calculate manual probability with specific ELO weight
            shelton_elo = filler.simulator.analyzer.get_player_elo("Ben Shelton", surface)
            gigante_elo = filler.simulator.analyzer.get_player_elo("Matteo Gigante", surface)
            
            elo_prob = filler.simulator.calculate_elo_win_probability("Ben Shelton", "Matteo Gigante", surface)
            stats_prob = 0.5  # Equal stats
            
            # Manual blend
            blended_prob = (elo_weight * elo_prob) + ((1-elo_weight-0.1) * stats_prob) + (0.1 * 0.5)
            
            # Simple win/loss
            import random
            if random.random() < blended_prob:
                wins += 1
        
        win_rate = wins / total * 100
        gap = win_rate - 63.6
        
        print(f"ELO weight {elo_weight:.1f}: {win_rate:>5.1f}% (gap: {gap:>+5.1f})")


def test_alternative_approach():
    """Test completely different approach - modify the ELO calculation itself."""
    print(f"\n🔄 TESTING ALTERNATIVE APPROACH")
    print("=" * 70)
    
    filler = EnhancedPlayerDataFiller(min_matches_threshold=10)
    surface = 'Clay'
    filler.enhance_player_data("Matteo Gigante", surface)
    
    # Get ELO ratings
    shelton_elo = filler.simulator.analyzer.get_player_elo("Ben Shelton", surface)
    gigante_elo = filler.simulator.analyzer.get_player_elo("Matteo Gigante", surface)
    
    print(f"Original ELOs: Shelton {shelton_elo:.1f}, Gigante {gigante_elo:.1f}")
    print(f"ELO difference: {shelton_elo - gigante_elo:.1f}")
    
    # Test different ELO dampening factors
    print(f"\nTesting ELO probability calculations:")
    
    k_factors = [400, 600, 800, 1000, 1200]
    
    for k in k_factors:
        # Calculate ELO probability with different K factors
        elo_diff = shelton_elo - gigante_elo
        raw_prob = 1 / (1 + 10**(-elo_diff / k))
        
        # Apply dampening
        dampened_prob = 0.5 + (raw_prob - 0.5) * 0.7
        
        print(f"K={k:>4}: Raw {raw_prob:.1%}, Dampened {dampened_prob:.1%}")
    
    # The issue might be that we need to modify the ELO ratings themselves
    print(f"\nTesting modified ELO ratings:")
    
    # Reduce the ELO gap artificially
    elo_reductions = [0, 50, 100, 150, 200]
    
    for reduction in elo_reductions:
        modified_shelton_elo = shelton_elo - reduction
        elo_diff = modified_shelton_elo - gigante_elo
        
        # Calculate probability with K=600
        raw_prob = 1 / (1 + 10**(-elo_diff / 600))
        dampened_prob = 0.5 + (raw_prob - 0.5) * 0.7
        
        print(f"Reduce Shelton ELO by {reduction:>3}: {modified_shelton_elo:.0f} vs {gigante_elo:.0f} = {dampened_prob:.1%}")


if __name__ == "__main__":
    test_high_variance_solution()
    test_alternative_approach()
