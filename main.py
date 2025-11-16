# Kendi modüllerimizden gerekli fonksiyonları ve sabitleri içe aktarıyoruz.
from connect4.game import (
    create_board, print_board, drop_piece, is_valid_location,
    get_next_open_row, winning_move, get_valid_locations,
    PLAYER_HUMAN, PLAYER_AI, COLS
)
from connect4.agent import get_best_move

# Standart kütüphaneler
import random
import sys

# Yapay zekanın ne kadar ileriyi düşüneceğini belirleyen derinlik.
# Değeri artırmak AI'ı daha zeki ama daha yavaş yapar. 4-5 iyi bir başlangıçtır.
AI_DEPTH = 8

def main():
    """
    Ana oyun fonksiyonu. Oyunu başlatır ve döngüyü yönetir.
    """
    board = create_board()
    game_over = False
    
    print("--- Connect4 AI Agent ---")
    print("Siz 'O' harfisiniz, Yapay Zekâ 'X' harfi.")
    
    # Oyuna kimin başlayacağını rastgele seçelim
    turn = random.choice([PLAYER_HUMAN, PLAYER_AI])
    if turn == PLAYER_HUMAN:
        print("Oyuna siz başlıyorsunuz.")
    else:
        print("Oyuna yapay zekâ başlıyor.")

    print_board(board)

    # --- Ana Oyun Döngüsü ---
    while not game_over:
        
        # --- İnsan Oyuncunun Sırası ---
        if turn == PLAYER_HUMAN:
            try:
                col_input = input(f"Sıra sizde. Bir sütun seçin (0-{COLS-1}): ")
                col = int(col_input)

                if 0 <= col < COLS and is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, PLAYER_HUMAN)

                    if winning_move(board, PLAYER_HUMAN):
                        print("\n*** TEBRİKLER! OYUNU KAZANDINIZ! ***")
                        game_over = True
                    
                    # Sırayı diğer oyuncuya geçir
                    turn = PLAYER_AI
                else:
                    print("Geçersiz hamle. Lütfen boş bir sütun seçin.")
                    continue # Döngünün başına dön, sırayı değiştirmeden tekrar sor

            except ValueError:
                print("Hatalı giriş. Lütfen 0 ile 6 arasında bir sayı girin.")
                continue
        
        # --- Yapay Zekânın Sırası ---
        if turn == PLAYER_AI and not game_over:
            # AI'dan en iyi hamleyi al
            col = get_best_move(board, PLAYER_AI, AI_DEPTH)

            # AI'ın hamlesini uygula
            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, PLAYER_AI)
                print(f"\nYapay zekâ {col}. sütunu seçti.")

                if winning_move(board, PLAYER_AI):
                    print("\n*** MAALESEF, YAPAY ZEKÂ KAZANDI! ***")
                    game_over = True
            
            # Sırayı diğer oyuncuya geçir
            turn = PLAYER_HUMAN

        # Her hamleden sonra tahtayı yazdır
        print_board(board)

        # Beraberlik durumunu kontrol et
        if not game_over and len(get_valid_locations(board)) == 0:
            print("\n*** OYUN BERABERE BİTTİ! ***")
            game_over = True

# Bu script doğrudan çalıştırıldığında main() fonksiyonunu çağır
if __name__ == "__main__":
    main()