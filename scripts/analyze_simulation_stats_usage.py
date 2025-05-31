#!/usr/bin/env python3
"""
Analyze what stats the simulation is actually using vs what it should use.
File location: /home/dustys/the net/tennis/scripts/analyze_simulation_stats_usage.py
"""

import os
import sys

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scripts.enhanced_player_data_filler import EnhancedPlayerDataFiller


def analyze_current_simulation_logic():
    """Analyze what the current simulation logic actually uses."""
    print("🔍 ANALYZING CURRENT SIMULATION LOGIC")
    print("=" * 70)
    
    filler = EnhancedPlayerDataFiller(min_matches_threshold=10)
    surface = 'Clay'
    filler.enhance_player_data("Matteo Gigante", surface)
    
    # Get the probabilities being used
    shelton_probs = filler.simulator.get_match_adjusted_probabilities("Ben Shelton", surface, True)
    gigante_probs = filler.simulator.get_match_adjusted_probabilities("Matteo Gigante", surface, True)
    
    print("1. CURRENT STATS BEING USED:")
    print("-" * 40)
    print("Ben Shelton:")
    for key, value in shelton_probs.items():
        print(f"  {key}: {value:.1f}%")
    
    print("\nMatteo Gigante:")
    for key, value in gigante_probs.items():
        print(f"  {key}: {value:.1f}%")
    
    print(f"\n2. HOW THESE STATS ARE USED IN SIMULATION:")
    print("-" * 40)
    print("Point Simulation Logic:")
    print("  1. Check for ace (based on ace_rate)")
    print("  2. Check for double fault (based on double_fault_rate)")
    print("  3. If neither, use service_points_won vs return_points_won")
    print("  4. Apply ELO blending to the service/return battle")
    print("  5. Add rally/fatigue/clutch multipliers")
    
    print(f"\n3. MISSING STATS THAT COULD MATTER:")
    print("-" * 40)
    print("Currently NOT used:")
    print("  • first_serve_percentage - only stored, not used in point logic")
    print("  • Break point conversion rates")
    print("  • Tiebreak performance")
    print("  • Set-specific performance patterns")
    print("  • Momentum/streakiness")
    print("  • Surface-specific adjustments beyond basic multipliers")
    
    # Check what other stats are available
    shelton_calc_stats = filler.simulator.analyzer.calculated_stats.get("Ben Shelton", {})
    gigante_calc_stats = filler.simulator.analyzer.calculated_stats.get("Matteo Gigante", {})
    
    print(f"\n4. AVAILABLE BUT UNUSED STATS:")
    print("-" * 40)
    print("Ben Shelton available stats:")
    for key, value in shelton_calc_stats.items():
        if key not in ['service_points_won', 'return_points_won', 'ace_rate', 'double_fault_rate', 'first_serve_percentage']:
            print(f"  {key}: {value}")
    
    print("\nMatteo Gigante available stats:")
    for key, value in gigante_calc_stats.items():
        if key not in ['service_points_won', 'return_points_won', 'ace_rate', 'double_fault_rate', 'first_serve_percentage']:
            print(f"  {key}: {value}")


