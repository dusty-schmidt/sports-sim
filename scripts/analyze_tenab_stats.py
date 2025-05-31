#!/usr/bin/env python3
"""
Analyze the Tennis Abstract derived stats and identify what should be incorporated.
File location: /home/dustys/the net/tennis/scripts/analyze_tenab_stats.py
"""

import os
import sys
import pandas as pd

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def analyze_serve_stats():
    """Analyze the serve.csv stats and identify key metrics."""
    print("🎾 ANALYZING TENNIS ABSTRACT SERVE STATS")
    print("=" * 70)

    serve_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'tenab_stats', 'serve.csv')
    df = pd.read_csv(serve_file, sep='\t')  # Try tab-separated first

    # If that doesn't work, try comma-separated
    if len(df.columns) == 1:
        df = pd.read_csv(serve_file)

    print("📊 AVAILABLE SERVE METRICS:")
    print("-" * 40)
    for i, col in enumerate(df.columns):
        print(f"  {i}: {col}")

    print(f"\nFirst few rows:")
    print(df.head(3))

    print(f"\n🔍 KEY METRICS WE'RE MISSING:")
    print("-" * 40)

    # Find the player column (might be index 1)
    player_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]

    # Find Ben Shelton's stats for comparison
    shelton_row = df[df[player_col].str.contains('Ben Shelton', na=False)]
    if not shelton_row.empty:
        shelton = shelton_row.iloc[0]
        print(f"Ben Shelton example:")
        print(f"  SPW (Service Points Won): {shelton['SPW']}")
        print(f"  1st% (First Serve %): {shelton['1st%']}")
        print(f"  2nd% (Second Serve %): {shelton['2nd%']}")
        print(f"  Hld% (Hold %): {shelton['Hld%']}")
        print(f"  Ace%: {shelton['Ace%']}")
        print(f"  DF%: {shelton['DF%']}")

    print(f"\n💡 CRITICAL MISSING STATS:")
    print("-" * 40)
    print("1. **Hold% (Service Game Win Rate)**")
    print("   - Current sim: Calculated from point simulation")
    print("   - Real data: Direct measurement from matches")
    print("   - Impact: HUGE - this is the core of tennis!")

    print("\n2. **Separate 1st% and 2nd% Serve Win Rates**")
    print("   - Current sim: Uses overall service_points_won")
    print("   - Real data: 1st serve vs 2nd serve breakdown")
    print("   - Impact: Major variance and realism")

    print("\n3. **DF/2s (Double Faults per Second Serve)**")
    print("   - Current sim: Overall DF rate")
    print("   - Real data: DF rate specifically on second serves")
    print("   - Impact: More accurate pressure situations")

    return df


def analyze_return_stats():
    """Analyze the return.csv stats and identify key metrics."""
    print(f"\n🎾 ANALYZING TENNIS ABSTRACT RETURN STATS")
    print("=" * 70)

    return_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'tenab_stats', 'return.csv')
    df = pd.read_csv(return_file)

    print("📊 AVAILABLE RETURN METRICS:")
    print("-" * 40)
    for col in df.columns:
        print(f"  {col}")

    # Find Ben Shelton's stats for comparison
    shelton_row = df[df['Player'].str.contains('Ben Shelton', na=False)]
    if not shelton_row.empty:
        shelton = shelton_row.iloc[0]
        print(f"\nBen Shelton example:")
        print(f"  RPW (Return Points Won): {shelton['RPW']}")
        print(f"  v1st% (vs First Serve): {shelton['v1st%']}")
        print(f"  v2nd% (vs Second Serve): {shelton['v2nd%']}")
        print(f"  Brk% (Break %): {shelton['Brk%']}")

    print(f"\n💡 CRITICAL MISSING STATS:")
    print("-" * 40)
    print("1. **Brk% (Break Rate)**")
    print("   - Current sim: Calculated from point simulation")
    print("   - Real data: Direct measurement of return games won")
    print("   - Impact: HUGE - break rates are everything in tennis!")

    print("\n2. **v1st% and v2nd% (Return vs Serve Type)**")
    print("   - Current sim: Uses overall return_points_won")
    print("   - Real data: Return success vs 1st vs 2nd serves")
    print("   - Impact: Major - returners perform very differently vs serve types")

    print("\n3. **vAce% and vDF% (Opponent Ace/DF Rates)**")
    print("   - Current sim: Not considered")
    print("   - Real data: How often opponents ace/DF against this returner")
    print("   - Impact: Defensive return positioning effects")

    return df


