"""
Enhanced Data Engine for main_sim
Integrates the_oracle's data capabilities with main_sim's existing analyzer

Location: tennis/sim_models/main_sim/enhanced_data_engine.py
"""

from typing import Dict, Optional, Set
from pathlib import Path
import json

from .analyzer import TennisStatsAnalyzer
from .enhanced_profiles import (
    EnhancedPlayerProfile, PlayerArchetype, 
    StatisticalProfile, ShotPatterns
)


class EnhancedDataEngine:
    """
    Enhanced data engine that extends main_sim's TennisStatsAnalyzer
    with the_oracle's advanced profiling capabilities
    """
    
    def __init__(self, data_source: str = None):
        """Initialize enhanced data engine"""
        print("🔄 Initializing Enhanced Data Engine...")
        
        # Use main_sim's existing analyzer as the foundation
        self.base_analyzer = TennisStatsAnalyzer(data_source)
        
        # Enhanced capabilities
        self.all_players: Set[str] = set()
        self.enhanced_profiles: Dict[str, EnhancedPlayerProfile] = {}
        
        # Build enhanced player database
        self._build_enhanced_player_database()
        
        print(f"✅ Enhanced Data Engine initialized with {len(self.all_players)} players")
    
    def _build_enhanced_player_database(self):
        """Build enhanced player database from main_sim data"""
        # Get all players from main_sim analyzer
        if hasattr(self.base_analyzer, 'calculated_stats'):
            self.all_players.update(self.base_analyzer.calculated_stats.keys())
            print(f"   Added {len(self.base_analyzer.calculated_stats)} players from main_sim data")
        
        if hasattr(self.base_analyzer, 'player_stats'):
            self.all_players.update(self.base_analyzer.player_stats.keys())
            print(f"   Total unique players: {len(self.all_players)}")
    
    def create_enhanced_player_profile(self, player_name: str, surface: str = "Hard") -> EnhancedPlayerProfile:
        """
        Create enhanced player profile combining main_sim data with ML insights
        
        Args:
            player_name: Player name
            surface: Court surface
            
        Returns:
            EnhancedPlayerProfile with all available data
        """
        print(f"   🔍 Creating enhanced profile for {player_name} on {surface}")
        
        # Get base statistical profile from main_sim
        statistical_profile = self._get_statistical_profile(player_name)
        
        # Create ML archetype (enhanced from basic classification)
        ml_archetype = self._classify_player_archetype(player_name, statistical_profile)
        
        # Extract shot patterns (basic implementation)
        shot_patterns = self._extract_shot_patterns(player_name)
        
        # Get momentum and fatigue factors from main_sim data
        momentum_factors, fatigue_resistance = self._get_momentum_fatigue_factors(player_name)
        
        # Create pressure profile
        pressure_profile = self._extract_pressure_profile(player_name, statistical_profile)
        
        # Get surface adjustments
        surface_adjustments = self._get_surface_adjustments(player_name, surface)
        
        # Calculate data completeness and confidence
        data_completeness = self._calculate_data_completeness(player_name)
        confidence_score = self._calculate_confidence_score(player_name, data_completeness)
        
        profile = EnhancedPlayerProfile(
            name=player_name,
            surface=surface,
            statistical_profile=statistical_profile,
            shot_patterns=shot_patterns,
            ml_archetype=ml_archetype,
            pressure_profile=pressure_profile,
            momentum_factors=momentum_factors,
            fatigue_resistance=fatigue_resistance,
            surface_adjustments=surface_adjustments,
            confidence_score=confidence_score,
            data_completeness=data_completeness
        )
        
        # Cache the profile
        self.enhanced_profiles[f"{player_name}_{surface}"] = profile
        
        return profile
    
    def _get_statistical_profile(self, player_name: str) -> StatisticalProfile:
        """Get statistical profile from main_sim data"""
        if (hasattr(self.base_analyzer, 'calculated_stats') and 
            player_name in self.base_analyzer.calculated_stats):
            
            stats = self.base_analyzer.calculated_stats[player_name]
            
            return StatisticalProfile(
                ace_rate=stats.get('ace_rate', 5.0),
                double_fault_rate=stats.get('double_fault_rate', 4.0),
                first_serve_percentage=stats.get('first_serve_percentage', 60.0),
                first_serve_points_won_pct=stats.get('service_points_won', 65.0),
                second_serve_points_won_pct=stats.get('service_points_won', 45.0) * 0.7,  # Estimate
                return_points_won_pct=stats.get('return_points_won', 35.0),
                break_points_converted_pct=40.0,  # Default
                break_points_saved_pct=60.0,     # Default
                win_percentage=stats.get('win_percentage', 50.0),
                games_won_pct=50.0,              # Default
                sets_won_pct=50.0,               # Default
                tiebreak_win_pct=50.0,           # Default
                deciding_set_win_pct=50.0        # Default
            )
        
        # Return default profile for unknown players
        return StatisticalProfile()
    
    def _classify_player_archetype(self, player_name: str, stats: StatisticalProfile) -> PlayerArchetype:
        """Classify player archetype based on statistical profile"""
        archetype = PlayerArchetype()
        
        # Basic classification based on serve statistics
        if stats.ace_rate > 8.0:
            archetype.primary_type = "power_server"
            archetype.archetype_confidence = 0.8
        elif stats.return_points_won_pct > 40.0:
            archetype.primary_type = "return_specialist"
            archetype.archetype_confidence = 0.7
        elif stats.double_fault_rate < 3.0:
            archetype.primary_type = "consistent_player"
            archetype.archetype_confidence = 0.6
        else:
            archetype.primary_type = "baseline_player"
            archetype.archetype_confidence = 0.5
        
        # Set surface advantages based on archetype
        if archetype.primary_type == "power_server":
            archetype.surface_advantages = {"Hard": 1.1, "Grass": 1.2, "Clay": 0.9}
        elif archetype.primary_type == "return_specialist":
            archetype.surface_advantages = {"Hard": 1.0, "Grass": 0.9, "Clay": 1.1}
        elif archetype.primary_type == "consistent_player":
            archetype.surface_advantages = {"Hard": 1.0, "Grass": 0.8, "Clay": 1.2}
        
        # Set betting-relevant metrics
        archetype.upset_probability = 0.15 if stats.win_percentage < 45.0 else 0.08
        archetype.consistency_score = min(1.0, (100 - stats.double_fault_rate) / 100)
        
        return archetype
    
    def _extract_shot_patterns(self, player_name: str) -> ShotPatterns:
        """Extract basic shot patterns (placeholder for future ML integration)"""
        # For now, return default patterns
        # This will be enhanced when ml_models/ is integrated
        return ShotPatterns()
    
    def _get_momentum_fatigue_factors(self, player_name: str) -> tuple:
        """Get momentum and fatigue factors from main_sim data"""
        momentum_factors = {'momentum_factor': 1.0}
        fatigue_resistance = 1.0
        
        if (hasattr(self.base_analyzer, 'calculated_stats') and 
            player_name in self.base_analyzer.calculated_stats):
            
            stats = self.base_analyzer.calculated_stats[player_name]
            momentum_factors['momentum_factor'] = stats.get('momentum_factor', 1.0)
            fatigue_resistance = stats.get('fatigue_resistance', 1.0)
        
        return momentum_factors, fatigue_resistance
    
    def _extract_pressure_profile(self, player_name: str, stats: StatisticalProfile) -> Dict[str, float]:
        """Extract pressure performance profile"""
        # Basic pressure profile based on statistical tendencies
        pressure_profile = {
            'break_point_performance': stats.break_points_saved_pct / 100.0,
            'deuce_performance': 0.5,  # Default
            'set_point_performance': stats.deciding_set_win_pct / 100.0,
            'pressure_sensitivity': 1.0 - (stats.consistency_score if hasattr(stats, 'consistency_score') else 0.5)
        }
        
        return pressure_profile
    
    def _get_surface_adjustments(self, player_name: str, surface: str) -> Dict[str, float]:
        """Get surface-specific adjustments"""
        # Basic surface adjustments
        surface_adjustments = {
            'serve_adjustment': 1.0,
            'return_adjustment': 1.0,
            'rally_adjustment': 1.0
        }
        
        # This will be enhanced with real surface-specific data
        return surface_adjustments
    
    def _calculate_data_completeness(self, player_name: str) -> float:
        """Calculate how complete our data is for this player"""
        completeness = 0.0
        
        # Check main_sim data availability
        if (hasattr(self.base_analyzer, 'calculated_stats') and 
            player_name in self.base_analyzer.calculated_stats):
            completeness += 0.6  # Base statistical data
        
        if (hasattr(self.base_analyzer, 'player_stats') and 
            player_name in self.base_analyzer.player_stats):
            completeness += 0.2  # Basic player data
        
        # Future: Add points for match charting data, ML features, etc.
        completeness += 0.2  # Placeholder for future data sources
        
        return min(1.0, completeness)
    
    def _calculate_confidence_score(self, player_name: str, data_completeness: float) -> float:
        """Calculate confidence in our player profile"""
        confidence = data_completeness * 0.7  # Base confidence from data completeness
        
        # Boost confidence for players with more matches
        if (hasattr(self.base_analyzer, 'calculated_stats') and 
            player_name in self.base_analyzer.calculated_stats):
            
            matches = self.base_analyzer.calculated_stats[player_name].get('matches', 0)
            match_boost = min(0.3, matches / 100.0)  # Up to 0.3 boost for 100+ matches
            confidence += match_boost
        
        return min(1.0, confidence)
    
    def player_exists(self, player_name: str) -> bool:
        """Check if player exists in our database"""
        return player_name in self.all_players
    
    def get_all_players(self) -> Set[str]:
        """Get all available players"""
        return self.all_players.copy()
    
    def get_cached_profile(self, player_name: str, surface: str = "Hard") -> Optional[EnhancedPlayerProfile]:
        """Get cached enhanced profile if available"""
        cache_key = f"{player_name}_{surface}"
        return self.enhanced_profiles.get(cache_key)
