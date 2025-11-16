# Connect4 AI Agent - Proje Yapısı

```
connect4-ai-agent/
│
├── connect4/                          # Ana AI modülü
│   ├── __init__.py                    
│   ├── game.py                        # Oyun motoru ve kuralları
│   ├── agent.py                       # Ana AI (Minimax + Alpha-Beta)
│   ├── algorithms.py                  # Tüm algoritmalar (BFS, DFS, UCS, A*, Minimax)
│   ├── benchmark.py                   # Performans karşılaştırma
│   └── visualizer.py                  # Search tree görselleştirme
│
├── main.py                            # Oynanabilir oyun (terminal)
├── app.py                             # Web arayüzü (Flask)
├── run_demo.py                        # Akademik demo (raporlar oluşturur)
│
├── README_ACADEMIC.md                 # Detaylı akademik dokümantasyon
├── PRESENTATION_GUIDE.md              # Sunum kılavuzu (Türkçe)
├── SUNUM_OZET.md                      # Hızlı özet
│
├── connect4_benchmark_report.txt      # Otomatik oluşturulan rapor
├── search_tree_with_pruning.txt       # Pruning ile search tree
├── search_tree_without_pruning.txt    # Pruning olmadan (karşılaştırma)
├── search_tree_with_pruning.dot       # GraphViz dosyası
├── search_tree_without_pruning.dot    # GraphViz dosyası
│
├── requirements.txt                   # Python bağımlılıkları
├── static/                            # Web arayüzü dosyaları
│   ├── style.css
│   └── script.js
└── templates/
    └── index.html
```

## Hızlı Başlangıç

### 1. Oyunu Oyna
```bash
python main.py
```

### 2. Akademik Demo (TÜM RAPORLARI OLUŞTUR)
```bash
python run_demo.py
```

### 3. Web Arayüzü
```bash
python app.py
# http://localhost:5000 adresine git
```

## Sunum İçin

1. **Önce çalıştır**: `python run_demo.py`
2. **Oku**: `PRESENTATION_GUIDE.md`
3. **Göster**: Oluşan .txt dosyalarını
4. **Oyna**: `python main.py` ile canlı demo

Başarılar! 🎓
