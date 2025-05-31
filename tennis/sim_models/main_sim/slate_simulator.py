"""
Tennis Slate Simulator
Simulates full slates of tennis matches for DFS lineup building

Location: tennis/sim_models/main_sim/slate_simulator.py
"""

import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from .simulator import FantasyTennisSimulator
from .stats import FantasyStats


@dataclass
class Match:
    """Individual match definition"""
    player1: str
    player2: str
    surface: str
    match_id: str = ""
    
    def __post_init__(self):
        if not self.match_id:
            self.match_id = f"{self.player1}_vs_{self.player2}_{self.surface}"


@dataclass
class MatchResult:
    """Result of a single match simulation"""
    match_id: str
    player1: str
    player2: str
    surface: str
    winner: int  # 0 for player1, 1 for player2
    winner_name: str
    loser_name: str
    final_score: str
    duration_minutes: float
    
    # Fantasy stats for both players
    player1_fantasy_points: float
    player1_sets_won: int
    player1_games_won: int
    player1_aces: int
    player1_double_faults: int
    player1_breaks: int
    
    player2_fantasy_points: float
    player2_sets_won: int
    player2_games_won: int
    player2_aces: int
    player2_double_faults: int
    player2_breaks: int


@dataclass
class SlateSimulation:
    """Results of one complete slate simulation"""
    simulation_id: int
    timestamp: str
    matches: List[MatchResult]
    total_fantasy_points: float
    
    def get_player_results(self) -> Dict[str, Dict[str, Any]]:
        """Get results organized by player"""
        player_results = {}
        
        for match in self.matches:
            # Player 1 results
            player_results[match.player1] = {
                'match_id': match.match_id,
                'opponent': match.player2,
                'surface': match.surface,
                'won': match.winner == 0,
                'fantasy_points': match.player1_fantasy_points,
                'sets_won': match.player1_sets_won,
                'games_won': match.player1_games_won,
                'aces': match.player1_aces,
                'double_faults': match.player1_double_faults,
                'breaks': match.player1_breaks
            }
            
            # Player 2 results
            player_results[match.player2] = {
                'match_id': match.match_id,
                'opponent': match.player1,
                'surface': match.surface,
                'won': match.winner == 1,
                'fantasy_points': match.player2_fantasy_points,
                'sets_won': match.player2_sets_won,
                'games_won': match.player2_games_won,
                'aces': match.player2_aces,
                'double_faults': match.player2_double_faults,
                'breaks': match.player2_breaks
            }
        
        return player_results


