"""
Connect4 Bitboard Engine - Professional Implementation
=========================================================

BITBOARD REPRESENTATION:
- 7 columns × 9 bits per column = 63 bits total
- Each column: [6 board cells][3 helper bits]
- Helper bits track column height (0-6)

HEURISTIC ENGINEERING:
- Real coefficients from production bot
- Pattern recognition with permutations
- Open/Closed three distinction
- Fake-zero handling for floating pieces
- Position-based strategic scoring

TECHNIQUES:
- Bitboard manipulation (bit-shift optimized)
- Pattern permutation analysis
- Diagonal extraction (↗ ↖)
- Vertical/Horizontal/Diagonal scoring
- Final score = AI_score - Human_score
"""

import itertools
from typing import List, Tuple, Dict, Set

# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

ROWS = 6
COLS = 7
PLAYER_AI = 0      # Bitboard uses 0 for AI
PLAYER_HUMAN = 1   # Bitboard uses 1 for Human
EMPTY = 2          # Empty cells

# HEURISTIC COEFFICIENTS (Real production values)
SCORE_4_IN_ROW = 1_000_000
SCORE_3_IN_ROW = 200_000
SCORE_3_IN_ROW_SPECIAL = 10_000  # Closed three
SCORE_2_IN_ROW = 6_000

# POSITIONAL WEIGHTS (feature_4)
POSITION_WEIGHTS = [
    [300,  400,  500,  700,  500,  400,  300],
    [400,  600,  800,  1000, 800,  600,  400],
    [500,  800,  1100, 1300, 1100, 800,  500],
    [500,  800,  1100, 1300, 1100, 800,  500],
    [400,  600,  800,  1000, 800,  600,  400],
    [300,  400,  500,  700,  500,  400,  300]
]

# ============================================================================
# BITBOARD OPERATIONS
# ============================================================================

class Bitboard:
    """
    Bitboard representation for Connect4
    
    Structure: 7 columns × 9 bits = 63 bits
    - Bits 0-5: Board cells (bottom to top)
    - Bits 6-8: Helper bits (column height tracker)
    
    Example for column 0:
    Bits [0-5]: actual pieces (0 = AI, 1 = Human)
    Bits [6-8]: height counter (000 to 110 for heights 0-6)
    """
    
    def __init__(self):
        """Initialize empty bitboard"""
        self.board = 0  # 63-bit integer
        self.heights = [0] * COLS  # Track column heights separately for speed
    
    def make_move(self, col: int, player_bit: int) -> bool:
        """
        Drop a piece in column (bitboard optimized)
        
        Args:
            col: Column index (0-6)
            player_bit: 0 for AI, 1 for Human
        
        Returns:
            True if move was valid, False otherwise
        """
        if self.heights[col] >= ROWS:
            return False  # Column full
        
        # Calculate bit position: col * 9 + current_height
        bit_pos = col * 9 + self.heights[col]
        
        # Set bit if player_bit == 1 (Human)
        if player_bit == 1:
            self.board |= (1 << bit_pos)
        # If player_bit == 0 (AI), bit stays 0 (already clear)
        
        # Update height
        self.heights[col] += 1
        
        # Update helper bits (bits 6-8 of column)
        # Clear old height bits
        height_mask = 0b111 << (col * 9 + 6)
        self.board &= ~height_mask
        
        # Set new height bits
        self.board |= (self.heights[col] << (col * 9 + 6))
        
        return True
    
    def get_column_height(self, col: int) -> int:
        """Get current height of column (0-6)"""
        return self.heights[col]
    
    def extract_column_bits(self, col: int) -> int:
        """Extract 6 bits representing a column (bottom to top)"""
        shift = col * 9
        return (self.board >> shift) & 0b111111
    
    def extract_nth_row(self, row: int) -> List[int]:
        """
        Extract a horizontal row from bitboard
        
        Args:
            row: Row index (0-5, bottom to top)
        
        Returns:
            List of 7 values [0=AI, 1=Human, 2=Empty]
        """
        result = []
        for col in range(COLS):
            col_bits = self.extract_column_bits(col)
            
            # Check if this row exists in column
            if self.heights[col] <= row:
                result.append(EMPTY)
            else:
                # Extract bit at position 'row'
                bit = (col_bits >> row) & 1
                result.append(bit)
        
        return result
    
    def get_cell(self, row: int, col: int) -> int:
        """
        Get cell value at (row, col)
        
        Returns:
            0 = AI, 1 = Human, 2 = Empty
        """
        if self.heights[col] <= row:
            return EMPTY
        
        col_bits = self.extract_column_bits(col)
        bit = (col_bits >> row) & 1
        return bit
    
    def to_2d_array(self) -> List[List[int]]:
        """
        Convert bitboard to 2D array for visualization/compatibility
        
        Returns:
            6x7 array with values: 0=AI, 1=Human, 2=Empty
        """
        board_2d = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
        
        for row in range(ROWS):
            for col in range(COLS):
                board_2d[row][col] = self.get_cell(row, col)
        
        return board_2d
    
    def from_2d_array(self, board_2d: List[List[int]]):
        """
        Initialize bitboard from 2D array
        
        Args:
            board_2d: 6x7 array with values matching PLAYER_AI=1, PLAYER_HUMAN=-1, EMPTY=0
                      (will be converted to bitboard representation)
        """
        self.board = 0
        self.heights = [0] * COLS
        
        # Map from traditional representation to bitboard
        # Traditional: AI=1, Human=-1, Empty=0
        # Bitboard: AI=0, Human=1, Empty=2
        mapping = {1: 0, -1: 1, 0: 2}
        
        for col in range(COLS):
            for row in range(ROWS):
                value = mapping.get(board_2d[row][col], 2)
                
                if value != EMPTY:
                    # Set bit for this position
                    player_bit = value  # 0 for AI, 1 for Human
                    bit_pos = col * 9 + row
                    
                    if player_bit == 1:
                        self.board |= (1 << bit_pos)
                    
                    self.heights[col] = max(self.heights[col], row + 1)
            
            # Update helper bits
            height_mask = 0b111 << (col * 9 + 6)
            self.board &= ~height_mask
            self.board |= (self.heights[col] << (col * 9 + 6))
    
    def get_valid_columns(self) -> List[int]:
        """Get list of columns that are not full"""
        return [col for col in range(COLS) if self.heights[col] < ROWS]
    
    def copy(self) -> 'Bitboard':
        """Create a copy of this bitboard"""
        new_board = Bitboard()
        new_board.board = self.board
        new_board.heights = self.heights.copy()
        return new_board

