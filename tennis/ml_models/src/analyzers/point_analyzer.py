"""
Point-by-Point Tennis Analysis

Analyzes tennis matches at the individual point level to extract betting insights.
"""

import pandas as pd
import re
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from data.loader import MCPDataLoader


class PointByPointAnalyzer:
    """Analyze tennis matches at the point-by-point level for betting insights."""
    
    def __init__(self, data_loader: Optional[MCPDataLoader] = None):
        """
        Initialize the analyzer.
        
        Args:
            data_loader: Optional MCPDataLoader instance
        """
        self.data_loader = data_loader or MCPDataLoader()
        self.shot_patterns = {}
        self.momentum_data = {}
        self.pressure_responses = {}
        self.betting_insights = {}
        
    def analyze_points_data(self, dataset: str = 'men_points', max_points: int = 10000) -> Dict:
        """
        Analyze point-by-point data for betting patterns.
        
        Args:
            dataset: Dataset to analyze ('men_points' or 'women_points')
            max_points: Maximum number of points to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        print(f"🔍 POINT-BY-POINT ANALYSIS: {dataset}")
        print("=" * 60)
        
        # Load data
        data = self.data_loader.load_all_data()
        
        if dataset not in data or data[dataset].empty:
            print(f"❌ Dataset '{dataset}' not found or empty")
            return {}
        
        points_df = data[dataset].head(max_points)
        print(f"📊 Analyzing {len(points_df):,} points...")
        
        # Perform analyses
        self._analyze_shot_sequences(points_df)
        self._analyze_momentum_patterns(points_df)
        self._analyze_pressure_situations(points_df)
        
        # Generate betting insights
        insights = self._generate_betting_insights()
        
        # Display results
        self._display_results(insights)
        
        return insights
    
    def _analyze_shot_sequences(self, points_df: pd.DataFrame) -> None:
        """Extract and analyze shot sequence patterns."""
        print("   🎾 Analyzing shot sequences...")
        
        sequence_patterns = defaultdict(lambda: {'count': 0, 'wins': 0})
        
        for _, point in points_df.iterrows():
            # Get shot sequence from Notes column
            sequence = point.get('Notes', '')
            winner = point.get('PtWinner', '0')
            
            if not sequence:
                continue
            
            # Extract patterns from sequence
            patterns = self._extract_shot_patterns(sequence)
            
            for pattern in patterns:
                sequence_patterns[pattern]['count'] += 1
                if str(winner) == '1':  # Server wins
                    sequence_patterns[pattern]['wins'] += 1
        
        # Calculate win rates and betting values
        self.shot_patterns = {}
        for pattern, data in sequence_patterns.items():
            if data['count'] >= 5:  # Minimum frequency threshold
                win_rate = data['wins'] / data['count']
                betting_value = self._calculate_betting_value(win_rate, data['count'])
                
                self.shot_patterns[pattern] = {
                    'frequency': data['count'],
                    'win_rate': win_rate,
                    'betting_value': betting_value,
                    'edge': (win_rate - 0.5) * 100  # Edge over 50%
                }
        
        print(f"   📈 Found {len(self.shot_patterns)} significant shot patterns")
    
    def _extract_shot_patterns(self, sequence: str) -> List[str]:
        """Extract meaningful patterns from shot sequence notation."""
        if not sequence or pd.isna(sequence):
            return []
        
        patterns = []
        sequence = str(sequence).strip()
        
        # Serve patterns (first character indicates serve placement)
        if len(sequence) > 0:
            first_char = sequence[0]
            if first_char in '123456789':
                if first_char in '147':  # Left side serves
                    patterns.append('serve_left')
                elif first_char in '369':  # Right side serves  
                    patterns.append('serve_right')
                elif first_char in '258':  # Center serves
                    patterns.append('serve_center')
                
                # Specific serve zones
                if first_char == '6':
                    patterns.append('serve_wide_deuce')
                elif first_char == '4':
                    patterns.append('serve_t_deuce')
                elif first_char == '5':
                    patterns.append('serve_body')
        
        # Shot type patterns
        if 'f' in sequence:
            patterns.append('forehand_used')
        if 'b' in sequence:
            patterns.append('backhand_used')
        
        # Outcome patterns
        if '+' in sequence:
            patterns.append('winner')
        if '@' in sequence:
            patterns.append('unforced_error')
        if '#' in sequence:
            patterns.append('ace_or_service_winner')
        if '=' in sequence:
            patterns.append('forced_error')
        
        # Rally length patterns
        shot_count = len([c for c in sequence if c in 'fb'])
        if shot_count == 0:
            patterns.append('serve_only')
        elif shot_count <= 2:
            patterns.append('short_rally')
        elif shot_count <= 5:
            patterns.append('medium_rally')
        else:
            patterns.append('long_rally')
        
        return patterns
    
    def _analyze_momentum_patterns(self, points_df: pd.DataFrame) -> None:
        """Analyze momentum shifts within matches."""
        print("   📈 Analyzing momentum patterns...")
        
        # Group points by match
        if 'match_id' in points_df.columns:
            match_groups = points_df.groupby('match_id')
        else:
            # If no match_id, treat all points as one match
            match_groups = [('single_match', points_df)]
        
        momentum_insights = {}
        
        for match_id, match_points in match_groups:
            if len(match_points) < 10:  # Skip very short matches
                continue
            
            # Calculate momentum for this match
            momentum_data = self._calculate_match_momentum(match_points)
            momentum_insights[match_id] = momentum_data
        
        self.momentum_data = momentum_insights
        print(f"   📊 Analyzed momentum for {len(momentum_insights)} matches")
    
    def _calculate_match_momentum(self, match_points: pd.DataFrame) -> Dict:
        """Calculate momentum indicators for a single match."""
        point_winners = []
        
        for _, point in match_points.iterrows():
            winner = point.get('PtWinner', '0')
            try:
                point_winners.append(int(winner))
            except (ValueError, TypeError):
                point_winners.append(0)
        
        if not point_winners:
            return {}
        
        # Calculate momentum runs
        runs = []
        current_run = 1
        current_player = point_winners[0]
        
        for winner in point_winners[1:]:
            if winner == current_player:
                current_run += 1
            else:
                runs.append((current_player, current_run))
                current_player = winner
                current_run = 1
        
        if current_run > 0:
            runs.append((current_player, current_run))
        
        # Calculate momentum statistics
        momentum_shifts = len([r for r in runs if r[1] >= 3])  # 3+ point runs
        max_run = max([r[1] for r in runs]) if runs else 0
        avg_run = sum(r[1] for r in runs) / len(runs) if runs else 0
        
        return {
            'total_points': len(point_winners),
            'momentum_shifts': momentum_shifts,
            'max_run': max_run,
            'avg_run_length': avg_run,
            'total_runs': len(runs)
        }
    
    def _analyze_pressure_situations(self, points_df: pd.DataFrame) -> None:
        """Analyze performance in pressure situations."""
        print("   🎯 Analyzing pressure situations...")
        
        pressure_performance = defaultdict(lambda: {'total': 0, 'wins': 0})
        
        for _, point in points_df.iterrows():
            # Get score information
            score_info = self._extract_score_info(point)
            winner = point.get('PtWinner', '0')
            
            # Identify pressure situations
            pressure_types = self._identify_pressure_situations(score_info)
            
            for pressure_type in pressure_types:
                pressure_performance[pressure_type]['total'] += 1
                if str(winner) == '1':  # Server wins
                    pressure_performance[pressure_type]['wins'] += 1
        
        # Calculate pressure performance metrics
        self.pressure_responses = {}
        for pressure_type, data in pressure_performance.items():
            if data['total'] >= 3:  # Minimum sample size
                win_rate = data['wins'] / data['total']
                pressure_impact = win_rate - 0.5  # Deviation from 50%
                
                self.pressure_responses[pressure_type] = {
                    'frequency': data['total'],
                    'win_rate': win_rate,
                    'pressure_impact': pressure_impact,
                    'edge': pressure_impact * 100
                }
        
        print(f"   📊 Analyzed {len(self.pressure_responses)} pressure situations")
    
    def _extract_score_info(self, point: pd.Series) -> Dict:
        """Extract score information from point data."""
        score_info = {}
        
        # Try to get score from various possible columns
        score_columns = ['Pts', 'Score', 'GameScore', 'score']
        for col in score_columns:
            if col in point and pd.notna(point[col]):
                score_info['game_score'] = str(point[col])
                break
        
        # Try to get set score
        set_columns = ['SetScore', 'Sets', 'set_score']
        for col in set_columns:
            if col in point and pd.notna(point[col]):
                score_info['set_score'] = str(point[col])
                break
        
        return score_info
    
    def _identify_pressure_situations(self, score_info: Dict) -> List[str]:
        """Identify pressure situations from score information."""
        pressure_types = []
        
        game_score = score_info.get('game_score', '')
        
        if not game_score:
            return pressure_types
        
        # Break point situations
        if any(bp in game_score for bp in ['40-30', '40-AD', 'AD-40', '30-40']):
            pressure_types.append('break_point')
        
        # Deuce situations
        if '40-40' in game_score or 'Deuce' in game_score:
            pressure_types.append('deuce')
        
        # Game point situations
        if '40-' in game_score and '40-40' not in game_score:
            pressure_types.append('game_point')
        
        # Set point situations (would need set score analysis)
        set_score = score_info.get('set_score', '')
        if set_score and any(sp in set_score for sp in ['6-5', '5-6', '7-6', '6-7']):
            pressure_types.append('set_point_game')
        
        return pressure_types
    
    def _calculate_betting_value(self, win_rate: float, frequency: int) -> float:
        """Calculate betting value of a pattern."""
        # Higher value for patterns that deviate significantly from 50%
        # and have reasonable frequency
        deviation = abs(win_rate - 0.5)
        frequency_weight = min(frequency / 20, 1.0)  # Cap at 20 occurrences
        
        return deviation * frequency_weight
    
    def _generate_betting_insights(self) -> Dict:
        """Generate actionable betting insights from analysis."""
        insights = {
            'high_value_patterns': [],
            'momentum_indicators': [],
            'pressure_advantages': [],
            'betting_recommendations': []
        }
        
        # High-value shot patterns
        if self.shot_patterns:
            sorted_patterns = sorted(
                self.shot_patterns.items(),
                key=lambda x: x[1]['betting_value'],
                reverse=True
            )
            
            for pattern, data in sorted_patterns[:10]:  # Top 10 patterns
                insights['high_value_patterns'].append({
                    'pattern': pattern,
                    'win_rate': data['win_rate'],
                    'frequency': data['frequency'],
                    'edge': data['edge']
                })
        
        # Momentum insights
        if self.momentum_data:
            total_matches = len(self.momentum_data)
            avg_shifts = sum(m.get('momentum_shifts', 0) for m in self.momentum_data.values()) / total_matches
            avg_max_run = sum(m.get('max_run', 0) for m in self.momentum_data.values()) / total_matches
            
            insights['momentum_indicators'].append({
                'avg_momentum_shifts_per_match': avg_shifts,
                'avg_max_run_length': avg_max_run,
                'total_matches_analyzed': total_matches
            })
        
        # Pressure advantages
        if self.pressure_responses:
            for pressure_type, data in self.pressure_responses.items():
                if abs(data['pressure_impact']) > 0.05:  # Significant impact (>5%)
                    insights['pressure_advantages'].append({
                        'situation': pressure_type,
                        'win_rate': data['win_rate'],
                        'edge': data['edge'],
                        'frequency': data['frequency']
                    })
        
        # Generate betting recommendations
        insights['betting_recommendations'] = self._generate_recommendations(insights)
        
        return insights
    
    def _generate_recommendations(self, insights: Dict) -> List[Dict]:
        """Generate specific betting recommendations."""
        recommendations = []
        
        # Pattern-based recommendations
        for pattern in insights['high_value_patterns']:
            if abs(pattern['edge']) > 5:  # >5% edge
                direction = 'for' if pattern['edge'] > 0 else 'against'
                recommendations.append({
                    'type': 'pattern_betting',
                    'description': f"Live bet {direction} server when {pattern['pattern']} occurs",
                    'edge': f"{pattern['edge']:+.1f}%",
                    'confidence': 'High' if pattern['frequency'] > 10 else 'Medium',
                    'frequency': pattern['frequency']
                })
        
        # Pressure-based recommendations
        for pressure in insights['pressure_advantages']:
            if abs(pressure['edge']) > 8:  # >8% edge
                direction = 'for' if pressure['edge'] > 0 else 'against'
                recommendations.append({
                    'type': 'pressure_betting',
                    'description': f"Bet {direction} server in {pressure['situation']}",
                    'edge': f"{pressure['edge']:+.1f}%",
                    'confidence': 'High',
                    'frequency': pressure['frequency']
                })
        
        return recommendations
    
    def _display_results(self, insights: Dict) -> None:
        """Display analysis results."""
        print("\n📊 BETTING INSIGHTS DISCOVERED:")
        print("=" * 60)
        
        # High-value patterns
        if insights['high_value_patterns']:
            print("\n🎯 High-Value Shot Patterns:")
            for pattern in insights['high_value_patterns'][:5]:
                print(f"   • {pattern['pattern']}: {pattern['win_rate']:.1%} win rate "
                      f"({pattern['edge']:+.1f}% edge, {pattern['frequency']} occurrences)")
        
        # Pressure advantages
        if insights['pressure_advantages']:
            print("\n⚡ Pressure Situation Advantages:")
            for pressure in insights['pressure_advantages']:
                print(f"   • {pressure['situation']}: {pressure['win_rate']:.1%} win rate "
                      f"({pressure['edge']:+.1f}% edge, {pressure['frequency']} occurrences)")
        
        # Momentum insights
        if insights['momentum_indicators']:
            print("\n📈 Momentum Insights:")
            for momentum in insights['momentum_indicators']:
                print(f"   • Average momentum shifts per match: {momentum['avg_momentum_shifts_per_match']:.1f}")
                print(f"   • Average max run length: {momentum['avg_max_run_length']:.1f}")
        
        # Betting recommendations
        if insights['betting_recommendations']:
            print("\n💰 BETTING RECOMMENDATIONS:")
            for rec in insights['betting_recommendations'][:5]:
                print(f"   • {rec['description']}")
                print(f"     Edge: {rec['edge']}, Confidence: {rec['confidence']}")


def main():
    """Demonstrate point-by-point analysis."""
    print("🎾 POINT-BY-POINT TENNIS ANALYSIS")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = PointByPointAnalyzer()
    
    # Analyze men's points
    insights = analyzer.analyze_points_data('men_points', max_points=5000)
    
    print("\n" + "=" * 60)
    print("💡 Analysis complete! Found betting opportunities in:")
    print(f"   • {len(insights.get('high_value_patterns', []))} shot patterns")
    print(f"   • {len(insights.get('pressure_advantages', []))} pressure situations")
    print(f"   • {len(insights.get('betting_recommendations', []))} actionable recommendations")


if __name__ == "__main__":
    main()
