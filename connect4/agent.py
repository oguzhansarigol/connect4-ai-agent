"""
Connect4 AI Agent - Minimax with Alpha-Beta Pruning
Bu modül, oyundaki ana AI mantığını içerir.
"""

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
    
    Heuristic Açıklama:
    - 4'lü tamamlanmış: Kazanma durumu (+10000)
    - 3'lü + 1 boş: Kazanmaya çok yakın (+10)
    - 2'li + 2 boş: Potansiyel oluşturuyor (+3)
    - Rakip 3'lü + 1 boş: Acil blok gerekli (-80)
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
    
    Bu heuristic fonksiyonu şu faktörleri değerlendirir:
    1. Merkez kontrolü (center column advantage)
    2. Yatay kazanma potansiyeli
    3. Dikey kazanma potansiyeli
    4. Çapraz kazanma potansiyeli (+ ve - eğimli)
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
    
    ALGORITMA SEÇİMİ NEDENLERİ:
    1. Connect4 iki kişilik, sıfır toplamlı, mükemmel bilgili bir oyundur
    2. Adversarial search gerektirir (rakip bizim skorumuzu minimize etmeye çalışır)
    3. Minimax bu tür oyunlar için optimal stratejidir
    4. Alpha-Beta Pruning aynı sonucu daha az node expand ederek verir
    
    COMPLEXITY:
    - Time: O(b^d) worst case, O(b^(d/2)) best case (b=branching factor≈7, d=depth)
    - Space: O(b*d) recursive stack
    - Completeness: Evet (sonlu oyun ağacı)
    - Optimality: Evet (optimal hamleyi garanti eder)
    
    PRUNING:
    - Alpha: MAX oyuncusunun garantileyebileceği minimum değer
    - Beta: MIN oyuncusunun garantileyebileceği maksimum değer
    - alpha >= beta olduğunda, o dal kesilir (explore edilmez)
    
    Args:
        board: Mevcut oyun tahtası
        depth: Arama derinliği (kaç hamle ilerisi)
        alpha: Alpha değeri (pruning için)
        beta: Beta değeri (pruning için)
        maximizing_player: True ise AI'ın (MAX), False ise rakibin (MIN) sırası
        
    Returns:
        (best_column, score): En iyi hamle ve skoru
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
                break # Beta cut-off: Rakip bu duruma izin vermez
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
                break # Alpha cut-off: AI bu duruma izin vermez
        return best_col, value

def get_best_move(board, piece, depth, developer_mode=False):
    """
    Verilen tahta durumu için AI'ın yapacağı en iyi hamleyi hesaplar.
    
    Args:
        board: Mevcut oyun tahtası
        piece: AI'ın oyuncu numarası (PLAYER_AI)
        depth: Arama derinliği
        developer_mode: True ise tüm sütunların skorlarını döndürür
        
    Returns:
        best_column: En iyi sütun hamlesi
        (developer_mode=True ise: (best_column, all_scores_dict))
    """
    print("AI düşünüyor...")
    
    if developer_mode:
        # Tüm geçerli sütunlar için skorları hesapla
        valid_locations = get_valid_locations(board)
        column_scores = {}
        
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = [row[:] for row in board]
            drop_piece(temp_board, row, col, PLAYER_AI)
            score = minimax(temp_board, depth - 1, -math.inf, math.inf, False)[1]
            column_scores[col] = score
        
        # En iyi sütunu bul
        best_col = max(column_scores.items(), key=lambda x: x[1])[0]
        best_score = column_scores[best_col]
        
        print(f"\n🔍 DEVELOPER MODE - Sütun Skorları:")
        print("   " + "-" * 50)
        for col in range(COLS):
            if col in column_scores:
                score = column_scores[col]
                is_best = "← EN İYİ ⭐" if col == best_col else ""
                bar_length = int((score + 100) / 10)  # Basit görselleştirme
                bar = "█" * max(0, min(bar_length, 30))
                print(f"   Sütun {col}: {score:8.2f} {bar} {is_best}")
            else:
                print(f"   Sütun {col}: {'DOLU':>8}")
        print("   " + "-" * 50)
        print(f"   ✅ Seçilen: Sütun {best_col} (Skor: {best_score:.2f})")
        
        return best_col, column_scores
    else:
        # Normal mode
        col, minimax_score = minimax(board, depth, -math.inf, math.inf, True)
        print(f"   Seçilen hamle: Sütun {col} (Skor: {minimax_score})")
        return col