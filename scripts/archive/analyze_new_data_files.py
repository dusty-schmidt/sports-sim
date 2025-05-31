"""
Analyze the newly added Overview, ServeBasics, and Rally data files
Extract key insights and prepare for integration into simulation
"""

import pandas as pd
import numpy as np
import json
from collections import defaultdict

def analyze_overview_data():
    """Analyze Overview files for key player statistics."""
    print("ANALYZING OVERVIEW DATA")
    print("="*60)
    
    overview_data = {}
    
    # Load men's and women's overview data
    for gender, file_suffix in [('M', 'm'), ('W', 'w')]:
        try:
            df = pd.read_csv(f"data/charting-{file_suffix}-stats-Overview.csv")
            print(f"\n{gender} Overview: {len(df)} players")
            print(f"Columns: {list(df.columns)}")
            
            # Show sample data
            if len(df) > 0:
                print(f"Sample data:")
                for col in df.columns[:8]:  # First 8 columns
                    if col in df.columns:
                        sample_vals = df[col].dropna().head(3).tolist()
                        print(f"  {col}: {sample_vals}")
            
            overview_data[gender] = df
            
        except Exception as e:
            print(f"Error loading {gender} overview: {e}")
    
    return overview_data

def analyze_serve_basics_data():
    """Analyze ServeBasics files for actual serving statistics."""
    print("\n\nANALYZING SERVE BASICS DATA")
    print("="*60)
    
    serve_data = {}
    
    for gender, file_suffix in [('M', 'm'), ('W', 'w')]:
        try:
            df = pd.read_csv(f"data/charting-{file_suffix}-stats-ServeBasics.csv")
            print(f"\n{gender} ServeBasics: {len(df)} players")
            print(f"Columns: {list(df.columns)}")
            
            # Show sample data
            if len(df) > 0:
                print(f"Sample data:")
                for col in df.columns[:8]:
                    if col in df.columns:
                        sample_vals = df[col].dropna().head(3).tolist()
                        print(f"  {col}: {sample_vals}")
            
            serve_data[gender] = df
            
        except Exception as e:
            print(f"Error loading {gender} serve basics: {e}")
    
    return serve_data

def analyze_rally_data():
    """Analyze Rally files for rally length distributions."""
    print("\n\nANALYZING RALLY DATA")
    print("="*60)
    
    rally_data = {}
    
    for gender, file_suffix in [('M', 'm'), ('W', 'w')]:
        try:
            df = pd.read_csv(f"data/charting-{file_suffix}-stats-Rally.csv")
            print(f"\n{gender} Rally: {len(df)} players")
            print(f"Columns: {list(df.columns)}")
            
            # Show sample data
            if len(df) > 0:
                print(f"Sample data:")
                for col in df.columns[:8]:
                    if col in df.columns:
                        sample_vals = df[col].dropna().head(3).tolist()
                        print(f"  {col}: {sample_vals}")
            
            rally_data[gender] = df
            
        except Exception as e:
            print(f"Error loading {gender} rally: {e}")
    
    return rally_data

def extract_actual_serving_stats(serve_data):
    """Extract actual ace rates and double fault rates from ServeBasics."""
    print("\n\nEXTRACTING ACTUAL SERVING STATISTICS")
    print("="*60)
    
    actual_stats = {}
    
    for gender, df in serve_data.items():
        if df is None or len(df) == 0:
            continue
            
        print(f"\n{gender} Serving Statistics:")
        
        # Look for ace and double fault columns
        ace_cols = [col for col in df.columns if 'ace' in col.lower()]
        df_cols = [col for col in df.columns if 'fault' in col.lower() or 'df' in col.lower()]
        
        print(f"  Ace columns found: {ace_cols}")
        print(f"  Double fault columns found: {df_cols}")
        
        if 'Player' in df.columns:
            # Extract stats for known players
            for _, row in df.head(10).iterrows():  # Sample first 10
                player = row['Player']
                player_stats = {}
                
                # Extract ace rate
                for ace_col in ace_cols:
                    if not pd.isna(row[ace_col]):
                        player_stats[ace_col] = row[ace_col]
                
                # Extract double fault rate  
                for df_col in df_cols:
                    if not pd.isna(row[df_col]):
                        player_stats[df_col] = row[df_col]
                
                if player_stats:
                    actual_stats[player] = player_stats
                    print(f"  {player}: {player_stats}")
    
    return actual_stats

