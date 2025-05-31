import React, { useState, useEffect } from 'react';
import { Play, Pause, RotateCcw } from 'lucide-react';

const MLBSimulator = () => {
  // Team rosters with realistic stats
  const teams = {
    'Yankees': {
      lineup: [
        { name: 'Aaron Judge', pos: 'RF', avg: 0.311, obp: 0.404, ops: 1.111 },
        { name: 'Gleyber Torres', pos: '2B', avg: 0.273, obp: 0.339, ops: 0.751 },
        { name: 'Juan Soto', pos: 'LF', avg: 0.288, obp: 0.421, ops: 0.953 },
        { name: 'Giancarlo Stanton', pos: 'DH', avg: 0.243, obp: 0.331, ops: 0.792 },
        { name: 'Anthony Rizzo', pos: '1B', avg: 0.228, obp: 0.301, ops: 0.717 },
        { name: 'DJ LeMahieu', pos: '3B', avg: 0.261, obp: 0.335, ops: 0.695 },
        { name: 'Jose Trevino', pos: 'C', avg: 0.215, obp: 0.276, ops: 0.615 },
        { name: 'Anthony Volpe', pos: 'SS', avg: 0.243, obp: 0.303, ops: 0.657 },
        { name: 'Alex Verdugo', pos: 'CF', avg: 0.233, obp: 0.291, ops: 0.632 }
      ],
      pitcher: { name: 'Gerrit Cole', era: 3.41, whip: 1.13, k9: 10.9 }
    },
    'Dodgers': {
      lineup: [
        { name: 'Mookie Betts', pos: 'RF', avg: 0.289, obp: 0.372, ops: 0.892 },
        { name: 'Freddie Freeman', pos: '1B', avg: 0.282, obp: 0.378, ops: 0.849 },
        { name: 'Will Smith', pos: 'C', avg: 0.248, obp: 0.328, ops: 0.794 },
        { name: 'Max Muncy', pos: '3B', avg: 0.232, obp: 0.360, ops: 0.811 },
        { name: 'Teoscar Hernandez', pos: 'LF', avg: 0.272, obp: 0.339, ops: 0.840 },
        { name: 'Gavin Lux', pos: '2B', avg: 0.251, obp: 0.320, ops: 0.712 },
        { name: 'Tommy Edman', pos: 'SS', avg: 0.237, obp: 0.294, ops: 0.646 },
        { name: 'Enrique Hernandez', pos: 'CF', avg: 0.229, obp: 0.302, ops: 0.641 },
        { name: 'Shohei Ohtani', pos: 'DH', avg: 0.310, obp: 0.390, ops: 1.036 }
      ],
      pitcher: { name: 'Walker Buehler', era: 5.38, whip: 1.55, k9: 8.7 }
    }
  };

  const [gameState, setGameState] = useState({
    inning: 1,
    topInning: true,
    homeTeam: 'Yankees',
    awayTeam: 'Dodgers',
    homeScore: 0,
    awayScore: 0,
    outs: 0,
    balls: 0,
    strikes: 0,
    bases: { first: null, second: null, third: null },
    currentBatter: 0,
    battingTeam: 'Dodgers',
    pitchingTeam: 'Yankees',
    gameLog: [],
    gameOver: false,
    isSimulating: false
  });

  const [simSpeed, setSimSpeed] = useState(2000);

  const resetGame = () => {
    setGameState({
      inning: 1,
      topInning: true,
      homeTeam: 'Yankees',
      awayTeam: 'Dodgers',
      homeScore: 0,
      awayScore: 0,
      outs: 0,
      balls: 0,
      strikes: 0,
      bases: { first: null, second: null, third: null },
      currentBatter: 0,
      battingTeam: 'Dodgers',
      pitchingTeam: 'Yankees',
      gameLog: [],
      gameOver: false,
      isSimulating: false
    });
  };

  const addToLog = (message) => {
    setGameState(prev => ({
      ...prev,
      gameLog: [...prev.gameLog.slice(-20), message]
    }));
  };

  const advanceRunners = (bases, advancement) => {
    let runs = 0;
    const newBases = { first: null, second: null, third: null };
    
    // Score runners
    if (bases.third && advancement >= 1) runs++;
    if (bases.second && advancement >= 2) runs++;
    if (bases.first && advancement >= 3) runs++;
    
    // Advance remaining runners
    if (bases.third && advancement === 0) newBases.third = bases.third;
    if (bases.second && advancement === 1) newBases.third = bases.second;
    if (bases.second && advancement === 0) newBases.second = bases.second;
    if (bases.first && advancement <= 1) newBases.second = bases.first;
    if (bases.first && advancement === 0) newBases.first = bases.first;
    
    return { newBases, runs };
  };

  const simulatePitch = () => {
    if (gameState.gameOver) return;

    const batter = teams[gameState.battingTeam].lineup[gameState.currentBatter];
    const pitcher = teams[gameState.pitchingTeam].pitcher;
    
    // Pitch outcome probabilities based on realistic MLB stats
    const rand = Math.random();
    
    if (rand < 0.15) {
      // Ball
      const newBalls = gameState.balls + 1;
      if (newBalls === 4) {
        // Walk
        addToLog(`${batter.name} walks`);
        const newBases = { ...gameState.bases };
        let runs = 0;
        
        if (newBases.third && newBases.second && newBases.first) {
          runs = 1;
          addToLog(`${newBases.third} scores on the walk!`);
        }
        
        if (newBases.second && newBases.first) {
          newBases.third = newBases.second;
        }
        if (newBases.first) {
          newBases.second = newBases.first;
        }
        newBases.first = batter.name;
        
        setGameState(prev => ({
          ...prev,
          balls: 0,
          strikes: 0,
          bases: newBases,
          currentBatter: (prev.currentBatter + 1) % 9,
          homeScore: prev.battingTeam === 'Yankees' ? prev.homeScore + runs : prev.homeScore,
          awayScore: prev.battingTeam === 'Dodgers' ? prev.awayScore + runs : prev.awayScore
        }));
      } else {
        addToLog(`Ball ${newBalls}. Count: ${newBalls}-${gameState.strikes}`);
        setGameState(prev => ({ ...prev, balls: newBalls }));
      }
    } else if (rand < 0.25) {
      // Strike (called or swinging)
      const newStrikes = gameState.strikes + 1;
      if (newStrikes === 3) {
        // Strikeout
        addToLog(`${batter.name} strikes out`);
        const newOuts = gameState.outs + 1;
        
        if (newOuts === 3) {
          endInning();
        } else {
          setGameState(prev => ({
            ...prev,
            outs: newOuts,
            balls: 0,
            strikes: 0,
            currentBatter: (prev.currentBatter + 1) % 9
          }));
        }
      } else {
        const strikeType = Math.random() < 0.6 ? 'called' : 'swinging';
        addToLog(`Strike ${newStrikes} ${strikeType}. Count: ${gameState.balls}-${newStrikes}`);
        setGameState(prev => ({ ...prev, strikes: newStrikes }));
      }
    } else {
      // Ball in play
      const ballInPlayRand = Math.random();
      
      if (ballInPlayRand < 0.05) {
        // Home run
        let runs = 1;
        const runners = [];
        if (gameState.bases.first) { runners.push(gameState.bases.first); runs++; }
        if (gameState.bases.second) { runners.push(gameState.bases.second); runs++; }
        if (gameState.bases.third) { runners.push(gameState.bases.third); runs++; }
        
        addToLog(`${batter.name} hits a ${runs}-run HOME RUN!`);
        
        setGameState(prev => ({
          ...prev,
          balls: 0,
          strikes: 0,
          bases: { first: null, second: null, third: null },
          currentBatter: (prev.currentBatter + 1) % 9,
          homeScore: prev.battingTeam === 'Yankees' ? prev.homeScore + runs : prev.homeScore,
          awayScore: prev.battingTeam === 'Dodgers' ? prev.awayScore + runs : prev.awayScore
        }));
      } else if (ballInPlayRand < 0.15) {
        // Triple
        const { runs } = advanceRunners(gameState.bases, 3);
        addToLog(`${batter.name} hits a triple!`);
        
        setGameState(prev => ({
          ...prev,
          balls: 0,
          strikes: 0,
          bases: { first: null, second: null, third: batter.name },
          currentBatter: (prev.currentBatter + 1) % 9,
          homeScore: prev.battingTeam === 'Yankees' ? prev.homeScore + runs : prev.homeScore,
          awayScore: prev.battingTeam === 'Dodgers' ? prev.awayScore + runs : prev.awayScore
        }));
      } else if (ballInPlayRand < 0.35) {
        // Double
        const { runs } = advanceRunners(gameState.bases, 2);
        addToLog(`${batter.name} hits a double!`);
        
        setGameState(prev => ({
          ...prev,
          balls: 0,
          strikes: 0,
          bases: { first: null, second: batter.name, third: null },
          currentBatter: (prev.currentBatter + 1) % 9,
          homeScore: prev.battingTeam === 'Yankees' ? prev.homeScore + runs : prev.homeScore,
          awayScore: prev.battingTeam === 'Dodgers' ? prev.awayScore + runs : prev.awayScore
        }));
      } else if (ballInPlayRand < 0.60) {
        // Single
        const { newBases, runs } = advanceRunners(gameState.bases, 1);
        newBases.first = batter.name;
        addToLog(`${batter.name} hits a single!`);
        
        setGameState(prev => ({
          ...prev,
          balls: 0,
          strikes: 0,
          bases: newBases,
          currentBatter: (prev.currentBatter + 1) % 9,
          homeScore: prev.battingTeam === 'Yankees' ? prev.homeScore + runs : prev.homeScore,
          awayScore: prev.battingTeam === 'Dodgers' ? prev.awayScore + runs : prev.awayScore
        }));
      } else {
        // Out (fielded)
        const outTypes = ['grounds out', 'flies out', 'lines out', 'pops out'];
        const outType = outTypes[Math.floor(Math.random() * outTypes.length)];
        addToLog(`${batter.name} ${outType}`);
        
        const newOuts = gameState.outs + 1;
        if (newOuts === 3) {
          endInning();
        } else {
          setGameState(prev => ({
            ...prev,
            outs: newOuts,
            balls: 0,
            strikes: 0,
            currentBatter: (prev.currentBatter + 1) % 9
          }));
        }
      }
    }
  };

  const endInning = () => {
    const isEndOfGame = !gameState.topInning && gameState.inning >= 9 && 
                       gameState.homeScore !== gameState.awayScore;
    
    if (isEndOfGame) {
      const winner = gameState.homeScore > gameState.awayScore ? gameState.homeTeam : gameState.awayTeam;
      addToLog(`Game Over! ${winner} wins ${Math.max(gameState.homeScore, gameState.awayScore)}-${Math.min(gameState.homeScore, gameState.awayScore)}`);
      setGameState(prev => ({ ...prev, gameOver: true, isSimulating: false }));
      return;
    }
    
    if (gameState.topInning) {
      addToLog(`End of top ${gameState.inning}. ${gameState.awayTeam} ${gameState.awayScore}, ${gameState.homeTeam} ${gameState.homeScore}`);
      setGameState(prev => ({
        ...prev,
        topInning: false,
        battingTeam: prev.homeTeam,
        pitchingTeam: prev.awayTeam,
        outs: 0,
        balls: 0,
        strikes: 0,
        bases: { first: null, second: null, third: null },
        currentBatter: 0
      }));
    } else {
      const nextInning = gameState.inning + 1;
      addToLog(`End of inning ${gameState.inning}. ${gameState.awayTeam} ${gameState.awayScore}, ${gameState.homeTeam} ${gameState.homeScore}`);
      setGameState(prev => ({
        ...prev,
        inning: nextInning,
        topInning: true,
        battingTeam: prev.awayTeam,
        pitchingTeam: prev.homeTeam,
        outs: 0,
        balls: 0,
        strikes: 0,
        bases: { first: null, second: null, third: null },
        currentBatter: 0
      }));
    }
  };

  useEffect(() => {
    let interval;
    if (gameState.isSimulating && !gameState.gameOver) {
      interval = setInterval(simulatePitch, simSpeed);
    }
    return () => clearInterval(interval);
  }, [gameState.isSimulating, simSpeed, gameState]);

  const toggleSimulation = () => {
    setGameState(prev => ({ ...prev, isSimulating: !prev.isSimulating }));
  };

  const currentBatter = teams[gameState.battingTeam].lineup[gameState.currentBatter];
  const currentPitcher = teams[gameState.pitchingTeam].pitcher;

  return (
    <div className="min-h-screen bg-green-900 text-white p-4">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-6 text-yellow-300">
          MLB Pitch-by-Pitch Simulator
        </h1>
        
        {/* Scoreboard */}
        <div className="bg-black rounded-lg p-6 mb-6">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <h2 className="text-xl font-bold text-blue-400">{gameState.awayTeam}</h2>
              <div className="text-3xl font-bold">{gameState.awayScore}</div>
            </div>
            <div>
              <div className="text-lg">
                {gameState.topInning ? 'Top' : 'Bottom'} {gameState.inning}
              </div>
              <div className="text-sm mt-2">
                {gameState.outs} Out{gameState.outs !== 1 ? 's' : ''}
              </div>
            </div>
            <div>
              <h2 className="text-xl font-bold text-red-400">{gameState.homeTeam}</h2>
              <div className="text-3xl font-bold">{gameState.homeScore}</div>
            </div>
          </div>
        </div>

        {/* Count and Bases */}
        <div className="grid md:grid-cols-2 gap-6 mb-6">
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-xl font-bold mb-4">Count</h3>
            <div className="text-center">
              <div className="text-3xl font-bold">
                {gameState.balls} - {gameState.strikes}
              </div>
              <div className="text-sm text-gray-300">Balls - Strikes</div>
            </div>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-xl font-bold mb-4">Bases</h3>
            <div className="relative w-32 h-32 mx-auto">
              {/* Diamond */}
              <div className="absolute inset-0 transform rotate-45 border-2 border-white"></div>
              
              {/* Base indicators */}
              <div className={`absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-4 h-4 rounded ${gameState.bases.second ? 'bg-yellow-400' : 'bg-gray-600'}`}></div>
              <div className={`absolute right-0 top-1/2 transform translate-x-1/2 -translate-y-1/2 w-4 h-4 rounded ${gameState.bases.first ? 'bg-yellow-400' : 'bg-gray-600'}`}></div>
              <div className={`absolute left-0 top-1/2 transform -translate-x-1/2 -translate-y-1/2 w-4 h-4 rounded ${gameState.bases.third ? 'bg-yellow-400' : 'bg-gray-600'}`}></div>
              <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-1/2 w-4 h-4 bg-white"></div>
              
              {/* Base labels */}
              <div className="absolute -top-6 left-1/2 transform -translate-x-1/2 text-xs">2nd</div>
              <div className="absolute -right-6 top-1/2 transform -translate-y-1/2 text-xs">1st</div>
              <div className="absolute -left-6 top-1/2 transform -translate-y-1/2 text-xs">3rd</div>
            </div>
          </div>
        </div>

        {/* Current Matchup */}
        <div className="bg-gray-800 rounded-lg p-4 mb-6">
          <h3 className="text-xl font-bold mb-4">Current At-Bat</h3>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-bold text-green-400">Batting</h4>
              <div>{currentBatter.name} ({currentBatter.pos})</div>
              <div className="text-sm text-gray-300">
                .{Math.floor(currentBatter.avg * 1000).toString().padStart(3, '0')} AVG | 
                .{Math.floor(currentBatter.obp * 1000).toString().padStart(3, '0')} OBP
              </div>
            </div>
            <div>
              <h4 className="font-bold text-red-400">Pitching</h4>
              <div>{currentPitcher.name}</div>
              <div className="text-sm text-gray-300">
                {currentPitcher.era} ERA | {currentPitcher.whip} WHIP
              </div>
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="bg-gray-800 rounded-lg p-4 mb-6">
          <div className="flex flex-wrap items-center justify-center gap-4">
            <button
              onClick={toggleSimulation}
              disabled={gameState.gameOver}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 px-4 py-2 rounded"
            >
              {gameState.isSimulating ? <Pause size={16} /> : <Play size={16} />}
              {gameState.isSimulating ? 'Pause' : 'Start'} Simulation
            </button>
            
            <button
              onClick={simulatePitch}
              disabled={gameState.isSimulating || gameState.gameOver}
              className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 px-4 py-2 rounded"
            >
              Next Pitch
            </button>
            
            <button
              onClick={resetGame}
              className="flex items-center gap-2 bg-red-600 hover:bg-red-700 px-4 py-2 rounded"
            >
              <RotateCcw size={16} />
              Reset Game
            </button>
            
            <div className="flex items-center gap-2">
              <label className="text-sm">Speed:</label>
              <select
                value={simSpeed}
                onChange={(e) => setSimSpeed(Number(e.target.value))}
                className="bg-gray-700 text-white px-2 py-1 rounded"
              >
                <option value={500}>Very Fast</option>
                <option value={1000}>Fast</option>
                <option value={2000}>Normal</option>
                <option value={3000}>Slow</option>
              </select>
            </div>
          </div>
        </div>

        {/* Game Log */}
        <div className="bg-gray-800 rounded-lg p-4">
          <h3 className="text-xl font-bold mb-4">Play-by-Play</h3>
          <div className="h-64 overflow-y-auto">
            {gameState.gameLog.map((log, index) => (
              <div key={index} className="py-1 border-b border-gray-700 text-sm">
                {log}
              </div>
            ))}
            {gameState.gameLog.length === 0 && (
              <div className="text-gray-400 text-center py-8">
                Game ready to start! Click "Start Simulation" or "Next Pitch"
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MLBSimulator;