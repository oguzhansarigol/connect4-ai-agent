from flask import Flask, render_template, request, jsonify, session
import random
import time
from connect4.game import (
    create_board, drop_piece, is_valid_location,
    get_next_open_row, winning_move, get_valid_locations,
    PLAYER_HUMAN, PLAYER_AI, COLS, ROWS
)
from connect4.agent import get_best_move
from connect4.agent_bitboard import get_best_move_bitboard  # Bitboard-optimized Minimax
from connect4.mcts_agent import get_best_move_mcts, MCTS_ITERATIONS
from connect4.mcts_agent_v2 import get_best_move_mcts_v2, MCTS_ITERATIONS as MCTS_ITERATIONS_V2  # Production MCTS

app = Flask(__name__)
app.secret_key = 'connect4-secret-key'  # Session için gerekli

# AI Configuration
USE_BITBOARD_MINIMAX = False  # Set to True to use bitboard-optimized minimax

# AI derinliği - Dinamik Yönetim
AI_DEPTH_MIN = 4   # Minimum depth
AI_DEPTH_MAX = 12  # Maximum depth
AI_DEPTH_DEFAULT = 6  # Başlangıç depth'i
TARGET_THINKING_TIME = 4.0  # Hedef düşünme süresi (saniye)
DEPTH_ADJUSTMENT_THRESHOLD = 2.5  # Depth değiştirmek için eşik (saniye)
MIN_ROUNDS_FOR_INCREASE = 4  # Depth artırmak için minimum tur sayısı
MAX_RUNTIME_THRESHOLD = 6.0  # Depth azaltmak için maksimum süre (saniye)

def adjust_depth_by_runtime(current_depth, actual_time, round_count, target_time=TARGET_THINKING_TIME):
    """
    Gerçek çalışma süresine göre depth'i dinamik olarak ayarla.
    
    Kurallar:
    1. DEPTH ARTIRMA:
       - runtime < (target_time - 2.5) VE
       - En az 4 tur oynandı
       → Depth +1
    
    2. DEPTH AZALTMA:
       - runtime > (target_time + 2.5) VE
       - runtime > 6 saniye
       → Depth -1
    
    3. Aksi halde depth sabit kalır
    
    Args:
        current_depth: Mevcut search depth
        actual_time: Gerçekleşen düşünme süresi (saniye)
        round_count: Oynanan toplam tur sayısı
        target_time: Hedef düşünme süresi (saniye)
    
    Returns:
        (yeni_depth, değişim_mesajı) tuple
    """
    lower_threshold = target_time - DEPTH_ADJUSTMENT_THRESHOLD  # 4.0 - 2.5 = 1.5s
    upper_threshold = target_time + DEPTH_ADJUSTMENT_THRESHOLD  # 4.0 + 2.5 = 6.5s
    
    change_msg = None
    
    # KURAL 1: DEPTH ARTIRMA
    if actual_time < lower_threshold and round_count >= MIN_ROUNDS_FOR_INCREASE:
        new_depth = min(current_depth + 1, AI_DEPTH_MAX)
        change_msg = f"⚡ Fast ({actual_time:.2f}s < {lower_threshold:.1f}s, Round≥{MIN_ROUNDS_FOR_INCREASE}) → +1 depth"
        print(f"{change_msg}: {current_depth} → {new_depth}")
        return new_depth, change_msg
    
    # KURAL 2: DEPTH AZALTMA (ama 6'nın altına düşmez)
    elif actual_time > upper_threshold and actual_time > MAX_RUNTIME_THRESHOLD:
        new_depth = max(current_depth - 1, AI_DEPTH_DEFAULT)  # AI_DEPTH_DEFAULT = 6
        change_msg = f"🐌 Slow ({actual_time:.2f}s > {upper_threshold:.1f}s AND > {MAX_RUNTIME_THRESHOLD:.1f}s) → -1 depth"
        print(f"{change_msg}: {current_depth} → {new_depth}")
        return new_depth, change_msg
    
    # KURAL 3: DEPTH SABİT
    else:
        reason = ""
        if actual_time < lower_threshold:
            reason = f"but only {round_count} rounds (need ≥{MIN_ROUNDS_FOR_INCREASE})"
        elif actual_time > upper_threshold:
            reason = f"but runtime {actual_time:.2f}s ≤ {MAX_RUNTIME_THRESHOLD:.1f}s"
        else:
            reason = f"within acceptable range ({lower_threshold:.1f}s - {upper_threshold:.1f}s)"
        
        change_msg = f"✅ Keep depth={current_depth} ({reason})"
        print(f"✅ AI runtime {actual_time:.2f}s → Keeping depth: {current_depth} ({reason})")
        return current_depth, change_msg

