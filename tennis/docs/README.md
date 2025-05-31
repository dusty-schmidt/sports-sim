# Tennis Project Documentation

## 🎾 Project Overview

This tennis project combines advanced simulation models with machine learning for comprehensive tennis match analysis, fantasy sports scoring, and betting insights.

## 📁 Project Structure

```
tennis/
├── .envrc                    # Environment configuration (direnv)
├── tennis_env/              # Virtual environment
├── pyproject.toml           # Project dependencies and configuration
├── sim_models/              # Tennis simulation models
│   ├── main_sim/           # Primary simulator (momentum, fatigue, variance)
│   └── the_oracle/         # ML-integrated simulator (betting, analytics)
├── ml_models/              # Machine learning components
│   └── src/                # ML source code
├── data/                   # Unified data directory
│   ├── tmcp/              # Tennis Match Charting Project data
│   ├── elo/               # ELO ratings
│   ├── exploratory/       # Analysis results
│   └── processed/         # Processed datasets
├── scripts/                # Utility scripts
│   ├── archive/           # Archived analysis scripts
│   ├── csv_processor.py   # Active utility
│   └── test_simulators.py # Simulator comparison tool
└── docs/                   # Documentation
```

## 🚀 Quick Start

### Environment Setup
```bash
# Activate environment (auto-installs dependencies)
source .envrc

# Test both simulators
python scripts/test_simulators.py
```

### Running Simulations

#### Main Simulator (Recommended)
```python
from sim_models.main_sim.simulator import FantasyTennisSimulator

sim = FantasyTennisSimulator()
p1_stats, p2_stats, sets = sim.simulate_match_detailed(
    "Novak Djokovic", "Rafael Nadal", "Clay", verbose=True
)
```

#### The Oracle (ML-Enhanced)
```python
from sim_models.the_oracle.core.data_engine import TennisOracleDataEngine
from sim_models.the_oracle.core.simulator import TennisOracleSimulator

data_engine = TennisOracleDataEngine()
simulator = TennisOracleSimulator(data_engine)
result = simulator.simulate_match_ultimate(
    "Novak Djokovic", "Rafael Nadal", "Clay",
    analysis_depth="comprehensive"
)
```

## 🎯 Simulator Features

### Main Sim Features
- ✅ **Momentum tracking** - Advanced momentum calculations
- ✅ **Fatigue modeling** - Set-by-set fatigue effects
- ✅ **Variance application** - Player-specific variance profiles
- ✅ **Pressure situations** - Break points, key moments
- ✅ **Fantasy scoring** - DraftKings compatible

### The Oracle Features
- ✅ **ML integration** - Player archetype classification
- ✅ **Betting analytics** - Edge detection and opportunities
- ✅ **Comprehensive analysis** - Multi-depth analysis modes
- ✅ **Data completeness** - Unified data engine

## 📊 Data Sources

- **Tennis Match Charting Project**: Point-by-point data (1.4M+ points)
- **ELO Ratings**: ATP/WTA player rankings
- **Processed Stats**: Calculated player statistics
- **Exploratory Analysis**: Feature engineering results

## 🔧 Development

### Environment Management
- **Single environment**: `tennis_env/` virtual environment
- **Dependency management**: `pyproject.toml` with editable install
- **Auto-activation**: direnv with `.envrc` configuration

### Testing
```bash
# Test both simulators
python scripts/test_simulators.py

# Test specific components
python -c "from sim_models.main_sim.simulator import FantasyTennisSimulator; print('✅ Working')"
```

## 📈 Next Steps

1. **Simulator Consolidation**: Merge ML features from the_oracle into main_sim
2. **ML Integration**: Connect ml_models/ with simulation engines
3. **Performance Optimization**: Profile and optimize simulation speed
4. **Enhanced Analytics**: Add more betting and fantasy insights

## 📋 File Descriptions

### Key Files
- `test_simulators.py` - Compare both simulation models
- `MERGE_CLEANUP_SUMMARY.md` - Project consolidation summary
- `pyproject.toml` - Project configuration and dependencies
- `.envrc` - Environment setup and activation

### Documentation
- `draftkings_scoring.md` - Fantasy sports scoring rules
- `decoder.csv` - Data format decoder
- `ml/` - Machine learning documentation

### Archived Scripts
- `scripts/archive/` - Historical data analysis scripts
- Preserved for reference but not actively maintained

## 🏆 Current Status

✅ **Environment**: Unified and working
✅ **Simulators**: Both functional
✅ **Data**: Consolidated and accessible
✅ **Dependencies**: Managed via pyproject.toml
✅ **Documentation**: Updated and current

Ready for Phase 2: Simulator consolidation and ML integration!
