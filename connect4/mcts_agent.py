"""
Monte Carlo Tree Search (MCTS) Agent for Connect4 - Improved Version
====================================================================

Geliştirmeler:
- Akıllı rollout (saf random yerine):
  - Önce kendi kazanabileceğin hamleyi oyna
  - Sonra rakibin kazanacağı hamleyi blokla
  - Sonra merkeze en yakın hamleyi seç
- Daha doğru ve sade backpropagation
- UCB1 exploration sabiti parametreleştirildi
- Zaman limiti + iterasyon limiti birlikte çalışıyor

UCB1: wins/visits + C * sqrt(ln(parent_visits) / visits)
"""

import math
import random
import time

from .game import (
    ROWS, COLS, EMPTY, PLAYER_AI, PLAYER_HUMAN,
    create_board, drop_piece, get_next_open_row,
    is_valid_location, winning_move, get_valid_locations
)

# ============================================================================
# CONFIGURATION
# ============================================================================
MCTS_ITERATIONS = 8000  # Default iterations - Test için kolayca değiştirilebilir


class MCTSNode:
    """
    Node in the Monte Carlo search tree
    """

    def __init__(self, board, parent=None, move=None, player=PLAYER_AI):
        # Board kopyası (her node için kendi state'i)
        self.board = [row[:] for row in board]
        self.parent = parent
        self.move = move          # Bu node'a gelinen hamle (kolon)
        self.player = player      # Bu node'da oynamış olan oyuncu (son hamleyi atan)

        self.children = []
        self.wins = 0.0           # Toplam kazanım (AI açısından)
        self.visits = 0
        self.untried_moves = get_valid_locations(board)

    def ucb1(self, exploration_constant=0.9):
        """
        Upper Confidence Bound 1 (UCB1)
        """
        if self.visits == 0:
            # Hiç ziyaret edilmemiş node'lar önce denenir
            return float('inf')

        exploitation = self.wins / self.visits
        exploration = exploration_constant * math.sqrt(
            math.log(self.parent.visits) / self.visits
        )
        return exploitation + exploration

    def select_child(self, exploration_constant=0.9):
        """UCB1'e göre en iyi çocuğu seç"""
        return max(self.children, key=lambda c: c.ucb1(exploration_constant))

    def add_child(self, move, board, player):
        """Yeni child node ekle"""
        child = MCTSNode(board, parent=self, move=move, player=player)
        if move in self.untried_moves:
            self.untried_moves.remove(move)
        self.children.append(child)
        return child

    def update(self, result):
        """
        Node istatistiklerini güncelle

        result: 1.0 = AI kazandı, 0.0 = AI kaybetti, 0.5 = beraberlik
        """
        self.visits += 1
        self.wins += result


# ---------------------------------------------------------------------------
# Yardımcı fonksiyonlar
# ---------------------------------------------------------------------------

def apply_move(board, col, player):
    """Board'a hamleyi uygula ve oynanan satırı döndür."""
    row = get_next_open_row(board, col)
    drop_piece(board, row, col, player)
    return row


def undo_move(board, row, col):
    """Son oynanan taşı geri al."""
    board[row][col] = EMPTY


def smart_rollout_move(board, valid_moves, player, opponent):
    """
    Rollout sırasında random yerine daha akıllı seçim yap:

    1) Eğer bu turda player hemen kazanabiliyorsa, oyna.
    2) Eğer opponent hemen kazanabiliyorsa, blokla.
    3) Aksi halde merkeze en yakın kolonu seç.
    """
    # 1) Kendi kazanma hamleni bul
    for col in valid_moves:
        row = get_next_open_row(board, col)
        drop_piece(board, row, col, player)
        if winning_move(board, player):
            undo_move(board, row, col)
            return col
        undo_move(board, row, col)

    # 2) Rakibin kazanma hamlesini blokla
    for col in valid_moves:
        row = get_next_open_row(board, col)
        drop_piece(board, row, col, opponent)
        if winning_move(board, opponent):
            undo_move(board, row, col)
            return col
        undo_move(board, row, col)

    # 3) Merkeze en yakın hamleyi seç
    center = COLS // 2
    best_col = min(valid_moves, key=lambda c: abs(c - center))
    return best_col


def simulate_random_game(start_board, start_player, current_player):
    """
    Tek bir rollout (oyunu sonuna kadar oyna).

    start_board: Node'un board'u
    start_player: Node'da oynayan son oyuncu
    current_player: Kökte karar veren oyuncu (AI veya HUMAN)

    Dönüş:
        result = 1.0 (AI kazanır)
               = 0.0 (AI kaybeder)
               = 0.5 (berabere)
    """
    board = [row[:] for row in start_board]

    # Sıradaki oyuncu (node.player son oynayan)
    sim_player = PLAYER_HUMAN if start_player == PLAYER_AI else PLAYER_AI
    opponent = PLAYER_HUMAN if sim_player == PLAYER_AI else PLAYER_AI

    # Önce: Node zaten terminal mi?
    if winning_move(board, PLAYER_AI):
        return 1.0 if current_player == PLAYER_AI else 0.0
    if winning_move(board, PLAYER_HUMAN):
        return 0.0 if current_player == PLAYER_AI else 1.0

    max_moves = ROWS * COLS  # güvenlik için üst sınır

    for _ in range(max_moves):
        valid_moves = get_valid_locations(board)
        if not valid_moves:
            # Berabere
            return 0.5

        # Akıllı rollout hamlesi
        move = smart_rollout_move(board, valid_moves, sim_player, opponent)
        row = get_next_open_row(board, move)
        drop_piece(board, row, move, sim_player)

        # Kazanan var mı?
        if winning_move(board, sim_player):
            if sim_player == current_player:
                return 1.0  # AI kazandı
            else:
                return 0.0  # AI kaybetti

        # Oyuncu değiştir
        sim_player = PLAYER_HUMAN if sim_player == PLAYER_AI else PLAYER_AI
        opponent = PLAYER_HUMAN if sim_player == PLAYER_AI else PLAYER_AI

    # Her ihtimale karşı
    return 0.5


