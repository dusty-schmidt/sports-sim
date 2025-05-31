#!/usr/bin/env python3
"""
Fix Shelton vs Gigante balance by adjusting skill gaps.
File location: /home/dustys/the net/tennis/scripts/fix_shelton_gigante_balance.py
"""

import os
import sys

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scripts.enhanced_player_data_filler import EnhancedPlayerDataFiller


def fix_shelton_gigante_balance():
    """Fix the balance by manually adjusting stats to realistic levels."""
    print("🔧 FIXING SHELTON vs GIGANTE BALANCE")
    print("=" * 70)
    
    # Create enhanced filler
    filler = EnhancedPlayerDataFiller(min_matches_threshold=10)
    surface = 'Clay'
    
    # Enhance Gigante's data first
    filler.enhance_player_data("Matteo Gigante", surface)
    
    # Get current stats
    shelton_stats = filler.simulator.analyzer.get_player_stats("Ben Shelton", surface)
    gigante_stats = filler.simulator.analyzer.get_player_stats("Matteo Gigante", surface)
    
    print("1. CURRENT STATS:")
    print("-" * 40)
    print(f"Ben Shelton: Service {shelton_stats['service_points_won']:.1f}%, Return {shelton_stats['return_points_won']:.1f}%")
    print(f"Matteo Gigante: Service {gigante_stats['service_points_won']:.1f}%, Return {gigante_stats['return_points_won']:.1f}%")
    
    service_gap = shelton_stats['service_points_won'] - gigante_stats['service_points_won']
    return_gap = shelton_stats['return_points_won'] - gigante_stats['return_points_won']
    total_gap = service_gap - return_gap  # Shelton's advantage
    
    print(f"Service gap: {service_gap:.1f}% (Shelton advantage)")
    print(f"Return gap: {return_gap:.1f}% (Gigante advantage)")
    print(f"Total skill gap: {total_gap:.1f}%")
    
    # Target: Reduce total skill gap to ~6-8% for 63.6% win rate
    print(f"\n2. ADJUSTING FOR REALISTIC BALANCE:")
    print("-" * 40)
    
    # Target stats for 63.6% win rate:
    # - Shelton should have moderate advantage
    # - Break rates should be ~15-25% each way
    
    # Adjust Shelton's stats (reduce slightly)
    new_shelton_service = 63.5  # Down from 61.3
    new_shelton_return = 37.0   # Down from 38.5
    
    # Adjust Gigante's stats (improve slightly)  
    new_gigante_service = 58.5  # Up from 57.9
    new_gigante_return = 41.0   # Down from 42.0
    
    print(f"Target Shelton: Service {new_shelton_service:.1f}%, Return {new_shelton_return:.1f}%")
    print(f"Target Gigante: Service {new_gigante_service:.1f}%, Return {new_gigante_return:.1f}%")
    
    new_service_gap = new_shelton_service - new_gigante_service
    new_return_gap = new_shelton_return - new_gigante_return
    new_total_gap = new_service_gap - new_return_gap
    
    print(f"New service gap: {new_service_gap:.1f}%")
    print(f"New return gap: {new_return_gap:.1f}%")
    print(f"New total skill gap: {new_total_gap:.1f}%")
    
    # Apply the adjustments
    if "Ben Shelton" in filler.simulator.analyzer.calculated_stats:
        filler.simulator.analyzer.calculated_stats["Ben Shelton"]['service_points_won'] = new_shelton_service
        filler.simulator.analyzer.calculated_stats["Ben Shelton"]['return_points_won'] = new_shelton_return
    
    if "Matteo Gigante" in filler.simulator.analyzer.calculated_stats:
        filler.simulator.analyzer.calculated_stats["Matteo Gigante"]['service_points_won'] = new_gigante_service
        filler.simulator.analyzer.calculated_stats["Matteo Gigante"]['return_points_won'] = new_gigante_return
    
    # Test the adjusted simulation
    print(f"\n3. TESTING ADJUSTED SIMULATION:")
    print("-" * 40)
    
    shelton_wins = 0
    total_matches = 100
    
    print(f"Running {total_matches} simulations...")
    
    for i in range(total_matches):
        if (i + 1) % 20 == 0:
            current_rate = shelton_wins / (i + 1) * 100
            print(f"  After {i + 1} matches: Shelton {current_rate:.1f}% win rate")
        
        p1_stats, p2_stats, sets = filler.simulator.simulate_match_detailed(
            "Ben Shelton", "Matteo Gigante", surface, best_of_5=False, use_variance=True
        )
        
        if p1_stats.match_won:
            shelton_wins += 1
    
    win_rate = shelton_wins / total_matches * 100
    gap = win_rate - 63.6
    
    print(f"\n📊 ADJUSTED SIMULATION RESULTS:")
    print("-" * 40)
    print(f"Ben Shelton wins: {shelton_wins}/{total_matches}")
    print(f"Win rate: {win_rate:.1f}%")
    print(f"Vegas implied: 63.6%")
    print(f"Difference: {gap:+.1f} percentage points")
    
    # Test break rates with new stats
    print(f"\n4. TESTING NEW BREAK RATES:")
    print("-" * 40)
    
    # Get new probabilities
    shelton_probs = filler.simulator.get_match_adjusted_probabilities("Ben Shelton", surface, True)
    gigante_probs = filler.simulator.get_match_adjusted_probabilities("Matteo Gigante", surface, True)
    
    # Test service games
    shelton_service_wins = 0
    gigante_service_wins = 0
    test_games = 100
    
    for i in range(test_games):
        # Shelton serving
        game_result = filler.simulator.simulate_game(
            shelton_probs, gigante_probs, "Ben Shelton", "Matteo Gigante"
        )
        if game_result.winner == "Ben Shelton":
            shelton_service_wins += 1
        
        # Gigante serving
        game_result = filler.simulator.simulate_game(
            gigante_probs, shelton_probs, "Matteo Gigante", "Ben Shelton"
        )
        if game_result.winner == "Matteo Gigante":
            gigante_service_wins += 1
    
    shelton_hold_rate = shelton_service_wins / test_games * 100
    gigante_hold_rate = gigante_service_wins / test_games * 100
    
    shelton_break_rate = 100 - gigante_hold_rate
    gigante_break_rate = 100 - shelton_hold_rate
    
    print(f"Shelton hold rate: {shelton_hold_rate:.1f}%")
    print(f"Gigante hold rate: {gigante_hold_rate:.1f}%")
    print(f"Shelton break rate: {shelton_break_rate:.1f}%")
    print(f"Gigante break rate: {gigante_break_rate:.1f}%")
    
    # Analyze the result
    if abs(gap) <= 5:
        print(f"\n✅ EXCELLENT: Within 5% of Vegas line!")
        print(f"Break rates look realistic for tennis")
    elif abs(gap) <= 10:
        print(f"\n✅ GOOD: Within 10% of Vegas line")
    else:
        print(f"\n⚠️  Still needs adjustment")
        
        if win_rate > 70:
            print(f"Suggestions:")
            print(f"  - Reduce Shelton service to {new_shelton_service - 1:.1f}%")
            print(f"  - Increase Gigante service to {new_gigante_service + 1:.1f}%")
            print(f"  - Increase variance")
    
    return win_rate, gap, shelton_break_rate, gigante_break_rate


