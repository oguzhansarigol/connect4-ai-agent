// Connect4 AI Agent - JavaScript

class Connect4Game {
    constructor() {
        this.board = null;
        this.turn = null;
        this.gameOver = false;
        this.winner = null;
        this.moveCount = 0;
        this.aiDepth = 6; // Default depth - SABIT (kullanıcı değiştiremiyor)
        this.devMode = false;
        this.lastMove = null; // Son oynanan hamle
        this.bitboardEnabled = false; // Bitboard state - backend'den güncellenecek
        
        this.initializeElements();
        this.bindEvents();
        this.loadGameState();
        this.updateDepthDisplay(); // Depth'i UI'da göster
        this.syncBitboardState(); // Bitboard state'i backend'den al
    }
    
    initializeElements() {
        this.statusElement = document.getElementById('game-status');
        this.boardElement = document.getElementById('board');
        this.columnButtonsElement = document.getElementById('column-buttons');
        this.resetBtn = document.getElementById('reset-btn');
        this.startHumanBtn = document.getElementById('start-human');
        this.startAiBtn = document.getElementById('start-ai');
        this.startRandomBtn = document.getElementById('start-random');
        this.aiVsAiBtn = document.getElementById('ai-vs-ai-btn');
        this.moveCountElement = document.getElementById('move-count');
        this.devModeToggle = document.getElementById('dev-mode-toggle');
        this.devSettings = document.getElementById('dev-settings');
        this.depthValue = document.getElementById('depth-value');
        this.depthSection = document.getElementById('depth-section');
        this.modal = document.getElementById('modal-overlay');
        this.modalTitle = document.getElementById('modal-title');
        this.modalMessage = document.getElementById('modal-message');
        this.modalNewGameBtn = document.getElementById('modal-new-game');
        this.modalCloseBtn = document.getElementById('modal-close');
        
        // AI Battle Panel elements (sağ tarafta sabit panel)
        this.battlePanel = document.getElementById('ai-battle-panel');
        this.closeBattleBtn = document.getElementById('close-battle');
        this.continueBattleBtn = document.getElementById('continue-battle');
        this.isAiVsAiMode = false;
        
        // Bitboard toggle elements
        this.bitboardToggle = document.getElementById('bitboard-toggle');
        this.bitboardToggleSection = document.getElementById('bitboard-toggle-section');
    }
    