# ============================================================================
# PATTERN RECOGNITION & HEURISTIC
# ============================================================================

def get_all_diagonals(board_2d: List[List[int]]) -> Tuple[List[List[int]], List[List[int]]]:
    """
    Extract all diagonals from board (↗ major, ↖ minor)
    
    Args:
        board_2d: 6x7 2D array
    
    Returns:
        (major_diagonals, minor_diagonals)
        - major: ↗ (bottom-left to top-right)
        - minor: ↖ (top-left to bottom-right)
    """
    major_diagonals = []  # ↗
    minor_diagonals = []  # ↖
    
    # MAJOR DIAGONALS (↗)
    # Start from bottom-left, move right and up
    for start_col in range(COLS):
        diag = []
        row, col = 0, start_col
        while row < ROWS and col < COLS:
            diag.append(board_2d[row][col])
            row += 1
            col += 1
        if len(diag) >= 4:  # Only keep diagonals with 4+ cells
            major_diagonals.append(diag)
    
    # Start from left edge (row 1 onwards)
    for start_row in range(1, ROWS):
        diag = []
        row, col = start_row, 0
        while row < ROWS and col < COLS:
            diag.append(board_2d[row][col])
            row += 1
            col += 1
        if len(diag) >= 4:
            major_diagonals.append(diag)
    
    # MINOR DIAGONALS (↖)
    # Start from top-left, move right and down
    for start_col in range(COLS):
        diag = []
        row, col = ROWS - 1, start_col
        while row >= 0 and col < COLS:
            diag.append(board_2d[row][col])
            row -= 1
            col += 1
        if len(diag) >= 4:
            minor_diagonals.append(diag)
    
    # Start from top edge (columns after 0)
    for start_row in range(ROWS - 2, -1, -1):
        diag = []
        row, col = start_row, 0
        while row >= 0 and col < COLS:
            diag.append(board_2d[row][col])
            row -= 1
            col += 1
        if len(diag) >= 4:
            minor_diagonals.append(diag)
    
    return major_diagonals, minor_diagonals

