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
    -   **Arama Algoritması:** `minimax_optimized` fonksiyonu, en iyi hamleyi bulmak için alpha-beta pruning ile optimize edilmiş bir arama yapar. `get_best_move_optimized` bu süreci başlatan ana fonksiyondur.

## 🚀 Optimizasyonlar

Agent, **7 kritik optimizasyon** kullanır:

### 1. **Alpha-Beta Pruning** (Temel)
- Time complexity: O(b^d) → O(b^(d/2)) best case
- ~60-80% node reduction

### 2. **Move Ordering** ⭐⭐⭐⭐⭐
- %30-50 ek hızlanma
- Sıralama: [kazanma → tehdit bloklama → killer moves → merkez → kenar]
- Önce iyi hamleleri dener → daha fazla cutoff

### 3. **Transposition Table** ⭐⭐⭐⭐
- %20-40 hızlanma
- Daha önce görülen pozisyonları cache'ler
- `transposition_table = {}` global dictionary

### 4. **Threat Detection** ⭐⭐⭐
- %15-25 daha stratejik oyun
- Rakibin 3-taş tehditlerini **-1000** skorla cezalandırır
- `detect_immediate_threats()` fonksiyonu ile acil tehditler tespit edilir

### 5. **Killer Moves** ⭐⭐⭐⭐
- %15-20 ek budama
- Cutoff'a sebep olan hamleleri hatırlar
- `killer_moves = {depth: [move1, move2]}` global table

### 6. **Evaluation Board** ⭐⭐
- Stratejik pozisyonlara 3-13 arası bonus puan
- Merkez ve orta sıralar en değerli

### 7. **Center Column Bonus** ⭐⭐⭐
- Merkez sütuna +3 bonus
- Merkez 13 farklı 4'lü kombinasyona katılır

## Temel Kurallar ve Temsiller

-   **Tahta Boyutu:** `6` satır x `7` sütun.
-   **Oyuncu Temsili:**
    -   `1`: Yapay Zekâ (AI)
    -   `-1`: İnsan Oyuncu
    -   `0`: Boş hücre
-   **Veri Akışı:** `main.py` -> `agent.py` (hamle istemek için) -> `game.py` (durumu değerlendirmek için).

## Geliştirici Akışı

-   **Oyunu Çalıştırma:** 
    -   Terminal: `python main.py` 
    -   Web: `python app.py` (Flask)
-   **Bağımlılıklar:** `Flask==3.0.0` (web için)
-   **Değişiklik Yapma:**
    -   Oyun kurallarını değiştirmek için `connect4/game.py`
    -   AI optimizasyonlarını ayarlamak için `connect4/agent.py`
    -   Heuristic skorlaması `evaluate_window()` ve `score_position()` içinde
    -   AI derinliği `main.py` içinde `AI_DEPTH` sabiti (varsayılan: 8)

## Web Arayüzü

-   **Flask Backend**: `app.py`
-   **Endpoints**: `/api/game`, `/api/move`, `/api/ai-move`, `/api/reset`
-   **Developer Mode**: Depth slider (1-12) + AI decision visualization
-   **Frontend**: `templates/index.html`, `static/style.css`, `static/script.js`