def create_game_session(first_player=None):
    """Yeni bir oyun oturumu oluşturur"""
    board = create_board()
    if first_player is None:
        turn = random.choice([PLAYER_HUMAN, PLAYER_AI])
    else:
        turn = first_player
    return {
        'board': board,
        'turn': turn,
        'game_over': False,
        'winner': None,
        'last_move': None,
        'move_count': 0,  # Hamle sayacı
        'current_depth': AI_DEPTH_DEFAULT  # Başlangıç depth'i
    }

def board_to_json(board):
    """Board'u JSON formatına çevirir"""
    return [[cell for cell in row] for row in board]

@app.route('/')
def index():
    """Ana sayfa - oyun arayüzü"""
    if 'game' not in session:
        session['game'] = create_game_session()
        session.modified = True
    return render_template('index.html')

@app.route('/api/game', methods=['GET'])
def get_game_state():
    """Mevcut oyun durumunu döndürür"""
    if 'game' not in session:
        session['game'] = create_game_session()
    
    game = session['game']
    return jsonify({
        'board': board_to_json(game['board']),
        'turn': game['turn'],
        'game_over': game['game_over'],
        'winner': game['winner'],
        'last_move': game['last_move'],
        'valid_columns': get_valid_locations(game['board'])
    })

@app.route('/api/move', methods=['POST'])
def make_move():
    """Oyuncu hamlesi yapar"""
    data = request.get_json()
    col = int(data['column'])
    
    if 'game' not in session:
        session['game'] = create_game_session()
    
    game = session['game']
    board = game['board']
    
    # move_count yoksa ekle
    if 'move_count' not in game:
        game['move_count'] = 0
    
    # Oyun bitmiş mi kontrol et
    if game['game_over']:
        return jsonify({'error': 'Oyun zaten bitti'}), 400
    
    # Geçerli hamle mi kontrol et
    if not is_valid_location(board, col):
        return jsonify({'error': 'Geçersiz hamle'}), 400
    
    # İnsan oyuncunun hamlesi
    if game['turn'] == PLAYER_HUMAN:
        row = get_next_open_row(board, col)
        drop_piece(board, row, col, PLAYER_HUMAN)
        game['last_move'] = {'player': PLAYER_HUMAN, 'row': row, 'col': col}
        game['move_count'] = game['move_count'] + 1  # Hamle sayacını artır
        
        # Kazanma kontrolü
        if winning_move(board, PLAYER_HUMAN):
            game['game_over'] = True
            game['winner'] = PLAYER_HUMAN
        elif len(get_valid_locations(board)) == 0:
            game['game_over'] = True
            game['winner'] = None  # Beraberlik
        else:
            game['turn'] = PLAYER_AI
    
    session['game'] = game
    session.modified = True
    
    # SADECE kullanıcı hamlesini döndür - AI hamlesi ayrı endpoint'ten gelecek
    response_data = {
        'board': board_to_json(game['board']),
        'turn': game['turn'],
        'game_over': game['game_over'],
        'winner': game['winner'],
        'last_move': game['last_move'],
        'valid_columns': get_valid_locations(game['board'])
    }
    
    return jsonify(response_data)

