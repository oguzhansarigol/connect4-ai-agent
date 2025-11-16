// Connect4 AI Agent - JavaScript

class Connect4Game {
    constructor() {
        this.board = null;
        this.turn = null;
        this.gameOver = false;
        this.winner = null;
        this.moveCount = 0;
        this.aiDepth = 8; // Default depth
        this.devMode = false;
        
        this.initializeElements();
        this.bindEvents();
        this.loadGameState();
    }
    
    initializeElements() {
        this.statusElement = document.getElementById('game-status');
        this.boardElement = document.getElementById('board');
        this.columnButtonsElement = document.getElementById('column-buttons');
        this.resetBtn = document.getElementById('reset-btn');
        this.startHumanBtn = document.getElementById('start-human');
        this.startAiBtn = document.getElementById('start-ai');
        this.startRandomBtn = document.getElementById('start-random');
        this.moveCountElement = document.getElementById('move-count');
        this.devModeToggle = document.getElementById('dev-mode-toggle');
        this.devSettings = document.getElementById('dev-settings');
        this.depthSlider = document.getElementById('depth-slider');
        this.depthValue = document.getElementById('depth-value');
        this.modal = document.getElementById('modal-overlay');
        this.modalTitle = document.getElementById('modal-title');
        this.modalMessage = document.getElementById('modal-message');
        this.modalNewGameBtn = document.getElementById('modal-new-game');
        this.modalCloseBtn = document.getElementById('modal-close');
    }
    
