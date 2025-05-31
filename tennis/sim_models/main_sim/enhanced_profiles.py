"""
Enhanced Player Profiling System for main_sim
Migrated from the_oracle with main_sim integration

Location: tennis/sim_models/main_sim/enhanced_profiles.py
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class PlayerArchetype:
    """ML-derived player archetype with betting and tactical insights"""
    
    # Primary classification
    primary_type: str = "baseline_player"
    archetype_confidence: float = 0.7
    
    # Shot pattern signatures
    signature_patterns: Dict[str, float] = field(default_factory=dict)
    high_value_patterns: List[Dict] = field(default_factory=list)
    
    # Pressure and momentum response
    pressure_responses: Dict[str, float] = field(default_factory=dict)
    clutch_factor: float = 0.5
    momentum_sensitivity: float = 0.5
    
    # Surface specialization
    surface_advantages: Dict[str, float] = field(default_factory=lambda: {
        "Hard": 1.0, "Clay": 1.0, "Grass": 1.0
    })
    surface_penalties: Dict[str, float] = field(default_factory=dict)
    
    # Tactical tendencies
    rally_preferences: Dict[str, Any] = field(default_factory=dict)
    serve_patterns: Dict[str, Any] = field(default_factory=dict)
    return_patterns: Dict[str, Any] = field(default_factory=dict)
    
    # Betting-relevant metrics
    upset_probability: float = 0.1
    consistency_score: float = 0.5
    variance_factors: Dict[str, float] = field(default_factory=dict)


@dataclass
class StatisticalProfile:
    """Comprehensive statistical profile from real data"""
    
    # Serve statistics
    ace_rate: float = 5.0
    double_fault_rate: float = 4.0
    first_serve_percentage: float = 60.0
    first_serve_points_won_pct: float = 65.0
    second_serve_points_won_pct: float = 45.0
    
    # Return statistics
    return_points_won_pct: float = 35.0
    break_points_converted_pct: float = 40.0
    break_points_saved_pct: float = 60.0
    
    # Overall performance
    win_percentage: float = 50.0
    games_won_pct: float = 50.0
    sets_won_pct: float = 50.0
    
    # Additional metrics
    tiebreak_win_pct: float = 50.0
    deciding_set_win_pct: float = 50.0
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for main_sim compatibility"""
        return {
            'ace_rate': self.ace_rate,
            'double_fault_rate': self.double_fault_rate,
            'first_serve_percentage': self.first_serve_percentage,
            'first_serve_points_won_pct': self.first_serve_points_won_pct,
            'second_serve_points_won_pct': self.second_serve_points_won_pct,
            'return_points_won_pct': self.return_points_won_pct,
            'break_points_converted_pct': self.break_points_converted_pct,
            'break_points_saved_pct': self.break_points_saved_pct,
            'win_percentage': self.win_percentage,
            'games_won_pct': self.games_won_pct,
            'sets_won_pct': self.sets_won_pct,
            'tiebreak_win_pct': self.tiebreak_win_pct,
            'deciding_set_win_pct': self.deciding_set_win_pct
        }


