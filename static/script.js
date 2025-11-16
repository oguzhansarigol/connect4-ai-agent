// Connect4 AI Agent - JavaScript

class Connect4Game {
    constructor() {
        this.board = null;
        this.turn = null;
        this.gameOver = false;
        this.winner = null;
        this.moveCount = 0;
        this.aiThinkingTime = 0;
        
        this.initializeElements();
        this.bindEvents();
        this.loadGameState();
    }
    
    initializeElements() {
        this.statusElement = document.getElementById('game-status');
        this.boardElement = document.getElementById('board');
        this.columnButtonsElement = document.getElementById('column-buttons');
        this.resetBtn = document.getElementById('reset-btn');
        this.hintBtn = document.getElementById('hint-btn');
        this.moveCountElement = document.getElementById('move-count');
        this.aiTimeElement = document.getElementById('ai-time');
        this.modal = document.getElementById('modal-overlay');
        this.modalTitle = document.getElementById('modal-title');
        this.modalMessage = document.getElementById('modal-message');
        this.modalNewGameBtn = document.getElementById('modal-new-game');
        this.modalCloseBtn = document.getElementById('modal-close');
    }
    
    bindEvents() {
        this.resetBtn.addEventListener('click', () => this.resetGame());
        this.hintBtn.addEventListener('click', () => this.showHint());
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
                this.statusElement.textContent = '🎉 Tebrikler! Kazandınız!';
                this.statusElement.style.color = '#27ae60';
            } else if (this.winner === 1) {
                this.statusElement.textContent = '🤖 AI Kazandı!';
                this.statusElement.style.color = '#e74c3c';
            } else {
                this.statusElement.textContent = '🤝 Berabere!';
                this.statusElement.style.color = '#f39c12';
            }
        } else {
            if (this.turn === -1) {
                this.statusElement.textContent = '🔴 Sizin sıranız';
                this.statusElement.style.color = '#e74c3c';
            } else {
                this.statusElement.innerHTML = '🟡 AI düşünüyor... <span class="loading"></span>';
                this.statusElement.style.color = '#f39c12';
            }
        }
    }
    
    updateMoveCount() {
        this.moveCountElement.textContent = this.moveCount;
    }
    
    async makeMove(col) {
        if (this.gameOver || this.turn !== -1) return;
        
        const startTime = Date.now();
        this.disableColumnButtons();
        this.updateStatus();
        
        try {
            const response = await fetch('/api/move', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ column: col })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Hamle yapılırken hata oluştu');
            }
            
            this.moveCount++;
            this.updateGameState(data);
            
            // AI düşünme süresini hesapla
            if (data.ai_move) {
                const endTime = Date.now();
                this.aiThinkingTime = ((endTime - startTime) / 1000).toFixed(1);
                this.aiTimeElement.textContent = `${this.aiThinkingTime}s`;
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
        try {
            const response = await fetch('/api/reset', { method: 'POST' });
            const data = await response.json();
            
            this.moveCount = 0;
            this.aiThinkingTime = 0;
            this.aiTimeElement.textContent = '-';
            this.updateGameState(data);
            this.hideModal();
            
        } catch (error) {
            console.error('Oyun sıfırlanırken hata:', error);
            alert('Oyun sıfırlanırken hata oluştu!');
        }
    }
    
    showHint() {
        // Bu özellik gelecekte AI'ın önerdiği hamleyi gösterebilir
        alert('İpucu özelliği henüz geliştirilmedi!');
    }
    
    showGameOverModal() {
        if (this.winner === -1) {
            this.modalTitle.textContent = '🎉 Tebrikler!';
            this.modalMessage.textContent = 'Harika oynadınız ve AI\'ı yendiniz!';
        } else if (this.winner === 1) {
            this.modalTitle.textContent = '🤖 AI Kazandı';
            this.modalMessage.textContent = 'Bu sefer AI daha iyiydi. Tekrar deneyin!';
        } else {
            this.modalTitle.textContent = '🤝 Berabere';
            this.modalMessage.textContent = 'İyi mücadele! İkiniz de harika oynadınız.';
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