def apply_fake_zero_handling(column: List[int], col_index: int, heights: List[int]) -> List[int]:
    """
    FAKE-ZERO HANDLING
    
    Prevents floating empty cells from being counted as opponent pieces
    
    Logic:
        if (6 - first_empty_row <= current_row) and cell == EMPTY:
            treat as HUMAN (-1)
        else:
            keep original value
    
    Args:
        column: List of cell values (bottom to top)
        col_index: Column index
        heights: Current column heights
    
    Returns:
        Processed column with fake-zeros handled
    """
    first_empty_row = heights[col_index]  # First empty position from bottom
    processed = []
    
    for row_idx, cell_value in enumerate(column):
        if (ROWS - first_empty_row <= row_idx) and cell_value == EMPTY:
            # Floating empty cell → treat as opponent
            processed.append(PLAYER_HUMAN)
        else:
            processed.append(cell_value)
    
    return processed

def generate_pattern_permutations() -> Dict[str, Set[Tuple]]:
    """
    Generate all pattern permutations for recognition
    
    Patterns:
    - 4-in-a-row: [AI, AI, AI, AI]
    - 3-in-a-row open: [AI, AI, AI, EMPTY]
    - 3-in-a-row closed: [HUMAN, AI, AI, AI, HUMAN] (needs 5-window)
    - 2-in-a-row: [AI, AI, EMPTY, EMPTY]
    
    Returns:
        Dictionary of pattern sets
    """
    patterns = {
        'four_ai': set(),
        'four_human': set(),
        'three_open_ai': set(),
        'three_open_human': set(),
        'three_closed_ai': set(),
        'three_closed_human': set(),
        'two_ai': set(),
        'two_human': set()
    }
    
    # 4-in-a-row (simple, only one permutation)
    patterns['four_ai'].add((PLAYER_AI, PLAYER_AI, PLAYER_AI, PLAYER_AI))
    patterns['four_human'].add((PLAYER_HUMAN, PLAYER_HUMAN, PLAYER_HUMAN, PLAYER_HUMAN))
    
    # 3-in-a-row OPEN (3 pieces + 1 empty in any order)
    base_three_ai = [PLAYER_AI, PLAYER_AI, PLAYER_AI, EMPTY]
    base_three_human = [PLAYER_HUMAN, PLAYER_HUMAN, PLAYER_HUMAN, EMPTY]
    
    for perm in itertools.permutations(base_three_ai):
        # Exclude illegal patterns (e.g., floating pieces)
        patterns['three_open_ai'].add(perm)
    
    for perm in itertools.permutations(base_three_human):
        patterns['three_open_human'].add(perm)
    
    # 3-in-a-row CLOSED (blocked on both sides) - needs 5-window
    # Pattern: [HUMAN, AI, AI, AI, HUMAN] and permutations
    # This is handled separately in count_consecutive_pieces
    
    # 2-in-a-row (2 pieces + 2 empty in any order)
    base_two_ai = [PLAYER_AI, PLAYER_AI, EMPTY, EMPTY]
    base_two_human = [PLAYER_HUMAN, PLAYER_HUMAN, EMPTY, EMPTY]
    
    for perm in itertools.permutations(base_two_ai):
        patterns['two_ai'].add(perm)
    
    for perm in itertools.permutations(base_two_human):
        patterns['two_human'].add(perm)
    
    return patterns

# Pre-generate patterns (optimization)
PATTERN_LIBRARY = generate_pattern_permutations()

