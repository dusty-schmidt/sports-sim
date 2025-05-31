"""
Simple CSV processing utilities for tennis data analysis.
Alternative to pandas for environments where pandas installation is difficult.
"""

import csv
from typing import Dict, List, Any, Optional
from pathlib import Path


class SimpleDataFrame:
    """A lightweight alternative to pandas DataFrame for basic CSV operations."""
    
    def __init__(self, data: List[Dict[str, Any]] = None, columns: List[str] = None):
        self.data = data or []
        self.columns = columns or []
        if self.data and not self.columns:
            self.columns = list(self.data[0].keys()) if self.data else []
    
    @classmethod
    def read_csv(cls, filepath: str, encoding: str = 'utf-8') -> 'SimpleDataFrame':
        """Read CSV file into SimpleDataFrame."""
        data = []
        columns = []
        
        try:
            with open(filepath, 'r', encoding=encoding, newline='') as file:
                reader = csv.DictReader(file)
                columns = reader.fieldnames or []
                data = list(reader)
        except UnicodeDecodeError:
            # Try different encodings
            for enc in ['latin-1', 'cp1252', 'utf-8-sig']:
                try:
                    with open(filepath, 'r', encoding=enc, newline='') as file:
                        reader = csv.DictReader(file)
                        columns = reader.fieldnames or []
                        data = list(reader)
                    break
                except UnicodeDecodeError:
                    continue
        
        return cls(data, columns)
    
    def __len__(self) -> int:
        return len(self.data)
    
    def __getitem__(self, key):
        if isinstance(key, str):
            # Column access
            return [row.get(key) for row in self.data]
        elif isinstance(key, int):
            # Row access
            return self.data[key]
        elif isinstance(key, slice):
            # Slice access
            return SimpleDataFrame(self.data[key], self.columns)
    
    def head(self, n: int = 5) -> 'SimpleDataFrame':
        """Return first n rows."""
        return SimpleDataFrame(self.data[:n], self.columns)
    
    def tail(self, n: int = 5) -> 'SimpleDataFrame':
        """Return last n rows."""
        return SimpleDataFrame(self.data[-n:], self.columns)
    
    def filter(self, condition_func) -> 'SimpleDataFrame':
        """Filter rows based on condition function."""
        filtered_data = [row for row in self.data if condition_func(row)]
        return SimpleDataFrame(filtered_data, self.columns)
    
    def unique(self, column: str) -> List[Any]:
        """Get unique values in a column."""
        values = [row.get(column) for row in self.data]
        return list(set(filter(None, values)))
    
    def group_by(self, column: str) -> Dict[Any, 'SimpleDataFrame']:
        """Group data by column values."""
        groups = {}
        for row in self.data:
            key = row.get(column)
            if key not in groups:
                groups[key] = []
            groups[key].append(row)
        
        return {k: SimpleDataFrame(v, self.columns) for k, v in groups.items()}
    
    def to_dict(self, orient: str = 'records') -> Any:
        """Convert to dictionary."""
        if orient == 'records':
            return self.data
        elif orient == 'list':
            return {col: self[col] for col in self.columns}
        elif orient == 'series':
            return {col: self[col] for col in self.columns}
    
    def describe(self) -> Dict[str, Dict[str, Any]]:
        """Basic statistics for numeric columns."""
        stats = {}
        for col in self.columns:
            values = [row.get(col) for row in self.data]
            numeric_values = []
            
            for val in values:
                try:
                    numeric_values.append(float(val))
                except (ValueError, TypeError):
                    continue
            
            if numeric_values:
                stats[col] = {
                    'count': len(numeric_values),
                    'mean': sum(numeric_values) / len(numeric_values),
                    'min': min(numeric_values),
                    'max': max(numeric_values),
                    'unique': len(set(str(v) for v in values if v is not None))
                }
            else:
                stats[col] = {
                    'count': len([v for v in values if v is not None]),
                    'unique': len(set(str(v) for v in values if v is not None)),
                    'type': 'text'
                }
        
        return stats
    
    def info(self) -> Dict[str, Any]:
        """Information about the DataFrame."""
        return {
            'rows': len(self.data),
            'columns': len(self.columns),
            'column_names': self.columns,
            'memory_usage': f"~{len(str(self.data)) / 1024:.1f} KB"
        }


class TennisStatsAnalyzer:
    """Analyze tennis stats files without pandas dependency."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.loaded_files = {}
    
    def load_stats_file(self, filename: str) -> Optional[SimpleDataFrame]:
        """Load a tennis stats CSV file."""
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            print(f"❌ File not found: {filepath}")
            return None
        
        try:
            df = SimpleDataFrame.read_csv(str(filepath))
            self.loaded_files[filename] = df
            print(f"✅ Loaded {filename}: {len(df)} rows, {len(df.columns)} columns")
            return df
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")
            return None
    
    def analyze_file_structure(self, filename: str) -> Dict[str, Any]:
        """Analyze the structure of a stats file."""
        df = self.loaded_files.get(filename) or self.load_stats_file(filename)
        
        if df is None:
            return {}
        
        info = df.info()
        stats = df.describe()
        sample_data = df.head(3).to_dict('records')
        
        return {
            'filename': filename,
            'info': info,
            'statistics': stats,
            'sample_data': sample_data,
            'player_coverage': self._estimate_player_coverage(df),
            'data_quality': self._assess_data_quality(df)
        }
    
    def _estimate_player_coverage(self, df: SimpleDataFrame) -> int:
        """Estimate number of unique players in the dataset."""
        # Look for player name columns
        player_columns = [col for col in df.columns 
                         if any(keyword in col.lower() 
                               for keyword in ['player', 'name'])]
        
        if player_columns:
            return len(df.unique(player_columns[0]))
        return len(df)
    
    def _assess_data_quality(self, df: SimpleDataFrame) -> Dict[str, Any]:
        """Assess data quality metrics."""
        total_cells = len(df) * len(df.columns)
        empty_cells = 0
        
        for row in df.data:
            for col in df.columns:
                if not row.get(col) or row.get(col) == '':
                    empty_cells += 1
        
        return {
            'completeness': (total_cells - empty_cells) / total_cells if total_cells > 0 else 0,
            'total_cells': total_cells,
            'empty_cells': empty_cells,
            'data_types': self._infer_column_types(df)
        }
    
    def _infer_column_types(self, df: SimpleDataFrame) -> Dict[str, str]:
        """Infer data types for each column."""
        types = {}
        
        for col in df.columns:
            values = [row.get(col) for row in df.data[:100]]  # Sample first 100 rows
            
            numeric_count = 0
            text_count = 0
            
            for val in values:
                if val is None or val == '':
                    continue
                try:
                    float(val)
                    numeric_count += 1
                except (ValueError, TypeError):
                    text_count += 1
            
            if numeric_count > text_count:
                types[col] = 'numeric'
            else:
                types[col] = 'text'
        
        return types


def main():
    """Example usage of the CSV processor."""
    analyzer = TennisStatsAnalyzer("data")
    
    # Example: analyze a stats file
    result = analyzer.analyze_file_structure("charting-m-stats-Overview.csv")
    
    if result:
        print("📊 File Analysis Results:")
        print(f"Rows: {result['info']['rows']}")
        print(f"Columns: {result['info']['columns']}")
        print(f"Player Coverage: {result['player_coverage']}")
        print(f"Data Completeness: {result['data_quality']['completeness']:.1%}")


if __name__ == "__main__":
    main()
