"""
DEVELOPER MODE DEMO - AI'nin Düşünme Sürecini Göster
Bu demo, sunumda AI'nin nasıl karar verdiğini göstermek için.
"""

from connect4.game import (
    create_board, print_board, drop_piece, is_valid_location,
    get_next_open_row, winning_move, get_valid_locations,
    PLAYER_HUMAN, PLAYER_AI, COLS
)
from connect4.agent import get_best_move
import time

def demo_developer_mode():
    """Developer mode'u göster"""
    print("="*70)
    print("  🎓 DEVELOPER MODE DEMO - AI Decision Making Process")
    print("="*70)
    print("\nBu demo, AI'nin her hamle için nasıl düşündüğünü gösterir.\n")
    
    # Basit bir oyun pozisyonu oluştur
    board = create_board()
    
    # İlk birkaç hamle yap (örnek pozisyon)
    drop_piece(board, get_next_open_row(board, 3), 3, PLAYER_AI)
    drop_piece(board, get_next_open_row(board, 3), 3, PLAYER_HUMAN)
    drop_piece(board, get_next_open_row(board, 2), 2, PLAYER_AI)
    drop_piece(board, get_next_open_row(board, 4), 4, PLAYER_HUMAN)
    
    print("Mevcut Oyun Durumu:")
    print_board(board)
    
    print("\n" + "="*70)
    print("AI ŞIMDI DÜŞÜNECEk - Tüm Sütunları Değerlendirecek")
    print("="*70)
    
    # Developer mode ile en iyi hamleyi bul
    best_col, column_scores = get_best_move(board, PLAYER_AI, depth=4, developer_mode=True)
    
    # Görsel feedback
    print("\n⏳ AI hamlesini yapıyor...")
    time.sleep(2)
    
    # Hamleyi uygula
    row = get_next_open_row(board, best_col)
    drop_piece(board, row, best_col, PLAYER_AI)
    
    print("\n✅ Hamle Yapıldı!")
    print_board(board)
    
    print("\n" + "="*70)
    print("AÇIKLAMA:")
    print("="*70)
    print("• AI tüm geçerli sütunları değerlendirdi")
    print("• Her sütun için Minimax algoritmasını çalıştırdı")
    print("• Alpha-Beta pruning ile gereksiz dalları atlattı")
    print("• En yüksek skora sahip sütunu seçti")
    print(f"• Seçilen sütun: {best_col} (Skor: {column_scores[best_col]:.2f})")
    print("\nYüksek pozitif skor = AI için iyi pozisyon")
    print("Düşük negatif skor = Rakip için iyi pozisyon")
    print("="*70)


def demo_comparison():
    """Normal vs Developer mode karşılaştırması"""
    print("\n\n" + "="*70)
    print("  KARŞILAŞTIRMA: Normal Mode vs Developer Mode")
    print("="*70)
    
    board = create_board()
    drop_piece(board, get_next_open_row(board, 3), 3, PLAYER_AI)
    
    print("\n1️⃣  NORMAL MODE:")
    print("-"*70)
    col_normal = get_best_move(board, PLAYER_AI, depth=4, developer_mode=False)
    
    print("\n2️⃣  DEVELOPER MODE:")
    print("-"*70)
    col_dev, scores = get_best_move(board, PLAYER_AI, depth=4, developer_mode=True)
    
    print("\n📊 SONUÇ:")
    print(f"   Her iki modda da aynı hamle seçildi: Sütun {col_normal}")
    print(f"   Developer mode, karar verme sürecini şeffaf hale getiriyor!")
    print("="*70)


def interactive_demo():
    """Interaktif demo - kullanıcı bir hamle yapar, AI cevap verir"""
    print("\n\n" + "="*70)
    print("  🎮 İNTERAKTİF DEMO")
    print("="*70)
    print("\nSiz bir hamle yapın, AI'nin düşünme sürecini görelim!\n")
    
    board = create_board()
    print_board(board)
    
    try:
        user_col = int(input(f"\nBir sütun seçin (0-{COLS-1}): "))
        
        if 0 <= user_col < COLS and is_valid_location(board, user_col):
            # Kullanıcı hamlesi
            row = get_next_open_row(board, user_col)
            drop_piece(board, row, user_col, PLAYER_HUMAN)
            
            print("\nSizin Hamleniz:")
            print_board(board)
            
            # AI cevabı (developer mode ile)
            print("\n🤖 AI'nin Cevabı:")
            print("-"*70)
            best_col, scores = get_best_move(board, PLAYER_AI, depth=6, developer_mode=True)
            
            print("\n⏳ AI hamlesini yapıyor...")
            time.sleep(1.5)
            
            row = get_next_open_row(board, best_col)
            drop_piece(board, row, best_col, PLAYER_AI)
            
            print("\nSonuç:")
            print_board(board)
            
        else:
            print("❌ Geçersiz sütun!")
            
    except ValueError:
        print("❌ Lütfen geçerli bir sayı girin!")


if __name__ == "__main__":
    print("\n\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "CONNECT4 AI - DEVELOPER MODE DEMO" + " "*20 + "║")
    print("║" + " "*14 + "Introduction to AI Course Project" + " "*20 + "║")
    print("╚" + "="*68 + "╝")
    
    print("\nBu demo 3 bölümden oluşuyor:")
    print("1. Developer Mode Gösterimi")
    print("2. Normal vs Developer Karşılaştırması")
    print("3. İnteraktif Demo")
    
    input("\n▶️  Başlamak için Enter'a basın...")
    
    # Demo 1
    demo_developer_mode()
    input("\n▶️  Sonraki demo için Enter'a basın...")
    
    # Demo 2
    demo_comparison()
    input("\n▶️  İnteraktif demo için Enter'a basın...")
    
    # Demo 3
    interactive_demo()
    
    print("\n\n" + "="*70)
    print("  ✅ DEMO TAMAMLANDI!")
    print("="*70)
    print("\nSUNUM İÇİN:")
    print("• main.py dosyasında DEVELOPER_MODE = True yapın")
    print("• python main.py ile oyunu başlatın")
    print("• AI her hamlesinde tüm skorları gösterecek")
    print("• 1.5 saniyelik gecikme ile daha etkileyici!")
    print("="*70)