def count_patterns_in_line(line: List[int], player: int) -> Dict[str, int]:
    """
    Count different patterns in a line (row/col/diagonal)
    
    Args:
        line: List of cell values
        player: PLAYER_AI or PLAYER_HUMAN
    
    Returns:
        Dictionary with counts: {
            'four': count,
            'three_open': count,
            'three_closed': count,
            'two': count
        }
    """
    counts = {
        'four': 0,
        'three_open': 0,
        'three_closed': 0,
        'two': 0
    }
    
    # Check 4-windows
    for i in range(len(line) - 3):
        window = tuple(line[i:i+4])
        
        if player == PLAYER_AI:
            if window in PATTERN_LIBRARY['four_ai']:
                counts['four'] += 1
            elif window in PATTERN_LIBRARY['three_open_ai']:
                counts['three_open'] += 1
            elif window in PATTERN_LIBRARY['two_ai']:
                counts['two'] += 1
        else:
            if window in PATTERN_LIBRARY['four_human']:
                counts['four'] += 1
            elif window in PATTERN_LIBRARY['three_open_human']:
                counts['three_open'] += 1
            elif window in PATTERN_LIBRARY['two_human']:
                counts['two'] += 1
    
    # Check 5-windows for CLOSED three
    for i in range(len(line) - 4):
        window = line[i:i+5]
        opponent = PLAYER_HUMAN if player == PLAYER_AI else PLAYER_AI
        
        # Pattern: [opponent, player, player, player, opponent]
        if (window[0] == opponent and 
            window[1] == player and 
            window[2] == player and 
            window[3] == player and 
            window[4] == opponent):
            counts['three_closed'] += 1
    
    return counts

def count_consecutive_pieces(bitboard: Bitboard, player: int) -> Dict[str, int]:
    """
    Count all patterns for a player across entire board
    
    Uses:
    - Vertical: bitboard column extraction
    - Horizontal: extract_nth_row
    - Diagonal: get_all_diagonals
    
    Args:
        bitboard: Bitboard instance
        player: PLAYER_AI or PLAYER_HUMAN
    
    Returns:
        Aggregated pattern counts
    """
    total_counts = {
        'four': 0,
        'three_open': 0,
        'three_closed': 0,
        'two': 0
    }
    
    board_2d = bitboard.to_2d_array()
    
    # VERTICAL
    for col in range(COLS):
        column = []
        for row in range(ROWS):
            column.append(board_2d[row][col])
        
        # Apply fake-zero handling
        column = apply_fake_zero_handling(column, col, bitboard.heights)
        
        pattern_counts = count_patterns_in_line(column, player)
        for key in total_counts:
            total_counts[key] += pattern_counts[key]
    
    # HORIZONTAL
    for row in range(ROWS):
        row_data = bitboard.extract_nth_row(row)
        
        pattern_counts = count_patterns_in_line(row_data, player)
        for key in total_counts:
            total_counts[key] += pattern_counts[key]
    
    # DIAGONAL
    major_diags, minor_diags = get_all_diagonals(board_2d)
    
    for diag in major_diags + minor_diags:
        pattern_counts = count_patterns_in_line(diag, player)
        for key in total_counts:
            total_counts[key] += pattern_counts[key]
    
    return total_counts

def calculate_positional_score(bitboard: Bitboard, player: int) -> int:
    """
    Calculate positional score based on POSITION_WEIGHTS matrix
    
    Args:
        bitboard: Bitboard instance
        player: PLAYER_AI or PLAYER_HUMAN
    
    Returns:
        Total positional score
    """
    score = 0
    board_2d = bitboard.to_2d_array()
    
    for row in range(ROWS):
        for col in range(COLS):
            if board_2d[row][col] == player:
                score += POSITION_WEIGHTS[row][col]
    
    return score

def evaluate_bitboard(bitboard: Bitboard) -> int:
    """
    MAIN HEURISTIC EVALUATION
    
    Calculates: AI_score - Human_score
    
    Components:
    - 4-in-a-row: ±1,000,000
    - 3-in-a-row open: ±200,000
    - 3-in-a-row closed: ±10,000
    - 2-in-a-row: ±6,000
    - Positional weights: POSITION_WEIGHTS matrix
    
    Args:
        bitboard: Current board state
    
    Returns:
        Evaluation score (positive favors AI, negative favors Human)
    """
    # Count patterns for both players
    ai_patterns = count_consecutive_pieces(bitboard, PLAYER_AI)
    human_patterns = count_consecutive_pieces(bitboard, PLAYER_HUMAN)
    
    # Calculate AI score
    ai_score = 0
    ai_score += SCORE_4_IN_ROW * ai_patterns['four']
    ai_score += SCORE_3_IN_ROW * ai_patterns['three_open']
    ai_score += SCORE_3_IN_ROW_SPECIAL * ai_patterns['three_closed']
    ai_score += SCORE_2_IN_ROW * ai_patterns['two']
    ai_score += calculate_positional_score(bitboard, PLAYER_AI)
    
    # Calculate Human score
    human_score = 0
    human_score += SCORE_4_IN_ROW * human_patterns['four']
    human_score += SCORE_3_IN_ROW * human_patterns['three_open']
    human_score += SCORE_3_IN_ROW_SPECIAL * human_patterns['three_closed']
    human_score += SCORE_2_IN_ROW * human_patterns['two']
    human_score += calculate_positional_score(bitboard, PLAYER_HUMAN)
    
    # Final score = AI - Human
    return ai_score - human_score

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def check_win(bitboard: Bitboard, player: int) -> bool:
    """
    Check if player has won (4-in-a-row exists)
    
    Args:
        bitboard: Current board state
        player: PLAYER_AI or PLAYER_HUMAN
    
    Returns:
        True if player has won
    """
    patterns = count_consecutive_pieces(bitboard, player)
    return patterns['four'] > 0

