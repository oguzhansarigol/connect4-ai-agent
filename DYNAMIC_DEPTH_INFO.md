# 🚀 Runtime-Based Dynamic Depth - Kullanım Kılavuzu

## Nasıl Çalışır?

AI, her hamle sonrası kendi performansını ölçer ve depth'ini otomatik ayarlar:

### Hedef: **1.5 saniye** düşünme süresi

### Tolerans Aralığı: ±40%
- **Optimal aralık**: 0.9s - 2.1s
- **Çok hızlı**: < 0.9s
- **Çok yavaş**: > 2.1s

## Depth Artış Kuralları

### Normal Artış (+1)
```
Süre: 0.9s - 0.45s
Artış: +1 depth
Mesaj: "⚡ Fast"
```

### Agresif Artış (+2)
```
Süre: < 0.45s (çok çok hızlı)
Artış: +2 depth
Mesaj: "⚡⚡ VERY FAST"
```

### Azaltma (-1)
```
Süre: > 2.1s
Azaltma: -1 depth
Mesaj: "🐌 Slow"
```

### Değişiklik Yok
```
Süre: 0.9s - 2.1s
Mesaj: "✅ Optimal"
```

## Depth Limitleri

- **Minimum**: 4
- **Maksimum**: 12
- **Başlangıç**: 6

## Frontend Görsel Feedback

### 1. Depth Badge Animasyonu
- Depth değiştiğinde badge nabız atar
- Renk değişir (mor-pembe gradient)
- 1.5 saniye animasyon

### 2. Toast Notification
- Sağ üst köşede bildirim
- 3 saniye görünür
- Depth değişimini gösterir
  - Örn: "AI Depth: 6 → 8"
  - Alt mesaj: "⚡⚡ VERY FAST (0.23s) → +2 depth"

### 3. Console Log
```javascript
🔄 Depth Change: 6 → 8 (⚡⚡ VERY FAST (0.23s) → +2 depth)
```

## Backend Console Output

```bash
⚡⚡ VERY FAST (0.23s) → +2 depth: 6 → 8
⚡ Fast (0.87s) → +1 depth: 8 → 9
✅ AI runtime optimal (1.54s) → Keeping depth: 9
🐌 Slow (2.87s) → -1 depth: 9 → 8
```

## Örnek Senaryo

```
Hamle 1: depth=6, süre=0.8s  → 0.8 < 0.9  → ⚡ +1 → depth=7
Hamle 2: depth=7, süre=0.3s  → 0.3 < 0.45 → ⚡⚡ +2 → depth=9
Hamle 3: depth=9, süre=1.8s  → Optimal    → ✅ → depth=9
Hamle 4: depth=9, süre=2.5s  → 2.5 > 2.1  → 🐌 -1 → depth=8
Hamle 5: depth=8, süre=1.2s  → Optimal    → ✅ → depth=8
```

## Avantajlar

✅ **Otomatik Optimizasyon**: Manuel ayar gerekmez
✅ **Adaptif**: Oyun karmaşıklığına göre ayarlanır
✅ **Hızlı Yanıt**: Yavaş cihazlarda bile akıcı
✅ **Maksimum Zeka**: Hızlı cihazlarda daha derin düşünür
✅ **Görsel Feedback**: Kullanıcı depth değişimlerini görür

## Test Etmek İçin

1. Oyunu başlatın
2. Console'u açın (F12)
3. Her AI hamlesi sonrası:
   - Console'da depth değişimini görün
   - Sağ üstte toast notification'ı izleyin
   - Sol panelde depth badge'inin değiştiğini ve animasyon yaptığını görün

## İyileştirme Parametreleri

`app.py` dosyasında:

```python
TARGET_THINKING_TIME = 1.5  # Hedef süre (saniye)
AI_DEPTH_MIN = 4           # Min depth
AI_DEPTH_MAX = 12          # Max depth
AI_DEPTH_DEFAULT = 6       # Başlangıç
tolerance = 0.4            # %40 tolerans
```

Bu parametreleri değiştirerek AI'ın davranışını özelleştirebilirsiniz.
