"""
Farklı arama algoritmalarını karşılaştıran benchmark modülü.
Akademik sunum için detaylı metrikler ve analiz sağlar.
"""

import time
import sys
from typing import Dict, List, Any
from .game import create_board, drop_piece, get_next_open_row, PLAYER_AI
from .algorithms import (
    SearchMetrics,
    minimax_basic,
    minimax_alpha_beta,
    bfs_search,
    dfs_search,
    ucs_search,
    astar_search
)


class AlgorithmBenchmark:
    """Algoritma performans karşılaştırması"""
    
    def __init__(self, depth=4):
        self.depth = depth
        self.results = {}
        
    def run_algorithm(self, name: str, board, algorithm_func, *args):
        """Tek bir algoritma çalıştır ve metriklerini topla"""
        print(f"\n🔍 Testing {name}...")
        
        start_time = time.time()
        
        try:
            if 'minimax' in name.lower():
                metrics = SearchMetrics()
                if 'alpha' in name.lower():
                    move, score = algorithm_func(board, self.depth, -float('inf'), float('inf'), True, metrics)
                else:
                    move, score = algorithm_func(board, self.depth, True, metrics)
                metrics.time_taken = time.time() - start_time
                result = {
                    'move': move,
                    'score': score,
                    'metrics': metrics
                }
            else:
                move, metrics = algorithm_func(board, self.depth)
                result = {
                    'move': move,
                    'score': 0,
                    'metrics': metrics
                }
            
            self.results[name] = result
            print(f"✅ {name} completed in {metrics.time_taken:.4f}s")
            print(f"   Nodes expanded: {metrics.nodes_expanded}")
            print(f"   Max depth: {metrics.max_depth_reached}")
            if hasattr(metrics, 'pruned_branches') and metrics.pruned_branches > 0:
                print(f"   Pruned branches: {metrics.pruned_branches}")
            
            return result
            
        except Exception as e:
            print(f"❌ {name} failed: {str(e)}")
            return None
    
    def run_all_algorithms(self, board):
        """Tüm algoritmaları çalıştır"""
        print("\n" + "="*60)
        print("🎯 ALGORITHM BENCHMARK - Connect4 AI")
        print("="*60)
        print(f"Depth: {self.depth}")
        print(f"Board State: Starting position")
        
        algorithms = [
            ("Minimax (Basic)", minimax_basic),
            ("Minimax + Alpha-Beta Pruning", minimax_alpha_beta),
            ("Breadth-First Search (BFS)", bfs_search),
            ("Depth-First Search (DFS)", dfs_search),
            ("Uniform Cost Search (UCS)", ucs_search),
            ("A* Search", astar_search),
        ]
        
        for name, func in algorithms:
            self.run_algorithm(name, board, func)
        
        print("\n" + "="*60)
        print("✅ Benchmark Completed!")
        print("="*60)
        
        return self.results
    
    def generate_comparison_table(self) -> str:
        """Karşılaştırma tablosu oluştur"""
        if not self.results:
            return "No results to compare."
        
        table = "\n" + "="*100 + "\n"
        table += "ALGORITHM COMPARISON TABLE\n"
        table += "="*100 + "\n"
        table += f"{'Algorithm':<35} {'Nodes':<10} {'Time(s)':<10} {'Pruned':<10} {'Memory(KB)':<12}\n"
        table += "-"*100 + "\n"
        
        for name, result in self.results.items():
            if result:
                m = result['metrics']
                table += f"{name:<35} "
                table += f"{m.nodes_expanded:<10} "
                table += f"{m.time_taken:<10.4f} "
                table += f"{getattr(m, 'pruned_branches', 0):<10} "
                table += f"{getattr(m, 'memory_used', 0):<12.2f}\n"
        
        table += "="*100 + "\n"
        return table
    
    def generate_complexity_analysis(self) -> str:
        """Complexity analizi oluştur"""
        analysis = "\n" + "="*100 + "\n"
        analysis += "COMPLEXITY ANALYSIS\n"
        analysis += "="*100 + "\n\n"
        
        complexity_data = {
            "Minimax (Basic)": {
                "Time": "O(b^d)",
                "Space": "O(b*d)",
                "Complete": "Yes",
                "Optimal": "Yes",
                "Notes": "Explores all nodes, no pruning"
            },
            "Minimax + Alpha-Beta Pruning": {
                "Time": "O(b^(d/2)) best, O(b^d) worst",
                "Space": "O(b*d)",
                "Complete": "Yes",
                "Optimal": "Yes",
                "Notes": "Prunes branches, much faster"
            },
            "Breadth-First Search (BFS)": {
                "Time": "O(b^d)",
                "Space": "O(b^d)",
                "Complete": "Yes",
                "Optimal": "Yes (uniform cost)",
                "Notes": "High memory usage, stores all levels"
            },
            "Depth-First Search (DFS)": {
                "Time": "O(b^m)",
                "Space": "O(b*m)",
                "Complete": "No (infinite paths)",
                "Optimal": "No",
                "Notes": "Low memory, not optimal"
            },
            "Uniform Cost Search (UCS)": {
                "Time": "O(b^(C*/ε))",
                "Space": "O(b^(C*/ε))",
                "Complete": "Yes",
                "Optimal": "Yes",
                "Notes": "Similar to Dijkstra, explores by cost"
            },
            "A* Search": {
                "Time": "O(b^d)",
                "Space": "O(b^d)",
                "Complete": "Yes",
                "Optimal": "Yes (admissible heuristic)",
                "Notes": "Uses heuristic, more efficient than UCS"
            }
        }
        
        for algo, data in complexity_data.items():
            analysis += f"📊 {algo}\n"
            analysis += f"   Time Complexity:  {data['Time']}\n"
            analysis += f"   Space Complexity: {data['Space']}\n"
            analysis += f"   Completeness:     {data['Complete']}\n"
            analysis += f"   Optimality:       {data['Optimal']}\n"
            analysis += f"   Notes:            {data['Notes']}\n\n"
        
        analysis += "="*100 + "\n"
        
        # Empirical results
        if self.results:
            analysis += "\nEMPIRICAL RESULTS FROM BENCHMARK:\n"
            analysis += "-"*100 + "\n"
            
            # Find fastest
            fastest = min(self.results.items(), 
                         key=lambda x: x[1]['metrics'].time_taken if x[1] else float('inf'))
            analysis += f"⚡ Fastest: {fastest[0]} ({fastest[1]['metrics'].time_taken:.4f}s)\n"
            
            # Find most efficient (least nodes)
            efficient = min(self.results.items(),
                          key=lambda x: x[1]['metrics'].nodes_expanded if x[1] else float('inf'))
            analysis += f"🎯 Most Efficient: {efficient[0]} ({efficient[1]['metrics'].nodes_expanded} nodes)\n"
            
            # Alpha-Beta improvement
            if 'Minimax (Basic)' in self.results and 'Minimax + Alpha-Beta Pruning' in self.results:
                basic = self.results['Minimax (Basic)']['metrics']
                alpha_beta = self.results['Minimax + Alpha-Beta Pruning']['metrics']
                
                node_reduction = ((basic.nodes_expanded - alpha_beta.nodes_expanded) / basic.nodes_expanded) * 100
                time_reduction = ((basic.time_taken - alpha_beta.time_taken) / basic.time_taken) * 100
                
                analysis += f"\n💡 Alpha-Beta Pruning Improvement:\n"
                analysis += f"   Nodes reduced: {node_reduction:.2f}%\n"
                analysis += f"   Time reduced:  {time_reduction:.2f}%\n"
                analysis += f"   Branches pruned: {alpha_beta.pruned_branches}\n"
            
            analysis += "\n" + "="*100 + "\n"
        
        return analysis
    
    def generate_recommendation(self) -> str:
        """Algoritma seçim önerisi"""
        rec = "\n" + "="*100 + "\n"
        rec += "🎓 ALGORITHM SELECTION RECOMMENDATION FOR CONNECT4\n"
        rec += "="*100 + "\n\n"
        
        rec += "WHY WE CHOSE MINIMAX + ALPHA-BETA PRUNING:\n\n"
        
        rec += "1. PROBLEM CHARACTERISTICS:\n"
        rec += "   - Connect4 is a two-player, zero-sum, perfect information game\n"
        rec += "   - Adversarial search is required (opponent tries to minimize our score)\n"
        rec += "   - Game tree is finite but large (branching factor ≈ 7, depth ≈ 42)\n\n"
        
        rec += "2. WHY NOT UNINFORMED SEARCH:\n"
        rec += "   ❌ BFS/DFS: Don't model adversarial nature, high memory usage\n"
        rec += "   ❌ UCS: No consideration of opponent's best response\n"
        rec += "   ❌ These are for single-agent pathfinding, not game playing\n\n"
        
        rec += "3. WHY MINIMAX:\n"
        rec += "   ✅ Designed for two-player games\n"
        rec += "   ✅ Guarantees optimal play (if fully expanded)\n"
        rec += "   ✅ Complete and optimal\n\n"
        
        rec += "4. WHY ALPHA-BETA PRUNING:\n"
        rec += "   ✅ Same result as Minimax, but faster\n"
        rec += f"   ✅ Empirical improvement: ~{self._get_pruning_improvement():.1f}% fewer nodes\n"
        rec += "   ✅ Allows deeper search in same time\n"
        rec += "   ✅ No loss in optimality\n\n"
        
        rec += "5. WHY HEURISTIC EVALUATION:\n"
        rec += "   ✅ Can't search to end of game (too deep)\n"
        rec += "   ✅ Heuristic estimates position value\n"
        rec += "   ✅ Considers: center control, 3-in-a-rows, threats\n"
        rec += "   ✅ Makes AI play intelligently at limited depth\n\n"
        
        rec += "6. INFORMED vs UNINFORMED:\n"
        rec += "   - A* is 'informed' (uses heuristic for pathfinding)\n"
        rec += "   - Alpha-Beta uses heuristic BUT for position evaluation, not search guidance\n"
        rec += "   - Classification: Minimax is adversarial search (different category)\n"
        rec += "   - We use heuristics because full tree search is impractical\n\n"
        
        rec += "="*100 + "\n"
        return rec
    
    def _get_pruning_improvement(self) -> float:
        """Alpha-beta pruning iyileştirmesi yüzdesini hesapla"""
        if 'Minimax (Basic)' in self.results and 'Minimax + Alpha-Beta Pruning' in self.results:
            basic = self.results['Minimax (Basic)']['metrics'].nodes_expanded
            alpha = self.results['Minimax + Alpha-Beta Pruning']['metrics'].nodes_expanded
            return ((basic - alpha) / basic) * 100
        return 0.0
    
    def save_report(self, filename="benchmark_report.txt"):
        """Tam raporu dosyaya kaydet"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self.generate_comparison_table())
            f.write("\n\n")
            f.write(self.generate_complexity_analysis())
            f.write("\n\n")
            f.write(self.generate_recommendation())
        
        print(f"\n📄 Full report saved to: {filename}")


def run_benchmark(depth=4):
    """Benchmark'ı çalıştır"""
    board = create_board()
    
    # İlk hamleyi yapalım (daha ilginç bir pozisyon için)
    drop_piece(board, get_next_open_row(board, 3), 3, PLAYER_AI)
    
    benchmark = AlgorithmBenchmark(depth=depth)
    benchmark.run_all_algorithms(board)
    
    print(benchmark.generate_comparison_table())
    print(benchmark.generate_complexity_analysis())
    print(benchmark.generate_recommendation())
    
    benchmark.save_report("connect4_benchmark_report.txt")
    
    return benchmark


if __name__ == "__main__":
    run_benchmark(depth=4)
