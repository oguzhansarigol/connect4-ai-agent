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
            const response = await fetch('/api/move', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    column: col,
                    depth: this.aiDepth 
                })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Hamle yapılırken hata oluştu');
            }
            
            this.moveCount++;
            this.updateGameState(data);
            
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
            const response = await fetch('/api/ai-move', { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ depth: this.aiDepth })
            });
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'AI hamle yapılırken hata oluştu');
            }
            
            this.moveCount++;
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