def extract_rally_patterns(rally_data):
    """Extract rally length patterns from Rally data."""
    print("\n\nEXTRACTING RALLY PATTERNS")
    print("="*60)
    
    rally_patterns = {}
    
    for gender, df in rally_data.items():
        if df is None or len(df) == 0:
            continue
            
        print(f"\n{gender} Rally Patterns:")
        
        # Look for rally length columns
        rally_cols = [col for col in df.columns if any(x in col.lower() for x in ['rally', 'shot', 'length'])]
        print(f"  Rally columns found: {rally_cols}")
        
        # Look for percentage/distribution columns
        pct_cols = [col for col in df.columns if '%' in col or 'pct' in col.lower()]
        print(f"  Percentage columns found: {pct_cols}")
        
        if len(df) > 0:
            # Sample rally data
            print(f"  Sample rally data:")
            for col in rally_cols[:5]:
                if col in df.columns:
                    sample_vals = df[col].dropna().head(3).tolist()
                    print(f"    {col}: {sample_vals}")
    
    return rally_patterns

def compare_with_current_stats(actual_stats):
    """Compare actual stats with our current calculated stats."""
    print("\n\nCOMPARING WITH CURRENT STATISTICS")
    print("="*60)
    
    try:
        # Load our current stats
        with open('data/calculated_player_stats.json', 'r') as f:
            current_stats = json.load(f)
        
        print("Comparison for sample players:")
        print(f"{'Player':<20} {'Current Ace':<12} {'Actual Ace':<12} {'Difference':<12}")
        print("-" * 60)
        
        comparisons = []
        for player, actual_data in list(actual_stats.items())[:10]:
            if player in current_stats:
                current_ace = current_stats[player]['ace_rate']
                
                # Find actual ace rate (look for percentage columns)
                actual_ace = None
                for key, val in actual_data.items():
                    if 'ace' in key.lower() and isinstance(val, (int, float)):
                        if 0 <= val <= 100:  # Likely a percentage
                            actual_ace = val
                            break
                        elif 0 <= val <= 1:  # Likely a decimal
                            actual_ace = val * 100
                            break
                
                if actual_ace is not None:
                    diff = abs(current_ace - actual_ace)
                    comparisons.append(diff)
                    print(f"{player:<20} {current_ace:<12.2f} {actual_ace:<12.2f} {diff:<12.2f}")
        
        if comparisons:
            avg_diff = np.mean(comparisons)
            print(f"\nAverage difference: {avg_diff:.2f} percentage points")
            
            if avg_diff < 2.0:
                print("✅ Our calculated stats are quite accurate!")
            elif avg_diff < 5.0:
                print("⚠️  Moderate differences - consider updating with actual data")
            else:
                print("❌ Large differences - should replace with actual data")
        
    except Exception as e:
        print(f"Could not compare with current stats: {e}")

def main():
    """Analyze all new data files."""
    print("ANALYZING NEW DATA FILES")
    print("="*80)
    print("Files: Overview, ServeBasics, Rally")
    print("="*80)
    
    # Analyze each file type
    overview_data = analyze_overview_data()
    serve_data = analyze_serve_basics_data()
    rally_data = analyze_rally_data()
    
    # Extract key insights
    actual_stats = extract_actual_serving_stats(serve_data)
    rally_patterns = extract_rally_patterns(rally_data)
    
    # Compare with current approach
    compare_with_current_stats(actual_stats)
    
    # Save analysis results
    analysis_results = {
        'overview_summary': {gender: len(df) if df is not None else 0 for gender, df in overview_data.items()},
        'serve_summary': {gender: len(df) if df is not None else 0 for gender, df in serve_data.items()},
        'rally_summary': {gender: len(df) if df is not None else 0 for gender, df in rally_data.items()},
        'actual_serving_stats': actual_stats
    }
    
    with open('data/new_data_analysis.json', 'w') as f:
        json.dump(analysis_results, f, indent=2, default=str)
    
    print(f"\n✅ Analysis complete! Results saved to data/new_data_analysis.json")
    
    # Recommendations
    print(f"\n" + "="*60)
    print("INTEGRATION RECOMMENDATIONS")
    print("="*60)
    
    if actual_stats:
        print("✅ ServeBasics contains actual serving statistics")
        print("   Recommend: Replace calculated ace/DF rates with actual data")
    
    if overview_data:
        print("✅ Overview data available for validation")
        print("   Recommend: Cross-check player classifications")
    
    if rally_data:
        print("✅ Rally data available for point simulation")
        print("   Recommend: Replace exponential(3.0) with actual distributions")

if __name__ == "__main__":
    main()