@app.route('/api/ai-move', methods=['POST'])
def make_ai_move():
    """AI hamlesini yapar - DİNAMİK DEPTH ile"""
    import time
    
    if 'game' not in session:
        return jsonify({'error': 'Oyun oturumu bulunamadı'}), 400
    
    data = request.get_json() or {}
    developer_mode = data.get('developer_mode', False)  # Developer mode kontrolü
    
    game = session['game']
    board = game['board']
    
    if game['game_over'] or game['turn'] != PLAYER_AI:
        return jsonify({'error': 'AI hamle yapamaz'}), 400
    
    # Mevcut depth'i al veya başlangıç değerini kullan
    current_depth = game.get('current_depth', AI_DEPTH_DEFAULT)
    
    # Toplam tur sayısını hesapla (move_count / 2 = tur sayısı)
    move_count = game.get('move_count', 0)
    round_count = (move_count + 1) // 2  # Her tur 2 hamle (insan + AI)
    
    # Kullanıcıdan gelen depth varsa kullan (eski davranış - artık yok)
    if 'depth' in data:
        depth = int(data['depth'])
    else:
        depth = current_depth  # Session'dan gelen depth'i kullan
    
    # AI hamlesini yap (developer mode ile veya olmadan)
    column_scores = None
    start_time = time.time()
    if developer_mode:
        if USE_BITBOARD_MINIMAX:
            ai_col, column_scores = get_best_move_bitboard(board, PLAYER_AI, depth, developer_mode=True)
        else:
            ai_col, column_scores = get_best_move(board, PLAYER_AI, depth, developer_mode=True)
    else:
        if USE_BITBOARD_MINIMAX:
            ai_col, _ = get_best_move_bitboard(board, PLAYER_AI, depth, developer_mode=False)
        else:
            ai_col = get_best_move(board, PLAYER_AI, depth, developer_mode=False)
    thinking_time = time.time() - start_time
    
    # ⚡ RUNTIME-BASED DYNAMIC DEPTH ADJUSTMENT (YENİ KURALLAR)
    new_depth, depth_change_msg = adjust_depth_by_runtime(depth, thinking_time, round_count, TARGET_THINKING_TIME)
    game['current_depth'] = new_depth  # Yeni depth'i kaydet
    
    ai_row = get_next_open_row(board, ai_col)
    drop_piece(board, ai_row, ai_col, PLAYER_AI)
    game['last_move'] = {'player': PLAYER_AI, 'row': ai_row, 'col': ai_col}
    game['move_count'] = game.get('move_count', 0) + 1  # Hamle sayacını artır
    
    # Kazanma kontrolü
    if winning_move(board, PLAYER_AI):
        game['game_over'] = True
        game['winner'] = PLAYER_AI
    elif len(get_valid_locations(board)) == 0:
        game['game_over'] = True
        game['winner'] = None
    else:
        game['turn'] = PLAYER_HUMAN
    
    session['game'] = game
    session.modified = True
    
    response = {
        'board': board_to_json(game['board']),
        'turn': game['turn'],
        'game_over': game['game_over'],
        'winner': game['winner'],
        'last_move': game['last_move'],
        'valid_columns': get_valid_locations(game['board']),
        'ai_move': {
            'row': ai_row, 
            'col': ai_col,
            'thinking_time': round(thinking_time, 3),
            'depth': new_depth,  # YENİ depth'i frontend'e gönder
            'previous_depth': depth,  # Önceki depth
            'depth_changed': (new_depth != depth),  # Depth değişti mi?
            'depth_change_msg': depth_change_msg,  # Değişim mesajı
            'round_count': round_count  # Kaç tur oynandı (debug için)
        }
    }
    
    # Developer mode ise sütun skorlarını da ekle
    if developer_mode and column_scores:
        response['ai_move']['column_scores'] = {str(k): float(v) if v is not None else None for k, v in column_scores.items()}
    
    return jsonify(response)

