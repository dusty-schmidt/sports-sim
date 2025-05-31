"""
Betting Strategy Generator

Generates actionable betting strategies from tennis analysis insights.
"""

import pandas as pd
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import math


class BettingStrategyGenerator:
    """Generate betting strategies from tennis analysis insights."""
    
    def __init__(self):
        """Initialize the strategy generator."""
        self.strategies = {}
        self.bankroll_management = {}
        
    def generate_strategies(self, insights: Dict) -> Dict[str, List[Dict]]:
        """
        Generate betting strategies from analysis insights.
        
        Args:
            insights: Dictionary containing analysis insights
            
        Returns:
            Dictionary of betting strategies by category
        """
        print("💰 GENERATING BETTING STRATEGIES")
        print("=" * 50)
        
        strategies = {
            'pre_match': [],
            'live_betting': [],
            'prop_bets': [],
            'arbitrage': []
        }
        
        # Generate pre-match strategies
        strategies['pre_match'] = self._generate_pre_match_strategies(insights)
        
        # Generate live betting strategies
        strategies['live_betting'] = self._generate_live_strategies(insights)
        
        # Generate prop bet strategies
        strategies['prop_bets'] = self._generate_prop_strategies(insights)
        
        # Add bankroll management
        strategies['bankroll_management'] = self._generate_bankroll_strategy()
        
        self._display_strategies(strategies)
        
        return strategies
    
    def _generate_pre_match_strategies(self, insights: Dict) -> List[Dict]:
        """Generate pre-match betting strategies."""
        print("   🎯 Generating pre-match strategies...")
        
        strategies = []
        
        # Pattern-based pre-match strategies
        high_value_patterns = insights.get('high_value_patterns', [])
        
        for pattern in high_value_patterns:
            if abs(pattern['edge']) > 8:  # Strong edge threshold
                strategy = {
                    'name': f"Pre-match {pattern['pattern']} Strategy",
                    'description': f"Bet based on {pattern['pattern']} historical performance",
                    'edge': pattern['edge'],
                    'confidence': 'High' if pattern['frequency'] > 15 else 'Medium',
                    'bet_type': 'match_winner',
                    'trigger': f"Player historically strong in {pattern['pattern']}",
                    'stake_percentage': self._calculate_kelly_stake(pattern['edge'], 0.75),
                    'expected_roi': pattern['edge'] * 0.6  # Conservative estimate
                }
                strategies.append(strategy)
        
        # Pressure-based pre-match strategies
        pressure_advantages = insights.get('pressure_advantages', [])
        
        for pressure in pressure_advantages:
            if abs(pressure['edge']) > 10:  # Strong pressure edge
                strategy = {
                    'name': f"Pre-match {pressure['situation']} Strategy",
                    'description': f"Target players strong/weak in {pressure['situation']}",
                    'edge': pressure['edge'],
                    'confidence': 'High',
                    'bet_type': 'match_winner',
                    'trigger': f"Historical {pressure['situation']} performance differential",
                    'stake_percentage': self._calculate_kelly_stake(pressure['edge'], 0.8),
                    'expected_roi': pressure['edge'] * 0.7
                }
                strategies.append(strategy)
        
        return strategies
    
    def _generate_live_strategies(self, insights: Dict) -> List[Dict]:
        """Generate live betting strategies."""
        print("   ⚡ Generating live betting strategies...")
        
        strategies = []
        
        # Momentum-based live strategies
        momentum_indicators = insights.get('momentum_indicators', [])
        
        if momentum_indicators:
            momentum = momentum_indicators[0]  # Take first momentum indicator
            
            strategy = {
                'name': "Live Momentum Reversal Strategy",
                'description': "Bet against extreme momentum (mean reversion)",
                'edge': 8.5,  # Estimated edge from momentum analysis
                'confidence': 'Medium',
                'bet_type': 'next_game_winner',
                'trigger': f"Player on {momentum.get('avg_max_run_length', 4):.0f}+ point run",
                'stake_percentage': 2.0,  # Conservative live betting
                'expected_roi': 12.0,
                'timing': 'During games with momentum runs'
            }
            strategies.append(strategy)
        
        # Pattern-based live strategies
        high_value_patterns = insights.get('high_value_patterns', [])
        
        for pattern in high_value_patterns[:3]:  # Top 3 patterns for live betting
            if pattern['frequency'] > 5:  # Sufficient frequency for live betting
                strategy = {
                    'name': f"Live {pattern['pattern']} Strategy",
                    'description': f"Live bet when {pattern['pattern']} pattern emerges",
                    'edge': pattern['edge'],
                    'confidence': 'High' if pattern['frequency'] > 10 else 'Medium',
                    'bet_type': 'next_point_winner',
                    'trigger': f"Real-time detection of {pattern['pattern']}",
                    'stake_percentage': self._calculate_kelly_stake(pattern['edge'], 0.6),
                    'expected_roi': pattern['edge'] * 0.8,
                    'timing': 'Real-time during points'
                }
                strategies.append(strategy)
        
        # Pressure situation live strategies
        pressure_advantages = insights.get('pressure_advantages', [])
        
        for pressure in pressure_advantages:
            if pressure['frequency'] > 3:  # Sufficient occurrences
                strategy = {
                    'name': f"Live {pressure['situation']} Strategy",
                    'description': f"Live bet in {pressure['situation']} based on player tendencies",
                    'edge': pressure['edge'],
                    'confidence': 'High',
                    'bet_type': 'point_winner',
                    'trigger': f"Real-time {pressure['situation']} detection",
                    'stake_percentage': self._calculate_kelly_stake(pressure['edge'], 0.7),
                    'expected_roi': pressure['edge'] * 0.75,
                    'timing': f"During {pressure['situation']} situations"
                }
                strategies.append(strategy)
        
        return strategies
    
    def _generate_prop_strategies(self, insights: Dict) -> List[Dict]:
        """Generate prop bet strategies."""
        print("   🎲 Generating prop bet strategies...")
        
        strategies = []
        
        # Rally length prop bets
        high_value_patterns = insights.get('high_value_patterns', [])
        rally_patterns = [p for p in high_value_patterns if 'rally' in p['pattern']]
        
        for pattern in rally_patterns:
            if abs(pattern['edge']) > 6:
                strategy = {
                    'name': f"Rally Length Prop Strategy",
                    'description': f"Bet on rally length based on {pattern['pattern']} tendencies",
                    'edge': pattern['edge'],
                    'confidence': 'Medium',
                    'bet_type': 'total_rally_length',
                    'trigger': f"Player matchup favors {pattern['pattern']}",
                    'stake_percentage': 1.5,
                    'expected_roi': pattern['edge'] * 0.5,
                    'prop_details': f"Over/Under rally length based on {pattern['pattern']}"
                }
                strategies.append(strategy)
        
        # Ace/Double fault prop bets
        ace_patterns = [p for p in high_value_patterns if 'ace' in p['pattern'] or 'serve' in p['pattern']]
        
        for pattern in ace_patterns:
            if abs(pattern['edge']) > 5:
                strategy = {
                    'name': "Serve Performance Prop Strategy",
                    'description': f"Bet on serve stats based on {pattern['pattern']} analysis",
                    'edge': pattern['edge'],
                    'confidence': 'Medium',
                    'bet_type': 'total_aces',
                    'trigger': f"Server historically strong/weak in {pattern['pattern']}",
                    'stake_percentage': 1.0,
                    'expected_roi': pattern['edge'] * 0.4,
                    'prop_details': f"Over/Under aces based on {pattern['pattern']}"
                }
                strategies.append(strategy)
        
        # Break point conversion props
        pressure_advantages = insights.get('pressure_advantages', [])
        bp_advantages = [p for p in pressure_advantages if 'break' in p['situation']]
        
        for pressure in bp_advantages:
            strategy = {
                'name': "Break Point Conversion Prop Strategy",
                'description': f"Bet on break point conversion rates",
                'edge': pressure['edge'],
                'confidence': 'High',
                'bet_type': 'break_point_conversion',
                'trigger': f"Player differential in {pressure['situation']}",
                'stake_percentage': 2.0,
                'expected_roi': pressure['edge'] * 0.6,
                'prop_details': f"Over/Under break point conversion based on analysis"
            }
            strategies.append(strategy)
        
        return strategies
    
    def _generate_bankroll_strategy(self) -> Dict:
        """Generate bankroll management strategy."""
        print("   💼 Generating bankroll management strategy...")
        
        return {
            'name': "Conservative Kelly Criterion",
            'description': "Fractional Kelly betting with risk management",
            'max_stake_per_bet': 5.0,  # Maximum 5% of bankroll
            'kelly_fraction': 0.25,    # Use 25% of full Kelly
            'daily_loss_limit': 10.0,  # Stop at 10% daily loss
            'profit_target': 25.0,     # Take profits at 25% gain
            'minimum_edge': 5.0,       # Only bet with 5%+ edge
            'maximum_bets_per_day': 10,
            'diversification': "Spread bets across different bet types",
            'record_keeping': "Track all bets with edge, stake, and outcome"
        }
    
    def _calculate_kelly_stake(self, edge_percent: float, confidence: float) -> float:
        """
        Calculate Kelly Criterion stake percentage.
        
        Args:
            edge_percent: Expected edge percentage
            confidence: Confidence in the edge (0-1)
            
        Returns:
            Stake percentage of bankroll
        """
        # Convert edge to decimal
        edge = abs(edge_percent) / 100
        
        # Assume average odds of 1.9 (slight favorite)
        odds = 1.9
        win_probability = (edge + 0.5)  # Add edge to 50% baseline
        
        # Kelly formula: f = (bp - q) / b
        # where b = odds-1, p = win probability, q = 1-p
        b = odds - 1
        p = win_probability
        q = 1 - p
        
        kelly_fraction = (b * p - q) / b
        
        # Apply confidence factor and cap at reasonable limits
        adjusted_kelly = kelly_fraction * confidence
        
        # Cap between 0.5% and 5% of bankroll
        return max(0.5, min(5.0, adjusted_kelly * 100))
    
    def _display_strategies(self, strategies: Dict) -> None:
        """Display generated strategies."""
        print("\n💰 GENERATED BETTING STRATEGIES:")
        print("=" * 60)
        
        for category, strategy_list in strategies.items():
            if category == 'bankroll_management':
                print(f"\n💼 {category.upper().replace('_', ' ')}:")
                bankroll = strategy_list
                print(f"   • Strategy: {bankroll['name']}")
                print(f"   • Max stake per bet: {bankroll['max_stake_per_bet']}%")
                print(f"   • Minimum edge required: {bankroll['minimum_edge']}%")
                continue
            
            if strategy_list:
                print(f"\n🎯 {category.upper().replace('_', ' ')} STRATEGIES:")
                
                for i, strategy in enumerate(strategy_list[:3], 1):  # Show top 3
                    print(f"   {i}. {strategy['name']}")
                    print(f"      Edge: {strategy['edge']:+.1f}% | Confidence: {strategy['confidence']}")
                    print(f"      Stake: {strategy['stake_percentage']:.1f}% | Expected ROI: {strategy['expected_roi']:+.1f}%")
                    print(f"      Trigger: {strategy['trigger']}")
        
        print("\n" + "=" * 60)
        print("📊 STRATEGY SUMMARY:")
        total_strategies = sum(len(v) for k, v in strategies.items() if k != 'bankroll_management')
        print(f"   • Total strategies generated: {total_strategies}")
        print(f"   • Pre-match opportunities: {len(strategies['pre_match'])}")
        print(f"   • Live betting opportunities: {len(strategies['live_betting'])}")
        print(f"   • Prop bet opportunities: {len(strategies['prop_bets'])}")


def main():
    """Demonstrate strategy generation."""
    print("💰 BETTING STRATEGY GENERATOR DEMONSTRATION")
    print("=" * 60)
    
    # Sample insights (would come from analysis)
    sample_insights = {
        'high_value_patterns': [
            {'pattern': 'serve_wide_deuce', 'edge': 12.3, 'frequency': 18},
            {'pattern': 'short_rally', 'edge': 8.7, 'frequency': 25},
            {'pattern': 'ace_or_service_winner', 'edge': 15.2, 'frequency': 12}
        ],
        'pressure_advantages': [
            {'situation': 'break_point', 'edge': 14.3, 'frequency': 8},
            {'situation': 'deuce', 'edge': 9.1, 'frequency': 12}
        ],
        'momentum_indicators': [
            {'avg_momentum_shifts_per_match': 3.2, 'avg_max_run_length': 4.1}
        ]
    }
    
    # Generate strategies
    generator = BettingStrategyGenerator()
    strategies = generator.generate_strategies(sample_insights)
    
    print("\n💡 Strategy generation complete!")
    print("   Ready for implementation and backtesting.")


if __name__ == "__main__":
    main()
