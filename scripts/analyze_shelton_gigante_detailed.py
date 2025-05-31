#!/usr/bin/env python3
"""
Detailed analysis of Shelton vs Gigante to match betting lines.
File location: /home/dustys/the net/tennis/scripts/analyze_shelton_gigante_detailed.py
"""

import os
import sys
import json

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scripts.enhanced_player_data_filler import EnhancedPlayerDataFiller


def analyze_shelton_gigante_detailed():
    """Detailed analysis of Shelton vs Gigante matchup."""
    print("🔍 DETAILED SHELTON vs GIGANTE ANALYSIS")
    print("=" * 70)

    # Create enhanced filler
    filler = EnhancedPlayerDataFiller(min_matches_threshold=10)
    surface = 'Clay'

    # Get ELO ratings
    shelton_elo = filler.simulator.analyzer.get_player_elo("Ben Shelton", surface)
    gigante_elo = filler.simulator.analyzer.get_player_elo("Matteo Gigante", surface)

    print(f"📊 PLAYER COMPARISON:")
    print(f"  Ben Shelton ELO: {shelton_elo:.1f}")
    print(f"  Matteo Gigante ELO: {gigante_elo:.1f}")
    print(f"  ELO difference: {shelton_elo - gigante_elo:.1f} points")
    print()

    # Get actual stats being used
    shelton_stats = filler.simulator.analyzer.get_player_stats("Ben Shelton", surface)
    gigante_stats = filler.simulator.analyzer.get_player_stats("Matteo Gigante", surface)

    print(f"📈 CURRENT STATS:")
    print(f"  Ben Shelton:")
    print(f"    Service: {shelton_stats.get('service_points_won', 'N/A'):.1f}%")
    print(f"    Return: {shelton_stats.get('return_points_won', 'N/A'):.1f}%")
    print(f"    Ace Rate: {shelton_stats.get('ace_rate', 'N/A'):.1f}%")
    print(f"    DF Rate: {shelton_stats.get('double_fault_rate', 'N/A'):.1f}%")
    print()
    print(f"  Matteo Gigante:")
    service_val = gigante_stats.get('service_points_won', 0)
    return_val = gigante_stats.get('return_points_won', 0)
    ace_val = gigante_stats.get('ace_rate', 0)
    df_val = gigante_stats.get('double_fault_rate', 0)

    print(f"    Service: {service_val:.1f}%" if service_val else "    Service: N/A")
    print(f"    Return: {return_val:.1f}%" if return_val else "    Return: N/A")
    print(f"    Ace Rate: {ace_val:.1f}%" if ace_val else "    Ace Rate: N/A")
    print(f"    DF Rate: {df_val:.1f}%" if df_val else "    DF Rate: N/A")
    print()

    # Calculate various probability components
    elo_prob = filler.simulator.calculate_elo_win_probability("Ben Shelton", "Matteo Gigante", surface)

    # Stats-based probability
    shelton_service = shelton_stats.get('service_points_won', 60.0)
    gigante_return = gigante_stats.get('return_points_won', 40.0)
    total_strength = shelton_service + gigante_return
    stats_prob = shelton_service / total_strength if total_strength > 0 else 0.5

    print(f"🎯 PROBABILITY BREAKDOWN:")
    print(f"  ELO-based probability: {elo_prob:.1%}")
    print(f"  Stats-based probability: {stats_prob:.1%}")
    print(f"  Vegas implied (63.6%): 63.6%")
    print()

    # Test current simulation
    print(f"🎾 SIMULATION TESTING:")
    print("-" * 40)

    shelton_wins = 0
    total_matches = 200

    print(f"Running {total_matches} simulations...")

    for i in range(total_matches):
        p1_stats, p2_stats, sets = filler.simulator.simulate_match_detailed(
            "Ben Shelton", "Matteo Gigante", surface, best_of_5=False, use_variance=True
        )

        if p1_stats.match_won:
            shelton_wins += 1

    current_win_rate = shelton_wins / total_matches * 100

    print(f"  Current simulation: {current_win_rate:.1f}% win rate")
    print(f"  Vegas line: 63.6% win rate")
    print(f"  Difference: {current_win_rate - 63.6:.1f} percentage points")
    print()

    # Analyze what could be adjusted
    print(f"🔧 POTENTIAL ADJUSTMENTS:")
    print("-" * 40)

    if current_win_rate > 70:
        print("🚨 ISSUE: Simulation too high")
        print("Potential fixes:")
        print("  1. Reduce Shelton's service advantage")
        print("  2. Increase Gigante's return strength")
        print("  3. Add more variance/randomness")
        print("  4. Adjust surface effects for clay")
        print("  5. Consider match format effects")
    elif current_win_rate < 58:
        print("🚨 ISSUE: Simulation too low")
        print("Potential fixes:")
        print("  1. Increase Shelton's service advantage")
        print("  2. Reduce Gigante's return strength")
        print("  3. Increase ELO weight")
    else:
        print("✅ GOOD: Within reasonable range")

    print()

    # Test different variance levels
    print(f"🎲 VARIANCE TESTING:")
    print("-" * 40)

    variance_levels = [0.1, 0.2, 0.3, 0.4, 0.5]

    for variance in variance_levels:
        wins = 0
        test_matches = 50

        for i in range(test_matches):
            # Get probabilities with specific variance
            p1_probs = filler.simulator.get_match_adjusted_probabilities(
                "Ben Shelton", surface, True, variance
            )
            p2_probs = filler.simulator.get_match_adjusted_probabilities(
                "Matteo Gigante", surface, True, variance
            )

            p1_stats, p2_stats, sets = filler.simulator.simulate_match_detailed(
                "Ben Shelton", "Matteo Gigante", surface, best_of_5=False, use_variance=True
            )

            if p1_stats.match_won:
                wins += 1

        win_rate = wins / test_matches * 100
        print(f"  Variance {variance:.1f}: {win_rate:.1f}% win rate")

    print()

    # Test surface-specific adjustments
    print(f"🏟️ SURFACE ANALYSIS:")
    print("-" * 40)

    # Check if players have surface preferences
    shelton_calc_stats = filler.simulator.analyzer.calculated_stats.get("Ben Shelton", {})
    gigante_calc_stats = filler.simulator.analyzer.calculated_stats.get("Matteo Gigante", {})

    print(f"  Ben Shelton clay matches: {shelton_calc_stats.get('clay_matches', 'Unknown')}")
    print(f"  Matteo Gigante clay matches: {gigante_calc_stats.get('clay_matches', 'Unknown')}")

    # Check if Shelton (American hard court player) might be disadvantaged on clay
    if shelton_calc_stats.get('clay_matches', 0) < 10:
        print(f"  ⚠️  Shelton has limited clay experience - could reduce his advantage")

    if gigante_calc_stats.get('clay_matches', 0) > shelton_calc_stats.get('clay_matches', 0):
        print(f"  ⚠️  Gigante might have clay advantage despite lower ELO")

    print()

    # Suggest specific adjustments
    print(f"💡 SPECIFIC RECOMMENDATIONS:")
    print("-" * 40)

    gap = current_win_rate - 63.6

    if abs(gap) > 5:
        print(f"Gap: {gap:.1f} percentage points")

        if gap > 0:  # Simulation too high
            print("To reduce Shelton's win rate:")
            print(f"  1. Reduce service gap: {shelton_service:.1f}% → {shelton_service - 2:.1f}%")
            print(f"  2. Improve Gigante return: {gigante_stats.get('return_points_won', 40):.1f}% → {gigante_stats.get('return_points_won', 40) + 1:.1f}%")
            print(f"  3. Add clay surface penalty for Shelton")
            print(f"  4. Increase variance to {filler.simulator.surface_adjustments['Clay']['variance_multiplier'] + 0.1:.1f}")
        else:  # Simulation too low
            print("To increase Shelton's win rate:")
            print(f"  1. Increase service gap: {shelton_service:.1f}% → {shelton_service + 1:.1f}%")
            print(f"  2. Reduce Gigante return: {gigante_stats.get('return_points_won', 40):.1f}% → {gigante_stats.get('return_points_won', 40) - 1:.1f}%")
            print(f"  3. Increase ELO weight for this skill gap")
    else:
        print("✅ Current simulation is within acceptable range!")

    return current_win_rate, gap