def analyze_tennis_complexity():
    """Analyze the complexity of real tennis that we're missing."""
    print(f"\n🎾 TENNIS COMPLEXITY ANALYSIS")
    print("=" * 70)
    
    print("1. CURRENT OVERSIMPLIFICATIONS:")
    print("-" * 40)
    print("Point Level:")
    print("  • Only ace, DF, or service_points_won battle")
    print("  • No first serve vs second serve distinction")
    print("  • No rally length impact on point outcome")
    print("  • No court position/momentum within points")
    
    print("\nGame Level:")
    print("  • No break point pressure effects")
    print("  • No service game vs return game psychology")
    print("  • No 'clutch' serving under pressure")
    
    print("\nSet Level:")
    print("  • No momentum swings")
    print("  • No fatigue accumulation")
    print("  • No set-specific patterns (first set vs deciding set)")
    
    print("\nMatch Level:")
    print("  • No head-to-head history")
    print("  • No playing style matchups")
    print("  • No weather/conditions impact")
    
    print(f"\n2. WHAT REAL TENNIS LOOKS LIKE:")
    print("-" * 40)
    print("Service Games:")
    print("  • Elite players hold serve 85-95% of the time")
    print("  • Break points are rare and crucial")
    print("  • First serve % dramatically affects hold rate")
    print("  • Pressure situations change serving patterns")
    
    print("\nReturn Games:")
    print("  • Break rates vary enormously by surface")
    print("  • Return position and aggression matter")
    print("  • Some players are much better break point converters")
    
    print("\nSet Patterns:")
    print("  • Many sets decided by 1-2 break points")
    print("  • Tiebreaks are often coin flips")
    print("  • Momentum can swing dramatically")
    
    print(f"\n3. PROPOSED IMPROVEMENTS:")
    print("-" * 40)
    print("Immediate fixes:")
    print("  • Use first_serve_percentage in point simulation")
    print("  • Add break point conversion rates")
    print("  • Implement proper pressure multipliers")
    print("  • Add tiebreak-specific logic")
    
    print("\nMedium-term:")
    print("  • Rally length affects point outcome")
    print("  • Momentum tracking between games")
    print("  • Surface-specific break rates")
    print("  • Playing style matchup modifiers")
    
    print("\nAdvanced:")
    print("  • Machine learning point prediction")
    print("  • Dynamic pressure adjustments")
    print("  • Weather/conditions modeling")
    print("  • Fatigue accumulation over match")


def test_first_serve_impact():
    """Test how much first serve percentage should impact the simulation."""
    print(f"\n🎯 TESTING FIRST SERVE IMPACT")
    print("=" * 70)
    
    print("Real Tennis First Serve Impact:")
    print("  • First serve won: ~75% for elite players")
    print("  • Second serve won: ~55% for elite players")
    print("  • 20% difference in point win rate!")
    
    print("\nCurrent Simulation:")
    print("  • Uses overall service_points_won (~61-58%)")
    print("  • Ignores first_serve_percentage completely")
    print("  • This is a MAJOR oversimplification")
    
    print("\nProposed Fix:")
    print("  1. Calculate first serve vs second serve win rates")
    print("  2. Use first_serve_percentage to determine serve type")
    print("  3. Apply appropriate win rate for that serve type")
    print("  4. This should create more realistic variance")
    
    # Example calculation
    print(f"\nExample for Ben Shelton:")
    print("  Current: 61.3% service points won (flat)")
    print("  Realistic: 65.6% first serve percentage")
    print("    → 65.6% of points: 75% win rate (first serve)")
    print("    → 34.4% of points: 55% win rate (second serve)")
    print("    → Overall: 67.1% service points won")
    print("  This creates natural variance AND higher hold rates!")


def suggest_implementation_plan():
    """Suggest a plan to implement better tennis simulation."""
    print(f"\n📋 IMPLEMENTATION PLAN")
    print("=" * 70)
    
    print("PHASE 1: First Serve Logic (Immediate)")
    print("-" * 40)
    print("1. Modify simulate_point() to:")
    print("   • Check first_serve_percentage")
    print("   • Calculate separate first/second serve win rates")
    print("   • Use appropriate rate based on serve type")
    
    print("2. Expected impact:")
    print("   • More realistic service hold rates")
    print("   • Natural variance in point outcomes")
    print("   • Better break rate simulation")
    
    print("\nPHASE 2: Break Point Psychology (Next)")
    print("-" * 40)
    print("1. Add break point conversion stats")
    print("2. Implement pressure multipliers for:")
    print("   • Break points (0-40, 15-40, 30-40)")
    print("   • Game points when serving")
    print("   • Set points")
    
    print("\nPHASE 3: Momentum & Fatigue (Later)")
    print("-" * 40)
    print("1. Track momentum between games")
    print("2. Implement fatigue in longer matches")
    print("3. Add set-specific patterns")
    
    print(f"\n🎯 PRIORITY: Start with first serve logic!")
    print("This single change could fix the Shelton vs Gigante issue")
    print("by creating more realistic service hold rates.")


if __name__ == "__main__":
    analyze_current_simulation_logic()
    analyze_tennis_complexity()
    test_first_serve_impact()
    suggest_implementation_plan()
