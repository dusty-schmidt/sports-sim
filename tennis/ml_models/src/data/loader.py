"""
Match Charting Project Data Loader

Loads and preprocesses tennis match data from the MCP dataset for analysis.
"""

import pandas as pd
import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict


class MCPDataLoader:
    """Load and preprocess Match Charting Project data."""
    
    def __init__(self, data_dir: str = "TMCPdata/tennis_MatchChartingProject"):
        """
        Initialize the data loader.
        
        Args:
            data_dir: Path to the MCP data directory
        """
        self.data_dir = Path(data_dir)
        self.points_data = None
        self.matches_data = None
        self.stats_data = None
        
    def load_all_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load all available MCP data files.
        
        Returns:
            Dictionary containing all loaded datasets
        """
        print("🔄 Loading Match Charting Project data...")
        
        data = {}
        
        # Load point-by-point data
        print("   📊 Loading point-by-point data...")
        data['men_points'] = self._load_points_data('charting-m-points-2020s.csv')
        data['women_points'] = self._load_points_data('charting-w-points-2020s.csv')
        
        # Load match metadata
        print("   🎾 Loading match metadata...")
        data['men_matches'] = self._load_matches_data('charting-m-matches.csv')
        data['women_matches'] = self._load_matches_data('charting-w-matches.csv')
        
        # Load statistical summaries
        print("   📈 Loading statistical summaries...")
        data['men_stats'] = self._load_stats_data('charting-m-stats-Overview.csv')
        data['women_stats'] = self._load_stats_data('charting-w-stats-Overview.csv')
        
        print(f"✅ Data loading complete!")
        self._print_data_summary(data)
        
        return data
    
    def _load_points_data(self, filename: str) -> pd.DataFrame:
        """Load point-by-point data from CSV file."""
        file_path = self.data_dir / filename
        
        if not file_path.exists():
            print(f"   ⚠️  Warning: {filename} not found")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            print(f"   ✅ Loaded {len(df):,} points from {filename}")
            return df
        except Exception as e:
            print(f"   ❌ Error loading {filename}: {e}")
            return pd.DataFrame()
    
    def _load_matches_data(self, filename: str) -> pd.DataFrame:
        """Load match metadata from CSV file."""
        file_path = self.data_dir / filename
        
        if not file_path.exists():
            print(f"   ⚠️  Warning: {filename} not found")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            print(f"   ✅ Loaded {len(df):,} matches from {filename}")
            return df
        except Exception as e:
            print(f"   ❌ Error loading {filename}: {e}")
            return pd.DataFrame()
    
    def _load_stats_data(self, filename: str) -> pd.DataFrame:
        """Load statistical summary data from CSV file."""
        file_path = self.data_dir / filename
        
        if not file_path.exists():
            print(f"   ⚠️  Warning: {filename} not found")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            print(f"   ✅ Loaded {len(df):,} player stats from {filename}")
            return df
        except Exception as e:
            print(f"   ❌ Error loading {filename}: {e}")
            return pd.DataFrame()
    
    def _print_data_summary(self, data: Dict[str, pd.DataFrame]) -> None:
        """Print summary of loaded data."""
        print("\n📊 DATA SUMMARY:")
        print("=" * 50)
        
        total_points = 0
        total_matches = 0
        total_players = 0
        
        for key, df in data.items():
            if not df.empty:
                print(f"   {key}: {len(df):,} records")
                
                if 'points' in key:
                    total_points += len(df)
                elif 'matches' in key:
                    total_matches += len(df)
                elif 'stats' in key:
                    total_players += len(df)
        
        print("=" * 50)
        print(f"📈 TOTALS:")
        print(f"   • {total_points:,} total points")
        print(f"   • {total_matches:,} total matches")
        print(f"   • {total_players:,} total players")
        print("=" * 50)
    
    def get_sample_data(self, dataset: str, n_samples: int = 1000) -> pd.DataFrame:
        """
        Get a sample of data for testing/development.
        
        Args:
            dataset: Name of dataset ('men_points', 'women_points', etc.)
            n_samples: Number of samples to return
            
        Returns:
            Sample DataFrame
        """
        data = self.load_all_data()
        
        if dataset not in data or data[dataset].empty:
            print(f"❌ Dataset '{dataset}' not found or empty")
            return pd.DataFrame()
        
        df = data[dataset]
        sample_size = min(n_samples, len(df))
        sample = df.head(sample_size).copy()
        
        print(f"📊 Returning {len(sample):,} samples from {dataset}")
        return sample
    
    def filter_by_date_range(self, df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Filter data by date range.
        
        Args:
            df: DataFrame with date column
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Filtered DataFrame
        """
        # Try to find date column
        date_columns = [col for col in df.columns if 'date' in col.lower()]
        
        if not date_columns:
            print("⚠️  No date column found for filtering")
            return df
        
        date_col = date_columns[0]
        
        try:
            df[date_col] = pd.to_datetime(df[date_col])
            filtered = df[
                (df[date_col] >= start_date) & 
                (df[date_col] <= end_date)
            ].copy()
            
            print(f"📅 Filtered to {len(filtered):,} records between {start_date} and {end_date}")
            return filtered
            
        except Exception as e:
            print(f"❌ Error filtering by date: {e}")
            return df
    
    def get_player_matches(self, player_name: str, dataset: str = 'men_matches') -> pd.DataFrame:
        """
        Get all matches for a specific player.
        
        Args:
            player_name: Name of the player
            dataset: Dataset to search ('men_matches' or 'women_matches')
            
        Returns:
            DataFrame of player's matches
        """
        data = self.load_all_data()
        
        if dataset not in data or data[dataset].empty:
            print(f"❌ Dataset '{dataset}' not found or empty")
            return pd.DataFrame()
        
        df = data[dataset]
        
        # Search in player columns
        player_columns = [col for col in df.columns if 'player' in col.lower()]
        
        if not player_columns:
            print("⚠️  No player columns found")
            return pd.DataFrame()
        
        # Filter for matches involving the player
        mask = pd.Series([False] * len(df))
        for col in player_columns:
            mask |= df[col].str.contains(player_name, case=False, na=False)
        
        player_matches = df[mask].copy()
        
        print(f"🎾 Found {len(player_matches)} matches for {player_name}")
        return player_matches


def main():
    """Demonstrate data loading capabilities."""
    loader = MCPDataLoader()
    
    print("🎾 MATCH CHARTING PROJECT DATA LOADER")
    print("=" * 60)
    
    # Load all data
    data = loader.load_all_data()
    
    # Show sample of point data
    if 'men_points' in data and not data['men_points'].empty:
        print("\n📊 SAMPLE POINT DATA:")
        print("=" * 40)
        sample = data['men_points'].head(5)
        for col in sample.columns:
            print(f"   {col}: {sample[col].iloc[0] if not sample.empty else 'N/A'}")
    
    # Show available datasets
    print("\n📈 AVAILABLE DATASETS:")
    print("=" * 40)
    for key, df in data.items():
        if not df.empty:
            print(f"   • {key}: {len(df):,} records")
            print(f"     Columns: {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")


if __name__ == "__main__":
    main()
