"""
Validation and Testing Tools for Betting Market Tennis Simulator

Clean testing interface for validating simulation accuracy.
"""

from typing import Dict, List
import logging

try:
    from .odds_converter import BettingMarket, OddsConverter, SAMPLE_MARKETS
    from .probability_engine import ProbabilityEngine
    from .match_simulator import BettingSimulator
    from .results_tracker import MatchResult, SimulationResults
except ImportError:
    from odds_converter import BettingMarket, OddsConverter, SAMPLE_MARKETS
    from probability_engine import ProbabilityEngine
    from match_simulator import BettingSimulator
    from results_tracker import MatchResult, SimulationResults


class BettingSimulatorValidator:
    """Validates betting simulator accuracy against market expectations."""

    def __init__(self, seed: int = 42):
        """Initialize validator with reproducible seed."""
        self.simulator = BettingSimulator(seed)
        self.probability_engine = ProbabilityEngine(seed)

        # Setup minimal logging
        logging.basicConfig(level=logging.WARNING)

    def validate_single_market(self, market: BettingMarket,
                              num_simulations: int = 800) -> Dict[str, float]:
        """
        Validate a single betting market for accuracy.

        Args:
            market: BettingMarket to validate
            num_simulations: Number of simulations to run

        Returns:
            Validation results with accuracy metrics
        """
        # Get expected probability from odds
        if not market.player1_ml or not market.player2_ml:
            raise ValueError("Market must have moneyline odds for validation")

        odds_analysis = OddsConverter.analyze_moneyline(market.player1_ml, market.player2_ml)
        expected_p1_prob = odds_analysis['player1_match_prob']

        # Run simulations
        results = self.simulator.simulate_multiple_matches(market, num_simulations)

        # Calculate actual win rate
        p1_wins = sum(1 for r in results if r.winner == market.player1)
        actual_p1_prob = p1_wins / len(results)

        # Calculate error
        error = abs(expected_p1_prob - actual_p1_prob)
        error_percentage = error * 100

        return {
            'market': f"{market.player1} vs {market.player2}",
            'moneyline': f"{market.player1_ml} / {market.player2_ml}",
            'expected_p1_prob': expected_p1_prob,
            'actual_p1_prob': actual_p1_prob,
            'error': error,
            'error_percentage': error_percentage,
            'within_tolerance': error_percentage <= 5.0,  # 5% tolerance
            'num_simulations': num_simulations
        }

    def validate_all_sample_markets(self, num_simulations: int = 500) -> Dict[str, any]:
        """
        Validate all sample markets for overall accuracy.

        Args:
            num_simulations: Number of simulations per market

        Returns:
            Overall validation summary
        """
        results = []

        print("🎯 VALIDATING BETTING SIMULATOR ACCURACY")
        print("=" * 60)

        for i, market in enumerate(SAMPLE_MARKETS):
            print(f"\n📊 Market {i+1}: {market.player1} vs {market.player2}")

            validation = self.validate_single_market(market, num_simulations)
            results.append(validation)

            print(f"   Expected: {validation['expected_p1_prob']:.3f} ({validation['expected_p1_prob']*100:.1f}%)")
            print(f"   Actual:   {validation['actual_p1_prob']:.3f} ({validation['actual_p1_prob']*100:.1f}%)")
            print(f"   Error:    {validation['error_percentage']:.1f} percentage points")

            if validation['within_tolerance']:
                print(f"   ✅ EXCELLENT accuracy")
            else:
                print(f"   ❌ Poor accuracy - needs calibration")

        # Calculate overall metrics
        errors = [r['error_percentage'] for r in results]
        avg_error = sum(errors) / len(errors)
        max_error = max(errors)
        within_tolerance = sum(1 for r in results if r['within_tolerance'])

        print(f"\n📈 OVERALL ACCURACY SUMMARY:")
        print(f"   Average error: {avg_error:.1f} percentage points")
        print(f"   Maximum error: {max_error:.1f} percentage points")
        print(f"   Markets within 5%: {within_tolerance}/{len(results)}")

        overall_grade = "EXCELLENT" if avg_error <= 2.0 else "GOOD" if avg_error <= 4.0 else "POOR"
        print(f"   Overall grade: {overall_grade}")

        return {
            'individual_results': results,
            'summary': {
                'average_error': avg_error,
                'maximum_error': max_error,
                'markets_within_tolerance': within_tolerance,
                'total_markets': len(results),
                'overall_grade': overall_grade,
                'passing': avg_error <= 4.0
            }
        }

    def test_probability_engine(self) -> Dict[str, any]:
        """Test the probability engine calibration directly."""
        print(f"\n🔬 TESTING PROBABILITY ENGINE CALIBRATION")
        print("=" * 60)

        test_probs = [0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.90]
        results = []

        for target_prob in test_probs:
            # Get calibrated parameters
            params = self.probability_engine.derive_match_parameters(target_prob, "Hard")

            # Validate calibration
            validation = self.probability_engine.validate_accuracy(params, target_prob, 300)
            results.append(validation)

            print(f"Target: {target_prob:.2f} -> Actual: {validation['actual_probability']:.3f} "
                  f"(Error: {validation['error_percentage']:.1f}pp)")

        avg_error = sum(r['error_percentage'] for r in results) / len(results)
        print(f"\nAverage calibration error: {avg_error:.1f} percentage points")

        return {
            'calibration_results': results,
            'average_error': avg_error,
            'calibration_quality': "EXCELLENT" if avg_error <= 2.0 else "GOOD" if avg_error <= 4.0 else "POOR"
        }

    def run_full_validation(self) -> bool:
        """
        Run complete validation suite.

        Returns:
            True if validation passes, False otherwise
        """
        print("🚀 BETTING SIMULATOR VALIDATION SUITE")
        print("=" * 70)

        try:
            # Test probability engine
            engine_results = self.test_probability_engine()

            # Test market validation
            market_results = self.validate_all_sample_markets()

            # Overall assessment
            engine_passing = engine_results['average_error'] <= 4.0
            market_passing = market_results['summary']['passing']

            print(f"\n🎯 FINAL VALIDATION RESULTS:")
            print(f"   Probability Engine: {'✅ PASS' if engine_passing else '❌ FAIL'}")
            print(f"   Market Accuracy: {'✅ PASS' if market_passing else '❌ FAIL'}")

            overall_pass = engine_passing and market_passing
            print(f"   Overall: {'✅ PASS' if overall_pass else '❌ FAIL'}")

            if overall_pass:
                print(f"\n🎉 Betting simulator is ready for production use!")
                print(f"   Simulated win rates match betting market probabilities.")
            else:
                print(f"\n⚠️ Betting simulator needs calibration improvements.")

            return overall_pass

        except Exception as e:
            print(f"\n❌ Validation failed with error: {e}")
            return False


def main():
    """Run validation if script is called directly."""
    validator = BettingSimulatorValidator()
    success = validator.run_full_validation()

    if not success:
        exit(1)


if __name__ == "__main__":
    main()
