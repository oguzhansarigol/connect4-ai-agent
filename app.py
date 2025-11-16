from flask import Flask, render_template, request, jsonify, session
import random
from connect4.game import (
    create_board, drop_piece, is_valid_location,
    get_next_open_row, winning_move, get_valid_locations,
    PLAYER_HUMAN, PLAYER_AI, COLS, ROWS
)
from connect4.agent import get_best_move

app = Flask(__name__)
app.secret_key = 'connect4-secret-key'  # Session için gerekli

# AI derinliği
AI_DEPTH = 8

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
        'last_move': None
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
    depth = int(data.get('depth', AI_DEPTH))  # Depth parametresini al
    
    if 'game' not in session:
        session['game'] = create_game_session()
    
    game = session['game']
    board = game['board']
    
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
    
    response_data = {
        'board': board_to_json(game['board']),
        'turn': game['turn'],
        'game_over': game['game_over'],
        'winner': game['winner'],
        'last_move': game['last_move'],
        'valid_columns': get_valid_locations(game['board'])
    }
    
    # Eğer AI'ın sırası geldiyse ve oyun bitmeмиşse AI hamlesini yap
    if game['turn'] == PLAYER_AI and not game['game_over']:
        ai_col = get_best_move(board, PLAYER_AI, depth)
        ai_row = get_next_open_row(board, ai_col)
        drop_piece(board, ai_row, ai_col, PLAYER_AI)
        game['last_move'] = {'player': PLAYER_AI, 'row': ai_row, 'col': ai_col}
        
        # AI kazanma kontrolü
        if winning_move(board, PLAYER_AI):
            game['game_over'] = True
            game['winner'] = PLAYER_AI
        elif len(get_valid_locations(board)) == 0:
            game['game_over'] = True
            game['winner'] = None  # Beraberlik
        else:
            game['turn'] = PLAYER_HUMAN
        
        session['game'] = game
        session.modified = True
        
        response_data = {
            'board': board_to_json(game['board']),
            'turn': game['turn'],
            'game_over': game['game_over'],
            'winner': game['winner'],
            'last_move': game['last_move'],
            'valid_columns': get_valid_locations(game['board']),
            'ai_move': {'row': ai_row, 'col': ai_col}
        }
    
    return jsonify(response_data)

@app.route('/api/ai-move', methods=['POST'])
def make_ai_move():
    """AI hamlesini yapar"""
    if 'game' not in session:
        return jsonify({'error': 'Oyun oturumu bulunamadı'}), 400
    
    data = request.get_json() or {}
    depth = int(data.get('depth', AI_DEPTH))  # Depth parametresini al
    
    game = session['game']
    board = game['board']
    
    if game['game_over'] or game['turn'] != PLAYER_AI:
        return jsonify({'error': 'AI hamle yapamaz'}), 400
    
    # AI hamlesini yap
    ai_col = get_best_move(board, PLAYER_AI, depth)
    ai_row = get_next_open_row(board, ai_col)
    drop_piece(board, ai_row, ai_col, PLAYER_AI)
    game['last_move'] = {'player': PLAYER_AI, 'row': ai_row, 'col': ai_col}
    
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
    
    return jsonify({
        'board': board_to_json(game['board']),
        'turn': game['turn'],
        'game_over': game['game_over'],
        'winner': game['winner'],
        'last_move': game['last_move'],
        'valid_columns': get_valid_locations(game['board']),
        'ai_move': {'row': ai_row, 'col': ai_col}
    })

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
    
    session['game'] = create_game_session(first_player)
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)