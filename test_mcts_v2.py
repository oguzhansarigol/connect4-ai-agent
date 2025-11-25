from connect4.mcts_agent_v2 import get_best_move_mcts_v2
from connect4.game import create_board, drop_piece

# Test simple position
board = create_board()
drop_piece(board, 0, 3, 1)   # AI at column 3
drop_piece(board, 0, 2, -1)  # Human at column 2
drop_piece(board, 1, 3, 1)   # AI at column 3 (row 1)

print('Board (top to bottom):')
for r in range(5, -1, -1):
    print(f'Row {r}: {board[r]}')

print('\nMCTS V2 thinking...')
col, stats = get_best_move_mcts_v2(board, -1, iterations=5000, time_limit=2.0, developer_mode=True)

print(f'\nMCTS chose column: {col}')
print(f'Stats: {stats}')