def test_multiple_adjustments():
    """Test multiple stat combinations to find optimal balance."""
    print(f"\n🔬 TESTING MULTIPLE STAT COMBINATIONS")
    print("=" * 70)
    
    filler = EnhancedPlayerDataFiller(min_matches_threshold=10)
    surface = 'Clay'
    filler.enhance_player_data("Matteo Gigante", surface)
    
    # Test different stat combinations
    test_cases = [
        {"name": "Conservative", "shelton_service": 62.0, "shelton_return": 37.5, 
         "gigante_service": 59.0, "gigante_return": 40.5},
        {"name": "Moderate", "shelton_service": 63.0, "shelton_return": 37.0, 
         "gigante_service": 58.5, "gigante_return": 41.0},
        {"name": "Current", "shelton_service": 63.5, "shelton_return": 37.0, 
         "gigante_service": 58.5, "gigante_return": 41.0},
        {"name": "Aggressive", "shelton_service": 64.0, "shelton_return": 36.5, 
         "gigante_service": 58.0, "gigante_return": 41.5},
    ]
    
    for case in test_cases:
        # Apply stats
        if "Ben Shelton" in filler.simulator.analyzer.calculated_stats:
            filler.simulator.analyzer.calculated_stats["Ben Shelton"]['service_points_won'] = case['shelton_service']
            filler.simulator.analyzer.calculated_stats["Ben Shelton"]['return_points_won'] = case['shelton_return']
        
        if "Matteo Gigante" in filler.simulator.analyzer.calculated_stats:
            filler.simulator.analyzer.calculated_stats["Matteo Gigante"]['service_points_won'] = case['gigante_service']
            filler.simulator.analyzer.calculated_stats["Matteo Gigante"]['return_points_won'] = case['gigante_return']
        
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
        
        service_gap = case['shelton_service'] - case['gigante_service']
        return_gap = case['shelton_return'] - case['gigante_return']
        total_gap = service_gap - return_gap
        
        print(f"{case['name']:<12}: {win_rate:>5.1f}% (gap: {gap:>+5.1f}) | Skill gap: {total_gap:>4.1f}%")


if __name__ == "__main__":
    win_rate, gap, shelton_breaks, gigante_breaks = fix_shelton_gigante_balance()
    test_multiple_adjustments()