@app.route('/api/reset', methods=['POST'])
def reset_game():
    """Oyunu yeniden başlatır"""
    data = request.get_json() or {}
    first_player = data.get('first_player')
    if first_player == 'human':
        first_player = PLAYER_HUMAN
    elif first_player == 'ai':
        first_player = PLAYER_AI
    else:
        first_player = None
    
    # Yeni oyun başlarken depth'i default değere sıfırla
    session['game'] = create_game_session(first_player)
    session['game']['current_depth'] = AI_DEPTH_DEFAULT  # 6'ya resetle
    session.modified = True
    
    game = session['game']
    return jsonify({
        'board': board_to_json(game['board']),
        'turn': game['turn'],
        'game_over': game['game_over'],
        'winner': game['winner'],
        'last_move': game['last_move'],
        'valid_columns': get_valid_locations(game['board'])
    })


@app.route('/api/ai-vs-ai-minimax', methods=['POST'])
def ai_vs_ai_minimax():
    """
    AI vs AI: Minimax hamlesini yapar
    """
    if 'game' not in session:
        session['game'] = create_game_session(PLAYER_AI)
    
    game = session['game']
    board = game['board']
    
    if 'move_count' not in game:
        game['move_count'] = 0
    if 'current_depth' not in game:
        game['current_depth'] = AI_DEPTH_DEFAULT
    
    # Oyun bitmiş mi?
    if game['game_over']:
        return jsonify({'error': 'Game is already over'}), 400
    
    # Minimax hamlesi
    minimax_start = time.time()
    depth = game['current_depth']
    round_count = game['move_count']
    
    if USE_BITBOARD_MINIMAX:
        minimax_col, column_scores = get_best_move_bitboard(
            board, 
            PLAYER_AI, 
            depth=depth,
            developer_mode=True
        )
    else:
        minimax_col, column_scores = get_best_move(
            board, 
            PLAYER_AI, 
            depth=depth,
            developer_mode=True
        )
    
    minimax_time = time.time() - minimax_start
    
    # Minimax hamlesini uygula
    if not is_valid_location(board, minimax_col):
        return jsonify({'error': 'Invalid Minimax move'}), 500
    
    minimax_row = get_next_open_row(board, minimax_col)
    drop_piece(board, minimax_row, minimax_col, PLAYER_AI)
    game['move_count'] += 1
    
    # Kazandı mı?
    if winning_move(board, PLAYER_AI):
        game['game_over'] = True
        game['winner'] = 'minimax'
        session.modified = True
        
        return jsonify({
            'game_over': True,
            'winner': 'minimax',
            'board': board_to_json(board),
            'move': {
                'row': minimax_row,
                'col': minimax_col,
                'thinking_time': round(minimax_time, 3),
                'depth': depth,
                'heuristic': column_scores.get(minimax_col, 0) if column_scores else 0,
                'algorithm': 'Alpha-Beta Pruning'
            }
        })
    
    # Tahta doldu mu?
    if not get_valid_locations(board):
        game['game_over'] = True
        game['winner'] = 'draw'
        session.modified = True
        
        return jsonify({
            'game_over': True,
            'winner': 'draw',
            'board': board_to_json(board),
            'move': {
                'row': minimax_row,
                'col': minimax_col,
                'thinking_time': round(minimax_time, 3),
                'depth': depth,
                'heuristic': column_scores.get(minimax_col, 0) if column_scores else 0,
                'algorithm': 'Alpha-Beta Pruning'
            }
        })
    
    # Depth ayarlama
    new_depth, depth_change_msg = adjust_depth_by_runtime(
        depth, minimax_time, round_count
    )
    game['current_depth'] = new_depth
    session.modified = True
    
    return jsonify({
        'game_over': False,
        'board': board_to_json(board),
        'move': {
            'row': minimax_row,
            'col': minimax_col,
            'thinking_time': round(minimax_time, 3),
            'depth': depth,
            'new_depth': new_depth,
            'heuristic': column_scores.get(minimax_col, 0) if column_scores else 0,
            'algorithm': 'Alpha-Beta Pruning',
            'depth_change_msg': depth_change_msg
        }
    })


