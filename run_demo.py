"""
INTRODUCTION TO AI - CONNECT4 PROJECT DEMO
Bu script, sunum için tüm analizleri çalıştırır ve raporları oluşturur.
"""

import sys
from connect4.game import create_board, drop_piece, get_next_open_row, PLAYER_AI
from connect4.benchmark import run_benchmark
from connect4.visualizer import visualize_search_tree


def print_header(text):
    """Güzel başlık yazdır"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80 + "\n")


def main():
    print_header("CONNECT4 AI - ACADEMIC PRESENTATION DEMO")
    
    print("Bu demo şu çıktıları üretecek:")
    print("1. ✅ Algoritma karşılaştırma raporu")
    print("2. ✅ Search tree görselleştirmesi")
    print("3. ✅ Complexity analizi")
    print("4. ✅ Algoritma seçim gerekçeleri")
    print()
    
    input("Devam etmek için Enter'a basın...")
    
    # Başlangıç pozisyonu oluştur
    board = create_board()
    drop_piece(board, get_next_open_row(board, 3), 3, PLAYER_AI)
    
    # =========================================================================
    # PART 1: Algorithm Benchmark
    # =========================================================================
    print_header("PART 1: ALGORITHM BENCHMARK")
    print("Farklı arama algoritmalarını karşılaştırıyoruz...")
    print("(BFS, DFS, UCS, A*, Minimax, Minimax+Alpha-Beta)")
    print()
    
    benchmark = run_benchmark(depth=4)
    
    # =========================================================================
    # PART 2: Search Tree Visualization
    # =========================================================================
    print_header("PART 2: SEARCH TREE VISUALIZATION")
    print("Alpha-Beta Pruning'in etkisini görselleştiriyoruz...\n")
    
    print("📊 WITH Alpha-Beta Pruning:")
    visualizer_with = visualize_search_tree(board, depth=3, with_pruning=True)
    
    print("\n📊 WITHOUT Alpha-Beta Pruning (for comparison):")
    visualizer_without = visualize_search_tree(board, depth=3, with_pruning=False)
    
    # Karşılaştırma
    print_header("PRUNING COMPARISON")
    print(f"Without Pruning: {visualizer_without.total_nodes} nodes expanded")
    print(f"With Pruning:    {visualizer_with.total_nodes} nodes expanded")
    print(f"Nodes Saved:     {visualizer_without.total_nodes - visualizer_with.total_nodes}")
    print(f"Efficiency:      {(visualizer_with.pruned_nodes/visualizer_with.total_nodes*100):.2f}% pruned")
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print_header("GENERATED FILES")
    print("Aşağıdaki dosyalar oluşturuldu:\n")
    print("📄 connect4_benchmark_report.txt")
    print("   - Tüm algoritmaların detaylı karşılaştırması")
    print("   - Complexity analizi")
    print("   - Algoritma seçim gerekçeleri\n")
    
    print("🌳 search_tree_with_pruning.txt")
    print("   - Alpha-Beta pruning ile search tree")
    print("   - ASCII art görselleştirme\n")
    
    print("🌳 search_tree_without_pruning.txt")
    print("   - Pruning olmadan search tree (karşılaştırma için)\n")
    
    print("📊 search_tree_with_pruning.dot")
    print("   - GraphViz formatında görsel")
    print("   - Kullanım: dot -Tpng search_tree_with_pruning.dot -o tree.png\n")
    
    print("📊 search_tree_without_pruning.dot")
    print("   - GraphViz formatında görsel (pruning olmadan)\n")
    
    print_header("PRESENTATION TALKING POINTS")
    print("""
SUNUMDA KULLANILACAK ANA NOKTALAR:

1. PROBLEM TANIMI:
   ✓ Connect4 iki oyunculu, sıfır toplamlı, perfect information oyun
   ✓ Adversarial search gerekli (rakip bizim skorumuzu minimize eder)
   
2. NEDEN MİNIMAX SEÇTİK:
   ✓ BFS/DFS/UCS tek agent pathfinding için, oyun oynamak için değil
   ✓ Connect4 adversarial olduğu için Minimax ideal
   ✓ Complete ve optimal (sonlu ağaç için)
   
3. NEDEN ALPHA-BETA PRUNING EKLEDİK:
   ✓ Aynı sonucu verir ama çok daha hızlı
   ✓ Empirik verilerimize göre %{:.1f} daha az node expand ediyor
   ✓ Daha derinlere arama yapabiliyoruz aynı sürede
   
4. NEDEN HEURISTIC KULLANDIK:
   ✓ Oyun ağacı çok derin (42 hamle)
   ✓ Tüm ağacı aramak imkansız (b^d complexity)
   ✓ Heuristic ile limited depth'te akıllı değerlendirme
   ✓ Center control, threats, potential wins değerlendiriliyor
   
5. INFORMED vs UNINFORMED:
   ✓ Minimax adversarial search (farklı kategori)
   ✓ Heuristic evaluation kullanıyoruz ama A*'daki gibi değil
   ✓ A* pathfinding için heuristic kullanır
   ✓ Biz position evaluation için kullanıyoruz
   
6. KARŞILAŞTIĞIMIZ SORUNLAR:
   ✓ Depth artırınca exponential complexity
   ✓ Memory problemi (özellikle BFS'de)
   ✓ Alpha-Beta pruning ile çözdük
   ✓ Heuristic optimization ile depth 8'e çıkardık
   
7. COMPLEXITY ANALİZİ:
   ✓ Time: O(b^d) worst, O(b^(d/2)) best with alpha-beta
   ✓ Space: O(b*d) recursive stack
   ✓ b ≈ 7 (branching factor), d = 8 (our depth)
   ✓ Without pruning: 7^8 = 5,764,801 nodes
   ✓ With pruning: ~{} nodes (see benchmark)

DEMO İÇİN:
1. Oyunu çalıştır (main.py)
2. Benchmark sonuçlarını göster
3. Search tree görselleştirmesini göster
4. Pruning'in etkisini vurgula
""".format(
        benchmark._get_pruning_improvement(),
        benchmark.results.get('Minimax + Alpha-Beta Pruning', {}).get('metrics', type('obj', (), {'nodes_expanded': 'N/A'})()).nodes_expanded
    ))
    
    print_header("DEMO COMPLETED")
    print("Tüm raporlar oluşturuldu. Başarılar! 🎓")


if __name__ == "__main__":
    main()
