# Archived Analysis Scripts

This directory contains historical data analysis and feature engineering scripts that were used during the development of the tennis simulation models. These scripts are preserved for reference but are not actively maintained.

## 📊 Data Analysis Scripts

### Player Statistics
- `calculate_real_player_stats.py` - Extract player statistics from match data
- `calculate_player_variance.py` - Calculate player-specific variance profiles
- `calculate_time_weighted_stats.py` - Time-weighted statistical analysis

### Feature Engineering
- `extract_clutch_factors.py` - Extract clutch performance factors
- `extract_real_serving_stats.py` - Extract serving statistics from real data
- `analyze_momentum_endurance.py` - Analyze momentum and endurance patterns

### Data Exploration
- `comprehensive_data_analysis.py` - Comprehensive dataset analysis
- `analyze_new_data_files.py` - Analysis of new data sources
- `analyze_keypoints_data.py` - Key points analysis
- `analyze_surface_variance.py` - Surface-specific variance analysis
- `quick_data_insights.py` - Quick data insights and summaries

### Testing & Validation
- `test_clutch_factor_integration.py` - Test clutch factor integration
- `test_point_simulation_granular.py` - Granular point simulation testing
- `test_real_data_improvements.py` - Validate real data improvements

## 🎯 Purpose

These scripts were instrumental in:
1. **Data Discovery** - Understanding the tennis datasets
2. **Feature Engineering** - Creating player profiles and statistics
3. **Model Validation** - Testing simulation accuracy
4. **Performance Analysis** - Analyzing player patterns and tendencies

## 📋 Current Status

- **Archived**: No longer actively maintained
- **Reference**: Available for understanding development process
- **Superseded**: Functionality integrated into main simulators
- **Historical**: Documents the evolution of the project

## 🔄 Migration

The insights and functionality from these scripts have been integrated into:
- `sim_models/main_sim/` - Core simulation mechanics
- `sim_models/the_oracle/` - ML-enhanced simulation
- `ml_models/` - Machine learning components

## 💡 Usage

If you need to reference or run any of these scripts:

```bash
# Activate environment
source ../../.envrc

# Run archived script (example)
python archive/comprehensive_data_analysis.py
```

**Note**: Some scripts may require data paths or dependencies that have changed since archival.
