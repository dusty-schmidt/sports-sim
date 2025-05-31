# DraftKings Tennis Scoring System

## Overview
This document outlines the official DraftKings fantasy tennis scoring system for single match contests. Players earn fantasy points based on their performance in individual tennis matches.

## Contest Format
- **Salary Cap**: $50,000 per lineup
- **Format**: Single match tennis
- **Scoring**: Best of 3 Sets (WTA) or Best of 5 Sets (Men's Grand Slams)

## Scoring Categories

### Base Scoring

| Category | Best of 3 Sets | Best of 5 Sets |
|----------|----------------|----------------|
| **Match Played** | +30 pts | +30 pts |
| **Game Won** | +2.5 pts | +2 pts |
| **Game Lost** | -2 pts | -1.6 pts |
| **Set Won** | +6 pts | +5 pts |
| **Set Lost** | -3 pts | -2.5 pts |
| **Match Won** | +6 pts | +5 pts |
| **Advanced By Walkover** | +30 pts | +30 pts |

### Point-Level Scoring

| Category | Best of 3 Sets | Best of 5 Sets |
|----------|----------------|----------------|
| **Ace** | +0.4 pts | +0.25 pts |
| **Double Fault** | -1 pt | -1 pt |
| **Break** | +0.75 pts | +0.5 pts |

### Bonus Categories

| Bonus Type | Best of 3 Sets | Best of 5 Sets |
|------------|----------------|----------------|
| **Clean Set Bonus** | +4 pts | +2.5 pts |
| **Straight Sets Bonus** | +6 pts | +5 pts |
| **No Double Fault Bonus** | +2.5 pts | +5 pts |
| **10+ Ace Bonus** | +2 pts | -- |
| **15+ Ace Bonus** | -- | +2 pts |

## Detailed Scoring Rules

### Clean Set Bonus
- Awarded for winning a set without losing a single game (6-0 or 7-0 in tiebreak)

### Straight Sets Bonus
- Awarded for winning the entire match without losing a set (2-0 in Best of 3, 3-0 in Best of 5)

### Break Points
- A "Break" is awarded when a player wins a game while their opponent is serving
- Each break of serve earns the breaking player points

### Ace Bonuses
- **Best of 3**: Bonus for hitting 10 or more aces in the match
- **Best of 5**: Bonus for hitting 15 or more aces in the match

## Example Scoring Scenarios (Best of 3 Sets)

### Scenario 1: Dominant Straight Set Win (6-2, 6-1)
- Match Played: +30 pts
- Match Won: +6 pts
- Sets Won (2): +12 pts (6 × 2)
- Sets Lost (0): 0 pts
- Games Won (12): +30 pts (2.5 × 12)
- Games Lost (3): -6 pts (-2 × 3)
- Aces (8): +3.2 pts (0.4 × 8)
- Double Faults (1): -1 pt
- Breaks (4): +3 pts (0.75 × 4)
- Straight Sets Bonus: +6 pts
- **Total: 83.2 points**

### Scenario 2: Close Three Set Win (6-4, 4-6, 6-3)
- Match Played: +30 pts
- Match Won: +6 pts
- Sets Won (2): +12 pts (6 × 2)
- Sets Lost (1): -3 pts (-3 × 1)
- Games Won (16): +40 pts (2.5 × 16)
- Games Lost (13): -26 pts (-2 × 13)
- Aces (5): +2 pts (0.4 × 5)
- Double Faults (3): -3 pts
- Breaks (3): +2.25 pts (0.75 × 3)
- **Total: 60.25 points**

### Scenario 3: Straight Set Loss (2-6, 1-6)
- Match Played: +30 pts
- Match Won: 0 pts
- Sets Won (0): 0 pts
- Sets Lost (2): -6 pts (-3 × 2)
- Games Won (3): +7.5 pts (2.5 × 3)
- Games Lost (12): -24 pts (-2 × 12)
- Aces (2): +0.8 pts (0.4 × 2)
- Double Faults (4): -4 pts
- Breaks (0): 0 pts
- **Total: 4.3 points**

## Key Tracking Requirements for Simulation

### Essential Stats to Track (Per Player)
1. **Match Participation**: Always +30 pts (unless walkover)
2. **Match Outcome**: Win (+6 pts) or Loss (0 pts)
3. **Sets Won/Lost**: +6 pts per set won, -3 pts per set lost
4. **Games Won/Lost**: +2.5 pts per game won, -2 pts per game lost
5. **Aces**: +0.4 pts per ace
6. **Double Faults**: -1 pt per double fault
7. **Breaks**: +0.75 pts per break of serve

### Bonus Tracking
1. **Clean Set**: +4 pts for winning a set 6-0 (or 7-0 in tiebreak)
2. **Straight Sets**: +6 pts for winning match without losing a set
3. **No Double Faults**: +2.5 pts for zero double faults in match
4. **10+ Aces**: +2 pts for 10 or more aces in match

### Critical Implementation Details

#### Game Counting
- **Games Won**: Every game won by the player (service holds + breaks)
- **Games Lost**: Every game lost by the player (broken serves + failed breaks)
- **Total Games**: Must equal opponent's total (zero-sum)

#### Break Counting
- **Break**: Winning a game when opponent is serving
- **Only the breaking player** gets break points
- **Service holds** do not count as breaks

#### Set Scoring
- **Set Won**: Player wins the set (regardless of score)
- **Set Lost**: Player loses the set
- **Clean Set**: Winning set 6-0, 7-0, or winning tiebreak 7-0

## Fantasy Scoring Formula (Best of 3)

```
Total Points = 30 (Match Played) +
               (Match Won × 6) +
               (Sets Won × 6) +
               (Sets Lost × -3) +
               (Games Won × 2.5) +
               (Games Lost × -2) +
               (Aces × 0.4) +
               (Double Faults × -1) +
               (Breaks × 0.75) +
               (Bonuses)

Bonuses = (Clean Sets × 4) +
          (Straight Sets × 6) +
          (No Double Faults × 2.5) +
          (10+ Aces × 2)
```

## Validation Requirements

### Statistical Realism
- **Ace rates**: 3-12% of service points (varies by player/surface)
- **Double fault rates**: 2-8% of service points
- **Games per set**: Typically 6-13 games (6-0 to 7-6 with tiebreak)
- **Break rates**: Usually 15-40% of return games

### Scoring Validation
- **Winners score more**: Match winners should typically outscore losers
- **Dominant wins score highest**: Straight set wins with many breaks
- **Consistent scoring**: Similar performances should yield similar scores
- **Bonus triggers**: Clean sets and ace bonuses should be rare but achievable

## Testing Scenarios

### High-Scoring Scenarios (80+ points)
- Straight set wins with multiple breaks
- High ace counts (8+ aces)
- Clean sets (6-0 sets)
- No double faults

### Medium-Scoring Scenarios (40-80 points)
- Three-set wins
- Moderate break counts
- Average ace/double fault ratios

### Low-Scoring Scenarios (<40 points)
- Straight set losses
- High double fault counts
- Few or no breaks
- Many games lost

### Edge Cases to Test
- Tiebreak-heavy matches (7-6, 7-6)
- Bagel sets (6-0)
- High ace matches (10+ aces)
- Error-prone matches (5+ double faults)
