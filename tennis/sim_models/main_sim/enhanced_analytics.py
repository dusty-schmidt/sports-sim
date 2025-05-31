"""
Enhanced Analytics System for main_sim
Migrated from the_oracle with main_sim integration

Location: tennis/sim_models/main_sim/enhanced_analytics.py
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from .enhanced_profiles import EnhancedPlayerProfile
from .stats import FantasyStats, SetResult


@dataclass
class MLInsights:
    """ML-based insights and analysis"""

    # Player archetype analysis
    p1_archetype: str = ""
    p2_archetype: str = ""
    archetype_matchup: str = ""

    # Surface analysis
    surface_advantage: str = ""
    surface_impact: float = 0.0

    # Data quality
    p1_data_completeness: float = 0.0
    p2_data_completeness: float = 0.0

    # Prediction confidence
    prediction_confidence: float = 0.5
    upset_probability: float = 0.1


@dataclass
class TacticalAnalysis:
    """Tactical match analysis"""

    # Match statistics
    total_games: int = 0
    total_points: int = 0
    avg_points_per_game: float = 0.0

    # Break point analysis
    total_breaks: int = 0
    total_break_opportunities: int = 0
    break_conversion_rate: float = 0.0

    # Rally analysis
    avg_rally_length: float = 0.0
    short_rallies_pct: float = 0.0
    long_rallies_pct: float = 0.0

    # Pressure situations
    pressure_points: int = 0
    pressure_conversion_rate: float = 0.0


@dataclass
class MomentumAnalysis:
    """Momentum and flow analysis"""

    # Momentum shifts
    momentum_swings: int = 0
    momentum_description: str = ""

    # Set momentum
    set_momentum_changes: List[str] = field(default_factory=list)

    # Key moments
    turning_points: List[Dict] = field(default_factory=list)

    # Momentum winners
    momentum_winner: str = ""
    momentum_impact: float = 0.0


@dataclass
class BettingOpportunity:
    """Individual betting opportunity"""

    type: str
    description: str
    confidence: float
    value_rating: float = 0.0
    suggested_bet: str = ""


@dataclass
class BettingAnalysis:
    """Comprehensive betting analysis"""

    # Opportunities
    opportunities: List[BettingOpportunity] = field(default_factory=list)

    # Value assessments
    match_value_rating: float = 0.0
    upset_potential: float = 0.0

    # Specific markets
    ace_count_analysis: Dict[str, Any] = field(default_factory=dict)
    break_count_analysis: Dict[str, Any] = field(default_factory=dict)
    set_betting_analysis: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnhancedMatchResult:
    """
    Enhanced match result with comprehensive analytics
    Extends main_sim results with the_oracle insights
    """

    # Basic match information
    player1_name: str
    player2_name: str
    surface: str
    winner: int
    final_score: List[Tuple[int, int]]

    # Match data
    sets: List[SetResult]
    total_time_minutes: float
    fantasy_stats: Tuple[FantasyStats, FantasyStats]

    # Enhanced analytics (optional based on analysis depth)
    ml_insights: Optional[MLInsights] = None
    tactical_analysis: Optional[TacticalAnalysis] = None
    momentum_analysis: Optional[MomentumAnalysis] = None
    betting_analysis: Optional[BettingAnalysis] = None

    # Analysis metadata
    analysis_depth: str = "standard"
    simulation_time: float = 0.0

    def display_basic_summary(self):
        """Display basic match summary"""
        winner_name = self.player1_name if self.winner == 0 else self.player2_name
        score_str = " ".join([f"{s1}-{s2}" for s1, s2 in self.final_score])

        print(f"\n🏆 MATCH RESULT:")
        print(f"   Winner: {winner_name}")
        print(f"   Score: {score_str}")
        print(f"   Surface: {self.surface}")
        print(f"   Duration: {self.total_time_minutes:.1f} minutes")

    def display_fantasy_summary(self):
        """Display fantasy scoring summary"""
        p1_stats, p2_stats = self.fantasy_stats

        print(f"\n💰 FANTASY SCORING:")
        print(f"   {p1_stats.player_name}: {p1_stats.calculate_fantasy_points():.1f} points")
        print(f"     Sets: {p1_stats.sets_won}-{p1_stats.sets_lost}")
        print(f"     Games: {p1_stats.games_won}-{p1_stats.games_lost}")
        print(f"     Aces: {p1_stats.aces}, DFs: {p1_stats.double_faults}, Breaks: {p1_stats.breaks}")

        print(f"   {p2_stats.player_name}: {p2_stats.calculate_fantasy_points():.1f} points")
        print(f"     Sets: {p2_stats.sets_won}-{p2_stats.sets_lost}")
        print(f"     Games: {p2_stats.games_won}-{p2_stats.games_lost}")
        print(f"     Aces: {p2_stats.aces}, DFs: {p2_stats.double_faults}, Breaks: {p2_stats.breaks}")

    def display_ml_insights(self):
        """Display ML insights if available"""
        if not self.ml_insights:
            print("\n🧠 ML INSIGHTS: Not available")
            return

        insights = self.ml_insights
        print(f"\n🧠 ML INSIGHTS:")
        print(f"   Matchup: {insights.archetype_matchup}")
        print(f"   Surface Impact: {insights.surface_advantage}")
        print(f"   Data Quality: P1 {insights.p1_data_completeness:.1%}, P2 {insights.p2_data_completeness:.1%}")
        print(f"   Prediction Confidence: {insights.prediction_confidence:.1%}")

    def display_tactical_analysis(self):
        """Display tactical analysis if available"""
        if not self.tactical_analysis:
            print("\n⚡ TACTICAL ANALYSIS: Not available")
            return

        analysis = self.tactical_analysis
        print(f"\n⚡ TACTICAL ANALYSIS:")
        print(f"   Total Games: {analysis.total_games}")
        print(f"   Avg Points/Game: {analysis.avg_points_per_game:.1f}")
        print(f"   Break Conversion: {analysis.break_conversion_rate:.1%} ({analysis.total_breaks}/{analysis.total_break_opportunities})")
        print(f"   Avg Rally Length: {analysis.avg_rally_length:.1f} shots")

    def display_betting_opportunities(self):
        """Display betting opportunities if available"""
        if not self.betting_analysis or not self.betting_analysis.opportunities:
            print("\n📊 BETTING OPPORTUNITIES: None detected")
            return

        print(f"\n📊 BETTING OPPORTUNITIES:")
        for opp in self.betting_analysis.opportunities:
            print(f"   {opp.type}: {opp.description} (Confidence: {opp.confidence:.1%})")

    def display_complete_analysis(self):
        """Display all available analysis"""
        self.display_basic_summary()
        self.display_fantasy_summary()
        self.display_ml_insights()
        self.display_tactical_analysis()
        self.display_betting_opportunities()


class EnhancedAnalyticsEngine:
    """Analytics engine for generating insights from match results"""

    def generate_ml_insights(self, p1_profile: EnhancedPlayerProfile,
                           p2_profile: EnhancedPlayerProfile,
                           result: EnhancedMatchResult) -> MLInsights:
        """Generate ML-based insights"""
        insights = MLInsights()

        # Archetype analysis
        insights.p1_archetype = p1_profile.ml_archetype.primary_type
        insights.p2_archetype = p2_profile.ml_archetype.primary_type
        insights.archetype_matchup = f"{insights.p1_archetype} vs {insights.p2_archetype}"

        # Surface analysis
        p1_surface_adv = p1_profile.get_surface_multiplier(result.surface)
        p2_surface_adv = p2_profile.get_surface_multiplier(result.surface)

        if p1_surface_adv > p2_surface_adv:
            insights.surface_advantage = f"{p1_profile.name} has surface advantage on {result.surface}"
            insights.surface_impact = p1_surface_adv - p2_surface_adv
        elif p2_surface_adv > p1_surface_adv:
            insights.surface_advantage = f"{p2_profile.name} has surface advantage on {result.surface}"
            insights.surface_impact = p2_surface_adv - p1_surface_adv
        else:
            insights.surface_advantage = f"Even surface matchup on {result.surface}"
            insights.surface_impact = 0.0

        # Data completeness
        insights.p1_data_completeness = p1_profile.data_completeness
        insights.p2_data_completeness = p2_profile.data_completeness

        # Prediction confidence based on data quality
        avg_completeness = (insights.p1_data_completeness + insights.p2_data_completeness) / 2
        insights.prediction_confidence = 0.5 + (avg_completeness * 0.3)

        # Upset probability
        insights.upset_probability = min(p1_profile.ml_archetype.upset_probability,
                                       p2_profile.ml_archetype.upset_probability)

        return insights

    def generate_tactical_analysis(self, sets: List[SetResult]) -> TacticalAnalysis:
        """Generate tactical analysis from match data"""
        analysis = TacticalAnalysis()

        # Basic statistics from SetResult structure
        analysis.total_games = sum(set_result.winner_games + set_result.loser_games for set_result in sets)

        # Estimate total points (rough calculation: ~4.5 points per game average)
        analysis.total_points = int(analysis.total_games * 4.5)

        if analysis.total_games > 0:
            analysis.avg_points_per_game = analysis.total_points / analysis.total_games

        # Break point analysis (simplified estimation)
        # Count breaks as games where the non-server won
        total_service_games = analysis.total_games
        service_holds = 0

        # Estimate service holds vs breaks (rough calculation)
        # In a typical match, about 80-85% of service games are held
        estimated_hold_rate = 0.82
        estimated_holds = int(total_service_games * estimated_hold_rate)
        analysis.total_breaks = total_service_games - estimated_holds

        # Estimate break opportunities (typically 2-3x the number of actual breaks)
        analysis.total_break_opportunities = max(analysis.total_breaks * 3, analysis.total_breaks)

        if analysis.total_break_opportunities > 0:
            analysis.break_conversion_rate = analysis.total_breaks / analysis.total_break_opportunities

        # Rally analysis (estimated)
        analysis.avg_rally_length = 4.2  # Typical tennis rally length
        analysis.short_rallies_pct = 65.0  # 1-4 shots
        analysis.long_rallies_pct = 15.0   # 9+ shots

        return analysis

    def generate_betting_opportunities(self, result: EnhancedMatchResult) -> BettingAnalysis:
        """Generate betting opportunities from match result"""
        analysis = BettingAnalysis()
        p1_stats, p2_stats = result.fantasy_stats

        # High ace count opportunity
        if p1_stats.aces >= 8 or p2_stats.aces >= 8:
            analysis.opportunities.append(BettingOpportunity(
                type="Ace Count",
                description="High ace count detected - consider over bets on aces",
                confidence=0.7,
                value_rating=0.6
            ))

        # Break count opportunity
        total_breaks = p1_stats.breaks + p2_stats.breaks
        if total_breaks >= 5:
            analysis.opportunities.append(BettingOpportunity(
                type="Break Count",
                description="High break count - volatile match with service breaks",
                confidence=0.6,
                value_rating=0.5
            ))

        # Set betting analysis
        if p1_stats.sets_won == 2 and p1_stats.sets_lost == 0:
            analysis.opportunities.append(BettingOpportunity(
                type="Straight Sets",
                description="Straight sets victory - dominant performance",
                confidence=0.8,
                value_rating=0.7
            ))

        # Calculate overall value rating
        if analysis.opportunities:
            analysis.match_value_rating = sum(opp.value_rating for opp in analysis.opportunities) / len(analysis.opportunities)

        return analysis
