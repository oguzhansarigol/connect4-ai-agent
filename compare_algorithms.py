"""
MCTS vs Alpha-Beta Comparison Script
====================================

Sunum için kullanılacak kapsamlı karşılaştırma.

Metrics:
- Win Rate (%)
- Average Thinking Time
- Games Played
- Algorithm Efficiency
"""

import time
import json
from datetime import datetime
from connect4.game import (
    create_board, print_board, drop_piece,
    get_next_open_row, winning_move, get_valid_locations,
    PLAYER_AI, PLAYER_HUMAN
)
from connect4.agent import get_best_move_optimized
from connect4.mcts_agent import get_best_move_mcts


def play_single_game(ai1_func, ai1_params, ai2_func, ai2_params, verbose=False):
    """
    Play one game: AI1 (Player 1) vs AI2 (Player 2)
    
    Returns:
        (winner, moves, ai1_time, ai2_time)
        winner: 'ai1', 'ai2', or 'draw'
    """
    board = create_board()
    turn = PLAYER_AI  # AI1 starts as PLAYER_AI
    move_count = 0
    ai1_total_time = 0
    ai2_total_time = 0
    
    max_moves = 42
    
    while move_count < max_moves:
        valid = get_valid_locations(board)
        if not valid:
            return 'draw', move_count, ai1_total_time, ai2_total_time
        
        start = time.time()
        
        if turn == PLAYER_AI:  # AI1's turn
            col = ai1_func(board, PLAYER_AI, **ai1_params)
            elapsed = time.time() - start
            ai1_total_time += elapsed
        else:  # AI2's turn
            col = ai2_func(board, PLAYER_HUMAN, **ai2_params)
            elapsed = time.time() - start
            ai2_total_time += elapsed
        
        if col not in valid:
            return ('ai2' if turn == PLAYER_AI else 'ai1'), move_count, ai1_total_time, ai2_total_time
        
        row = get_next_open_row(board, col)
        drop_piece(board, row, col, turn)
        move_count += 1
        
        if verbose:
            print(f"\nMove {move_count}: {'AI1' if turn == PLAYER_AI else 'AI2'} -> col {col}")
            print_board(board)
        
        if winning_move(board, turn):
            winner = 'ai1' if turn == PLAYER_AI else 'ai2'
            return winner, move_count, ai1_total_time, ai2_total_time
        
        turn = PLAYER_HUMAN if turn == PLAYER_AI else PLAYER_AI
    
    return 'draw', move_count, ai1_total_time, ai2_total_time


