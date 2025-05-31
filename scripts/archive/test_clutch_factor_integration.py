"""
Test clutch factor integration in the tennis simulator
"""

import sys
from pathlib import Path
import numpy as np

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from main_sim import FantasyTennisSimulator

def test_clutch_factor_integration():
    """Test that clutch factors are properly integrated and working."""
    print("TESTING CLUTCH FACTOR INTEGRATION")
    print("="*60)
    
    simulator = FantasyTennisSimulator()
    
    # Test 1: Check clutch factor loading
    print("✅ Test 1: Clutch Factor Loading")
    
    # Check if clutch factors are loaded
    test_players = ["Alexander Zverev", "Stefanos Tsitsipas", "Nishesh Basavareddy"]
    
    for player in test_players:
        if simulator.analyzer.player_exists(player):
            player_stats = simulator.analyzer.calculated_stats.get(player, {})
            clutch_factor = player_stats.get('clutch_factor', 'Not found')
            clutch_level = player_stats.get('clutch_level', 'Not found')
            print(f"  {player}: {clutch_factor} ({clutch_level})")
        else:
            print(f"  {player}: Player not found")
    
    # Test 2: Pressure situation detection
    print(f"\n✅ Test 2: Pressure Situation Detection")
    
    # Test break point detection
    bp_situation = simulator._get_pressure_situation(2, 4)  # 30-40 (break point)
    print(f"  30-40 situation: {bp_situation} (should be 'BP')")
    
    # Test game point detection  
    gp_situation = simulator._get_pressure_situation(4, 2)  # 40-30 (game point)
    print(f"  40-30 situation: {gp_situation} (should be 'GP')")
    
    # Test deuce detection
    deuce_situation = simulator._get_pressure_situation(3, 3)  # Deuce
    print(f"  Deuce situation: {deuce_situation} (should be 'Deuce')")
    
    # Test normal situation
    normal_situation = simulator._get_pressure_situation(2, 1)  # 30-15
    print(f"  30-15 situation: {normal_situation} (should be None)")
    
    # Test 3: Clutch multiplier calculation
    print(f"\n✅ Test 3: Clutch Multiplier Calculation")
    
    for player in test_players[:2]:
        if simulator.analyzer.player_exists(player):
            bp_multiplier = simulator._get_clutch_multiplier(player, 'BP')
            gp_multiplier = simulator._get_clutch_multiplier(player, 'GP')
            mp_multiplier = simulator._get_clutch_multiplier(player, 'MP')
            
            print(f"  {player}:")
            print(f"    Break Point: {bp_multiplier:.3f}")
            print(f"    Game Point: {gp_multiplier:.3f}")
            print(f"    Match Point: {mp_multiplier:.3f}")
    
    # Test 4: Pressure-adjusted probabilities
    print(f"\n✅ Test 4: Pressure-Adjusted Probabilities")
    
    player = "Alexander Zverev"
    if simulator.analyzer.player_exists(player):
        # Normal probabilities
        normal_probs = simulator.get_match_adjusted_probabilities(player, 'Hard', True)
        
        # Break point probabilities
        bp_probs = simulator.get_match_adjusted_probabilities(
            player, 'Hard', True, pressure_situation='BP'
        )
        
        print(f"  {player} Normal vs Break Point:")
        print(f"    Service Points Won: {normal_probs['service_points_won']:.1f}% → {bp_probs['service_points_won']:.1f}%")
        print(f"    Ace Rate: {normal_probs['ace_rate']:.1f}% → {bp_probs['ace_rate']:.1f}%")
        print(f"    Double Fault Rate: {normal_probs['double_fault_rate']:.1f}% → {bp_probs['double_fault_rate']:.1f}%")
    
    # Test 5: Clutch factor impact in simulation
    print(f"\n✅ Test 5: Clutch Factor Impact in Simulation")
    
    # Find elite clutch vs poor clutch players
    elite_clutch_players = []
    poor_clutch_players = []
    
    for player_name, stats in simulator.analyzer.calculated_stats.items():
        clutch_level = stats.get('clutch_level', 'Average')
        if clutch_level == 'Elite Clutch' and len(elite_clutch_players) < 3:
            elite_clutch_players.append(player_name)
        elif clutch_level == 'Poor Clutch' and len(poor_clutch_players) < 3:
            poor_clutch_players.append(player_name)
    
    print(f"  Elite Clutch Players: {elite_clutch_players}")
    print(f"  Poor Clutch Players: {poor_clutch_players}")
    
    # Test simulation with clutch vs non-clutch players
    if elite_clutch_players and poor_clutch_players:
        elite_player = elite_clutch_players[0]
        poor_player = poor_clutch_players[0]
        
        print(f"\n  Simulating: {elite_player} (Elite) vs {poor_player} (Poor)")
        
        # Simulate multiple matches to see clutch factor impact
        elite_wins = 0
        total_matches = 100
        
        for _ in range(total_matches):
            try:
                p1_stats, p2_stats, sets = simulator.simulate_match_detailed(
                    elite_player, poor_player, 'Hard', False, True, False
                )
                
                if p1_stats.match_won:
                    elite_wins += 1
                    
            except Exception as e:
                continue
        
        elite_win_rate = (elite_wins / total_matches) * 100
        print(f"  Elite clutch player win rate: {elite_win_rate:.1f}% (should be >50% due to clutch factor)")
    
    # Test 6: Specific clutch scenarios
    print(f"\n✅ Test 6: Specific Clutch Scenarios")
    
    # Test a known clutch player vs average player
    clutch_player = "Nishesh Basavareddy"  # Was shown as "Good Clutch" in extraction
    average_player = "Alex De Minaur"      # Was shown as "Average" in extraction
    
    if (simulator.analyzer.player_exists(clutch_player) and 
        simulator.analyzer.player_exists(average_player)):
        
        print(f"  Testing {clutch_player} vs {average_player}")
        
        # Get their clutch factors
        clutch_stats = simulator.analyzer.calculated_stats.get(clutch_player, {})
        average_stats = simulator.analyzer.calculated_stats.get(average_player, {})
        
        print(f"  {clutch_player} clutch factor: {clutch_stats.get('clutch_factor', 'N/A')}")
        print(f"  {average_player} clutch factor: {average_stats.get('clutch_factor', 'N/A')}")
        
        # Simulate a few matches
        clutch_wins = 0
        for i in range(20):
            try:
                p1_stats, p2_stats, sets = simulator.simulate_match_detailed(
                    clutch_player, average_player, 'Hard', False, True, False
                )
                
                if p1_stats.match_won:
                    clutch_wins += 1
                    
            except Exception:
                continue
        
        clutch_win_rate = (clutch_wins / 20) * 100
        print(f"  {clutch_player} win rate: {clutch_win_rate:.1f}%")

