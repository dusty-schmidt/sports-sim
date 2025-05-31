#!/usr/bin/env python3
"""
Advanced Tennis Betting Analytics - Main Execution Script

This script demonstrates the complete pipeline from data loading to betting strategy generation.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data.loader import MCPDataLoader
from analyzers.point_analyzer import PointByPointAnalyzer
from features.pattern_extractor import PatternExtractor
from betting.strategy_generator import BettingStrategyGenerator
from validation.backtest_engine import BacktestEngine


def main():
    """Execute the complete tennis betting analytics pipeline."""
    print("🎾 ADVANCED TENNIS BETTING ANALYTICS")
    print("=" * 70)
    print("Complete pipeline: Data → Analysis → Patterns → Strategies → Validation")
    print("=" * 70)
    
    try:
        # Step 1: Load Data
        print("\n📁 STEP 1: DATA LOADING")
        print("-" * 40)
        loader = MCPDataLoader()
        data = loader.load_all_data()
        
        if not data or all(df.empty for df in data.values()):
            print("❌ No data loaded. Please check TMCPdata directory.")
            return
        
        # Step 2: Point-by-Point Analysis
        print("\n🔍 STEP 2: POINT-BY-POINT ANALYSIS")
        print("-" * 40)
        analyzer = PointByPointAnalyzer(loader)
        
        # Analyze men's data first
        insights = analyzer.analyze_points_data('men_points', max_points=5000)
        
        if not insights:
            print("❌ No insights generated from analysis.")
            return
        
        # Step 3: Feature Extraction (demonstration)
        print("\n🔧 STEP 3: FEATURE EXTRACTION")
        print("-" * 40)
        extractor = PatternExtractor()
        
        # Get sample data for feature extraction
        sample_data = loader.get_sample_data('men_points', 100)
        if not sample_data.empty:
            features_df = extractor.extract_all_features(sample_data)
            print(f"✅ Extracted features from {len(features_df)} sample points")
        else:
            print("⚠️ No sample data available for feature extraction")
        
        # Step 4: Strategy Generation
        print("\n💰 STEP 4: BETTING STRATEGY GENERATION")
        print("-" * 40)
        strategy_generator = BettingStrategyGenerator()
        strategies = strategy_generator.generate_strategies(insights)
        
        # Step 5: Backtesting and Validation
        print("\n📊 STEP 5: STRATEGY VALIDATION")
        print("-" * 40)
        backtest_engine = BacktestEngine()
        
        # Use sample data for backtesting
        historical_data = loader.get_sample_data('men_points', 1000)
        if not historical_data.empty:
            backtest_results = backtest_engine.backtest_strategies(strategies, historical_data)
        else:
            print("⚠️ No historical data available for backtesting")
            backtest_results = {}
        
        # Step 6: Summary and Next Steps
        print("\n🎯 STEP 6: PIPELINE SUMMARY")
        print("-" * 40)
        display_pipeline_summary(data, insights, strategies, backtest_results)
        
        # Step 7: Implementation Recommendations
        print("\n🚀 STEP 7: IMPLEMENTATION ROADMAP")
        print("-" * 40)
        display_implementation_roadmap(insights, strategies, backtest_results)
        
    except Exception as e:
        print(f"❌ Error in pipeline execution: {e}")
        print("Please check your data files and try again.")


def display_pipeline_summary(data, insights, strategies, backtest_results):
    """Display summary of the complete pipeline execution."""
    print("📊 PIPELINE EXECUTION SUMMARY:")
    print("=" * 50)
    
    # Data summary
    total_points = sum(len(df) for df in data.values() if not df.empty)
    print(f"📁 Data Loaded:")
    print(f"   • Total data points: {total_points:,}")
    print(f"   • Datasets available: {len([k for k, v in data.items() if not v.empty])}")
    
    # Analysis summary
    print(f"\n🔍 Analysis Results:")
    print(f"   • High-value patterns found: {len(insights.get('high_value_patterns', []))}")
    print(f"   • Pressure advantages identified: {len(insights.get('pressure_advantages', []))}")
    print(f"   • Momentum indicators: {len(insights.get('momentum_indicators', []))}")
    
    # Strategy summary
    total_strategies = sum(len(v) for k, v in strategies.items() if k != 'bankroll_management')
    print(f"\n💰 Strategies Generated:")
    print(f"   • Total strategies: {total_strategies}")
    print(f"   • Pre-match strategies: {len(strategies.get('pre_match', []))}")
    print(f"   • Live betting strategies: {len(strategies.get('live_betting', []))}")
    print(f"   • Prop bet strategies: {len(strategies.get('prop_bets', []))}")
    
    # Backtest summary
    if backtest_results:
        overall = backtest_results.get('overall_metrics', {})
        print(f"\n📊 Backtest Results:")
        print(f"   • Overall ROI: {overall.get('overall_roi', 0):+.1%}")
        print(f"   • Win rate: {overall.get('overall_win_rate', 0):.1%}")
        print(f"   • Profitable strategies: {overall.get('profitable_strategies', 0)}/{overall.get('total_strategies', 0)}")
    
    print("=" * 50)


def display_implementation_roadmap(insights, strategies, backtest_results):
    """Display implementation roadmap based on results."""
    print("🚀 IMPLEMENTATION ROADMAP:")
    print("=" * 50)
    
    # Assess readiness
    readiness_score = assess_implementation_readiness(insights, strategies, backtest_results)
    
    print(f"📈 Implementation Readiness: {readiness_score}/10")
    
    if readiness_score >= 8:
        print("\n✅ HIGH READINESS - Ready for live implementation")
        print("   Recommended next steps:")
        print("   1. Start with paper trading for 2-4 weeks")
        print("   2. Begin with smallest stake sizes (0.5-1% bankroll)")
        print("   3. Focus on highest-confidence strategies first")
        print("   4. Monitor performance daily and adjust as needed")
        
    elif readiness_score >= 6:
        print("\n⚠️ MEDIUM READINESS - Needs refinement before live implementation")
        print("   Recommended next steps:")
        print("   1. Expand data analysis to full dataset (400K+ points)")
        print("   2. Improve strategy selection criteria")
        print("   3. Extended backtesting on more historical data")
        print("   4. Paper trade for 4-6 weeks before going live")
        
    elif readiness_score >= 4:
        print("\n🔄 LOW READINESS - Significant development needed")
        print("   Recommended next steps:")
        print("   1. Analyze complete dataset for better patterns")
        print("   2. Develop more sophisticated models")
        print("   3. Implement real-time data processing")
        print("   4. Extended validation period (2-3 months)")
        
    else:
        print("\n❌ NOT READY - Major improvements required")
        print("   Recommended next steps:")
        print("   1. Revisit data analysis methodology")
        print("   2. Develop more robust pattern detection")
        print("   3. Improve strategy generation algorithms")
        print("   4. Extensive testing before any live implementation")
    
    # Phase-based roadmap
    print(f"\n📅 PHASE-BASED DEVELOPMENT ROADMAP:")
    print("   Phase 1 (Weeks 1-2): Complete data analysis on full dataset")
    print("   Phase 2 (Weeks 3-4): Refine strategies and validation")
    print("   Phase 3 (Weeks 5-8): Paper trading and performance monitoring")
    print("   Phase 4 (Weeks 9-12): Live implementation with small stakes")
    print("   Phase 5 (Months 4-6): Scale up and optimize")
    
    # Key metrics to track
    print(f"\n📊 KEY METRICS TO TRACK:")
    print("   • Prediction accuracy (target: 75%+)")
    print("   • ROI per strategy (target: 15%+ annually)")
    print("   • Maximum drawdown (keep under 10%)")
    print("   • Sharpe ratio (target: 1.5+)")
    print("   • Strategy hit rate (target: 70%+ profitable)")
    
    print("=" * 50)


def assess_implementation_readiness(insights, strategies, backtest_results):
    """Assess readiness for live implementation on a scale of 1-10."""
    score = 0
    
    # Data quality and insights (0-3 points)
    if insights.get('high_value_patterns'):
        score += 1
    if insights.get('pressure_advantages'):
        score += 1
    if len(insights.get('high_value_patterns', [])) >= 3:
        score += 1
    
    # Strategy quality (0-3 points)
    total_strategies = sum(len(v) for k, v in strategies.items() if k != 'bankroll_management')
    if total_strategies >= 3:
        score += 1
    if total_strategies >= 6:
        score += 1
    if strategies.get('bankroll_management'):
        score += 1
    
    # Backtest performance (0-4 points)
    if backtest_results:
        overall = backtest_results.get('overall_metrics', {})
        risk = backtest_results.get('risk_analysis', {})
        
        if overall.get('overall_roi', 0) > 0:
            score += 1
        if overall.get('overall_roi', 0) > 0.1:
            score += 1
        if overall.get('overall_win_rate', 0) > 0.6:
            score += 1
        if risk.get('risk_level') in ['Low', 'Medium']:
            score += 1
    
    return score


if __name__ == "__main__":
    main()
