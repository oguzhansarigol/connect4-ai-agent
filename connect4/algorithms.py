"""
Connect4 için farklı arama algoritmalarının implementasyonları.
Akademik karşılaştırma amacıyla: BFS, DFS, UCS, A*, Minimax, Alpha-Beta Pruning
"""

import math
import random
import time
from collections import deque
from typing import List, Tuple, Optional, Dict, Any
from .game import (
    ROWS, COLS, WINDOW_LENGTH, EMPTY, PLAYER_AI, PLAYER_HUMAN,
    is_terminal_node, winning_move, get_valid_locations,
    get_next_open_row, drop_piece
)


class SearchMetrics:
    """Arama algoritması metriklerini toplar"""
    def __init__(self):
        self.nodes_expanded = 0
        self.max_depth_reached = 0
        self.time_taken = 0.0
        self.memory_used = 0  # KB cinsinden
        self.branching_factor = 0.0
        self.pruned_branches = 0
        self.solution_depth = 0
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'nodes_expanded': self.nodes_expanded,
            'max_depth_reached': self.max_depth_reached,
            'time_taken': self.time_taken,
            'memory_used_kb': self.memory_used,
            'branching_factor': self.branching_factor,
            'pruned_branches': self.pruned_branches,
            'solution_depth': self.solution_depth
        }


def evaluate_window(window, piece):
    """Heuristic değerlendirme - 4'lü pencere için skor"""
    score = 0
    opponent_piece = PLAYER_HUMAN if piece == PLAYER_AI else PLAYER_AI

    piece_count = window.count(piece)
    empty_count = window.count(EMPTY)
    opponent_count = window.count(opponent_piece)

    if piece_count == 4:
        score += 10000
    elif piece_count == 3 and empty_count == 1:
        score += 10
    elif piece_count == 2 and empty_count == 2:
        score += 3

    if opponent_count == 3 and empty_count == 1:
        score -= 80

    return score


def score_position(board, piece):
    """Heuristic değerlendirme - tüm tahta için skor"""
    score = 0

    # Merkez sütun bonusu
    center_array = [board[r][COLS // 2] for r in range(ROWS)]
    center_count = center_array.count(piece)
    score += center_count * 5

    # Yatay
    for r in range(ROWS):
        row_array = board[r]
        for c in range(COLS - (WINDOW_LENGTH - 1)):
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Dikey
    for c in range(COLS):
        col_array = [board[r][c] for r in range(ROWS)]
        for r in range(ROWS - (WINDOW_LENGTH - 1)):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Pozitif çapraz
    for r in range(ROWS - (WINDOW_LENGTH - 1)):
        for c in range(COLS - (WINDOW_LENGTH - 1)):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    # Negatif çapraz
    for r in range(ROWS - (WINDOW_LENGTH - 1)):
        for c in range(COLS - (WINDOW_LENGTH - 1)):
            window = [board[r+i][c+(WINDOW_LENGTH-1)-i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)
            
    return score


# ============================================================================
# 1. MINIMAX (Uninformed - temel versiyonu)
# ============================================================================

def minimax_basic(board, depth, maximizing_player, metrics: SearchMetrics):
    """
    Temel Minimax (Alpha-Beta olmadan)
    Completeness: Evet (sonlu oyun ağacı)
    Optimality: Evet (optimal hamleyi bulur)
    Time: O(b^d) - b: branching factor, d: depth
    Space: O(b*d) - recursive stack
    """
    metrics.nodes_expanded += 1
    metrics.max_depth_reached = max(metrics.max_depth_reached, depth)
    
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)

    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, PLAYER_AI):
                return (None, 10000000)
            elif winning_move(board, PLAYER_HUMAN):
                return (None, -10000000)
            else:
                return (None, 0)
        else:
            return (None, score_position(board, PLAYER_AI))

    if maximizing_player:
        value = -math.inf
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = [row[:] for row in board]
            drop_piece(temp_board, row, col, PLAYER_AI)
            new_score = minimax_basic(temp_board, depth - 1, False, metrics)[1]
            if new_score > value:
                value = new_score
                best_col = col
        return best_col, value
    else:
        value = math.inf
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = [row[:] for row in board]
            drop_piece(temp_board, row, col, PLAYER_HUMAN)
            new_score = minimax_basic(temp_board, depth - 1, True, metrics)[1]
            if new_score < value:
                value = new_score
                best_col = col
        return best_col, value


# ============================================================================
# 2. MINIMAX with ALPHA-BETA PRUNING (Informed Search)
# ============================================================================

def minimax_alpha_beta(board, depth, alpha, beta, maximizing_player, metrics: SearchMetrics):
    """
    Minimax + Alpha-Beta Pruning
    Completeness: Evet
    Optimality: Evet (aynı sonuç, daha az node)
    Time: O(b^(d/2)) - best case, O(b^d) - worst case
    Space: O(b*d)
    AVANTAJ: Daha az node expand eder (pruning sayesinde)
    """
    metrics.nodes_expanded += 1
    metrics.max_depth_reached = max(metrics.max_depth_reached, depth)
    
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)

    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, PLAYER_AI):
                return (None, 10000000)
            elif winning_move(board, PLAYER_HUMAN):
                return (None, -10000000)
            else:
                return (None, 0)
        else:
            return (None, score_position(board, PLAYER_AI))

    if maximizing_player:
        value = -math.inf
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = [row[:] for row in board]
            drop_piece(temp_board, row, col, PLAYER_AI)
            new_score = minimax_alpha_beta(temp_board, depth - 1, alpha, beta, False, metrics)[1]
            if new_score > value:
                value = new_score
                best_col = col
            alpha = max(alpha, value)
            if alpha >= beta:
                metrics.pruned_branches += 1
                break  # Beta cut-off
        return best_col, value
    else:
        value = math.inf
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = [row[:] for row in board]
            drop_piece(temp_board, row, col, PLAYER_HUMAN)
            new_score = minimax_alpha_beta(temp_board, depth - 1, alpha, beta, True, metrics)[1]
            if new_score < value:
                value = new_score
                best_col = col
            beta = min(beta, value)
            if alpha >= beta:
                metrics.pruned_branches += 1
                break  # Alpha cut-off
        return best_col, value