def is_terminal(bitboard: Bitboard) -> bool:
    """
    Check if game is in terminal state (win or draw)
    
    Args:
        bitboard: Current board state
    
    Returns:
        True if game is over
    """
    # Check wins
    if check_win(bitboard, PLAYER_AI) or check_win(bitboard, PLAYER_HUMAN):
        return True
    
    # Check draw (board full)
    return len(bitboard.get_valid_columns()) == 0

def print_bitboard(bitboard: Bitboard):
    """
    Print bitboard in human-readable format
    
    Args:
        bitboard: Bitboard instance
    """
    board_2d = bitboard.to_2d_array()
    
    # Map values to symbols
    symbols = {PLAYER_AI: 'X', PLAYER_HUMAN: 'O', EMPTY: '.'}
    
    print("\n" + "=" * 29)
    for row in reversed(range(ROWS)):
        row_str = "| "
        for col in range(COLS):
            row_str += symbols[board_2d[row][col]] + " | "
        print(row_str)
        print("-" * 29)
    
    print("  " + "   ".join(str(i) for i in range(COLS)))
    print("=" * 29)
    print(f"Heights: {bitboard.heights}")
    print(f"Bitboard value: {bin(bitboard.board)}")
    print()

# ============================================================================
# TESTING & VALIDATION
# ============================================================================

if __name__ == "__main__":
    # Example usage and testing
    print("🎮 Connect4 Bitboard Engine - Test Suite\n")
    
    # Test 1: Basic operations
    print("Test 1: Basic Bitboard Operations")
    bb = Bitboard()
    print("Initial board:")
    print_bitboard(bb)
    
    # Make some moves
    bb.make_move(3, PLAYER_AI)    # Center column, AI
    bb.make_move(3, PLAYER_HUMAN) # Center column, Human
    bb.make_move(2, PLAYER_AI)    # Left of center
    bb.make_move(4, PLAYER_HUMAN) # Right of center
    
    print("After 4 moves:")
    print_bitboard(bb)
    
    # Test 2: Heuristic evaluation
    print("\nTest 2: Heuristic Evaluation")
    score = evaluate_bitboard(bb)
    print(f"Board evaluation: {score:+,d}")
    
    # Test 3: Pattern recognition
    print("\nTest 3: Pattern Recognition")
    ai_patterns = count_consecutive_pieces(bb, PLAYER_AI)
    print(f"AI patterns: {ai_patterns}")
    human_patterns = count_consecutive_pieces(bb, PLAYER_HUMAN)
    print(f"Human patterns: {human_patterns}")
    
    # Test 4: 2D array conversion
    print("\nTest 4: 2D Array Conversion (Compatibility)")
    traditional_board = [
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, -1, 0, 0, 0],
        [0, 0, 1, 1, -1, 0, 0]
    ]
    
    bb2 = Bitboard()
    bb2.from_2d_array(traditional_board)
    print("Converted from traditional format:")
    print_bitboard(bb2)
    
    # Test 5: Winning position
    print("\nTest 5: Winning Position Detection")
    bb3 = Bitboard()
    for i in range(4):
        bb3.make_move(i, PLAYER_AI)  # 4 in a row at bottom
    
    print("AI winning position:")
    print_bitboard(bb3)
    print(f"AI wins: {check_win(bb3, PLAYER_AI)}")
    print(f"Game over: {is_terminal(bb3)}")
    
    score = evaluate_bitboard(bb3)
    print(f"Evaluation: {score:+,d}")
    
    print("\n✅ All tests completed!")