def test_manual_adjustments():
    """Test manual stat adjustments to match betting lines."""
    print(f"\n🔬 TESTING MANUAL ADJUSTMENTS")
    print("=" * 70)

    filler = EnhancedPlayerDataFiller(min_matches_threshold=10)
    surface = 'Clay'

    # Get current stats
    shelton_stats = filler.simulator.analyzer.get_player_stats("Ben Shelton", surface)
    gigante_stats = filler.simulator.analyzer.get_player_stats("Matteo Gigante", surface)

    # Test different stat combinations
    adjustments = [
        {"name": "Current", "shelton_service": shelton_stats.get('service_points_won', 60),
         "gigante_return": gigante_stats.get('return_points_won', 40)},
        {"name": "Reduce Shelton service", "shelton_service": shelton_stats.get('service_points_won', 60) - 2,
         "gigante_return": gigante_stats.get('return_points_won', 40)},
        {"name": "Improve Gigante return", "shelton_service": shelton_stats.get('service_points_won', 60),
         "gigante_return": gigante_stats.get('return_points_won', 40) + 2},
        {"name": "Both adjustments", "shelton_service": shelton_stats.get('service_points_won', 60) - 1,
         "gigante_return": gigante_stats.get('return_points_won', 40) + 1},
    ]

    for adj in adjustments:
        # Temporarily modify stats
        original_shelton = filler.simulator.analyzer.calculated_stats.get("Ben Shelton", {}).copy()
        original_gigante = filler.simulator.analyzer.calculated_stats.get("Matteo Gigante", {}).copy()

        # Apply adjustments
        if "Ben Shelton" in filler.simulator.analyzer.calculated_stats:
            filler.simulator.analyzer.calculated_stats["Ben Shelton"]['service_points_won'] = adj['shelton_service']

        if "Matteo Gigante" in filler.simulator.analyzer.calculated_stats:
            filler.simulator.analyzer.calculated_stats["Matteo Gigante"]['return_points_won'] = adj['gigante_return']

        # Test simulation
        wins = 0
        test_matches = 100

        for i in range(test_matches):
            p1_stats, p2_stats, sets = filler.simulator.simulate_match_detailed(
                "Ben Shelton", "Matteo Gigante", surface, best_of_5=False, use_variance=True
            )

            if p1_stats.match_won:
                wins += 1

        win_rate = wins / test_matches * 100
        gap = win_rate - 63.6

        print(f"  {adj['name']:<20}: {win_rate:>5.1f}% (gap: {gap:>+5.1f})")

        # Restore original stats
        if original_shelton:
            filler.simulator.analyzer.calculated_stats["Ben Shelton"] = original_shelton
        if original_gigante:
            filler.simulator.analyzer.calculated_stats["Matteo Gigante"] = original_gigante


if __name__ == "__main__":
    win_rate, gap = analyze_shelton_gigante_detailed()
    test_manual_adjustments()