# ============================================================================
# 3. BREADTH-FIRST SEARCH (BFS) - Uninformed
# ============================================================================

def bfs_search(board, max_depth=3):
    """
    BFS - Level-by-level arama
    Completeness: Evet
    Optimality: Evet (eğer cost uniform ise)
    Time: O(b^d)
    Space: O(b^d) - TÜM LEVEL'I HAFIZADA TUTAR! (PROBLEM!)
    
    DEZAVANTAJ: Connect4 için çok fazla memory kullanır
    """
    metrics = SearchMetrics()
    start_time = time.time()
    
    queue = deque()
    queue.append((board, 0, None))  # (board_state, depth, move)
    
    best_move = None
    best_score = -math.inf
    
    while queue and metrics.nodes_expanded < 10000:  # Limit to prevent explosion
        current_board, depth, move = queue.popleft()
        metrics.nodes_expanded += 1
        metrics.max_depth_reached = max(metrics.max_depth_reached, depth)
        
        if depth >= max_depth:
            score = score_position(current_board, PLAYER_AI)
            if score > best_score:
                best_score = score
                best_move = move
            continue
            
        valid_locations = get_valid_locations(current_board)
        for col in valid_locations:
            row = get_next_open_row(current_board, col)
            temp_board = [r[:] for r in current_board]
            drop_piece(temp_board, row, col, PLAYER_AI)
            
            first_move = move if move is not None else col
            queue.append((temp_board, depth + 1, first_move))
    
    metrics.time_taken = time.time() - start_time
    metrics.memory_used = len(queue) * 0.5  # Rough estimate KB
    
    return best_move if best_move is not None else random.choice(get_valid_locations(board)), metrics


# ============================================================================
# 4. DEPTH-FIRST SEARCH (DFS) - Uninformed
# ============================================================================

def dfs_search(board, max_depth=3):
    """
    DFS - Derinliğe öncelik veren arama
    Completeness: Hayır (sonsuz dallarda)
    Optimality: Hayır
    Time: O(b^m) - m: max depth
    Space: O(b*m) - BFS'den daha iyi!
    
    AVANTAJ: Daha az memory
    DEZAVANTAJ: Optimal olmayabilir
    """
    metrics = SearchMetrics()
    start_time = time.time()
    
    stack = [(board, 0, None)]
    best_move = None
    best_score = -math.inf
    
    while stack and metrics.nodes_expanded < 10000:
        current_board, depth, move = stack.pop()
        metrics.nodes_expanded += 1
        metrics.max_depth_reached = max(metrics.max_depth_reached, depth)
        
        if depth >= max_depth:
            score = score_position(current_board, PLAYER_AI)
            if score > best_score:
                best_score = score
                best_move = move
            continue
            
        valid_locations = get_valid_locations(current_board)
        for col in reversed(valid_locations):  # Reversed for stack order
            row = get_next_open_row(current_board, col)
            temp_board = [r[:] for r in current_board]
            drop_piece(temp_board, row, col, PLAYER_AI)
            
            first_move = move if move is not None else col
            stack.append((temp_board, depth + 1, first_move))
    
    metrics.time_taken = time.time() - start_time
    metrics.memory_used = len(stack) * 0.5
    
    return best_move if best_move is not None else random.choice(get_valid_locations(board)), metrics


