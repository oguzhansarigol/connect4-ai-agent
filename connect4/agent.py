import math
import random
from .game import (
    ROWS, COLS, WINDOW_LENGTH, EMPTY, PLAYER_AI, PLAYER_HUMAN,
    is_terminal_node, winning_move, get_valid_locations,
    get_next_open_row, drop_piece
)

# --- Heuristic Değerlendirme Fonksiyonları ---

def evaluate_window(window, piece):
    """
    Verilen 4'lü bir pencereyi (yatay, dikey veya çapraz)
    belirli bir oyuncu (piece) için değerlendirir ve bir skor döndürür.
    """
    score = 0
    opponent_piece = PLAYER_HUMAN if piece == PLAYER_AI else PLAYER_AI

    piece_count = window.count(piece)
    empty_count = window.count(EMPTY)
    opponent_count = window.count(opponent_piece)

    if piece_count == 4:
        score += 10000  # Kazanma durumu, çok yüksek skor
    elif piece_count == 3 and empty_count == 1:
        score += 10  # Kazanmaya bir adım kalmış
    elif piece_count == 2 and empty_count == 2:
        score += 3   # Potansiyel oluşturan durum

    # Rakibin kazanma tehditlerini de değerlendir (bloklama önceliği)
    if opponent_count == 3 and empty_count == 1:
        score -= 80  # Rakip kazanmak üzere, acil blokla!

    return score

def score_position(board, piece):
    """
    Tüm tahtanın mevcut durumunu belirli bir oyuncu (piece) için
    değerlendirir ve genel bir skor döndürür.
    """
    score = 0

    # Merkez sütun bonusu: Merkezdeki taşlar daha fazla kazanma yolu açar.
    center_array = [board[r][COLS // 2] for r in range(ROWS)]
    center_count = center_array.count(piece)
    score += center_count * 5

    # Yatay pencereleri değerlendir
    for r in range(ROWS):
        row_array = board[r]
        for c in range(COLS - (WINDOW_LENGTH - 1)):
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Dikey pencereleri değerlendir
    for c in range(COLS):
        col_array = [board[r][c] for r in range(ROWS)]
        for r in range(ROWS - (WINDOW_LENGTH - 1)):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Pozitif eğimli çapraz pencereleri değerlendir
    for r in range(ROWS - (WINDOW_LENGTH - 1)):
        for c in range(COLS - (WINDOW_LENGTH - 1)):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    # Negatif eğimli çapraz pencereleri değerlendir
    for r in range(ROWS - (WINDOW_LENGTH - 1)):
        for c in range(COLS - (WINDOW_LENGTH - 1)):
            window = [board[r+i][c+(WINDOW_LENGTH-1)-i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)
            
    return score

# --- Minimax ve Alpha-Beta Pruning ---

def minimax(board, depth, alpha, beta, maximizing_player):
    """
    Minimax algoritmasını alpha-beta budaması ile uygular.
    En iyi skoru ve ilgili sütunu döndürür.
    """
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)

    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, PLAYER_AI):
                return (None, 10000000) # AI kazandı
            elif winning_move(board, PLAYER_HUMAN):
                return (None, -10000000) # İnsan kazandı
            else: # Beraberlik
                return (None, 0)
        else: # Derinlik 0'a ulaştı
            return (None, score_position(board, PLAYER_AI))

    if maximizing_player:
        value = -math.inf
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = [row[:] for row in board] # Tahtanın kopyasını oluştur
            drop_piece(temp_board, row, col, PLAYER_AI)
            new_score = minimax(temp_board, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                best_col = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break # Beta kesmesi
        return best_col, value
    else: # Minimizing player
        value = math.inf
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = [row[:] for row in board] # Tahtanın kopyasını oluştur
            drop_piece(temp_board, row, col, PLAYER_HUMAN)
            new_score = minimax(temp_board, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                best_col = col
            beta = min(beta, value)
            if alpha >= beta:
                break # Alpha kesmesi
        return best_col, value

def get_best_move(board, piece, depth):
    """
    Verilen tahta durumu için AI'ın yapacağı en iyi hamleyi hesaplar.
    """
    print("AI düşünüyor...")
    col, minimax_score = minimax(board, depth, -math.inf, math.inf, True)
    return col