@dataclass
class ShotPatterns:
    """Shot pattern analysis from match charting data"""
    
    # Shot type frequencies
    forehand_frequency: float = 45.0
    backhand_frequency: float = 35.0
    volley_frequency: float = 5.0
    overhead_frequency: float = 2.0
    
    # Directional tendencies
    crosscourt_tendency: float = 60.0
    down_the_line_tendency: float = 25.0
    inside_out_tendency: float = 15.0
    
    # Outcome rates
    winner_rate: float = 8.0
    error_rate: float = 12.0
    forced_error_rate: float = 15.0
    
    # Rally characteristics
    avg_rally_length: float = 4.5
    short_rally_win_rate: float = 55.0  # 1-3 shots
    medium_rally_win_rate: float = 50.0  # 4-8 shots
    long_rally_win_rate: float = 45.0   # 9+ shots
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for analysis"""
        return {
            'forehand_frequency': self.forehand_frequency,
            'backhand_frequency': self.backhand_frequency,
            'volley_frequency': self.volley_frequency,
            'overhead_frequency': self.overhead_frequency,
            'crosscourt_tendency': self.crosscourt_tendency,
            'down_the_line_tendency': self.down_the_line_tendency,
            'inside_out_tendency': self.inside_out_tendency,
            'winner_rate': self.winner_rate,
            'error_rate': self.error_rate,
            'forced_error_rate': self.forced_error_rate,
            'avg_rally_length': self.avg_rally_length,
            'short_rally_win_rate': self.short_rally_win_rate,
            'medium_rally_win_rate': self.medium_rally_win_rate,
            'long_rally_win_rate': self.long_rally_win_rate
        }


@dataclass
class EnhancedPlayerProfile:
    """
    Enhanced player profile combining main_sim mechanics with the_oracle insights
    Integrates with existing main_sim momentum, fatigue, and variance systems
    """
    
    # Basic information
    name: str
    surface: str = "Hard"
    
    # Core profiles from different data sources
    statistical_profile: StatisticalProfile = field(default_factory=StatisticalProfile)
    shot_patterns: ShotPatterns = field(default_factory=ShotPatterns)
    ml_archetype: PlayerArchetype = field(default_factory=PlayerArchetype)
    
    # Pressure and momentum (enhanced from main_sim)
    pressure_profile: Dict[str, float] = field(default_factory=dict)
    momentum_factors: Dict[str, float] = field(default_factory=dict)
    fatigue_resistance: float = 1.0
    
    # Surface adjustments
    surface_adjustments: Dict[str, float] = field(default_factory=dict)
    
    # Data quality metrics
    confidence_score: float = 0.5
    data_completeness: float = 0.5
    
    def get_serve_stats(self) -> Dict[str, float]:
        """Get serving statistics for main_sim compatibility"""
        return {
            'ace_rate': self.statistical_profile.ace_rate,
            'double_fault_rate': self.statistical_profile.double_fault_rate,
            'first_serve_percentage': self.statistical_profile.first_serve_percentage,
            'first_serve_points_won_pct': self.statistical_profile.first_serve_points_won_pct,
            'second_serve_points_won_pct': self.statistical_profile.second_serve_points_won_pct
        }
    
    def get_return_stats(self) -> Dict[str, float]:
        """Get return statistics for main_sim compatibility"""
        return {
            'return_points_won_pct': self.statistical_profile.return_points_won_pct,
            'break_points_converted_pct': self.statistical_profile.break_points_converted_pct
        }
    
    def get_pressure_performance(self, situation: str) -> float:
        """Get pressure performance for specific situation"""
        return self.pressure_profile.get(situation, 0.5)
    
    def get_surface_multiplier(self, surface: str) -> float:
        """Get surface performance multiplier"""
        return self.ml_archetype.surface_advantages.get(surface, 1.0)
    
    def get_momentum_factor(self) -> float:
        """Get momentum factor for main_sim integration"""
        return self.momentum_factors.get('momentum_factor', 1.0)
    
    def get_fatigue_resistance(self) -> float:
        """Get fatigue resistance for main_sim integration"""
        return self.fatigue_resistance
    
    def summary(self) -> str:
        """Generate a summary of the enhanced player profile"""
        return f"""
Enhanced Player Profile: {self.name} ({self.surface})
Archetype: {self.ml_archetype.primary_type} (confidence: {self.ml_archetype.archetype_confidence:.2f})
Data Completeness: {self.data_completeness:.2f}
Confidence Score: {self.confidence_score:.2f}
Surface Advantages: {self.ml_archetype.surface_advantages}
Momentum Factor: {self.get_momentum_factor():.2f}
Fatigue Resistance: {self.fatigue_resistance:.2f}
        """.strip()
    
    def to_main_sim_format(self) -> Dict[str, Any]:
        """Convert to main_sim compatible format"""
        return {
            **self.statistical_profile.to_dict(),
            'momentum_factor': self.get_momentum_factor(),
            'fatigue_resistance': self.fatigue_resistance,
            'clutch_factor': self.ml_archetype.clutch_factor,
            'surface_multiplier': self.get_surface_multiplier(self.surface),
            'archetype': self.ml_archetype.primary_type,
            'confidence': self.confidence_score
        }