    bindEvents() {
        this.resetBtn.addEventListener('click', () => this.resetGame());
        this.startHumanBtn.addEventListener('click', () => this.startNewGame('human'));
        this.startAiBtn.addEventListener('click', () => this.startNewGame('ai'));
        this.startRandomBtn.addEventListener('click', () => this.startNewGame('random'));
        this.devModeToggle.addEventListener('change', (e) => this.toggleDevMode(e.target.checked));
        this.depthSlider.addEventListener('input', (e) => this.updateDepth(e.target.value));
        this.modalNewGameBtn.addEventListener('click', () => this.newGameFromModal());
        this.modalCloseBtn.addEventListener('click', () => this.hideModal());
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) this.hideModal();
        });
    }
    
    async loadGameState() {
        try {
            const response = await fetch('/api/game');
            const data = await response.json();
            this.updateGameState(data);
        } catch (error) {
            console.error('Oyun durumu yüklenirken hata:', error);
            this.statusElement.textContent = 'Bağlantı hatası!';
        }
    }
    
    updateGameState(data) {
        this.board = data.board;
        this.turn = data.turn;
        this.gameOver = data.game_over;
        this.winner = data.winner;
        
        this.createBoard();
        this.createColumnButtons(data.valid_columns);
        this.updateStatus();
        this.updateMoveCount();
        
        if (this.gameOver) {
            this.showGameOverModal();
        } else if (this.turn === 1) {
            // AI'ın sırası geldiyse otomatik hamle yap
            setTimeout(() => this.makeAIMove(), 500);
        }
    }
    
    createBoard() {
        this.boardElement.innerHTML = '';
        
        // Tahtayı ters sırada oluştur (üstten alta)
        for (let row = 5; row >= 0; row--) {
            for (let col = 0; col < 7; col++) {
                const cell = document.createElement('div');
                cell.className = 'cell';
                cell.dataset.row = row;
                cell.dataset.col = col;
                
                const value = this.board[row][col];
                if (value === 1) {
                    cell.classList.add('ai');
                } else if (value === -1) {
                    cell.classList.add('human');
                } else {
                    cell.classList.add('empty');
                }
                
                // Hücreye tıklama event'i ekle
                cell.addEventListener('click', () => {
                    if (!this.gameOver && this.turn === -1) {
                        this.makeMove(col);
                    }
                });
                
                // Hover efekti için cursor ekle
                if (!this.gameOver && this.turn === -1) {
                    cell.style.cursor = 'pointer';
                }
                
                this.boardElement.appendChild(cell);
            }
        }
    }
    
    createColumnButtons(validColumns) {
        this.columnButtonsElement.innerHTML = '';
        
        for (let col = 0; col < 7; col++) {
            const button = document.createElement('button');
            button.className = 'column-btn';
            button.textContent = col + 1;
            button.dataset.col = col;
            
            if (!validColumns.includes(col) || this.gameOver || this.turn !== -1) {
                button.disabled = true;
            }
            
            button.addEventListener('click', () => this.makeMove(col));
            this.columnButtonsElement.appendChild(button);
        }
    }
    
    updateStatus() {
        if (this.gameOver) {
            if (this.winner === -1) {
                this.statusElement.textContent = '🎉 Congratulations! You won!';
                this.statusElement.style.color = '#27ae60';
            } else if (this.winner === 1) {
                this.statusElement.textContent = '🤖 AI Won!';
                this.statusElement.style.color = '#e74c3c';
            } else {
                this.statusElement.textContent = '🤝 Draw!';
                this.statusElement.style.color = '#f39c12';
            }
        } else {
            if (this.turn === -1) {
                this.statusElement.textContent = '🔴 Your turn';
                this.statusElement.style.color = '#e74c3c';
            } else {
                this.statusElement.innerHTML = '🟡 AI is thinking... <span class="loading"></span>';
                this.statusElement.style.color = '#f39c12';
            }
        }
    }
    
    toggleDevMode(enabled) {
        this.devMode = enabled;
        if (enabled) {
            this.devSettings.classList.add('active');
        } else {
            this.devSettings.classList.remove('active');
        }
    }
    
    updateDepth(value) {
        this.aiDepth = parseInt(value);
        this.depthValue.textContent = value;
    }
    
    updateMoveCount() {
        this.moveCountElement.textContent = this.moveCount;
    }
    
    async makeMove(col) {
        if (this.gameOver || this.turn !== -1) return;
        
        this.disableColumnButtons();
        this.updateStatus();
        
        try {
            // 1. Önce kullanıcı hamlesini yap
            const response = await fetch('/api/move', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    column: col,
                    depth: this.aiDepth,
                    developer_mode: this.devMode
                })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Hamle yapılırken hata oluştu');
            }
            
            this.moveCount++;
            
            // 2. Kullanıcı hamlesini HEMEN ekrana yansıt
            this.updateGameState(data);
            
            // 3. Eğer AI'ın sırası geldiyse, kısa bir gecikme sonrası AI hamlesini tetikle
            if (data.turn === 1 && !data.game_over) {
                // Kullanıcı hamlesinin görünmesi için 300ms bekle
                setTimeout(() => this.makeAIMove(), 300);
            }
            
        } catch (error) {
            console.error('Hamle yapılırken hata:', error);
            alert('Hamle yapılırken hata oluştu: ' + error.message);
        }
    }
    
    disableColumnButtons() {
        const buttons = this.columnButtonsElement.querySelectorAll('.column-btn');
        buttons.forEach(button => button.disabled = true);
    }
    
    async resetGame() {
        // Rastgele bir başlangıç oyuncusu seç
        await this.startNewGame('random');
    }
    
    async startNewGame(firstPlayer) {
        try {
            const response = await fetch('/api/reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ first_player: firstPlayer })
            });
            const data = await response.json();
            
            this.moveCount = 0;
            this.updateGameState(data);
            this.hideModal();
            
        } catch (error) {
            console.error('Yeni oyun başlatılırken hata:', error);
            alert('Yeni oyun başlatılırken hata oluştu!');
        }
    }
    
    async makeAIMove() {
        if (this.gameOver || this.turn !== 1) return;
        
        this.disableColumnButtons();
        this.updateStatus();
        
        try {
            const startTime = performance.now();
            
            const response = await fetch('/api/ai-move', { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    depth: this.aiDepth,
                    developer_mode: this.devMode
                })
            });
            const data = await response.json();
            
            const thinkingTime = ((performance.now() - startTime) / 1000).toFixed(3);
            
            if (!response.ok) {
                throw new Error(data.error || 'AI hamle yapılırken hata oluştu');
            }
            
            this.moveCount++;
            
            // Developer mode ise skorları göster
            if (this.devMode && data.ai_move) {
                const aiScores = data.ai_move.column_scores || null;
                const aiTime = data.ai_move.thinking_time || null;
                if (aiScores) {
                    this.showColumnScores(aiScores, data.ai_move.col, aiTime);
                }
            }
            
            this.updateGameState(data);
            
        } catch (error) {
            console.error('AI hamle yapılırken hata:', error);
            alert('AI hamle yapılırken hata oluştu: ' + error.message);
        }
    }
    
    showGameOverModal() {
        if (this.winner === -1) {
            this.modalTitle.textContent = '🎉 Congratulations!';
            this.modalMessage.textContent = 'Great game! You beat the AI!';
        } else if (this.winner === 1) {
            this.modalTitle.textContent = '🤖 AI Won';
            this.modalMessage.textContent = 'AI was better this time. Try again!';
        } else {
            this.modalTitle.textContent = '🤝 Draw';
            this.modalMessage.textContent = 'Good fight! You both played great.';
        }
        
        this.modal.classList.add('show');
    }
    
    hideModal() {
        this.modal.classList.remove('show');
    }
    
    newGameFromModal() {
        this.resetGame();
    }
    
    showColumnScores(columnScores, bestCol, thinkingTime = null) {
        // Skor panelini oluştur veya güncelle
        let scorePanel = document.getElementById('score-panel');
        if (!scorePanel) {
            scorePanel = document.createElement('div');
            scorePanel.id = 'score-panel';
            scorePanel.className = 'score-panel';
            document.querySelector('.container').appendChild(scorePanel);
        }
        
        // En yüksek ve en düşük skorları bul (normalizasyon için)
        const scores = Object.values(columnScores).map(v => parseFloat(v));
        const maxScore = Math.max(...scores);
        const minScore = Math.min(...scores);
        const scoreRange = maxScore - minScore || 1;
        
        let html = '<div class="score-header">🔍 AI Decision Process</div>';
        html += '<div class="score-subtitle">Column Evaluations (Minimax Scores)</div>';
        
        // AI düşünme süresini göster
        if (thinkingTime !== null) {
            html += `<div class="thinking-time">⏱️ Thinking Time: ${thinkingTime}s</div>`;
        }
        
        html += '<div class="scores-container">';
        
        for (let col = 0; col < 7; col++) {
            const score = columnScores[col];
            const isBest = col == bestCol;
            const isValid = score !== undefined && score !== null;
            
            if (isValid) {
                // Normalize score for bar visualization (0-100)
                const normalizedScore = ((parseFloat(score) - minScore) / scoreRange) * 100;
                const barWidth = Math.max(5, normalizedScore);
                
                // Color based on score
                let barColor = '#3498db'; // Default blue
                if (parseFloat(score) > 50) barColor = '#2ecc71'; // High score = green
                else if (parseFloat(score) < -50) barColor = '#e74c3c'; // Low score = red
                else if (parseFloat(score) > 0) barColor = '#95a5a6'; // Positive = gray
                
                if (isBest) barColor = '#f39c12'; // Best = orange
                
                html += `
                    <div class="score-row ${isBest ? 'best-score' : ''}">
                        <div class="score-label">Column ${col + 1}:</div>
                        <div class="score-bar-container">
                            <div class="score-bar" style="width: ${barWidth}%; background: ${barColor}"></div>
                        </div>
                        <div class="score-value">${parseFloat(score).toFixed(2)}</div>
                        ${isBest ? '<div class="best-badge">⭐ BEST</div>' : ''}
                    </div>
                `;
            } else {
                html += `
                    <div class="score-row disabled">
                        <div class="score-label">Column ${col + 1}:</div>
                        <div class="score-bar-container">
                            <div class="score-bar" style="width: 0%; background: #bdc3c7"></div>
                        </div>
                        <div class="score-value">FULL</div>
                    </div>
                `;
            }
        }
        
        html += '</div>';
        html += '<div class="score-legend">';
        html += '<span>💡 Higher = Better for AI</span> | ';
        html += '<span>🎯 Negative = Risky</span>';
        html += '</div>';
        
        scorePanel.innerHTML = html;
        scorePanel.classList.add('show');
        
        // Panel açık kalsın, kapanmasın
    }
}

// Sayfa yüklendiğinde oyunu başlat
document.addEventListener('DOMContentLoaded', () => {
    new Connect4Game();
});

// Klavye kısayolları
document.addEventListener('keydown', (e) => {
    // R tuşu ile yeni oyun
    if (e.key === 'r' || e.key === 'R') {
        document.getElementById('reset-btn').click();
    }
    
    // 1-7 tuşları ile sütun seçimi
    const colNum = parseInt(e.key);
    if (colNum >= 1 && colNum <= 7) {
        const colBtn = document.querySelector(`[data-col="${colNum - 1}"]`);
        if (colBtn && !colBtn.disabled) {
            colBtn.click();
        }
    }
    
    // ESC tuşu ile modal kapatma
    if (e.key === 'Escape') {
        document.getElementById('modal-close').click();
    }
});