"""
Minimax arama ağacını görselleştiren modül.
Alpha-beta pruning'in etkisini göstermek için.
"""

import math
import random
from typing import List, Tuple, Optional, Dict, Any
from .game import (
    ROWS, COLS, PLAYER_AI, PLAYER_HUMAN,
    is_terminal_node, winning_move, get_valid_locations,
    get_next_open_row, drop_piece
)
from .algorithms import score_position


class TreeNode:
    """Minimax ağacında bir düğüm"""
    def __init__(self, depth, move, board_state, is_max_node):
        self.depth = depth
        self.move = move  # Bu düğüme ulaşmak için yapılan hamle
        self.board_state = board_state
        self.is_max_node = is_max_node
        self.value = None
        self.children = []
        self.is_pruned = False
        self.alpha = None
        self.beta = None
        
    def __repr__(self):
        node_type = "MAX" if self.is_max_node else "MIN"
        pruned = " [PRUNED]" if self.is_pruned else ""
        return f"Node(d={self.depth}, move={self.move}, type={node_type}, val={self.value}{pruned})"


class SearchTreeVisualizer:
    """Arama ağacını görselleştir ve analiz et"""
    
    def __init__(self, max_depth=3):
        self.max_depth = max_depth
        self.root = None
        self.total_nodes = 0
        self.pruned_nodes = 0
        self.max_branching_factor = 0
        
    def build_minimax_tree(self, board, depth, alpha, beta, maximizing_player, 
                          parent_node=None, move=None, with_pruning=True):
        """Minimax ağacını oluştur (alpha-beta ile veya olmadan)"""
        
        # Düğüm oluştur
        node = TreeNode(depth, move, board, maximizing_player)
        node.alpha = alpha
        node.beta = beta
        
        if parent_node:
            parent_node.children.append(node)
        else:
            self.root = node
        
        self.total_nodes += 1
        
        valid_locations = get_valid_locations(board)
        is_terminal = is_terminal_node(board)
        
        # Terminal veya max depth
        if depth == 0 or is_terminal:
            if is_terminal:
                if winning_move(board, PLAYER_AI):
                    node.value = 10000000
                elif winning_move(board, PLAYER_HUMAN):
                    node.value = -10000000
                else:
                    node.value = 0
            else:
                node.value = score_position(board, PLAYER_AI)
            return node.value
        
        # Branching factor güncelle
        self.max_branching_factor = max(self.max_branching_factor, len(valid_locations))
        
        if maximizing_player:
            value = -math.inf
            for col in valid_locations:
                row = get_next_open_row(board, col)
                temp_board = [row[:] for row in board]
                drop_piece(temp_board, row, col, PLAYER_AI)
                
                child_value = self.build_minimax_tree(
                    temp_board, depth - 1, alpha, beta, False, node, col, with_pruning
                )
                
                value = max(value, child_value)
                alpha = max(alpha, value)
                
                if with_pruning and alpha >= beta:
                    # Prune remaining children
                    for remaining_col in valid_locations[valid_locations.index(col)+1:]:
                        pruned_node = TreeNode(depth-1, remaining_col, None, False)
                        pruned_node.is_pruned = True
                        node.children.append(pruned_node)
                        self.pruned_nodes += 1
                    break
                    
            node.value = value
            return value
        else:
            value = math.inf
            for col in valid_locations:
                row = get_next_open_row(board, col)
                temp_board = [row[:] for row in board]
                drop_piece(temp_board, row, col, PLAYER_HUMAN)
                
                child_value = self.build_minimax_tree(
                    temp_board, depth - 1, alpha, beta, True, node, col, with_pruning
                )
                
                value = min(value, child_value)
                beta = min(beta, value)
                
                if with_pruning and alpha >= beta:
                    # Prune remaining children
                    for remaining_col in valid_locations[valid_locations.index(col)+1:]:
                        pruned_node = TreeNode(depth-1, remaining_col, None, True)
                        pruned_node.is_pruned = True
                        node.children.append(pruned_node)
                        self.pruned_nodes += 1
                    break
                    
            node.value = value
            return value
    
    def print_tree(self, node=None, prefix="", is_last=True, file=None):
        """Ağacı ASCII art olarak yazdır"""
        if node is None:
            node = self.root
        
        if node is None:
            return
        
        # Düğüm bilgisi
        connector = "└── " if is_last else "├── "
        node_type = "MAX" if node.is_max_node else "MIN"
        
        if node.is_pruned:
            line = f"{prefix}{connector}Move {node.move}: PRUNED ✂️"
        else:
            value_str = f"{node.value:.2f}" if node.value is not None else "?"
            alpha_str = f"{node.alpha:.2f}" if node.alpha is not None and node.alpha != -math.inf else "-∞"
            beta_str = f"{node.beta:.2f}" if node.beta is not None and node.beta != math.inf else "+∞"
            line = f"{prefix}{connector}Move {node.move}: {node_type} | v={value_str} | α={alpha_str}, β={beta_str}"
        
        print(line, file=file)
        
        # Alt düğümler için prefix
        if not is_last:
            prefix += "│   "
        else:
            prefix += "    "
        
        # Çocukları yazdır
        for i, child in enumerate(node.children):
            is_last_child = (i == len(node.children) - 1)
            self.print_tree(child, prefix, is_last_child, file)
    
    def generate_statistics(self) -> str:
        """Ağaç istatistikleri"""
        stats = "\n" + "="*80 + "\n"
        stats += "SEARCH TREE STATISTICS\n"
        stats += "="*80 + "\n"
        stats += f"Total nodes created:      {self.total_nodes}\n"
        stats += f"Nodes pruned:             {self.pruned_nodes}\n"
        stats += f"Nodes evaluated:          {self.total_nodes - self.pruned_nodes}\n"
        stats += f"Pruning efficiency:       {(self.pruned_nodes/self.total_nodes*100):.2f}%\n"
        stats += f"Max branching factor:     {self.max_branching_factor}\n"
        stats += f"Max depth:                {self.max_depth}\n"
        
        # Theoretical vs actual
        theoretical_nodes = sum(self.max_branching_factor**d for d in range(self.max_depth + 1))
        stats += f"\nTheoretical nodes (no pruning): {theoretical_nodes}\n"
        stats += f"Actual nodes (with pruning):    {self.total_nodes}\n"
        stats += f"Reduction:                      {((theoretical_nodes-self.total_nodes)/theoretical_nodes*100):.2f}%\n"
        stats += "="*80 + "\n"
        
        return stats
    
    def save_tree_visualization(self, filename="search_tree.txt"):
        """Ağacı dosyaya kaydet"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("MINIMAX SEARCH TREE with ALPHA-BETA PRUNING\n")
            f.write("="*80 + "\n\n")
            f.write("Legend:\n")
            f.write("  MAX: Maximizing player (AI)\n")
            f.write("  MIN: Minimizing player (Opponent)\n")
            f.write("  v: Node value\n")
            f.write("  α: Alpha value\n")
            f.write("  β: Beta value\n")
            f.write("  ✂️: Pruned branch\n\n")
            f.write("="*80 + "\n\n")
            
            self.print_tree(file=f)
            
            f.write("\n\n")
            f.write(self.generate_statistics())
        
        print(f"🌳 Search tree saved to: {filename}")
    
    def generate_graphviz_dot(self, filename="search_tree.dot"):
        """GraphViz DOT formatında ağaç (görsel için)"""
        def node_id(node):
            return f"node_{id(node)}"
        
        def traverse(node, dot_lines):
            if node is None:
                return
            
            nid = node_id(node)
            node_type = "MAX" if node.is_max_node else "MIN"
            
            if node.is_pruned:
                label = f"Move {node.move}\\nPRUNED"
                color = "red"
                style = "dashed"
            else:
                value_str = f"{node.value:.1f}" if node.value is not None else "?"
                label = f"Move {node.move}\\n{node_type}\\nv={value_str}"
                color = "lightblue" if node.is_max_node else "lightgreen"
                style = "filled"
            
            dot_lines.append(f'  {nid} [label="{label}", style="{style}", fillcolor="{color}"];')
            
            for child in node.children:
                child_id = node_id(child)
                edge_style = "dashed" if child.is_pruned else "solid"
                dot_lines.append(f'  {nid} -> {child_id} [style="{edge_style}"];')
                traverse(child, dot_lines)
        
        dot_lines = [
            "digraph MinimaxTree {",
            "  rankdir=TB;",
            "  node [shape=box];",
        ]
        
        traverse(self.root, dot_lines)
        dot_lines.append("}")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(dot_lines))
        
        print(f"📊 GraphViz DOT file saved to: {filename}")
        print(f"   Use: dot -Tpng {filename} -o search_tree.png")


def visualize_search_tree(board, depth=3, with_pruning=True):
    """Search tree'yi görselleştir"""
    print("\n🌳 Building search tree...")
    
    visualizer = SearchTreeVisualizer(max_depth=depth)
    visualizer.build_minimax_tree(
        board, depth, -math.inf, math.inf, True, 
        with_pruning=with_pruning
    )
    
    print("\nSearch Tree:")
    print("="*80)
    visualizer.print_tree()
    
    print(visualizer.generate_statistics())
    
    visualizer.save_tree_visualization(
        f"search_tree_{'with' if with_pruning else 'without'}_pruning.txt"
    )
    visualizer.generate_graphviz_dot(
        f"search_tree_{'with' if with_pruning else 'without'}_pruning.dot"
    )
    
    return visualizer


if __name__ == "__main__":
    from .game import create_board, drop_piece, get_next_open_row, PLAYER_AI
    
    board = create_board()
    drop_piece(board, get_next_open_row(board, 3), 3, PLAYER_AI)
    
    print("\n1. WITH Alpha-Beta Pruning:")
    visualize_search_tree(board, depth=3, with_pruning=True)
    
    print("\n\n2. WITHOUT Alpha-Beta Pruning:")
    visualize_search_tree(board, depth=3, with_pruning=False)