def run_comparison(games=10):
    """
    Run comprehensive comparison
    
    Matchups:
    1. Alpha-Beta D6 vs MCTS 1000
    2. Alpha-Beta D8 vs MCTS 2000
    """
    
    print("=" * 80)
    print("🏆 CONNECT4 AI COMPARISON: ALPHA-BETA vs MONTE CARLO")
    print("=" * 80)
    print()
    
    # Configuration
    alpha_beta_d6 = {
        'name': 'Alpha-Beta Pruning (Depth 6)',
        'func': get_best_move_optimized,
        'params': {'depth': 6}
    }
    
    alpha_beta_d8 = {
        'name': 'Alpha-Beta Pruning (Depth 8)',
        'func': get_best_move_optimized,
        'params': {'depth': 8}
    }
    
    mcts_1k = {
        'name': 'Monte Carlo Tree Search (1000 iterations)',
        'func': get_best_move_mcts,
        'params': {'iterations': 1000, 'time_limit': 5.0}
    }
    
    mcts_2k = {
        'name': 'Monte Carlo Tree Search (2000 iterations)',
        'func': get_best_move_mcts,
        'params': {'iterations': 2000, 'time_limit': 10.0}
    }
    
    # Run matchups
    results = {}
    
    # MATCHUP 1: Alpha-Beta D6 vs MCTS 1k
    print(f"\n{'='*80}")
    print(f"📊 MATCHUP 1: {alpha_beta_d6['name']} vs {mcts_1k['name']}")
    print(f"{'='*80}\n")
    
    ab_d6_wins = 0
    mcts_1k_wins = 0
    draws = 0
    ab_d6_time = 0
    mcts_1k_time = 0
    
    for i in range(games):
        print(f"Game {i+1}/{games}...", end=' ')
        winner, moves, t1, t2 = play_single_game(
            alpha_beta_d6['func'], alpha_beta_d6['params'],
            mcts_1k['func'], mcts_1k['params']
        )
        
        ab_d6_time += t1
        mcts_1k_time += t2
        
        if winner == 'ai1':
            ab_d6_wins += 1
            print(f"✅ Alpha-Beta wins ({moves} moves)")
        elif winner == 'ai2':
            mcts_1k_wins += 1
            print(f"✅ MCTS wins ({moves} moves)")
        else:
            draws += 1
            print(f"🤝 Draw ({moves} moves)")
    
    results['matchup1'] = {
        'config': f"{alpha_beta_d6['name']} vs {mcts_1k['name']}",
        'alpha_beta': {
            'wins': ab_d6_wins,
            'win_rate': ab_d6_wins / games * 100,
            'avg_time': ab_d6_time / games
        },
        'mcts': {
            'wins': mcts_1k_wins,
            'win_rate': mcts_1k_wins / games * 100,
            'avg_time': mcts_1k_time / games
        },
        'draws': draws
    }
    
    # MATCHUP 2: Alpha-Beta D8 vs MCTS 2k
    print(f"\n{'='*80}")
    print(f"📊 MATCHUP 2: {alpha_beta_d8['name']} vs {mcts_2k['name']}")
    print(f"{'='*80}\n")
    
    ab_d8_wins = 0
    mcts_2k_wins = 0
    draws2 = 0
    ab_d8_time = 0
    mcts_2k_time = 0
    
    for i in range(games):
        print(f"Game {i+1}/{games}...", end=' ')
        winner, moves, t1, t2 = play_single_game(
            alpha_beta_d8['func'], alpha_beta_d8['params'],
            mcts_2k['func'], mcts_2k['params']
        )
        
        ab_d8_time += t1
        mcts_2k_time += t2
        
        if winner == 'ai1':
            ab_d8_wins += 1
            print(f"✅ Alpha-Beta wins ({moves} moves)")
        elif winner == 'ai2':
            mcts_2k_wins += 1
            print(f"✅ MCTS wins ({moves} moves)")
        else:
            draws2 += 1
            print(f"🤝 Draw ({moves} moves)")
    
    results['matchup2'] = {
        'config': f"{alpha_beta_d8['name']} vs {mcts_2k['name']}",
        'alpha_beta': {
            'wins': ab_d8_wins,
            'win_rate': ab_d8_wins / games * 100,
            'avg_time': ab_d8_time / games
        },
        'mcts': {
            'wins': mcts_2k_wins,
            'win_rate': mcts_2k_wins / games * 100,
            'avg_time': mcts_2k_time / games
        },
        'draws': draws2
    }
    
    # Print summary
    print("\n" + "="*80)
    print("📈 FINAL RESULTS")
    print("="*80)
    
    print(f"\n🥊 MATCHUP 1: Alpha-Beta D6 vs MCTS 1k")
    print(f"  Alpha-Beta: {ab_d6_wins} wins ({ab_d6_wins/games*100:.1f}%), avg {ab_d6_time/games:.2f}s")
    print(f"  MCTS:       {mcts_1k_wins} wins ({mcts_1k_wins/games*100:.1f}%), avg {mcts_1k_time/games:.2f}s")
    print(f"  Draws:      {draws}")
    
    print(f"\n🥊 MATCHUP 2: Alpha-Beta D8 vs MCTS 2k")
    print(f"  Alpha-Beta: {ab_d8_wins} wins ({ab_d8_wins/games*100:.1f}%), avg {ab_d8_time/games:.2f}s")
    print(f"  MCTS:       {mcts_2k_wins} wins ({mcts_2k_wins/games*100:.1f}%), avg {mcts_2k_time/games:.2f}s")
    print(f"  Draws:      {draws2}")
    
    # Save to JSON
    output = {
        'timestamp': datetime.now().isoformat(),
        'total_games': games,
        'results': results
    }
    
    filename = f'ai_comparison_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Results saved: {filename}")
    
    return results


if __name__ == "__main__":
    print("\n🚀 Starting AI Comparison...\n")
    run_comparison(games=10)
    print("\n✅ Comparison complete!\n")