@app.route('/api/ai-vs-ai-mcts', methods=['POST'])
def ai_vs_ai_mcts():
    """
    AI vs AI: MCTS hamlesini yapar
    """
    if 'game' not in session:
        return jsonify({'error': 'No active game'}), 400
    
    game = session['game']
    board = game['board']
    
    # Oyun bitmiş mi?
    if game['game_over']:
        return jsonify({'error': 'Game is already over'}), 400
    
    # MCTS hamlesi (V2 - Production Optimized)
    mcts_start = time.time()
    
    mcts_col, mcts_stats = get_best_move_mcts_v2(
        board,
        PLAYER_HUMAN,  # MCTS plays as PLAYER_HUMAN
        iterations=MCTS_ITERATIONS_V2,  # Use V2's higher iteration count
        time_limit=5.0,
        developer_mode=True
    )
    
    mcts_time = time.time() - mcts_start
    
    # MCTS hamlesini uygula
    if not is_valid_location(board, mcts_col):
        return jsonify({'error': 'Invalid MCTS move'}), 500
    
    mcts_row = get_next_open_row(board, mcts_col)
    drop_piece(board, mcts_row, mcts_col, PLAYER_HUMAN)
    game['move_count'] += 1
    
    # Kazandı mı?
    if winning_move(board, PLAYER_HUMAN):
        game['game_over'] = True
        game['winner'] = 'mcts'
        session.modified = True
        
        return jsonify({
            'game_over': True,
            'winner': 'mcts',
            'board': board_to_json(board),
            'move': {
                'row': mcts_row,
                'col': mcts_col,
                'thinking_time': round(mcts_time, 3),
                'iterations': mcts_stats.get('iterations', MCTS_ITERATIONS),
                'exploration_constant': mcts_stats.get('exploration_constant', 0.9),
                'algorithm': 'Monte Carlo Tree Search'
            }
        })
    
    # Tahta doldu mu?
    if not get_valid_locations(board):
        game['game_over'] = True
        game['winner'] = 'draw'
        session.modified = True
    
    session.modified = True
    
    return jsonify({
        'game_over': game['game_over'],
        'winner': game.get('winner'),
        'board': board_to_json(board),
        'move': {
            'row': mcts_row,
            'col': mcts_col,
            'thinking_time': round(mcts_time, 3),
            'iterations': mcts_stats.get('iterations', MCTS_ITERATIONS),
            'exploration_constant': mcts_stats.get('exploration_constant', 0.9),
            'algorithm': 'Monte Carlo Tree Search'
        }
    })


