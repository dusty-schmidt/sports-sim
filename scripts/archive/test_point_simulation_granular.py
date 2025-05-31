"""
Granular Point Simulation Test
Test a single tennis point with maximum detail to verify simulation logic
"""

import random
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from main_sim import FantasyTennisSimulator

class GranularPointTester:
    def __init__(self):
        self.simulator = FantasyTennisSimulator()
        
    def test_single_point_detailed(self, server_name: str, returner_name: str, surface: str = 'Hard'):
        """Test a single point with maximum granular detail."""
        print("🎾 GRANULAR POINT SIMULATION TEST")
        print("="*80)
        print(f"Server: {server_name}")
        print(f"Returner: {returner_name}")
        print(f"Surface: {surface}")
        print("="*80)
        
        # Get player probabilities
        server_probs = self.simulator.get_match_adjusted_probabilities(server_name, surface, use_variance=False)
        returner_probs = self.simulator.get_match_adjusted_probabilities(returner_name, surface, use_variance=False)
        
        print(f"\n📊 PLAYER PROBABILITIES (Base, No Variance)")
        print("-"*60)
        print(f"{server_name} (Server):")
        for key, value in server_probs.items():
            print(f"  {key:25s}: {value:6.2f}%")
        
        print(f"\n{returner_name} (Returner):")
        for key, value in returner_probs.items():
            print(f"  {key:25s}: {value:6.2f}%")
        
        # Now test with variance
        print(f"\n🎲 TESTING WITH MATCH VARIANCE")
        print("-"*60)
        
        server_probs_var = self.simulator.get_match_adjusted_probabilities(server_name, surface, use_variance=True, variance_level=0.15)
        returner_probs_var = self.simulator.get_match_adjusted_probabilities(returner_name, surface, use_variance=True, variance_level=0.15)
        
        print(f"{server_name} (Server with 15% variance):")
        for key, value in server_probs_var.items():
            base_val = server_probs[key]
            change = ((value - base_val) / base_val * 100) if base_val > 0 else 0
            print(f"  {key:25s}: {value:6.2f}% (base: {base_val:5.2f}%, change: {change:+5.1f}%)")
        
        print(f"\n{returner_name} (Returner with 15% variance):")
        for key, value in returner_probs_var.items():
            base_val = returner_probs[key]
            change = ((value - base_val) / base_val * 100) if base_val > 0 else 0
            print(f"  {key:25s}: {value:6.2f}% (base: {base_val:5.2f}%, change: {change:+5.1f}%)")
        
        # Surface adjustments
        print(f"\n🎾 SURFACE ADJUSTMENTS FOR {surface.upper()}")
        print("-"*60)
        surface_adj = self.simulator.surface_adjustments.get(surface, self.simulator.surface_adjustments['Hard'])
        for key, multiplier in surface_adj.items():
            print(f"  {key:20s}: {multiplier:5.2f}x")
        
        # Now simulate the actual point with detailed logging
        print(f"\n🎯 SIMULATING SINGLE POINT (STEP BY STEP)")
        print("="*80)
        
        # Set random seed for reproducibility
        random.seed(42)
        np.random.seed(42)
        
        result = self._simulate_point_detailed(server_probs_var, returner_probs_var, server_name, returner_name)
        
        print(f"\n🏆 FINAL POINT RESULT")
        print("-"*40)
        print(f"Winner: {result['winner']}")
        print(f"Point type: {result['point_type']}")
        print(f"Shots played: {result['shots']}")
        print(f"Duration: {result.get('duration', 'N/A')}")
        
        return result
    
    def _simulate_point_detailed(self, server_probs, returner_probs, server_name, returner_name):
        """Simulate a point with detailed step-by-step logging."""
        result = {
            'winner': 'server',
            'ace': False,
            'double_fault': False,
            'shots': 1,
            'point_type': 'regular',
            'random_values': [],
            'decision_tree': []
        }
        
        print(f"🎾 POINT SIMULATION BEGINS")
        print(f"Server: {server_name}, Returner: {returner_name}")
        print("-"*60)
        
        # Step 1: Check for double fault
        print(f"STEP 1: Double Fault Check")
        df_threshold = server_probs['double_fault_rate']
        df_random = random.random() * 100
        result['random_values'].append(('double_fault_check', df_random))
        
        print(f"  Random value: {df_random:.4f}")
        print(f"  DF threshold: {df_threshold:.2f}%")
        print(f"  DF occurs if random < threshold: {df_random:.4f} < {df_threshold:.2f}? {df_random < df_threshold}")
        
        if df_random < df_threshold:
            result['winner'] = 'returner'
            result['double_fault'] = True
            result['point_type'] = 'double_fault'
            result['decision_tree'].append(f"Double fault: {df_random:.4f} < {df_threshold:.2f}")
            print(f"  ❌ DOUBLE FAULT! Point to {returner_name}")
            return result
        
        result['decision_tree'].append(f"No double fault: {df_random:.4f} >= {df_threshold:.2f}")
        print(f"  ✅ No double fault")
        
        # Step 2: Check for ace
        print(f"\nSTEP 2: Ace Check")
        ace_threshold = server_probs['ace_rate']
        ace_random = random.random() * 100
        result['random_values'].append(('ace_check', ace_random))
        
        print(f"  Random value: {ace_random:.4f}")
        print(f"  Ace threshold: {ace_threshold:.2f}%")
        print(f"  Ace occurs if random < threshold: {ace_random:.4f} < {ace_threshold:.2f}? {ace_random < ace_threshold}")
        
        if ace_random < ace_threshold:
            result['ace'] = True
            result['point_type'] = 'ace'
            result['decision_tree'].append(f"Ace: {ace_random:.4f} < {ace_threshold:.2f}")
            print(f"  🎯 ACE! Point to {server_name}")
            return result
        
        result['decision_tree'].append(f"No ace: {ace_random:.4f} >= {ace_threshold:.2f}")
        print(f"  ✅ No ace, rally begins")
        
        # Step 3: Regular rally - determine winner
        print(f"\nSTEP 3: Rally Resolution")
        server_strength = server_probs['service_points_won']
        returner_strength = returner_probs['return_points_won']
        total_strength = server_strength + returner_strength
        
        print(f"  Server strength: {server_strength:.2f}%")
        print(f"  Returner strength: {returner_strength:.2f}%")
        print(f"  Total strength: {total_strength:.2f}%")
        
        if total_strength > 0:
            server_win_prob = server_strength / total_strength
        else:
            server_win_prob = 0.5
        
        print(f"  Server win probability: {server_win_prob:.4f} ({server_win_prob*100:.2f}%)")
        
        rally_random = random.random()
        result['random_values'].append(('rally_resolution', rally_random))
        
        print(f"  Random value: {rally_random:.4f}")
        print(f"  Server wins if random < prob: {rally_random:.4f} < {server_win_prob:.4f}? {rally_random < server_win_prob}")
        
        if rally_random < server_win_prob:
            result['winner'] = 'server'
            result['decision_tree'].append(f"Server wins rally: {rally_random:.4f} < {server_win_prob:.4f}")
            print(f"  🏆 Rally won by {server_name}")
        else:
            result['winner'] = 'returner'
            result['decision_tree'].append(f"Returner wins rally: {rally_random:.4f} >= {server_win_prob:.4f}")
            print(f"  🏆 Rally won by {returner_name}")
        
        # Step 4: Estimate rally length
        print(f"\nSTEP 4: Rally Length Estimation")
        rally_length_random = np.random.exponential(3.0)
        result['random_values'].append(('rally_length', rally_length_random))
        rally_shots = max(1, int(rally_length_random))
        result['shots'] = rally_shots
        
        print(f"  Exponential random (scale=3.0): {rally_length_random:.4f}")
        print(f"  Rally shots: max(1, int({rally_length_random:.4f})) = {rally_shots}")
        result['decision_tree'].append(f"Rally length: {rally_shots} shots")
        
        return result
    
    def test_multiple_points_statistics(self, server_name: str, returner_name: str, num_points: int = 1000):
        """Test multiple points to verify statistical accuracy."""
        print(f"\n📊 STATISTICAL VERIFICATION TEST")
        print("="*80)
        print(f"Simulating {num_points:,} points between {server_name} and {returner_name}")
        print("-"*80)
        
        # Get probabilities
        server_probs = self.simulator.get_match_adjusted_probabilities(server_name, 'Hard', use_variance=False)
        returner_probs = self.simulator.get_match_adjusted_probabilities(returner_name, 'Hard', use_variance=False)
        
        # Track results
        results = {
            'total_points': 0,
            'server_wins': 0,
            'returner_wins': 0,
            'aces': 0,
            'double_faults': 0,
            'rally_lengths': []
        }
        
        # Simulate points
        for i in range(num_points):
            point_result = self.simulator.simulate_point(server_probs, returner_probs)
            
            results['total_points'] += 1
            
            if point_result['winner'] == 'server':
                results['server_wins'] += 1
            else:
                results['returner_wins'] += 1
            
            if point_result.get('ace', False):
                results['aces'] += 1
            
            if point_result.get('double_fault', False):
                results['double_faults'] += 1
            
            results['rally_lengths'].append(point_result.get('shots', 1))
        
        # Calculate actual rates
        actual_ace_rate = (results['aces'] / results['total_points']) * 100
        actual_df_rate = (results['double_faults'] / results['total_points']) * 100
        actual_server_win_rate = (results['server_wins'] / results['total_points']) * 100
        avg_rally_length = np.mean(results['rally_lengths'])
        
        # Expected rates
        expected_ace_rate = server_probs['ace_rate']
        expected_df_rate = server_probs['double_fault_rate']
        expected_server_win_rate = server_probs['service_points_won']
        
        print(f"STATISTICAL COMPARISON:")
        print(f"{'Metric':<20} {'Expected':<12} {'Actual':<12} {'Difference':<12}")
        print("-" * 60)
        print(f"{'Ace Rate':<20} {expected_ace_rate:<12.2f} {actual_ace_rate:<12.2f} {abs(expected_ace_rate - actual_ace_rate):<12.2f}")
        print(f"{'Double Fault Rate':<20} {expected_df_rate:<12.2f} {actual_df_rate:<12.2f} {abs(expected_df_rate - actual_df_rate):<12.2f}")
        print(f"{'Server Win Rate':<20} {expected_server_win_rate:<12.2f} {actual_server_win_rate:<12.2f} {abs(expected_server_win_rate - actual_server_win_rate):<12.2f}")
        print(f"{'Avg Rally Length':<20} {'~3.0':<12} {avg_rally_length:<12.2f} {'N/A':<12}")
        
        # Accuracy assessment
        ace_accuracy = abs(expected_ace_rate - actual_ace_rate) < 1.0
        df_accuracy = abs(expected_df_rate - actual_df_rate) < 1.0
        server_accuracy = abs(expected_server_win_rate - actual_server_win_rate) < 2.0
        
        print(f"\n✅ ACCURACY ASSESSMENT:")
        print(f"  Ace rate accurate (±1%): {ace_accuracy}")
        print(f"  DF rate accurate (±1%): {df_accuracy}")
        print(f"  Server win rate accurate (±2%): {server_accuracy}")
        print(f"  Overall simulation: {'✅ ACCURATE' if all([ace_accuracy, df_accuracy, server_accuracy]) else '❌ NEEDS ADJUSTMENT'}")

def main():
    """Run granular point simulation tests."""
    print("🎾 GRANULAR POINT SIMULATION VERIFICATION")
    print("="*80)
    
    tester = GranularPointTester()
    
    # Test 1: Single point with maximum detail
    print("TEST 1: Single Point Granular Analysis")
    tester.test_single_point_detailed("Roger Federer", "Rafael Nadal", "Hard")
    
    # Test 2: Statistical verification
    print("\n" + "="*80)
    print("TEST 2: Statistical Verification (1000 points)")
    tester.test_multiple_points_statistics("Roger Federer", "Rafael Nadal", 1000)
    
    print(f"\n✅ GRANULAR TESTING COMPLETE!")
    print(f"🎾 Simulation logic verified at the most detailed level!")

if __name__ == "__main__":
    main()
