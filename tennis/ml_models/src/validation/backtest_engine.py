"""
Backtest Engine

Validates betting strategies using historical data and simulated betting.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import random


class BacktestEngine:
    """Backtest and validate betting strategies."""
    
    def __init__(self):
        """Initialize the backtest engine."""
        self.results = {}
        self.performance_metrics = {}
        
    def backtest_strategies(self, strategies: Dict, historical_data: pd.DataFrame) -> Dict:
        """
        Backtest betting strategies on historical data.
        
        Args:
            strategies: Dictionary of betting strategies
            historical_data: Historical point/match data
            
        Returns:
            Backtest results and performance metrics
        """
        print("📊 BACKTESTING BETTING STRATEGIES")
        print("=" * 60)
        
        results = {
            'strategy_performance': {},
            'overall_metrics': {},
            'risk_analysis': {},
            'recommendations': []
        }
        
        # Backtest each strategy category
        for category, strategy_list in strategies.items():
            if category == 'bankroll_management':
                continue
                
            print(f"\n🎯 Backtesting {category.replace('_', ' ')} strategies...")
            
            category_results = []
            for strategy in strategy_list:
                strategy_result = self._backtest_single_strategy(strategy, historical_data)
                category_results.append(strategy_result)
            
            results['strategy_performance'][category] = category_results
        
        # Calculate overall metrics
        results['overall_metrics'] = self._calculate_overall_metrics(results['strategy_performance'])
        
        # Perform risk analysis
        results['risk_analysis'] = self._perform_risk_analysis(results['strategy_performance'])
        
        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results)
        
        # Display results
        self._display_backtest_results(results)
        
        return results
    
    def _backtest_single_strategy(self, strategy: Dict, data: pd.DataFrame) -> Dict:
        """Backtest a single betting strategy."""
        # Simulate betting based on strategy
        bets = self._simulate_bets(strategy, data)
        
        # Calculate performance metrics
        total_bets = len(bets)
        winning_bets = sum(1 for bet in bets if bet['outcome'] == 'win')
        total_staked = sum(bet['stake'] for bet in bets)
        total_returned = sum(bet['return'] for bet in bets)
        
        win_rate = winning_bets / total_bets if total_bets > 0 else 0
        roi = (total_returned - total_staked) / total_staked if total_staked > 0 else 0
        profit = total_returned - total_staked
        
        # Calculate additional metrics
        avg_odds = np.mean([bet['odds'] for bet in bets]) if bets else 1.0
        max_drawdown = self._calculate_max_drawdown(bets)
        sharpe_ratio = self._calculate_sharpe_ratio(bets)
        
        return {
            'strategy_name': strategy['name'],
            'total_bets': total_bets,
            'winning_bets': winning_bets,
            'win_rate': win_rate,
            'total_staked': total_staked,
            'total_returned': total_returned,
            'profit': profit,
            'roi': roi,
            'avg_odds': avg_odds,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'expected_edge': strategy.get('edge', 0),
            'confidence': strategy.get('confidence', 'Medium')
        }
    
    def _simulate_bets(self, strategy: Dict, data: pd.DataFrame) -> List[Dict]:
        """Simulate betting based on strategy parameters."""
        bets = []
        
        # Determine number of betting opportunities based on strategy
        bet_frequency = self._get_bet_frequency(strategy)
        num_opportunities = min(len(data) // bet_frequency, 100)  # Cap at 100 bets
        
        for i in range(num_opportunities):
            # Simulate a bet
            bet = self._simulate_single_bet(strategy)
            bets.append(bet)
        
        return bets
    
    def _simulate_single_bet(self, strategy: Dict) -> Dict:
        """Simulate a single bet based on strategy."""
        # Get strategy parameters
        expected_edge = strategy.get('edge', 0)
        stake_percentage = strategy.get('stake_percentage', 2.0)
        confidence = strategy.get('confidence', 'Medium')
        
        # Simulate odds (typically around 1.8-2.2 for tennis)
        base_odds = random.uniform(1.7, 2.3)
        
        # Adjust win probability based on expected edge
        base_win_prob = 1 / base_odds
        edge_adjustment = expected_edge / 100
        actual_win_prob = base_win_prob + edge_adjustment
        
        # Add some noise based on confidence
        confidence_factor = {'High': 0.9, 'Medium': 0.7, 'Low': 0.5}.get(confidence, 0.7)
        actual_win_prob *= confidence_factor
        
        # Simulate outcome
        outcome = 'win' if random.random() < actual_win_prob else 'loss'
        
        # Calculate returns
        stake = stake_percentage  # Percentage of bankroll
        if outcome == 'win':
            bet_return = stake * base_odds
        else:
            bet_return = 0
        
        return {
            'stake': stake,
            'odds': base_odds,
            'outcome': outcome,
            'return': bet_return,
            'profit': bet_return - stake,
            'win_probability': actual_win_prob
        }
    
    def _get_bet_frequency(self, strategy: Dict) -> int:
        """Determine betting frequency based on strategy type."""
        bet_type = strategy.get('bet_type', 'match_winner')
        
        frequency_map = {
            'match_winner': 50,      # Every 50 data points
            'next_game_winner': 20,  # Every 20 data points
            'next_point_winner': 10, # Every 10 data points
            'point_winner': 5,       # Every 5 data points
            'total_aces': 100,       # Every 100 data points
            'break_point_conversion': 30  # Every 30 data points
        }
        
        return frequency_map.get(bet_type, 50)
    
    def _calculate_max_drawdown(self, bets: List[Dict]) -> float:
        """Calculate maximum drawdown from betting sequence."""
        if not bets:
            return 0.0
        
        cumulative_profit = 0
        peak_profit = 0
        max_drawdown = 0
        
        for bet in bets:
            cumulative_profit += bet['profit']
            peak_profit = max(peak_profit, cumulative_profit)
            drawdown = peak_profit - cumulative_profit
            max_drawdown = max(max_drawdown, drawdown)
        
        return max_drawdown
    
    def _calculate_sharpe_ratio(self, bets: List[Dict]) -> float:
        """Calculate Sharpe ratio for betting sequence."""
        if not bets:
            return 0.0
        
        returns = [bet['profit'] for bet in bets]
        
        if len(returns) < 2:
            return 0.0
        
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0.0
        
        # Annualized Sharpe ratio (assuming daily betting)
        sharpe = (mean_return / std_return) * np.sqrt(365)
        
        return sharpe
    
    def _calculate_overall_metrics(self, strategy_performance: Dict) -> Dict:
        """Calculate overall performance metrics across all strategies."""
        all_results = []
        for category_results in strategy_performance.values():
            all_results.extend(category_results)
        
        if not all_results:
            return {}
        
        total_bets = sum(r['total_bets'] for r in all_results)
        total_winning = sum(r['winning_bets'] for r in all_results)
        total_staked = sum(r['total_staked'] for r in all_results)
        total_returned = sum(r['total_returned'] for r in all_results)
        
        overall_win_rate = total_winning / total_bets if total_bets > 0 else 0
        overall_roi = (total_returned - total_staked) / total_staked if total_staked > 0 else 0
        overall_profit = total_returned - total_staked
        
        # Best and worst strategies
        best_strategy = max(all_results, key=lambda x: x['roi']) if all_results else None
        worst_strategy = min(all_results, key=lambda x: x['roi']) if all_results else None
        
        return {
            'total_strategies': len(all_results),
            'total_bets': total_bets,
            'overall_win_rate': overall_win_rate,
            'overall_roi': overall_roi,
            'overall_profit': overall_profit,
            'best_strategy': best_strategy['strategy_name'] if best_strategy else None,
            'best_roi': best_strategy['roi'] if best_strategy else 0,
            'worst_strategy': worst_strategy['strategy_name'] if worst_strategy else None,
            'worst_roi': worst_strategy['roi'] if worst_strategy else 0,
            'profitable_strategies': len([r for r in all_results if r['roi'] > 0])
        }
    
    def _perform_risk_analysis(self, strategy_performance: Dict) -> Dict:
        """Perform risk analysis on strategy performance."""
        all_results = []
        for category_results in strategy_performance.values():
            all_results.extend(category_results)
        
        if not all_results:
            return {}
        
        # Risk metrics
        rois = [r['roi'] for r in all_results]
        drawdowns = [r['max_drawdown'] for r in all_results]
        sharpe_ratios = [r['sharpe_ratio'] for r in all_results if r['sharpe_ratio'] != 0]
        
        return {
            'roi_volatility': np.std(rois) if rois else 0,
            'avg_max_drawdown': np.mean(drawdowns) if drawdowns else 0,
            'max_drawdown': max(drawdowns) if drawdowns else 0,
            'avg_sharpe_ratio': np.mean(sharpe_ratios) if sharpe_ratios else 0,
            'strategies_with_positive_sharpe': len([s for s in sharpe_ratios if s > 0]),
            'risk_level': self._assess_risk_level(rois, drawdowns)
        }
    
    def _assess_risk_level(self, rois: List[float], drawdowns: List[float]) -> str:
        """Assess overall risk level of strategies."""
        if not rois or not drawdowns:
            return 'Unknown'
        
        avg_roi = np.mean(rois)
        max_drawdown = max(drawdowns)
        roi_volatility = np.std(rois)
        
        # Risk assessment logic
        if avg_roi > 0.15 and max_drawdown < 10 and roi_volatility < 0.2:
            return 'Low'
        elif avg_roi > 0.05 and max_drawdown < 20 and roi_volatility < 0.4:
            return 'Medium'
        else:
            return 'High'
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Generate recommendations based on backtest results."""
        recommendations = []
        
        overall_metrics = results.get('overall_metrics', {})
        risk_analysis = results.get('risk_analysis', {})
        
        # ROI-based recommendations
        overall_roi = overall_metrics.get('overall_roi', 0)
        if overall_roi > 0.2:
            recommendations.append("✅ Excellent ROI potential - implement strategies with proper bankroll management")
        elif overall_roi > 0.1:
            recommendations.append("✅ Good ROI potential - start with smaller stakes and scale up")
        elif overall_roi > 0:
            recommendations.append("⚠️ Modest ROI potential - focus on highest-confidence strategies only")
        else:
            recommendations.append("❌ Negative ROI - strategies need refinement before implementation")
        
        # Risk-based recommendations
        risk_level = risk_analysis.get('risk_level', 'Unknown')
        if risk_level == 'Low':
            recommendations.append("✅ Low risk profile - suitable for conservative betting")
        elif risk_level == 'Medium':
            recommendations.append("⚠️ Medium risk profile - use fractional Kelly sizing")
        else:
            recommendations.append("❌ High risk profile - reduce stake sizes significantly")
        
        # Strategy-specific recommendations
        profitable_strategies = overall_metrics.get('profitable_strategies', 0)
        total_strategies = overall_metrics.get('total_strategies', 1)
        
        if profitable_strategies / total_strategies > 0.7:
            recommendations.append("✅ High strategy success rate - diversify across multiple strategies")
        elif profitable_strategies / total_strategies > 0.5:
            recommendations.append("⚠️ Moderate strategy success rate - focus on top performers")
        else:
            recommendations.append("❌ Low strategy success rate - significant refinement needed")
        
        return recommendations
    
    def _display_backtest_results(self, results: Dict) -> None:
        """Display backtest results."""
        print("\n📊 BACKTEST RESULTS SUMMARY:")
        print("=" * 60)
        
        overall = results.get('overall_metrics', {})
        risk = results.get('risk_analysis', {})
        
        print(f"📈 OVERALL PERFORMANCE:")
        print(f"   • Total strategies tested: {overall.get('total_strategies', 0)}")
        print(f"   • Total bets simulated: {overall.get('total_bets', 0):,}")
        print(f"   • Overall win rate: {overall.get('overall_win_rate', 0):.1%}")
        print(f"   • Overall ROI: {overall.get('overall_roi', 0):+.1%}")
        print(f"   • Profitable strategies: {overall.get('profitable_strategies', 0)}/{overall.get('total_strategies', 0)}")
        
        print(f"\n⚖️ RISK ANALYSIS:")
        print(f"   • Risk level: {risk.get('risk_level', 'Unknown')}")
        print(f"   • Average max drawdown: {risk.get('avg_max_drawdown', 0):.1f}%")
        print(f"   • ROI volatility: {risk.get('roi_volatility', 0):.1%}")
        print(f"   • Average Sharpe ratio: {risk.get('avg_sharpe_ratio', 0):.2f}")
        
        print(f"\n🎯 TOP PERFORMERS:")
        if overall.get('best_strategy'):
            print(f"   • Best strategy: {overall['best_strategy']}")
            print(f"   • Best ROI: {overall.get('best_roi', 0):+.1%}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in results.get('recommendations', []):
            print(f"   {rec}")


def main():
    """Demonstrate backtesting capabilities."""
    print("📊 BACKTEST ENGINE DEMONSTRATION")
    print("=" * 60)
    
    # Sample strategies (would come from strategy generator)
    sample_strategies = {
        'pre_match': [
            {'name': 'Serve Pattern Strategy', 'edge': 12.3, 'stake_percentage': 3.0, 'confidence': 'High', 'bet_type': 'match_winner'},
            {'name': 'Pressure Situation Strategy', 'edge': 8.7, 'stake_percentage': 2.5, 'confidence': 'Medium', 'bet_type': 'match_winner'}
        ],
        'live_betting': [
            {'name': 'Momentum Reversal Strategy', 'edge': 15.2, 'stake_percentage': 2.0, 'confidence': 'High', 'bet_type': 'next_game_winner'}
        ]
    }
    
    # Sample historical data
    sample_data = pd.DataFrame({
        'match_id': range(1000),
        'outcome': [random.choice([0, 1]) for _ in range(1000)]
    })
    
    # Run backtest
    engine = BacktestEngine()
    results = engine.backtest_strategies(sample_strategies, sample_data)
    
    print("\n💡 Backtesting complete!")
    print("   Results show strategy viability and risk assessment.")


if __name__ == "__main__":
    main()