def compare_with_current_simulation():
    """Compare Tennis Abstract stats with our current simulation."""
    print(f"\n🔧 COMPARISON WITH CURRENT SIMULATION")
    print("=" * 70)

    serve_df = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'tenab_stats', 'serve.csv'))
    return_df = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'tenab_stats', 'return.csv'))

    # Find Ben Shelton in both
    shelton_serve = serve_df[serve_df['Player'].str.contains('Ben Shelton', na=False)].iloc[0]
    shelton_return = return_df[return_df['Player'].str.contains('Ben Shelton', na=False)].iloc[0]

    print("📊 BEN SHELTON - REAL vs SIMULATION:")
    print("-" * 40)
    print("SERVE:")
    print(f"  Real Hold Rate: {shelton_serve['Hld%']}%")
    print(f"  Real 1st Serve Win: {shelton_serve['1st%']}%")
    print(f"  Real 2nd Serve Win: {shelton_serve['2nd%']}%")
    print(f"  Real Overall SPW: {shelton_serve['SPW']}%")
    print()
    print(f"  Current Sim SPW: ~61.3% (from our enhanced data)")
    print(f"  Current Sim Hold: Calculated from points (probably ~88%)")

    print("\nRETURN:")
    print(f"  Real Break Rate: {shelton_return['Brk%']}%")
    print(f"  Real vs 1st Serve: {shelton_return['v1st%']}%")
    print(f"  Real vs 2nd Serve: {shelton_return['v2nd%']}%")
    print(f"  Real Overall RPW: {shelton_return['RPW']}%")
    print()
    print(f"  Current Sim RPW: ~38.5% (from our enhanced data)")
    print(f"  Current Sim Break: Calculated from points (probably ~14%)")

    print(f"\n🚨 THE PROBLEM:")
    print("-" * 40)
    print("Our simulation calculates hold/break rates from point simulation,")
    print("but Tennis Abstract has the ACTUAL hold/break rates from real matches!")
    print()
    print("This explains why our simulation is off - we should use:")
    print(f"  1. Real hold rates ({shelton_serve['Hld%']}%) instead of calculated")
    print(f"  2. Real break rates ({shelton_return['Brk%']}%) instead of calculated")
    print(f"  3. Real serve type breakdowns (1st vs 2nd serve)")


def suggest_implementation_priority():
    """Suggest which stats to implement first for maximum impact."""
    print(f"\n🎯 IMPLEMENTATION PRIORITY")
    print("=" * 70)

    print("PHASE 1: HOLD/BREAK RATES (IMMEDIATE - HIGHEST IMPACT)")
    print("-" * 50)
    print("1. Load Hld% (Hold Rate) from serve.csv")
    print("2. Load Brk% (Break Rate) from return.csv")
    print("3. Use these DIRECTLY instead of point-by-point calculation")
    print("4. This should fix the Shelton vs Gigante issue immediately!")
    print()
    print("Expected impact:")
    print("  - Shelton Hold Rate: 88.4% (real) vs ~95% (current sim)")
    print("  - Shelton Break Rate: 14.5% (real) vs ~30% (current sim)")
    print("  - This alone should get us to ~65% win rate!")

    print("\nPHASE 2: SERVE TYPE BREAKDOWN (NEXT)")
    print("-" * 50)
    print("1. Use 1st% and 2nd% from serve.csv")
    print("2. Use v1st% and v2nd% from return.csv")
    print("3. Implement proper first/second serve logic")
    print("4. Add DF/2s (double faults per second serve)")

    print("\nPHASE 3: ADVANCED METRICS (LATER)")
    print("-" * 50)
    print("1. vAce% and vDF% (opponent rates against returner)")
    print("2. Pts/SG and PtsL/SG (points per service game)")
    print("3. Pressure situation modifiers")
    print("4. Surface-specific adjustments")

    print(f"\n🔥 IMMEDIATE ACTION:")
    print("-" * 40)
    print("Load the hold/break rates and use them DIRECTLY in simulation")
    print("instead of calculating from points. This should solve the")
    print("Shelton vs Gigante calibration issue immediately!")


def find_gigante_equivalent():
    """Find players similar to Gigante's level for comparison."""
    print(f"\n🔍 FINDING GIGANTE-LEVEL PLAYERS")
    print("=" * 70)

    serve_df = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'tenab_stats', 'serve.csv'))
    return_df = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'tenab_stats', 'return.csv'))

    # Look for players with similar win rates to what Gigante might have
    print("Players with 40-50% match win rates (similar to Gigante level):")
    print("-" * 60)

    low_win_rate_players = serve_df[serve_df['M W%'].str.rstrip('%').astype(float) < 55]

    for _, player in low_win_rate_players.head(10).iterrows():
        player_name = player['Player'].split(' (')[0]  # Remove URL part
        win_rate = player['M W%']
        hold_rate = player['Hld%']

        # Find corresponding return stats
        return_row = return_df[return_df['Player'].str.contains(player_name.split()[0], na=False)]
        if not return_row.empty:
            break_rate = return_row.iloc[0]['Brk%']
            print(f"  {player_name:<25}: {win_rate:>6} win | {hold_rate:>5}% hold | {break_rate:>5}% break")

    print(f"\nFor comparison, Ben Shelton:")
    shelton_serve = serve_df[serve_df['Player'].str.contains('Ben Shelton', na=False)].iloc[0]
    shelton_return = return_df[return_df['Player'].str.contains('Ben Shelton', na=False)].iloc[0]
    print(f"  Ben Shelton: {shelton_serve['M W%']:>6} win | {shelton_serve['Hld%']:>5}% hold | {shelton_return['Brk%']:>5}% break")


if __name__ == "__main__":
    serve_df = analyze_serve_stats()
    return_df = analyze_return_stats()
    compare_with_current_simulation()
    suggest_implementation_priority()
    find_gigante_equivalent()