# ---------------------------------------------------------------------------
# Ana MCTS araması
# ---------------------------------------------------------------------------

def mcts_search(
    board,
    current_player,
    iterations=MCTS_ITERATIONS,
    time_limit=None,
    exploration_constant=0.9
):
    """
    Monte Carlo Tree Search

    Args:
        board: Mevcut oyun tahtası
        current_player: Sıradaki oyuncu (PLAYER_AI veya PLAYER_HUMAN)
        iterations: En fazla MCTS iterasyonu
        time_limit: Saniye cinsinden süre limiti (opsiyonel)
        exploration_constant: UCB1 C parametresi

    Returns:
        best_column: Seçilen en iyi kolon (int)
    """
    # root.player = bir önce oynayan oyuncu
    root = MCTSNode(board, player=-current_player)

    start_time = time.time()
    iteration_count = 0

    while iteration_count < iterations:
        if time_limit is not None and (time.time() - start_time) >= time_limit:
            break

        # 1. SELECTION
        node = root
        # temp_board: selection + expansion boyunca board'u ilerletmek için
        temp_board = [row[:] for row in board]

        while node.untried_moves == [] and node.children:
            node = node.select_child(exploration_constant)
            if node.move is not None:
                # node.player bu node'da oynamış olan
                apply_move(temp_board, node.move, node.player)

        # 2. EXPANSION
        if node.untried_moves:
            move = random.choice(node.untried_moves)
            next_player = PLAYER_HUMAN if node.player == PLAYER_AI else PLAYER_AI
            apply_move(temp_board, move, next_player)
            node = node.add_child(move, temp_board, next_player)

        # 3. SIMULATION (Rollout)
        result = simulate_random_game(
            node.board,
            node.player,
            current_player
        )

        # 4. BACKPROPAGATION
        # result zaten AI açısından (current_player) tanımlı:
        # AI kazanırsa 1.0, kaybederse 0.0
        while node is not None:
            # current_player AI ise result zaten AI açısından
            if current_player == PLAYER_AI:
                node.update(result)
            else:
                # current_player HUMAN ise, AI'nin sonucu ters
                node.update(1.0 - result)
            node = node.parent

        iteration_count += 1

    # Hiç child yoksa random geçerli hamle seç
    if not root.children:
        return random.choice(get_valid_locations(board)), iteration_count

    # En çok ziyaret edilen child'ı seç (en stabil hamle)
    best_child = max(root.children, key=lambda c: c.visits)
    return best_child.move, iteration_count  # Gerçek iterasyon sayısını da döndür


def get_best_move_mcts(
    board,
    player,
    iterations=MCTS_ITERATIONS,
    time_limit=2.0,
    developer_mode=False
):
    """
    MCTS Agent interface

    Args:
        board: Game board
        player: Sıradaki oyuncu
        iterations: MCTS iterasyon sayısı
        time_limit: Saniye cinsinden süre limiti
        developer_mode: True ise istatistik de döndür

    Returns:
        col (int) veya (col, stats) eğer developer_mode=True
    """
    start_time = time.time()

    best_col, actual_iterations = mcts_search(  # Gerçek iterasyon sayısını al
        board,
        current_player=player,
        iterations=iterations,
        time_limit=time_limit,
        exploration_constant=0.9,
    )

    thinking_time = time.time() - start_time

    print(
        f"🎲 MCTS: col={best_col}, actual_iterations={actual_iterations}/{iterations}, "
        f"time={thinking_time:.2f}s"
    )

    if developer_mode:
        stats = {
            "iterations": actual_iterations,  # Gerçek iterasyon sayısını kullan
            "thinking_time": thinking_time,
            "algorithm": "MCTS_improved",
            "exploration_constant": 0.9,
        }
        return best_col, stats

    return best_col


# ============================================================================ #
# TESTING
# ============================================================================ #

if __name__ == "__main__":
    print("🎲 Monte Carlo Tree Search - Improved Test Suite\n")

    # Test 1: Empty board
    print("Test 1: MCTS on empty board (5000 iterations)")
    board = create_board()
    col = get_best_move_mcts(board, PLAYER_AI, iterations=5000, time_limit=2.0)
    print(f"Best move (AI): {col}")
    print()

    # Test 2: After one center move
    print("Test 2: MCTS after center move")
    board = create_board()
    row = get_next_open_row(board, COLS // 2)
    drop_piece(board, row, COLS // 2, PLAYER_AI)
    col = get_best_move_mcts(board, PLAYER_HUMAN, iterations=5000, time_limit=2.0)
    print(f"Best response (HUMAN): {col}")
    print()

    # Test 3: Immediate win detection
    print("Test 3: Immediate win detection")
    board = create_board()
    # AI için 3 yatay taş
    for c in range(3):
        row = get_next_open_row(board, c)
        drop_piece(board, row, c, PLAYER_AI)
    col = get_best_move_mcts(board, PLAYER_AI, iterations=2000, time_limit=1.0)
    print(f"Should play col 3 → got: {col}")
    print()

    print("✅ All tests completed!")