class TennisSlateSimulator:
    """
    Simulates full slates of tennis matches for DFS analysis
    """
    
    def __init__(self, data_source: Optional[str] = None):
        """Initialize the slate simulator"""
        print("🎾 Initializing Tennis Slate Simulator...")
        self.simulator = FantasyTennisSimulator(data_source)
        self.results_history: List[SlateSimulation] = []
        print("✅ Slate Simulator ready!")
    
    def simulate_match(self, match: Match, verbose: bool = False) -> MatchResult:
        """Simulate a single match and return structured result"""
        if verbose:
            print(f"   🎾 Simulating: {match.player1} vs {match.player2} on {match.surface}")
        
        # Run the simulation
        p1_stats, p2_stats, sets = self.simulator.simulate_match_detailed(
            match.player1, match.player2, match.surface, verbose=False
        )
        
        # Determine winner
        winner = 0 if p1_stats.sets_won > p2_stats.sets_won else 1
        winner_name = match.player1 if winner == 0 else match.player2
        loser_name = match.player2 if winner == 0 else match.player1
        
        # Create score string
        score_parts = []
        for set_result in sets:
            if winner == 0:
                score_parts.append(f"{set_result.winner_games}-{set_result.loser_games}")
            else:
                score_parts.append(f"{set_result.loser_games}-{set_result.winner_games}")
        final_score = " ".join(score_parts)
        
        # Estimate match duration (rough calculation)
        total_games = sum(s.winner_games + s.loser_games for s in sets)
        duration_minutes = total_games * 8.5  # ~8.5 minutes per game average
        
        return MatchResult(
            match_id=match.match_id,
            player1=match.player1,
            player2=match.player2,
            surface=match.surface,
            winner=winner,
            winner_name=winner_name,
            loser_name=loser_name,
            final_score=final_score,
            duration_minutes=duration_minutes,
            player1_fantasy_points=p1_stats.calculate_fantasy_points(),
            player1_sets_won=p1_stats.sets_won,
            player1_games_won=p1_stats.games_won,
            player1_aces=p1_stats.aces,
            player1_double_faults=p1_stats.double_faults,
            player1_breaks=p1_stats.breaks,
            player2_fantasy_points=p2_stats.calculate_fantasy_points(),
            player2_sets_won=p2_stats.sets_won,
            player2_games_won=p2_stats.games_won,
            player2_aces=p2_stats.aces,
            player2_double_faults=p2_stats.double_faults,
            player2_breaks=p2_stats.breaks
        )
    
    def simulate_slate(self, matches: List[Match], simulation_id: int = None, 
                      verbose: bool = False) -> SlateSimulation:
        """Simulate a complete slate of matches"""
        if simulation_id is None:
            simulation_id = len(self.results_history) + 1
        
        if verbose:
            print(f"\n🏆 Simulating Slate #{simulation_id} ({len(matches)} matches)")
        
        # Simulate each match
        match_results = []
        total_fantasy_points = 0.0
        
        for i, match in enumerate(matches, 1):
            if verbose:
                print(f"   Match {i}/{len(matches)}: {match.player1} vs {match.player2}")
            
            result = self.simulate_match(match, verbose=False)
            match_results.append(result)
            total_fantasy_points += result.player1_fantasy_points + result.player2_fantasy_points
        
        # Create slate simulation result
        slate_sim = SlateSimulation(
            simulation_id=simulation_id,
            timestamp=datetime.now().isoformat(),
            matches=match_results,
            total_fantasy_points=total_fantasy_points
        )
        
        # Store in history
        self.results_history.append(slate_sim)
        
        if verbose:
            print(f"✅ Slate #{simulation_id} complete! Total fantasy points: {total_fantasy_points:.1f}")
        
        return slate_sim
    
    def simulate_multiple_slates(self, matches: List[Match], num_simulations: int = 100, 
                               verbose: bool = True) -> List[SlateSimulation]:
        """Simulate the same slate multiple times"""
        if verbose:
            print(f"\n🎯 Running {num_simulations} simulations of {len(matches)}-match slate")
        
        simulations = []
        for i in range(1, num_simulations + 1):
            if verbose and i % 10 == 0:
                print(f"   Completed {i}/{num_simulations} simulations...")
            
            slate_sim = self.simulate_slate(matches, simulation_id=i, verbose=False)
            simulations.append(slate_sim)
        
        if verbose:
            print(f"✅ All {num_simulations} simulations complete!")
        
        return simulations
    
    def get_player_statistics(self, player_name: str, num_recent_sims: int = None) -> Dict[str, Any]:
        """Get aggregated statistics for a specific player across simulations"""
        if num_recent_sims:
            sims_to_analyze = self.results_history[-num_recent_sims:]
        else:
            sims_to_analyze = self.results_history
        
        player_results = []
        for sim in sims_to_analyze:
            player_data = sim.get_player_results()
            if player_name in player_data:
                player_results.append(player_data[player_name])
        
        if not player_results:
            return {"error": f"No data found for {player_name}"}
        
        # Calculate statistics
        fantasy_points = [r['fantasy_points'] for r in player_results]
        wins = [r['won'] for r in player_results]
        aces = [r['aces'] for r in player_results]
        breaks = [r['breaks'] for r in player_results]
        
        return {
            'player': player_name,
            'simulations': len(player_results),
            'avg_fantasy_points': sum(fantasy_points) / len(fantasy_points),
            'min_fantasy_points': min(fantasy_points),
            'max_fantasy_points': max(fantasy_points),
            'win_rate': sum(wins) / len(wins),
            'avg_aces': sum(aces) / len(aces),
            'avg_breaks': sum(breaks) / len(breaks),
            'surfaces_played': list(set(r['surface'] for r in player_results))
        }
    
    def export_results(self, filename: str = None, format: str = 'json') -> str:
        """Export simulation results to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"slate_simulations_{timestamp}"
        
        if format == 'json':
            filepath = f"{filename}.json"
            data = [asdict(sim) for sim in self.results_history]
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        
        elif format == 'csv':
            # Flatten results for CSV
            rows = []
            for sim in self.results_history:
                for match in sim.matches:
                    rows.append({
                        'simulation_id': sim.simulation_id,
                        'timestamp': sim.timestamp,
                        'match_id': match.match_id,
                        'player1': match.player1,
                        'player2': match.player2,
                        'surface': match.surface,
                        'winner': match.winner_name,
                        'final_score': match.final_score,
                        'p1_fantasy_points': match.player1_fantasy_points,
                        'p2_fantasy_points': match.player2_fantasy_points,
                        'p1_aces': match.player1_aces,
                        'p2_aces': match.player2_aces,
                        'p1_breaks': match.player1_breaks,
                        'p2_breaks': match.player2_breaks
                    })
            
            filepath = f"{filename}.csv"
            df = pd.DataFrame(rows)
            df.to_csv(filepath, index=False)
        
        print(f"📁 Results exported to: {filepath}")
        return filepath
    
    def clear_history(self):
        """Clear simulation history"""
        self.results_history = []
        print("🗑️ Simulation history cleared")
    
    def summary(self) -> Dict[str, Any]:
        """Get summary of all simulations"""
        if not self.results_history:
            return {"message": "No simulations run yet"}
        
        total_sims = len(self.results_history)
        total_matches = sum(len(sim.matches) for sim in self.results_history)
        avg_fantasy_points = sum(sim.total_fantasy_points for sim in self.results_history) / total_sims
        
        return {
            'total_simulations': total_sims,
            'total_matches_simulated': total_matches,
            'avg_fantasy_points_per_slate': avg_fantasy_points,
            'latest_simulation': self.results_history[-1].timestamp if self.results_history else None
        }
