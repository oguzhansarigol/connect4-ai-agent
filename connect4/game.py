import sys

# --- Sabitler ---
ROWS = 6
COLS = 7
WINDOW_LENGTH = 4

PLAYER_HUMAN = -1
PLAYER_AI = 1
EMPTY = 0

# --- Tahta Operasyonları ---

def create_board():
    """
    6x7'lik bir Connect4 oyun tahtası oluşturur ve boş olarak başlatır.
    Tahta, 0'larla dolu bir 2D liste olarak temsil edilir.
    """
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]

def drop_piece(board, row, col, piece):
    """
    Belirtilen satır ve sütuna bir oyuncunun taşını bırakır.
    """
    board[row][col] = piece

def is_valid_location(board, col):
    """
    Bir sütunun hamle yapmak için geçerli olup olmadığını kontrol eder.
    (Yani, sütunun en üst satırı boş mu?)
    """
    return board[ROWS-1][col] == EMPTY

def get_next_open_row(board, col):
    """
    Belirtilen sütunda bir taşın düşeceği bir sonraki boş satırı bulur.
    """
    for r in range(ROWS):
        if board[r][col] == EMPTY:
            return r
    return None # Bu durum normalde is_valid_location ile önlenir.

def get_valid_locations(board):
    """
    Hamle yapılabilecek tüm geçerli sütunların bir listesini döndürür.
    """
    valid_locations = []
    for col in range(COLS):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

def print_board(board):
    """
    Oyun tahtasını terminale yazdırır. 0,0 sol alttadır.
    """
    # Tahtayı dikey olarak çevirerek yazdırıyoruz ki 0. satır altta görünsün.
    for r in reversed(range(ROWS)):
        row_str = "| "
        for c in range(COLS):
            if board[r][c] == PLAYER_AI:
                char = "X" # AI
            elif board[r][c] == PLAYER_HUMAN:
                char = "O" # İnsan
            else:
                char = " " # Boş
            row_str += f"{char} "
        print(row_str + "|")
    print("+" + "---" * COLS + "+")
    print("  " + " ".join(f" {c} " for c in range(COLS)))


# --- Oyun Durumu Kontrolü ---

def winning_move(board, piece):
    """
    Belirtilen oyuncunun son hamlesiyle oyunu kazanıp kazanmadığını kontrol eder.
    """
    # Yatay kontrol
    for c in range(COLS - (WINDOW_LENGTH - 1)):
        for r in range(ROWS):
            if all(board[r][c+i] == piece for i in range(WINDOW_LENGTH)):
                return True

    # Dikey kontrol
    for c in range(COLS):
        for r in range(ROWS - (WINDOW_LENGTH - 1)):
            if all(board[r+i][c] == piece for i in range(WINDOW_LENGTH)):
                return True

    # Pozitif eğimli çapraz kontrol
    for c in range(COLS - (WINDOW_LENGTH - 1)):
        for r in range(ROWS - (WINDOW_LENGTH - 1)):
            if all(board[r+i][c+i] == piece for i in range(WINDOW_LENGTH)):
                return True

    # Negatif eğimli çapraz kontrol
    for c in range(COLS - (WINDOW_LENGTH - 1)):
        for r in range(WINDOW_LENGTH - 1, ROWS):
            if all(board[r-i][c+i] == piece for i in range(WINDOW_LENGTH)):
                return True
    
    return False

def is_terminal_node(board):
    """
    Oyunun bitip bitmediğini kontrol eder (kazanan var veya tahta dolu).
    """
    return winning_move(board, PLAYER_HUMAN) or winning_move(board, PLAYER_AI) or len(get_valid_locations(board)) == 0