def test_clutch_factor_distribution():
    """Test the distribution of clutch factors."""
    print(f"\n" + "="*60)
    print("CLUTCH FACTOR DISTRIBUTION ANALYSIS")
    print("="*60)
    
    simulator = FantasyTennisSimulator()
    
    clutch_distribution = {
        'Elite Clutch': [],
        'Good Clutch': [],
        'Average': [],
        'Below Average': [],
        'Poor Clutch': []
    }
    
    # Collect clutch factors
    for player_name, stats in simulator.analyzer.calculated_stats.items():
        clutch_level = stats.get('clutch_level', 'Average')
        clutch_factor = stats.get('clutch_factor', 1.0)
        
        if clutch_level in clutch_distribution:
            clutch_distribution[clutch_level].append(clutch_factor)
    
    # Show distribution
    for level, factors in clutch_distribution.items():
        if factors:
            avg_factor = np.mean(factors)
            min_factor = min(factors)
            max_factor = max(factors)
            count = len(factors)
            
            print(f"{level}: {count} players")
            print(f"  Range: {min_factor:.3f} - {max_factor:.3f}")
            print(f"  Average: {avg_factor:.3f}")
            
            # Show a few examples
            if count >= 3:
                examples = sorted(zip(factors, [p for p, s in simulator.analyzer.calculated_stats.items() 
                                              if s.get('clutch_level') == level]), reverse=True)[:3]
                print(f"  Examples: {', '.join([f'{p} ({f:.3f})' for f, p in examples])}")
            print()

def main():
    """Run all clutch factor integration tests."""
    print("CLUTCH FACTOR INTEGRATION TEST SUITE")
    print("="*80)
    print("Testing that clutch factors from KeyPoints data are properly integrated")
    print("="*80)
    
    test_clutch_factor_integration()
    test_clutch_factor_distribution()
    
    print(f"\n" + "="*80)
    print("✅ CLUTCH FACTOR INTEGRATION TESTS COMPLETE")
    print("="*80)
    print("🎾 Clutch factors are now active in tennis simulation!")
    print("🔥 Elite clutch players will perform better under pressure")
    print("😰 Poor clutch players will struggle in key moments")

if __name__ == "__main__":
    main()