# ============================================================================
# 5. UNIFORM COST SEARCH (UCS) - Uninformed (Dijkstra benzeri)
# ============================================================================

def ucs_search(board, max_depth=3):
    """
    UCS - En düşük cost'lu path'i seçer
    Completeness: Evet
    Optimality: Evet
    Time: O(b^(C*/ε)) - C*: optimal cost
    Space: O(b^(C*/ε))
    
    Connect4 için cost=depth olarak tanımlanır
    """
    import heapq
    metrics = SearchMetrics()
    start_time = time.time()
    
    priority_queue = []
    heapq.heappush(priority_queue, (0, 0, board, None))  # (cost, counter, board, move)
    
    best_move = None
    best_score = -math.inf
    counter = 0
    
    while priority_queue and metrics.nodes_expanded < 10000:
        cost, _, current_board, move = heapq.heappop(priority_queue)
        metrics.nodes_expanded += 1
        depth = cost
        metrics.max_depth_reached = max(metrics.max_depth_reached, depth)
        
        if depth >= max_depth:
            score = score_position(current_board, PLAYER_AI)
            if score > best_score:
                best_score = score
                best_move = move
            continue
            
        valid_locations = get_valid_locations(current_board)
        for col in valid_locations:
            row = get_next_open_row(current_board, col)
            temp_board = [r[:] for r in current_board]
            drop_piece(temp_board, row, col, PLAYER_AI)
            
            first_move = move if move is not None else col
            counter += 1
            heapq.heappush(priority_queue, (cost + 1, counter, temp_board, first_move))
    
    metrics.time_taken = time.time() - start_time
    metrics.memory_used = len(priority_queue) * 0.5
    
    return best_move if best_move is not None else random.choice(get_valid_locations(board)), metrics


# ============================================================================
# 6. A* SEARCH - Informed Search
# ============================================================================

def astar_search(board, max_depth=3):
    """
    A* - f(n) = g(n) + h(n)
    g(n): cost so far (depth)
    h(n): heuristic (score_position)
    
    Completeness: Evet
    Optimality: Evet (eğer heuristic admissible ise)
    Time: O(b^d) - heuristic'e bağlı
    Space: O(b^d)
    
    AVANTAJ: Heuristic ile daha akıllı arama
    """
    import heapq
    metrics = SearchMetrics()
    start_time = time.time()
    
    # f(n) = g(n) + h(n)
    h_score = -score_position(board, PLAYER_AI)  # Negative for minimization
    priority_queue = []
    heapq.heappush(priority_queue, (h_score, 0, 0, board, None))  # (f, counter, g, board, move)
    
    best_move = None
    best_score = -math.inf
    counter = 0
    
    while priority_queue and metrics.nodes_expanded < 10000:
        _, _, g, current_board, move = heapq.heappop(priority_queue)
        metrics.nodes_expanded += 1
        depth = g
        metrics.max_depth_reached = max(metrics.max_depth_reached, depth)
        
        if depth >= max_depth:
            score = score_position(current_board, PLAYER_AI)
            if score > best_score:
                best_score = score
                best_move = move
            continue
            
        valid_locations = get_valid_locations(current_board)
        for col in valid_locations:
            row = get_next_open_row(current_board, col)
            temp_board = [r[:] for r in current_board]
            drop_piece(temp_board, row, col, PLAYER_AI)
            
            new_g = g + 1
            h = -score_position(temp_board, PLAYER_AI)
            f = new_g + h
            
            first_move = move if move is not None else col
            counter += 1
            heapq.heappush(priority_queue, (f, counter, new_g, temp_board, first_move))
    
    metrics.time_taken = time.time() - start_time
    metrics.memory_used = len(priority_queue) * 0.5
    
    return best_move if best_move is not None else random.choice(get_valid_locations(board)), metrics