@app.route('/api/ai-vs-ai', methods=['POST'])
def ai_vs_ai_move():
    """
    AI vs AI mod: Bir turda iki hamle yapar
    - Minimax (adaptive depth) hamlesini yapar
    - MCTS (configured iterations) hamlesini yapar
    - Her iki hamlede de stats döndürür
    """
    if 'game' not in session:
        session['game'] = create_game_session(PLAYER_AI)
    
    game = session['game']
    board = game['board']
    
    if 'move_count' not in game:
        game['move_count'] = 0
    if 'current_depth' not in game:
        game['current_depth'] = AI_DEPTH_DEFAULT
    
    # Oyun bitmiş mi?
    if game['game_over']:
        return jsonify({'error': 'Game is already over'}), 400
    
    # HAMLE 1: Minimax (Alpha-Beta)
    minimax_start = time.time()
    depth = game['current_depth']
    round_count = game['move_count']
    
    if USE_BITBOARD_MINIMAX:
        minimax_col, column_scores = get_best_move_bitboard(
            board, 
            PLAYER_AI, 
            depth=depth,
            developer_mode=True
        )
    else:
        minimax_col, column_scores = get_best_move(
            board, 
            PLAYER_AI, 
            depth=depth,
            developer_mode=True
        )
    
    minimax_time = time.time() - minimax_start
    
    # Minimax hamlesini uygula
    if not is_valid_location(board, minimax_col):
        return jsonify({'error': 'Invalid Minimax move'}), 500
    
    minimax_row = get_next_open_row(board, minimax_col)
    drop_piece(board, minimax_row, minimax_col, PLAYER_AI)
    game['move_count'] += 1
    
    # Kazandı mı?
    if winning_move(board, PLAYER_AI):
        game['game_over'] = True
        game['winner'] = 'minimax'
        session.modified = True
        
        return jsonify({
            'game_over': True,
            'winner': 'minimax',
            'board': board_to_json(board),
            'minimax_move': {
                'row': minimax_row,
                'col': minimax_col,
                'thinking_time': round(minimax_time, 3),
                'depth': depth,
                'heuristic': column_scores.get(minimax_col, 0) if column_scores else 0,
                'algorithm': 'Alpha-Beta Pruning'
            },
            'mcts_move': None
        })
    
    # Tahta doldu mu?
    if not get_valid_locations(board):
        game['game_over'] = True
        game['winner'] = 'draw'
        session.modified = True
        
        return jsonify({
            'game_over': True,
            'winner': 'draw',
            'board': board_to_json(board),
            'minimax_move': {
                'row': minimax_row,
                'col': minimax_col,
                'thinking_time': round(minimax_time, 3),
                'depth': depth,
                'heuristic': column_scores.get(minimax_col, 0) if column_scores else 0,
                'algorithm': 'Alpha-Beta Pruning'
            },
            'mcts_move': None
        })
    
    # HAMLE 2: MCTS
    mcts_start = time.time()
    
    mcts_col, mcts_stats = get_best_move_mcts(
        board,
        PLAYER_HUMAN,  # MCTS plays as PLAYER_HUMAN
        iterations=MCTS_ITERATIONS,
        time_limit=5.0,
        developer_mode=True
    )
    
    mcts_time = time.time() - mcts_start
    
    # MCTS hamlesini uygula
    if not is_valid_location(board, mcts_col):
        return jsonify({'error': 'Invalid MCTS move'}), 500
    
    mcts_row = get_next_open_row(board, mcts_col)
    drop_piece(board, mcts_row, mcts_col, PLAYER_HUMAN)
    game['move_count'] += 1
    
    # Kazandı mı?
    if winning_move(board, PLAYER_HUMAN):
        game['game_over'] = True
        game['winner'] = 'mcts'
        session.modified = True
        
        return jsonify({
            'game_over': True,
            'winner': 'mcts',
            'board': board_to_json(board),
            'minimax_move': {
                'row': minimax_row,
                'col': minimax_col,
                'thinking_time': round(minimax_time, 3),
                'depth': depth,
                'heuristic': column_scores.get(minimax_col, 0) if column_scores else 0,
                'algorithm': 'Alpha-Beta Pruning'
            },
            'mcts_move': {
                'row': mcts_row,
                'col': mcts_col,
                'thinking_time': round(mcts_time, 3),
                'iterations': mcts_stats.get('iterations', MCTS_ITERATIONS),
                'exploration_constant': mcts_stats.get('exploration_constant', 0.9),
                'algorithm': 'Monte Carlo Tree Search'
            }
        })
    
    # Depth ayarlama (Minimax için)
    new_depth, depth_change_msg = adjust_depth_by_runtime(
        depth, minimax_time, round_count
    )
    game['current_depth'] = new_depth
    
    # Tahta tekrar doldu mu?
    if not get_valid_locations(board):
        game['game_over'] = True
        game['winner'] = 'draw'
    
    session.modified = True
    
    return jsonify({
        'game_over': game['game_over'],
        'winner': game.get('winner'),
        'board': board_to_json(board),
        'minimax_move': {
            'row': minimax_row,
            'col': minimax_col,
            'thinking_time': round(minimax_time, 3),
            'depth': depth,
            'new_depth': new_depth,
            'heuristic': column_scores.get(minimax_col, 0) if column_scores else 0,
            'algorithm': 'Alpha-Beta Pruning',
            'depth_change_msg': depth_change_msg
        },
        'mcts_move': {
            'row': mcts_row,
            'col': mcts_col,
            'thinking_time': round(mcts_time, 3),
            'iterations': mcts_stats.get('iterations', MCTS_ITERATIONS),
            'exploration_constant': mcts_stats.get('exploration_constant', 0.9),
            'algorithm': 'Monte Carlo Tree Search'
        }
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)