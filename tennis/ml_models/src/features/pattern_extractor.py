"""
Pattern Extractor

Extracts betting-relevant patterns from tennis point data.
"""

import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional


class PatternExtractor:
    """Extract patterns from tennis point data for betting analysis."""
    
    def __init__(self):
        """Initialize the pattern extractor."""
        self.extracted_features = {}
        
    def extract_all_features(self, points_df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract all betting-relevant features from point data.
        
        Args:
            points_df: DataFrame containing point-by-point data
            
        Returns:
            DataFrame with extracted features
        """
        print("🔧 Extracting betting features from point data...")
        
        features_df = points_df.copy()
        
        # Extract shot sequence features
        features_df = self._extract_shot_features(features_df)
        
        # Extract momentum features
        features_df = self._extract_momentum_features(features_df)
        
        # Extract pressure features
        features_df = self._extract_pressure_features(features_df)
        
        # Extract serve features
        features_df = self._extract_serve_features(features_df)
        
        print(f"✅ Extracted {len([c for c in features_df.columns if c.startswith('feature_')])} features")
        
        return features_df
    
    def _extract_shot_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract shot sequence and pattern features."""
        print("   🎾 Extracting shot sequence features...")
        
        # Initialize feature columns
        df['feature_rally_length'] = 0
        df['feature_has_forehand'] = 0
        df['feature_has_backhand'] = 0
        df['feature_is_winner'] = 0
        df['feature_is_error'] = 0
        df['feature_is_ace'] = 0
        
        for idx, row in df.iterrows():
            sequence = str(row.get('Notes', ''))
            
            if pd.isna(sequence) or sequence == 'nan':
                continue
            
            # Rally length (count of f and b shots)
            rally_length = len([c for c in sequence if c in 'fb'])
            df.at[idx, 'feature_rally_length'] = rally_length
            
            # Shot types
            df.at[idx, 'feature_has_forehand'] = 1 if 'f' in sequence else 0
            df.at[idx, 'feature_has_backhand'] = 1 if 'b' in sequence else 0
            
            # Outcomes
            df.at[idx, 'feature_is_winner'] = 1 if '+' in sequence else 0
            df.at[idx, 'feature_is_error'] = 1 if '@' in sequence else 0
            df.at[idx, 'feature_is_ace'] = 1 if '#' in sequence else 0
        
        return df
    
    def _extract_momentum_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract momentum-related features."""
        print("   📈 Extracting momentum features...")
        
        # Initialize momentum features
        df['feature_momentum_server'] = 0.5  # Neutral momentum
        df['feature_points_in_run'] = 1
        df['feature_run_direction'] = 0  # 1 for server, -1 for returner
        
        # Group by match if possible
        if 'match_id' in df.columns:
            for match_id in df['match_id'].unique():
                match_mask = df['match_id'] == match_id
                match_df = df[match_mask].copy()
                
                # Calculate momentum for this match
                momentum_features = self._calculate_momentum_for_match(match_df)
                
                # Update the main dataframe
                for feature, values in momentum_features.items():
                    df.loc[match_mask, feature] = values
        
        return df
    
    def _calculate_momentum_for_match(self, match_df: pd.DataFrame) -> Dict[str, List]:
        """Calculate momentum features for a single match."""
        momentum_features = {
            'feature_momentum_server': [],
            'feature_points_in_run': [],
            'feature_run_direction': []
        }
        
        # Track point winners
        point_winners = []
        for _, row in match_df.iterrows():
            winner = row.get('PtWinner', '0')
            try:
                point_winners.append(int(winner))
            except (ValueError, TypeError):
                point_winners.append(0)
        
        # Calculate momentum using sliding window
        window_size = 5
        current_run = 1
        current_player = point_winners[0] if point_winners else 0
        
        for i, winner in enumerate(point_winners):
            # Calculate momentum (recent points weighted)
            start_idx = max(0, i - window_size + 1)
            recent_points = point_winners[start_idx:i+1]
            server_points = sum(1 for p in recent_points if p == 1)
            momentum = server_points / len(recent_points) if recent_points else 0.5
            
            # Calculate current run
            if i > 0 and winner == point_winners[i-1]:
                current_run += 1
            else:
                current_run = 1
                current_player = winner
            
            # Store features
            momentum_features['feature_momentum_server'].append(momentum)
            momentum_features['feature_points_in_run'].append(current_run)
            momentum_features['feature_run_direction'].append(1 if current_player == 1 else -1)
        
        return momentum_features
    
    def _extract_pressure_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract pressure situation features."""
        print("   🎯 Extracting pressure features...")
        
        # Initialize pressure features
        df['feature_is_break_point'] = 0
        df['feature_is_deuce'] = 0
        df['feature_is_game_point'] = 0
        df['feature_pressure_level'] = 0.0
        
        for idx, row in df.iterrows():
            # Extract score information
            score = str(row.get('Pts', ''))
            
            if pd.isna(score) or score == 'nan':
                continue
            
            pressure_level = 0.0
            
            # Break point situations
            if any(bp in score for bp in ['40-30', '40-AD', 'AD-40', '30-40']):
                df.at[idx, 'feature_is_break_point'] = 1
                pressure_level += 0.8
            
            # Deuce situations
            if '40-40' in score or 'Deuce' in score:
                df.at[idx, 'feature_is_deuce'] = 1
                pressure_level += 0.6
            
            # Game point situations
            if '40-' in score and '40-40' not in score:
                df.at[idx, 'feature_is_game_point'] = 1
                pressure_level += 0.4
            
            df.at[idx, 'feature_pressure_level'] = pressure_level
        
        return df
    
    def _extract_serve_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract serve-related features."""
        print("   🎯 Extracting serve features...")
        
        # Initialize serve features
        df['feature_serve_zone'] = 5  # Default center
        df['feature_serve_wide'] = 0
        df['feature_serve_body'] = 0
        df['feature_serve_t'] = 0
        
        for idx, row in df.iterrows():
            sequence = str(row.get('Notes', ''))
            
            if pd.isna(sequence) or sequence == 'nan' or len(sequence) == 0:
                continue
            
            # First character indicates serve placement
            first_char = sequence[0]
            if first_char.isdigit():
                serve_zone = int(first_char)
                df.at[idx, 'feature_serve_zone'] = serve_zone
                
                # Categorize serve placement
                if serve_zone in [3, 6, 9]:  # Wide serves
                    df.at[idx, 'feature_serve_wide'] = 1
                elif serve_zone in [2, 5, 8]:  # Body serves
                    df.at[idx, 'feature_serve_body'] = 1
                elif serve_zone in [1, 4, 7]:  # T serves
                    df.at[idx, 'feature_serve_t'] = 1
        
        return df


def main():
    """Demonstrate feature extraction."""
    print("🔧 PATTERN EXTRACTOR DEMONSTRATION")
    print("=" * 50)
    
    # Create sample data
    sample_data = pd.DataFrame({
        'Notes': ['6f2b1+', '5@', '4f3b2f1@', '6r1f2b3f4+', '#'],
        'PtWinner': [1, 0, 0, 1, 1],
        'Pts': ['30-15', '40-30', 'Deuce', '15-0', '0-0'],
        'match_id': ['match1', 'match1', 'match1', 'match1', 'match1']
    })
    
    print("📊 Sample input data:")
    print(sample_data)
    
    # Extract features
    extractor = PatternExtractor()
    features_df = extractor.extract_all_features(sample_data)
    
    # Show extracted features
    feature_columns = [col for col in features_df.columns if col.startswith('feature_')]
    print(f"\n🔧 Extracted {len(feature_columns)} features:")
    print(features_df[feature_columns])


if __name__ == "__main__":
    main()
