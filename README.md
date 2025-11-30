# 🎮 Connect4 AI Agent

**Advanced Connect4 AI using Alpha-Beta Pruning with 7 Strategic Optimizations**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Flask](https://img.shields.io/badge/flask-3.0.0-orange.svg)](https://flask.palletsprojects.com/)

An intelligent Connect4 game featuring a competitive AI agent powered by minimax algorithm with alpha-beta pruning and seven advanced optimization techniques. Play via terminal or interactive web interface with real-time decision visualization.

---

## ✨ Features

### 🧠 Intelligent AI Agent
- **Alpha-Beta Pruning**: Reduces search complexity from O(b^d) to O(b^(d/2))
- **7 Strategic Optimizations**: 9.76× speedup over baseline minimax
- **Dynamic Depth Adjustment**: Adapts search depth (6-12) based on performance
- **Real-time Decision Making**: Average 2-4 second response time

### 🎯 Game Modes
- **Human vs AI**: Challenge the AI at various difficulty levels
- **AI vs AI**: Watch Minimax battle against MCTS or Bitboard variants
- **Random Start**: AI can start first or human can begin

### 🖥️ Dual Interface
- **Terminal Mode**: Classic command-line gameplay
- **Web Interface**: Modern Flask-powered UI with visual board and analytics

### 📊 Developer Mode
- **Game Theory Visualization**: See S₀, TO-MOVE, ACTIONS, RESULT, IS-TERMINAL, UTILITY
- **Decision Process**: Column-by-column minimax score breakdown
- **AI Optimizations**: Real-time display of active optimization techniques
- **Performance Metrics**: Thinking time, search depth, and node statistics

---

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.8+
Flask 3.0.0 (for web interface)
NumPy
```

### Installation

```bash
# Clone repository
git clone https://github.com/oguzhansarigol/connect4-ai-agent.git
cd connect4-ai-agent

# Install dependencies
pip install Flask==3.0.0 numpy
```

### Running the Game

#### Terminal Mode
```bash
python main.py
```

#### Web Interface
```bash
python app.py
# Open browser at http://localhost:5000
```

---

## 🧩 Project Structure

```
connect4-ai-agent/
│
├── connect4/
│   ├── game.py              # Game engine (board, rules, victory detection)
│   ├── agent.py             # Alpha-Beta AI with optimizations
│   ├── agent_bitboard.py    # Bitboard-optimized variant
│   ├── mcts_agent.py        # Monte Carlo Tree Search implementation
│   └── mcts_agent_v2.py     # Enhanced MCTS with transposition table
│
├── templates/
│   └── index.html           # Web interface HTML
│
├── static/
│   ├── style.css            # UI styling
│   └── script.js            # Frontend logic
│
├── main.py                  # Terminal game launcher
├── app.py                   # Flask web server
├── compare_all_algorithms.py  # Algorithm benchmarking tool
├── test_pruning_efficiency.py # Pruning optimization tests
└── README.md
```

---

## 🎯 AI Architecture

### Core Algorithm: Alpha-Beta Minimax

```python
function ALPHA-BETA-MINIMAX(board, depth, alpha, beta, maximizing):
    if depth = 0 or GAME-OVER(board):
        return HEURISTIC-EVAL(board)
    
    if maximizing:
        for each valid_move:
            score = ALPHA-BETA-MINIMAX(new_board, depth-1, alpha, beta, false)
            alpha = MAX(alpha, score)
            if alpha ≥ beta:
                break  # Pruning!
        return alpha
    else:
        for each valid_move:
            score = ALPHA-BETA-MINIMAX(new_board, depth-1, alpha, beta, true)
            beta = MIN(beta, score)
            if alpha ≥ beta:
                break  # Pruning!
        return beta
```

### 🚀 Seven Strategic Optimizations

| Optimization | Impact | Description |
|--------------|--------|-------------|
| **Alpha-Beta Pruning** | 60-80% node reduction | Eliminates unpromising branches |
| **Move Ordering** ⭐⭐⭐⭐⭐ | 30-50% speedup | Prioritizes winning/threat-blocking moves |
| **Transposition Table** ⭐⭐⭐⭐ | 20-40% speedup | Caches previously evaluated positions |
| **Threat Detection** ⭐⭐⭐ | 25% better strategy | Penalizes opponent three-in-a-row |
| **Killer Moves** ⭐⭐⭐⭐ | 15-20% pruning | Remembers cutoff-causing moves per depth |
| **Evaluation Board** ⭐⭐ | Strategic positioning | Weights center/middle rows higher |
| **Center Column Bonus** ⭐⭐⭐ | Tactical advantage | +3 bonus for center pieces |

**Combined Result**: **9.76× speedup** (baseline: 1143ms → optimized: 198ms)

---

## 📊 Performance Benchmarks

### Pruning Efficiency Test Results

| Configuration | Avg Nodes | Avg Time (ms) | Pruning Ratio | Improvement |
|---------------|-----------|---------------|---------------|-------------|
| Baseline | 8,951 | 1,143.2 | 45.5% | — |
| Move Ordering | 1,682 | 393.1 | 63.3% | 5.32× faster |
| Killer Moves | 1,215 | 293.6 | 65.9% | 7.37× faster |
| **Full Heuristics** | **917** | **197.9** | **62.1%** | **9.76× faster** |

*Test conditions: 15 mid-game positions, depth=6*

### Algorithm Comparison: Win Rates

| Matchup | Result | Avg Time |
|---------|--------|----------|
| Alpha-Beta D6 vs MCTS 10K | **100% - 0%** | 0.87s vs 0.22s |
| Alpha-Beta D6 vs MCTS 50K | **100% - 0%** | 0.83s vs 11.14s |
| Bitboard D10 vs MCTS 50K | **90% - 10%** | 0.44s vs 8.04s |
| Alpha-Beta D6 vs Bitboard D10 | **100% - 0%** | 0.52s vs 0.24s |

**Key Finding**: Deterministic alpha-beta with heuristics dominates stochastic MCTS even at 50,000 iterations.

---

## 🎮 Usage Examples

### Terminal Gameplay
```bash
# Default: Human starts (Red), AI is Yellow
python main.py

# Different game modes available through web interface
```

### Web Interface Features

1. **Control Panel**
   - Toggle Developer Mode
   - Adjust AI search depth (6-12)
   - Choose game mode (I Start / AI Starts / Random)

2. **Developer Mode Panels**
   - **Game Theory Model**: Formal game state representation
   - **Decision Process**: Column evaluation scores
   - **AI Optimizations**: Active optimization techniques

3. **AI vs AI Battle Mode**
   - Minimax (Alpha-Beta) vs MCTS
   - Watch automated gameplay
   - Performance comparison

---

## 🧪 Running Tests

### Pruning Efficiency Analysis
```bash
python test_pruning_efficiency.py
```
Compares baseline, move ordering, killer moves, and full heuristics configurations.

### Algorithm Benchmarking
```bash
python compare_all_algorithms.py
```
Runs tournaments between Alpha-Beta, Bitboard, and MCTS variants.

---

## 🔬 Technical Details

### Game Representation
- **Board Size**: 6 rows × 7 columns
- **Player Encoding**: AI=1, Human=-1, Empty=0
- **Coordinate System**: (0,0) at bottom-left corner

### Heuristic Evaluation
```python
score = evaluate_window(window) + center_bonus + evaluation_board_weight
```
- **Window Analysis**: Scores 69 four-cell windows (24 horizontal, 21 vertical, 24 diagonal)
- **Scoring Rules**:
  - Four AI pieces: +100
  - Three AI pieces + empty: +5
  - Two AI pieces + two empty: +2
  - Opponent threats: -4 (three pieces), -100 (four pieces)

### Dynamic Depth Management
```python
if thinking_time < 3.0s and rounds ≥ 3:
    depth += 1  # Max: 12
elif thinking_time > 6.0s:
    depth -= 1  # Min: 6
```

---

## 🛠️ Configuration

### AI Parameters (`app.py`)
```python
AI_DEPTH_MIN = 6         # Minimum search depth
AI_DEPTH_MAX = 12        # Maximum search depth
AI_DEPTH_DEFAULT = 8     # Starting depth
TARGET_THINKING_TIME = 4.0  # Target response time (seconds)
```

### Optimization Flags
```python
config = {
    'enable_move_ordering': True,
    'enable_killer_moves': True,
    'enable_transposition_table': True,
    'enable_threat_detection': True
}
```

---

## 📈 Future Improvements

### 1. Opening Book Integration
Convert opening theory into JSON format for instant optimal moves in the first 4-6 plies, eliminating early-game computation.

### 2. Pruned Branch Visualization
Add UI feature to visualize alpha-beta cutoffs during search, showing which branches were pruned and why—enhancing demo transparency.

### 3. Migration to C++
Rewrite performance-critical components (board manipulation, window evaluation, minimax recursion) in C++ for 10-50× additional speedup, targeting depth-12-15 searches in 1-2 seconds.

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 👥 Authors

- **Oğuzhan Sarıgöl** - *Initial work* - [oguzhansarigol](https://github.com/oguzhansarigol)

---

## 🙏 Acknowledgments

- Alpha-beta pruning algorithm based on Russell & Norvig's "Artificial Intelligence: A Modern Approach"
- Game theory formalization follows standard adversarial search framework
- Optimization techniques inspired by chess engine development (Stockfish, AlphaZero)

---

## 📧 Contact

Project Link: [https://github.com/oguzhansarigol/connect4-ai-agent](https://github.com/oguzhansarigol/connect4-ai-agent)

---

**⭐ Star this repo if you found it helpful!**
