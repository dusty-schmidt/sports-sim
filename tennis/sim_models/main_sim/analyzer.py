"""
Tennis Statistics Analyzer
Loads and processes player statistics from various data sources
"""

import json
import csv
from pathlib import Path
from typing import Dict, Any, Optional


class TennisStatsAnalyzer:
    """Analyzes tennis statistics and provides player data."""

    def __init__(self, data_source: str = None):
        self.data_source = data_source
        self.player_stats = {}
        self.player_rankings = {}
        self.player_countries = {}
        self.calculated_stats = {}
        self.elo_ratings = {}  # Store ELO ratings for skill-based calculations

        # Load data
        self._load_elo_ratings()  # Load ELO ratings first
        self._load_player_data()

    def _load_elo_ratings(self):
        """Load surface-specific ELO ratings from ATP and WTA CSV files."""
        data_dir = Path("data/elo")
        atp_count = 0
        wta_count = 0

        # Store surface-specific ELO ratings
        self.surface_elo_ratings = {
            'Hard': {},
            'Clay': {},
            'Grass': {}
        }

        # Load ATP ELO ratings
        atp_elo_file = data_dir / "atp.csv"
        if atp_elo_file.exists():
            try:
                with open(atp_elo_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f, delimiter='\t')  # Tab-delimited
                    for row in reader:
                        player_name = row.get('Player', '').strip()
                        overall_elo = row.get('Elo', '').strip()
                        hard_elo = row.get('hElo', '').strip()
                        clay_elo = row.get('cElo', '').strip()
                        grass_elo = row.get('gElo', '').strip()

                        if player_name and overall_elo:
                            try:
                                # Store overall ELO for fallback
                                self.elo_ratings[player_name] = float(overall_elo)

                                # Store surface-specific ELOs
                                if hard_elo:
                                    self.surface_elo_ratings['Hard'][player_name] = float(hard_elo)
                                if clay_elo:
                                    self.surface_elo_ratings['Clay'][player_name] = float(clay_elo)
                                if grass_elo:
                                    self.surface_elo_ratings['Grass'][player_name] = float(grass_elo)

                                atp_count += 1
                            except ValueError:
                                continue
                print(f"✅ Loaded {atp_count} ATP ELO ratings")
            except Exception as e:
                print(f"Warning: Could not load ATP ELO data: {e}")

        # Load WTA ELO ratings
        wta_elo_file = data_dir / "wta.csv"
        if wta_elo_file.exists():
            try:
                with open(wta_elo_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f, delimiter='\t')  # Tab-delimited
                    for row in reader:
                        player_name = row.get('Player', '').strip()
                        overall_elo = row.get('Elo', '').strip()
                        hard_elo = row.get('hElo', '').strip()
                        clay_elo = row.get('cElo', '').strip()
                        grass_elo = row.get('gElo', '').strip()

                        if player_name and overall_elo:
                            try:
                                # Store overall ELO for fallback
                                self.elo_ratings[player_name] = float(overall_elo)

                                # Store surface-specific ELOs
                                if hard_elo:
                                    self.surface_elo_ratings['Hard'][player_name] = float(hard_elo)
                                if clay_elo:
                                    self.surface_elo_ratings['Clay'][player_name] = float(clay_elo)
                                if grass_elo:
                                    self.surface_elo_ratings['Grass'][player_name] = float(grass_elo)

                                wta_count += 1
                            except ValueError:
                                continue
                print(f"✅ Loaded {wta_count} WTA ELO ratings")
            except Exception as e:
                print(f"Warning: Could not load WTA ELO data: {e}")

        print(f"✅ Total ELO ratings loaded: {len(self.elo_ratings)}")
        print(f"✅ Surface-specific ratings - Hard: {len(self.surface_elo_ratings['Hard'])}, Clay: {len(self.surface_elo_ratings['Clay'])}, Grass: {len(self.surface_elo_ratings['Grass'])}")

        # Load calibrated player factors
        self._load_player_factors()

    def _load_player_factors(self):
        """Load calibrated player factors from exploratory analysis."""
        data_dir = Path("data/exploratory")

        # Initialize factor dictionaries
        self.clutch_factors = {}
        self.variance_factors = {}
        self.endurance_factors = {}
        self.rally_factors = {}
        self.surface_variance = {
            'Hard': 2.06,
            'Clay': 1.83,
            'Grass': 1.57
        }

        # Load clutch factors
        clutch_file = data_dir / "clutch_factor_analysis.json"
        if clutch_file.exists():
            try:
                with open(clutch_file, 'r') as f:
                    clutch_data = json.load(f)
                    for player, data in clutch_data.items():
                        self.clutch_factors[player] = {
                            'multiplier': data.get('clutch_multiplier', 1.0),
                            'level': data.get('clutch_level', 'Average')
                        }
                print(f"✅ Loaded clutch factors for {len(self.clutch_factors)} players")
            except Exception as e:
                print(f"Warning: Could not load clutch factors: {e}")

        # Load variance profiles
        variance_file = data_dir / "player_variance_profiles.json"
        if variance_file.exists():
            try:
                with open(variance_file, 'r') as f:
                    variance_data = json.load(f)
                    for player, data in variance_data.items():
                        self.variance_factors[player] = {
                            'multiplier': data.get('variance_multiplier', 0.15),
                            'level': data.get('variance_level', 'medium')
                        }
                print(f"✅ Loaded variance factors for {len(self.variance_factors)} players")
            except Exception as e:
                print(f"Warning: Could not load variance factors: {e}")

        # Load momentum/endurance factors
        momentum_file = data_dir / "momentum_endurance_analysis.json"
        if momentum_file.exists():
            try:
                with open(momentum_file, 'r') as f:
                    momentum_data = json.load(f)

                    # Extract rally fatigue data
                    rally_fatigue = momentum_data.get('rally_fatigue', {})
                    for player, data in rally_fatigue.items():
                        self.rally_factors[player] = {
                            'multiplier': data.get('rally_multiplier', 1.0),
                            'type': data.get('rally_type', 'Consistent')
                        }
                        self.endurance_factors[player] = {
                            'factor': data.get('endurance_factor', 1.0),
                            'type': data.get('endurance_type', 'Average Endurance')
                        }

                print(f"✅ Loaded rally/endurance factors for {len(self.rally_factors)} players")
            except Exception as e:
                print(f"Warning: Could not load momentum/endurance factors: {e}")

    def _get_skill_tier_from_elo(self, elo_rating: float, gender: str) -> str:
        """Convert ELO rating to skill tier for stat generation."""
        if gender == 'M':
            # ATP ELO tiers (based on current top players)
            if elo_rating >= 2150:  # Top 5 (Djokovic, Alcaraz level)
                return 'elite'
            elif elo_rating >= 2050:  # Top 20
                return 'top'
            elif elo_rating >= 1950:  # Top 50
                return 'high'
            elif elo_rating >= 1850:  # Top 100
                return 'mid'
            else:  # Below top 100
                return 'low'
        else:
            # WTA ELO tiers (based on current top players)
            if elo_rating >= 2100:  # Top 5 (Sabalenka, Swiatek level)
                return 'elite'
            elif elo_rating >= 2000:  # Top 20
                return 'top'
            elif elo_rating >= 1900:  # Top 50
                return 'high'
            elif elo_rating >= 1800:  # Top 100
                return 'mid'
            else:  # Below top 100
                return 'low'

    def _get_skill_tier_from_matches(self, matches: int) -> str:
        """Fallback method to assign skill tier based on match count."""
        if matches >= 200:
            return 'elite'
        elif matches >= 100:
            return 'top'
        elif matches >= 50:
            return 'high'
        elif matches >= 20:
            return 'mid'
        else:
            return 'low'

    def _load_player_data(self):
        """Load player data from available sources."""
        # Try to load pre-calculated stats first
        if self._load_calculated_stats():
            print(f"✅ Loaded {len(self.calculated_stats)} players from saved statistics")
            return

        # Fallback to calculating from raw data
        print("⚠️  No saved statistics found, calculating from raw data...")
        self._load_from_csv_data()
        self._load_from_js_file()
        self._create_default_players()

    def _load_calculated_stats(self):
        """Load pre-calculated player statistics from JSON file."""
        # Try to load momentum/endurance data first
        momentum_stats_file = Path("data/player_stats_with_momentum_endurance.json")
        if momentum_stats_file.exists():
            try:
                with open(momentum_stats_file, 'r') as f:
                    self.calculated_stats = json.load(f)
                print(f"✅ Loaded {len(self.calculated_stats)} players with momentum and endurance")

                # Also populate basic stats for compatibility
                for player_name, stats in self.calculated_stats.items():
                    self.player_stats[player_name] = {
                        'matches': stats.get('matches', 1),
                        'gender': stats.get('gender', 'M')
                    }
                    self.player_rankings[player_name] = stats.get('rank', 999)
                    self.player_countries[player_name] = 'N/A'

                return True
            except Exception as e:
                print(f"Warning: Could not load momentum/endurance stats: {e}")

        # Try to load clutch factor data as fallback
        clutch_stats_file = Path("data/player_stats_with_clutch_factors.json")
        if clutch_stats_file.exists():
            try:
                with open(clutch_stats_file, 'r') as f:
                    self.calculated_stats = json.load(f)
                print(f"✅ Loaded {len(self.calculated_stats)} players with clutch factors")

                # Also populate basic stats for compatibility
                for player_name, stats in self.calculated_stats.items():
                    self.player_stats[player_name] = {
                        'matches': stats.get('matches', 1),
                        'gender': stats.get('gender', 'M')
                    }
                    self.player_rankings[player_name] = stats.get('rank', 999)
                    self.player_countries[player_name] = 'N/A'

                return True
            except Exception as e:
                print(f"Warning: Could not load clutch stats: {e}")

        # Try to load real data as primary source
        real_stats_file = Path("data/processed/player_stats.json")
        if real_stats_file.exists():
            try:
                with open(real_stats_file, 'r') as f:
                    self.calculated_stats = json.load(f)
                print(f"✅ Loaded {len(self.calculated_stats)} players with real serving data")

                # Also populate basic stats for compatibility
                for player_name, stats in self.calculated_stats.items():
                    self.player_stats[player_name] = {
                        'matches': stats.get('matches', 1),
                        'gender': stats.get('gender', 'M')
                    }
                    self.player_rankings[player_name] = stats.get('rank', 999)
                    self.player_countries[player_name] = 'N/A'

                return True
            except Exception as e:
                print(f"Warning: Could not load real stats: {e}")

        # Fallback to calculated stats in exploratory folder
        stats_file = Path("data/exploratory/calculated_player_stats.json")
        if not stats_file.exists():
            # Try the old location as final fallback
            stats_file = Path("data/calculated_player_stats.json")
            if not stats_file.exists():
                return False

        try:
            with open(stats_file, 'r') as f:
                self.calculated_stats = json.load(f)

            # Also populate basic stats for compatibility
            for player_name, stats in self.calculated_stats.items():
                self.player_stats[player_name] = {
                    'matches': stats['matches'],
                    'gender': stats['gender']
                }
                self.player_rankings[player_name] = stats['rank']
                self.player_countries[player_name] = 'N/A'

            return True
        except Exception as e:
            print(f"Warning: Could not load calculated stats: {e}")
            return False

    def _load_from_csv_data(self):
        """Load player data from CSV files in data directory."""
        data_dir = Path("data")

        # Load WTA rankings if available
        wta_file = data_dir / "wta.csv"
        if wta_file.exists():
            try:
                with open(wta_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        player_name = row.get('player', '')
                        if player_name:
                            self.player_rankings[player_name] = row.get('rank', 'N/A')
                            self.player_countries[player_name] = row.get('country', 'N/A')

                            # Create basic stats
                            self.player_stats[player_name] = {
                                'matches': int(row.get('matches', 0)) if row.get('matches', '0').isdigit() else 0,
                                'rank': int(row.get('rank', 999)) if row.get('rank', '999').isdigit() else 999,
                                'country': row.get('country', 'N/A')
                            }
            except Exception as e:
                print(f"Warning: Could not load WTA data: {e}")

        # Load ATP rankings if available
        atp_file = data_dir / "atp.csv"
        if atp_file.exists():
            try:
                with open(atp_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        player_name = row.get('player', '')
                        if player_name:
                            self.player_rankings[player_name] = row.get('rank', 'N/A')
                            self.player_countries[player_name] = row.get('country', 'N/A')

                            # Create basic stats
                            self.player_stats[player_name] = {
                                'matches': int(row.get('matches', 0)) if row.get('matches', '0').isdigit() else 0,
                                'rank': int(row.get('rank', 999)) if row.get('rank', '999').isdigit() else 999,
                                'country': row.get('country', 'N/A')
                            }
            except Exception as e:
                print(f"Warning: Could not load ATP data: {e}")

    def _load_from_js_file(self):
        """Load player data from JavaScript file if available."""
        if not self.data_source:
            return

        js_file = Path(self.data_source)
        if js_file.exists():
            try:
                # This would parse the JS file - simplified for now
                print(f"Note: JS file {self.data_source} found but not parsed yet")
            except Exception as e:
                print(f"Warning: Could not load JS data: {e}")

    def _create_default_players(self):
        """Load real player statistics from our tennis match data."""
        # Load real players from our match data
        self._load_real_tennis_data()

        # Calculate derived statistics from real data
        self._calculate_player_statistics()

    def _load_real_tennis_data(self):
        """Load real player data from our tennis match files."""
        data_dir = Path("data")

        # Load men's matches
        men_matches_file = data_dir / "charting-m-matches(1).csv"
        if men_matches_file.exists():
            try:
                with open(men_matches_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        player1 = row.get('Player 1', '').strip()
                        player2 = row.get('Player 2', '').strip()

                        if player1:
                            if player1 not in self.player_stats:
                                self.player_stats[player1] = {'matches': 0, 'gender': 'M'}
                            self.player_stats[player1]['matches'] += 1

                        if player2:
                            if player2 not in self.player_stats:
                                self.player_stats[player2] = {'matches': 0, 'gender': 'M'}
                            self.player_stats[player2]['matches'] += 1

                print(f"✅ Loaded {len([p for p in self.player_stats if self.player_stats[p]['gender'] == 'M'])} men's players")
            except Exception as e:
                print(f"Warning: Could not load men's match data: {e}")

        # Load women's matches
        women_matches_file = data_dir / "charting-w-matches.csv"
        if women_matches_file.exists():
            try:
                with open(women_matches_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        player1 = row.get('Player 1', '').strip()
                        player2 = row.get('Player 2', '').strip()

                        if player1:
                            if player1 not in self.player_stats:
                                self.player_stats[player1] = {'matches': 0, 'gender': 'W'}
                            self.player_stats[player1]['matches'] += 1

                        if player2:
                            if player2 not in self.player_stats:
                                self.player_stats[player2] = {'matches': 0, 'gender': 'W'}
                            self.player_stats[player2]['matches'] += 1

                print(f"✅ Loaded {len([p for p in self.player_stats if self.player_stats[p]['gender'] == 'W'])} women's players")
            except Exception as e:
                print(f"Warning: Could not load women's match data: {e}")

        # Set rankings and countries for real players (simplified)
        for player_name, stats in self.player_stats.items():
            # Assign ranking based on match count (more matches = better ranking approximation)
            matches = stats.get('matches', 0)
            if matches >= 100:
                rank = 1 + (hash(player_name) % 20)  # Top 20
            elif matches >= 50:
                rank = 21 + (hash(player_name) % 30)  # 21-50
            elif matches >= 20:
                rank = 51 + (hash(player_name) % 50)  # 51-100
            else:
                rank = 101 + (hash(player_name) % 200)  # 101-300

            self.player_rankings[player_name] = rank
            self.player_countries[player_name] = 'N/A'  # We don't have country data in match files

    def _calculate_player_statistics(self):
        """Calculate realistic tennis statistics based on ELO ratings and tennis data patterns."""
        for player_name, basic_stats in self.player_stats.items():
            matches = basic_stats.get('matches', 1)
            gender = basic_stats.get('gender', 'M')

            # Get ELO rating for skill-based calculations
            elo_rating = self.elo_ratings.get(player_name, None)

            # Use ELO-based skill calculations if available, otherwise fallback to match-based
            if elo_rating:
                # Convert ELO to skill tier for realistic stat generation
                skill_tier = self._get_skill_tier_from_elo(elo_rating, gender)
            else:
                # Fallback to match-based tier assignment
                skill_tier = self._get_skill_tier_from_matches(matches)

            # Generate stats based on skill tier and add some variance
            variance = (hash(player_name) % 100 - 50) / 100  # -0.5 to 0.5

            if gender == 'M':
                # Men's tennis statistics (based on skill tier)
                if skill_tier == 'elite':  # Top 5 level (Djokovic, Alcaraz)
                    ace_rate = 9.5 + variance * 2.0  # 7.5-11.5%
                    df_rate = 2.5 + variance * 1.0   # 2.0-3.0%
                    service_pts = 68 + variance * 4   # 66-70%
                elif skill_tier == 'top':  # Top 20
                    ace_rate = 8.0 + variance * 2.0  # 6.0-10.0%
                    df_rate = 3.0 + variance * 1.0   # 2.5-3.5%
                    service_pts = 65 + variance * 4   # 63-67%
                elif skill_tier == 'high':  # Top 50
                    ace_rate = 6.5 + variance * 2.0  # 4.5-8.5%
                    df_rate = 3.5 + variance * 1.0   # 3.0-4.0%
                    service_pts = 62 + variance * 4   # 60-64%
                elif skill_tier == 'mid':  # Top 100
                    ace_rate = 5.5 + variance * 1.5  # 4.25-6.75%
                    df_rate = 4.0 + variance * 1.0   # 3.5-4.5%
                    service_pts = 59 + variance * 3   # 57.5-60.5%
                else:  # Below top 100
                    ace_rate = 4.5 + variance * 1.0  # 4.0-5.0%
                    df_rate = 4.8 + variance * 1.2   # 4.2-5.4%
                    service_pts = 56 + variance * 3   # 54.5-57.5%
            else:
                # Women's tennis statistics (based on skill tier)
                if skill_tier == 'elite':  # Top 5 level (Sabalenka, Swiatek)
                    ace_rate = 5.0 + variance * 1.5  # 4.25-5.75%
                    df_rate = 2.8 + variance * 0.8   # 2.4-3.2%
                    service_pts = 65 + variance * 4   # 63-67%
                elif skill_tier == 'top':  # Top 20
                    ace_rate = 4.2 + variance * 1.5  # 3.45-4.95%
                    df_rate = 3.2 + variance * 0.8   # 2.8-3.6%
                    service_pts = 62 + variance * 4   # 60-64%
                elif skill_tier == 'high':  # Top 50
                    ace_rate = 3.5 + variance * 1.0  # 3.0-4.0%
                    df_rate = 3.8 + variance * 0.8   # 3.4-4.2%
                    service_pts = 59 + variance * 3   # 57.5-60.5%
                elif skill_tier == 'mid':  # Top 100
                    ace_rate = 2.8 + variance * 0.8  # 2.4-3.2%
                    df_rate = 4.2 + variance * 0.8   # 3.8-4.6%
                    service_pts = 57 + variance * 3   # 55.5-58.5%
                else:  # Below top 100
                    ace_rate = 2.2 + variance * 0.6  # 1.9-2.5%
                    df_rate = 5.0 + variance * 1.0   # 4.5-5.5%
                    service_pts = 54 + variance * 3   # 52.5-55.5%

            # Ensure realistic bounds
            ace_rate = max(1.0, min(15.0, ace_rate))
            df_rate = max(1.0, min(8.0, df_rate))
            service_pts = max(50.0, min(75.0, service_pts))

            # First serve percentage (skill-based, more consistent for better players)
            if skill_tier == 'elite':
                first_serve_pct = 65 + variance * 3  # 63.5-66.5%
            elif skill_tier == 'top':
                first_serve_pct = 63 + variance * 4  # 61-65%
            elif skill_tier == 'high':
                first_serve_pct = 61 + variance * 4  # 59-63%
            elif skill_tier == 'mid':
                first_serve_pct = 59 + variance * 4  # 57-61%
            else:
                first_serve_pct = 57 + variance * 4  # 55-59%

            first_serve_pct = max(50.0, min(75.0, first_serve_pct))

            # Return points won (inverse relationship with service strength)
            return_pts_won = 100.0 - service_pts

            # Get ranking from our earlier calculation
            rank = self.player_rankings.get(player_name, 999)

            self.calculated_stats[player_name] = {
                'ace_rate': ace_rate,
                'double_fault_rate': df_rate,
                'first_serve_percentage': first_serve_pct,
                'service_points_won': service_pts,
                'return_points_won': return_pts_won,
                'rank': rank,
                'matches': matches,
                'gender': gender,
                'elo_rating': elo_rating,  # Include ELO rating
                'skill_tier': skill_tier   # Include skill tier for debugging
            }

    def get_player_stats(self, player_name: str, surface: str = None) -> Dict[str, Any]:
        """Get comprehensive statistics for a player, optionally surface-weighted."""
        baseline_stats = self.calculated_stats.get(player_name, {})

        # If surface is specified, apply surface weighting
        if surface and baseline_stats:
            return self._apply_surface_weighting(baseline_stats, surface)
        else:
            return baseline_stats

    def _apply_surface_weighting(self, baseline_stats: Dict[str, Any], surface: str) -> Dict[str, Any]:
        """Apply surface-specific weighting to baseline stats."""
        # Surface-specific adjustments based on tennis knowledge
        surface_adjustments = {
            'Clay': {
                'ace_rate_multiplier': 0.85,      # Fewer aces on clay
                'double_fault_multiplier': 1.1,   # Slightly more DFs on clay
                'service_points_multiplier': 0.98, # Slightly lower service dominance
                'return_points_multiplier': 1.02,  # Slightly better return opportunities
            },
            'Hard': {
                'ace_rate_multiplier': 1.0,       # Baseline
                'double_fault_multiplier': 1.0,   # Baseline
                'service_points_multiplier': 1.0, # Baseline
                'return_points_multiplier': 1.0,  # Baseline
            },
            'Grass': {
                'ace_rate_multiplier': 1.15,      # More aces on grass
                'double_fault_multiplier': 0.9,   # Fewer DFs on grass
                'service_points_multiplier': 1.05, # Higher service dominance
                'return_points_multiplier': 0.95,  # Harder to return
            }
        }

        adjustments = surface_adjustments.get(surface, surface_adjustments['Hard'])

        # Determine surface weighting based on player's surface experience
        surface_prefs = baseline_stats.get('surface_preferences', {})
        surface_pct = surface_prefs.get(surface, 0.33)  # Default to 33% if missing
        total_matches = baseline_stats.get('matches', 0)
        surface_matches = int(total_matches * surface_pct)

        # Adjust surface weight based on experience
        if surface_matches < 5:
            surface_weight = 0.3  # 30% surface weighting for low experience
        elif surface_matches < 10:
            surface_weight = 0.5  # 50% surface weighting for moderate experience
        else:
            surface_weight = 0.7  # 70% surface weighting for high experience

        # Calculate weighted stats
        weighted_stats = baseline_stats.copy()

        # Store the surface weight for ELO calculations
        weighted_stats['_surface_weight'] = surface_weight

        # Apply surface weighting: surface_weight * surface_adjusted + (1-surface_weight) * baseline
        for stat in ['ace_rate', 'double_fault_rate', 'service_points_won', 'return_points_won']:
            if stat not in baseline_stats:
                continue

            baseline_val = baseline_stats[stat]

            # Get the appropriate multiplier
            if stat == 'ace_rate':
                multiplier = adjustments['ace_rate_multiplier']
            elif stat == 'double_fault_rate':
                multiplier = adjustments['double_fault_multiplier']
            elif stat == 'service_points_won':
                multiplier = adjustments['service_points_multiplier']
            elif stat == 'return_points_won':
                multiplier = adjustments['return_points_multiplier']
            else:
                multiplier = 1.0

            # Calculate surface-adjusted value
            surface_adjusted_val = baseline_val * multiplier

            # Apply weighting: surface_weight * surface_specific + (1-surface_weight) * baseline
            weighted_val = (surface_weight * surface_adjusted_val) + ((1 - surface_weight) * baseline_val)

            weighted_stats[stat] = weighted_val

        return weighted_stats

    def get_player_elo(self, player_name: str, surface: str = None) -> Optional[float]:
        """Get ELO rating for a player, optionally surface-weighted."""
        overall_elo = self.elo_ratings.get(player_name, None)

        if not surface or not overall_elo:
            return overall_elo

        # Get surface-specific ELO if available
        surface_elo = None
        if hasattr(self, 'surface_elo_ratings') and surface in self.surface_elo_ratings:
            surface_elo = self.surface_elo_ratings[surface].get(player_name, None)

        if not surface_elo:
            return overall_elo

        # Apply the same surface weighting as used for stats
        baseline_stats = self.calculated_stats.get(player_name, {})
        if not baseline_stats:
            return surface_elo  # Use surface ELO if no baseline stats

        # Calculate surface weight using same logic as stats
        surface_prefs = baseline_stats.get('surface_preferences', {})
        surface_pct = surface_prefs.get(surface, 0.33)
        total_matches = baseline_stats.get('matches', 0)
        surface_matches = int(total_matches * surface_pct)

        # Same weighting logic as stats
        if surface_matches < 5:
            surface_weight = 0.3
        elif surface_matches < 10:
            surface_weight = 0.5
        else:
            surface_weight = 0.7

        # Apply weighting: surface_weight * surface_elo + (1-surface_weight) * overall_elo
        weighted_elo = (surface_weight * surface_elo) + ((1 - surface_weight) * overall_elo)

        return weighted_elo

    def get_player_clutch_factor(self, player_name: str) -> float:
        """Get clutch factor for a player."""
        if hasattr(self, 'clutch_factors') and player_name in self.clutch_factors:
            return self.clutch_factors[player_name]['multiplier']
        return 1.0  # Default average clutch

    def get_player_variance_factor(self, player_name: str) -> float:
        """Get variance factor for a player."""
        if hasattr(self, 'variance_factors') and player_name in self.variance_factors:
            return self.variance_factors[player_name]['multiplier']
        return 0.15  # Default medium variance

    def get_player_rally_factor(self, player_name: str) -> float:
        """Get rally factor for a player."""
        if hasattr(self, 'rally_factors') and player_name in self.rally_factors:
            return self.rally_factors[player_name]['multiplier']
        return 1.0  # Default consistent

    def get_player_endurance_factor(self, player_name: str) -> float:
        """Get endurance factor for a player."""
        if hasattr(self, 'endurance_factors') and player_name in self.endurance_factors:
            return self.endurance_factors[player_name]['factor']
        return 1.0  # Default average endurance

    def get_surface_variance(self, surface: str) -> float:
        """Get variance factor for a surface."""
        if hasattr(self, 'surface_variance'):
            return self.surface_variance.get(surface, 1.8)
        return 1.8  # Default variance

    def get_all_players(self) -> list:
        """Get list of all available players."""
        return list(self.calculated_stats.keys())

    def player_exists(self, player_name: str) -> bool:
        """Check if player exists in database."""
        return player_name in self.calculated_stats
