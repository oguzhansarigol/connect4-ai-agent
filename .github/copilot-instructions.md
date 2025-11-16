# Connect4 AI Agent - Copilot Yönergeleri

Bu proje, Python'da terminal tabanlı bir Connect4 oyunu ve ona karşı oynayan bir yapay zekâ ajanı içerir.

## Mimari ve Dosya Yapısı

Proje üç ana bileşenden oluşur:

1.  **`main.py` (Oyun Yöneticisi):**
    -   Ana oyun döngüsünü içerir.
    -   Kullanıcı girdilerini alır ve oyun akışını yönetir.
    -   Sırası geldiğinde yapay zekâ ajanını tetikler.

2.  **`connect4/game.py` (Oyun Motoru):**
    -   Connect4 oyununun temel kurallarını ve durumunu yönetir.
    -   `create_board`, `drop_piece`, `winning_move` gibi temel oyun fonksiyonlarını içerir.
    -   Oyun tahtası, `(0,0)` sol alt köşe olacak şekilde bir 2D liste (`list[list[int]]`) olarak temsil edilir.

3.  **`connect4/agent.py` (Yapay Zekâ Ajanı):**
    -   Yapay zekânın karar verme mantığını barındırır.
    -   **Heuristic Değerlendirme:** `score_position` fonksiyonu, oyunun bitmediği durumlarda tahtanın mevcut durumuna bir "fayda" (utility) skoru atar. Bu skor, 4'lü pencereleri (`evaluate_window`) analiz ederek ve merkez sütuna bonus vererek hesaplanır.
    -   **Arama Algoritması:** `minimax` fonksiyonu, en iyi hamleyi bulmak için alpha-beta pruning ile optimize edilmiş bir arama yapar. `get_best_move` bu süreci başlatan ana fonksiyondur.

## Temel Kurallar ve Temsiller

-   **Tahta Boyutu:** `6` satır x `7` sütun.
-   **Oyuncu Temsili:**
    -   `1`: Yapay Zekâ (AI)
    -   `-1`: İnsan Oyuncu
    -   `0`: Boş hücre
-   **Veri Akışı:** `main.py` -> `agent.py` (hamle istemek için) -> `game.py` (durumu değerlendirmek için).

## Geliştirici Akışı

-   **Oyunu Çalıştırma:** Proje, ana dizinde `python main.py` komutuyla çalıştırılmalıdır. Bu, `connect4` paketindeki modüllerin doğru bir şekilde import edilmesini sağlar.
-   **Bağımlılıklar:** Proje sadece standart Python kütüphanelerini kullanır. Harici bir bağımlılık (`requirements.txt`) yoktur.
-   **Değişiklik Yapma:**
    -   Oyun kurallarını (tahta boyutu, kazanma koşulu vb.) değiştirmek için `connect4/game.py` dosyasına bakın.
    -   Yapay zekânın zekâsını veya stratejisini (heuristic skorlaması, arama derinliği) ayarlamak için `connect4/agent.py` dosyasını düzenleyin. `AI_DEPTH` sabiti `main.py` içinde bulunur.
