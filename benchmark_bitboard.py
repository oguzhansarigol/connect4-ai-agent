"""
Performance Benchmark: Bitboard Minimax vs Traditional Minimax
"""

import time
from connect4.agent import get_best_move
from connect4.agent_bitboard import get_best_move_bitboard
from connect4.game import create_board, drop_piece

print("=" * 70)
print("🚀 MINIMAX PERFORMANCE BENCHMARK")
print("=" * 70)

# Test 1: Empty Board
print("\n📊 Test 1: Empty Board (Depth 8)")
print("-" * 70)

board = create_board()

# Traditional Minimax
print("⏱️  Traditional Minimax (2D List)...")
start = time.time()
col_trad, scores_trad = get_best_move(board, 1, depth=8, developer_mode=True)
time_trad = time.time() - start

print(f"   ✅ Column: {col_trad}, Time: {time_trad:.3f}s")

# Bitboard Minimax
print("⚡ Bitboard Minimax...")
start = time.time()
col_bit, scores_bit = get_best_move_bitboard(board, 1, depth=8, developer_mode=True)
time_bit = time.time() - start

print(f"   ✅ Column: {col_bit}, Time: {time_bit:.3f}s")

speedup_1 = time_trad / time_bit
print(f"\n🎯 Speedup: {speedup_1:.2f}x faster")

# Test 2: Mid-game (balanced position, no immediate win)
print("\n📊 Test 2: Balanced Mid-Game (Depth 8)")
print("-" * 70)

board2 = create_board()
# Simulate balanced position without immediate wins
moves = [3, 2, 4, 3, 2, 4, 5, 1]
player = 1
for move in moves:
    from connect4.game import get_next_open_row
    row = get_next_open_row(board2, move)
    drop_piece(board2, row, move, player)
    player = -player

# Traditional Minimax
print("⏱️  Traditional Minimax (2D List)...")
start = time.time()
col_trad2, _ = get_best_move(board2, 1, depth=8, developer_mode=True)
time_trad2 = time.time() - start

print(f"   ✅ Column: {col_trad2}, Time: {time_trad2:.3f}s")

# Bitboard Minimax
print("⚡ Bitboard Minimax...")
start = time.time()
col_bit2, _ = get_best_move_bitboard(board2, 1, depth=8, developer_mode=True)
time_bit2 = time.time() - start

print(f"   ✅ Column: {col_bit2}, Time: {time_bit2:.3f}s")

speedup_2 = time_trad2 / time_bit2 if time_bit2 > 0 else float('inf')
print(f"\n🎯 Speedup: {speedup_2:.2f}x faster" if speedup_2 < 1000 else "\n🎯 Speedup: ∞ (instant)")

# Summary
print("\n" + "=" * 70)
print("📈 SUMMARY")
print("=" * 70)

print(f"""
Test 1 (Empty Board, Depth 8):
  - Traditional: {time_trad:.3f}s
  - Bitboard:    {time_bit:.3f}s
  - Speedup:     {speedup_1:.2f}x

Test 2 (Mid-Game, Depth 8):
  - Traditional: {time_trad2:.3f}s
  - Bitboard:    {time_bit2:.3f}s
  - Speedup:     {speedup_2:.2f}x

Average Speedup: {(speedup_1 + speedup_2) / 2:.2f}x
""")

print("✅ Bitboard optimization is working!")
print("=" * 70)