    bindEvents() {
        this.resetBtn.addEventListener('click', () => this.resetGame());
        this.startHumanBtn.addEventListener('click', () => this.startNewGame('human'));
        this.startAiBtn.addEventListener('click', () => this.startNewGame('ai'));
        this.startRandomBtn.addEventListener('click', () => this.startNewGame('random'));
        this.aiVsAiBtn.addEventListener('click', () => this.startAiVsAi());
        this.devModeToggle.addEventListener('change', (e) => this.toggleDevMode(e.target.checked));
        this.modalNewGameBtn.addEventListener('click', () => this.newGameFromModal());
        this.modalCloseBtn.addEventListener('click', () => this.hideModal());
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) this.hideModal();
        });
        
        // Battle panel events
        this.closeBattleBtn.addEventListener('click', () => this.hideBattlePanel());
        this.continueBattleBtn.addEventListener('click', () => this.continueAiBattle());
        
        // Bitboard toggle event
        if (this.bitboardToggle) {
            this.bitboardToggle.addEventListener('change', (e) => this.toggleBitboard(e.target.checked));
        }
    }
    
    updateDepthDisplay() {
        // UI'da depth değerini güncelle
        if (this.depthValue) {
            this.depthValue.textContent = this.aiDepth;
        }
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
        
        // Sync move count from backend - SADECE AI vs AI modunda DEĞİL
        if (data.move_count !== undefined && !this.isAiVsAiMode) {
            this.moveCount = data.move_count;
        }
        this.lastMove = data.last_move;  // Son hamleyi kaydet
        
        this.createBoard();
        this.createColumnButtons(data.valid_columns);
        this.updateStatus();
        this.updateMoveCount();
        
        if (this.gameOver) {
            this.showGameOverModal();
        } else if (this.turn === 1 && !this.isAiVsAiMode) {
            // AI'ın sırası geldiyse otomatik hamle yap (AI vs AI modunda değilse)
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
                
                // Son hamleyi işaretle (yeşil çember)
                if (this.lastMove && this.lastMove.row === row && this.lastMove.col === col) {
                    cell.classList.add('last-move');
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
        
        // AI Search Depth görünürlüğünü kontrol et
        if (this.depthSection) {
            if (enabled) {
                this.depthSection.style.display = 'flex';
            } else {
                this.depthSection.style.display = 'none';
            }
        }
        
        // Bitboard Toggle görünürlüğünü kontrol et
        if (this.bitboardToggleSection) {
            if (enabled) {
                this.bitboardToggleSection.style.display = 'block';
            } else {
                this.bitboardToggleSection.style.display = 'none';
            }
        }
        
        // AI Decision Panel görünürlüğünü kontrol et
        const aiDecisionPanel = document.getElementById('ai-decision-panel');
        if (aiDecisionPanel) {
            if (!enabled) {
                // Developer mode kapandıysa paneli gizle ve temizle
                aiDecisionPanel.classList.remove('visible');
                aiDecisionPanel.innerHTML = '';
            }
            // Developer mode açıldığında eğer panelde içerik varsa göster
            else if (aiDecisionPanel.innerHTML.trim() !== '') {
                aiDecisionPanel.classList.add('visible');
            }
        }
        
        // Game Theory Panel görünürlüğünü kontrol et
        const gameTheoryPanel = document.getElementById('game-theory-panel');
        if (gameTheoryPanel) {
            if (!enabled) {
                gameTheoryPanel.classList.remove('visible');
                gameTheoryPanel.innerHTML = '';
            }
            else if (gameTheoryPanel.innerHTML.trim() !== '') {
                gameTheoryPanel.classList.add('visible');
            }
        }
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
            
            // 2. Kullanıcı hamlesini HEMEN ekrana yansıt
            this.updateGameState(data);
            
            // Update Game Theory panel if in developer mode
            if (this.devMode) {
                this.updateGameTheoryPanel();
            }
            
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
        // Depth'i varsayılan değere resetle
        this.aiDepth = 6;
        this.updateDepthDisplay();
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
            
            // I Start veya AI Start'a basıldığında da depth'i 6'ya resetle
            this.aiDepth = 6;
            this.updateDepthDisplay();
            
        } catch (error) {
            console.error('Yeni oyun başlatılırken hata:', error);
            alert('Yeni oyun başlatılırken hata oluştu!');
        }
    }
    
    async makeAIMove() {
        if (this.gameOver || this.turn !== 1) return;
        
        // Store current turn BEFORE AI move for Game Theory display
        this.turnBeforeAIMove = this.turn;
        
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
            
            // Backend'den depth bilgisi gelirse güncelle (dinamik depth yönetimi)
            if (data.ai_move && data.ai_move.depth !== undefined) {
                const previousDepth = this.aiDepth;
                this.aiDepth = data.ai_move.depth;
                this.updateDepthDisplay();
                
                // Depth değişimini kullanıcıya göster
                if (data.ai_move.depth_changed && data.ai_move.depth_change_msg) {
                    this.showDepthChangeNotification(
                        data.ai_move.previous_depth, 
                        data.ai_move.depth,
                        data.ai_move.depth_change_msg
                    );
                }
            }
            
            // Update game state FIRST to get correct gameOver/winner status
            this.updateGameState(data);
            
            // THEN show scores with updated state
            if (this.devMode && data.ai_move) {
                const aiScores = data.ai_move.column_scores || null;
                const aiTime = data.ai_move.thinking_time || null;
                if (aiScores) {
                    this.showColumnScores(aiScores, data.ai_move.col, aiTime);
                }
            }
            
        } catch (error) {
            console.error('AI hamle yapılırken hata:', error);
            alert('AI hamle yapılırken hata oluştu: ' + error.message);
        }
    }
    
    showDepthChangeNotification(oldDepth, newDepth, message) {
        // Depth değişim bildirimini göster
        const depthBadge = document.querySelector('.depth-value-badge');
        if (!depthBadge) return;
        
        // Animasyon için class ekle
        depthBadge.classList.add('depth-changing');
        
        // Konsola bilgi ver
        console.log(`🔄 Depth Change: ${oldDepth} → ${newDepth} (${message})`);
        
        // Kısa bir süre sonra animasyonu kaldır
        setTimeout(() => {
            depthBadge.classList.remove('depth-changing');
        }, 1500);
        
        // Toast notification göster (opsiyonel)
        this.showToast(`AI Depth: ${oldDepth} → ${newDepth}`, message);
    }
    
    showToast(title, message) {
        // Basit toast notification
        const existingToast = document.querySelector('.depth-toast');
        if (existingToast) {
            existingToast.remove();
        }
        
        const toast = document.createElement('div');
        toast.className = 'depth-toast';
        toast.innerHTML = `
            <div class="toast-title">${title}</div>
            <div class="toast-message">${message}</div>
        `;
        document.body.appendChild(toast);
        
        // 3 saniye sonra kaldır
        setTimeout(() => {
            toast.classList.add('fade-out');
            setTimeout(() => toast.remove(), 500);
        }, 3000);
    }
    
    showGameOverModal() {
        // AI vs AI mode için string winner kontrolü
        if (this.winner === 'minimax') {
            this.modalTitle.textContent = '🧠 Minimax Won!';
            this.modalMessage.textContent = 'Alpha-Beta Pruning dominated this match!';
        } else if (this.winner === 'mcts') {
            this.modalTitle.textContent = '🎲 MCTS Won!';
            this.modalMessage.textContent = 'Monte Carlo Tree Search found the winning path!';
        } else if (this.winner === -1) {
            this.modalTitle.textContent = '🎉 Congratulations!';
            this.modalMessage.textContent = 'Great game! You beat the AI!';
        } else if (this.winner === 1) {
            this.modalTitle.textContent = '🤖 AI Won';
            this.modalMessage.textContent = 'AI was better this time. Try again!';
        } else if (this.winner === 'draw') {
            this.modalTitle.textContent = '🤝 Draw';
            this.modalMessage.textContent = 'Good fight! Both algorithms played well.';
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
    
    updateGameTheoryPanel() {
        // Update Game Theory panel with current game state
        if (!this.devMode) return;
        
        let gameTheoryPanel = document.getElementById('game-theory-panel');
        if (!gameTheoryPanel) return;
        
        // Calculate valid columns from current board
        const validCols = [];
        for (let col = 0; col < 7; col++) {
            // Check if column is not full
            if (this.board[5][col] === 0) {
                validCols.push(col + 1);
            }
        }
        const actionsStr = validCols.length > 0 ? validCols.join(', ') : 'None';
        
        // TO-MOVE: Show NEXT player (who will move)
        // Backend: PLAYER_AI=1, PLAYER_HUMAN=-1
        const nextPlayer = this.turn === 1 ? 'AI (Yellow)' : 'Human (Red)';
        
        // IS-TERMINAL: Current game state
        let terminalStatus;
        if (this.gameOver) {
            if (this.winner === 1) {
                terminalStatus = '✅ YES - AI Victory (+1000 utility)';
            } else if (this.winner === -1) {
                terminalStatus = '✅ YES - Human Victory (-1000 utility)';
            } else {
                terminalStatus = '✅ YES - Draw (0 utility)';
            }
        } else {
            terminalStatus = '❌ NO - Game continues, next: ' + nextPlayer;
        }
        
        let theoryHtml = '';
        theoryHtml += '<div class="game-theory-header">📚 Game Theory Model</div>';
        theoryHtml += '<div class="game-theory-content">';
        theoryHtml += '<ul class="theory-list">';
        theoryHtml += '<li><strong>S₀:</strong> Initial state (empty 6×7 board)</li>';
        theoryHtml += `<li><strong>TO-MOVE(s):</strong> ${nextPlayer}</li>`;
        theoryHtml += `<li><strong>ACTIONS(s):</strong> Valid columns: {${actionsStr}}</li>`;
        theoryHtml += `<li><strong>RESULT(s,a):</strong> Drop disc in column a → New state s'</li>`;
        theoryHtml += `<li><strong>IS-TERMINAL(s):</strong> ${terminalStatus}</li>`;
        theoryHtml += '<li><strong>UTILITY(s,p):</strong> +1000 (AI win), -1000 (Human win), 0 (draw)</li>';
        theoryHtml += '</ul>';
        theoryHtml += '</div>';
        
        gameTheoryPanel.innerHTML = theoryHtml;
        gameTheoryPanel.classList.add('visible');
    }

    showColumnScores(columnScores, bestCol, thinkingTime = null) {
        // Sadece Developer Mode aktifse göster
        if (!this.devMode) {
            return;
        }
        
        // Update Game Theory Panel first
        this.updateGameTheoryPanel();
        
        // ============================================================
        // AI DECISION PROCESS PANEL (Sağda - Skor + Optimizasyonlar)
        // ============================================================
        let scorePanel = document.getElementById('ai-decision-panel');
        if (!scorePanel) {
            return;
        }
        
        // En yüksek ve en düşük skorları bul (normalizasyon için)
        const scores = Object.values(columnScores).map(v => parseFloat(v));
        const maxScore = Math.max(...scores);
        const minScore = Math.min(...scores);
        const scoreRange = maxScore - minScore || 1;
        
        let html = '';
        
        // DECISION PROCESS SECTION (Column Scores)
        html += '<div class="score-header">🔍 Decision Process</div>';
        html += '<div class="score-subtitle">Column Evaluations (Minimax Scores)</div>';
        
        // AI düşünme süresi ve bitboard status - HER ZAMAN GÖSTER
        const bitboardStatus = this.bitboardEnabled ? '✅ BITBOARD' : '⚪ 2D Array';
        const timeDisplay = thinkingTime !== null ? `⏱️ ${thinkingTime}s | ` : '';
        html += `<div class="thinking-time">${timeDisplay}Depth: ${this.aiDepth} | ${bitboardStatus}</div>`;
        
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
        
        // AI OPTIMIZATIONS SECTION (Decision Process'in altında)
        html += '<div class="optimizations-section">';
        html += '<div class="optimizations-header">🚀 AI Optimizations</div>';
        html += '<div class="optimizations-grid">';
        html += '<div class="opt-item"><span class="opt-check">✓</span> Alpha-Beta Pruning</div>';
        html += '<div class="opt-item"><span class="opt-check">✓</span> Move Ordering</div>';
        html += '<div class="opt-item"><span class="opt-check">✓</span> Transposition Table</div>';
        html += '<div class="opt-item"><span class="opt-check">✓</span> Threat Detection</div>';
        html += '<div class="opt-item"><span class="opt-check">✓</span> Killer Moves</div>';
        html += '<div class="opt-item"><span class="opt-check">✓</span> Center Column Bonus</div>';
        html += '<div class="opt-item"><span class="opt-check">✓</span> Window Evaluation</div>';
        html += '</div>';
        html += '</div>';
        
        scorePanel.innerHTML = html;
        scorePanel.classList.add('visible');
        
        // Panel açık kalsın, kapanmasın
    }
    
    // ========================================================================
    // AI vs AI Mode Functions
    // ========================================================================
    
    async startAiVsAi() {
        // Reset game and enter AI vs AI mode
        // AI vs AI modunda her zaman Minimax (PLAYER_AI) başlar
        await this.startNewGame('ai'); // AI (Minimax) başlasın
        
        // Move count'u sıfırla (startNewGame backend'den gelen değeri set eder)
        this.moveCount = 0;
        this.updateMoveCount();
        
        this.isAiVsAiMode = true;
        this.statusElement.textContent = '⚔️ AI vs AI Battle Mode';
        
        // Disable column buttons
        const buttons = this.columnButtonsElement.querySelectorAll('button');
        buttons.forEach(btn => btn.disabled = true);
        
        // Make first AI vs AI move
        setTimeout(() => this.makeAiVsAiMove(), 1000);
    }
    
    async makeAiVsAiMove() {
        if (this.gameOver || !this.isAiVsAiMode) return;
        
        try {
            // Step 1: Minimax plays
            this.statusElement.textContent = '🧠 Minimax is playing...';
            
            const minimaxResponse = await fetch('/api/ai-vs-ai-minimax', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const minimaxData = await minimaxResponse.json();
            
            if (!minimaxResponse.ok) {
                console.error('Minimax move error:', minimaxData.error);
                this.isAiVsAiMode = false;
                return;
            }
            
            // Update board with Minimax move
            this.board = minimaxData.board;
            this.moveCount++; // Hamle sayısını artır
            this.createBoard();
            this.updateMoveCount();
            
            // Update depth if changed
            if (minimaxData.move.new_depth) {
                this.aiDepth = minimaxData.move.new_depth;
                this.updateDepthDisplay();
            }
            
            // Check if game ended after Minimax move
            if (minimaxData.game_over) {
                this.gameOver = true;
                this.winner = minimaxData.winner;
                this.isAiVsAiMode = false;
                setTimeout(() => {
                    this.showGameOverModal();
                }, 1000);
                return;
            }
            
            // Wait before MCTS move
            await new Promise(resolve => setTimeout(resolve, 800));
            
            // Step 2: MCTS plays
            this.statusElement.textContent = '🎲 MCTS is playing...';
            
            const mctsResponse = await fetch('/api/ai-vs-ai-mcts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const mctsData = await mctsResponse.json();
            
            if (!mctsResponse.ok) {
                console.error('MCTS move error:', mctsData.error);
                this.isAiVsAiMode = false;
                return;
            }
            
            // Update board with MCTS move
            this.board = mctsData.board;
            this.gameOver = mctsData.game_over;
            this.winner = mctsData.winner;
            this.moveCount++; // Hamle sayısını artır
            this.createBoard();
            this.updateMoveCount();
            
            // Wait before showing panel
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // Step 3: Show battle panel with both stats
            this.showBattlePanel(minimaxData.move, mctsData.move);
            
            // Check if game over after both moves
            if (this.gameOver) {
                this.isAiVsAiMode = false;
                setTimeout(() => {
                    this.hideBattlePanel();
                    this.showGameOverModal();
                }, 3000);
            }
            
        } catch (error) {
            console.error('AI vs AI move error:', error);
            this.statusElement.textContent = 'Connection error!';
            this.isAiVsAiMode = false;
        }
    }
    
    showBattlePanel(minimaxMove, mctsMove) {
        // Update Minimax stats
        document.getElementById('minimax-move').textContent = `Column ${minimaxMove.col + 1}`;
        document.getElementById('minimax-depth').textContent = minimaxMove.depth;
        document.getElementById('minimax-heuristic').textContent = minimaxMove.heuristic.toFixed(2);
        document.getElementById('minimax-time').textContent = `${minimaxMove.thinking_time.toFixed(2)}s`;
        
        // Update MCTS stats
        document.getElementById('mcts-move').textContent = `Column ${mctsMove.col + 1}`;
        document.getElementById('mcts-iterations').textContent = mctsMove.iterations.toLocaleString();
        document.getElementById('mcts-exploration').textContent = mctsMove.exploration_constant.toFixed(2);
        document.getElementById('mcts-time').textContent = `${mctsMove.thinking_time.toFixed(2)}s`;
        
        // Show panel
        this.battlePanel.classList.add('active');
    }
    
    hideBattlePanel() {
        this.battlePanel.classList.remove('active');
    }
    
    continueAiBattle() {
        this.hideBattlePanel();
        
        if (!this.gameOver && this.isAiVsAiMode) {
            setTimeout(() => this.makeAiVsAiMove(), 500);
        }
    }
    
    async syncBitboardState() {
        // Fetch current bitboard state from backend
        try {
            const response = await fetch('/api/toggle-bitboard', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ enabled: this.bitboardEnabled })
            });
            
            const data = await response.json();
            
            if (response.ok && data.bitboard_enabled !== undefined) {
                this.bitboardEnabled = data.bitboard_enabled;
                if (this.bitboardToggle) {
                    this.bitboardToggle.checked = this.bitboardEnabled;
                }
                console.log(`Bitboard state synced: ${this.bitboardEnabled ? 'ENABLED' : 'DISABLED'}`);
            }
        } catch (error) {
            console.error('Failed to sync bitboard state:', error);
        }
    }

    async toggleBitboard(enabled) {
        // Bitboard toggle - backend'e gönder
        try {
            const response = await fetch('/api/toggle-bitboard', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ enabled: enabled })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Update local state from backend response
                this.bitboardEnabled = data.bitboard_enabled;
                
                // Sync checkbox with actual backend state
                if (this.bitboardToggle) {
                    this.bitboardToggle.checked = this.bitboardEnabled;
                }
                
                console.log(`Bitboard Minimax: ${this.bitboardEnabled ? 'ENABLED' : 'DISABLED'}`);
                this.showToast(
                    '⚡ Bitboard Minimax',
                    this.bitboardEnabled ? 'Bitboard optimization enabled!' : 'Using standard minimax'
                );
            } else {
                console.error('Bitboard toggle error:', data.error);
                // Hata olursa checkbox'u geri al
                this.bitboardToggle.checked = !enabled;
            }
        } catch (error) {
            console.error('Bitboard toggle request failed:', error);
            // Hata olursa checkbox'u geri al
            this.bitboardToggle.checked = !enabled;
        }
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
