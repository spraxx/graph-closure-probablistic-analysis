import networkx as nx
import random
import time
from typing import Tuple, Set, Dict, Optional

class ClosureSolver:
    def __init__(self, G: nx.DiGraph):
        self.original_graph = G
        # Pre-compute Condensation DAG (Handling Cycles/SCCs)
        self.dag, self.scc_mapping = self._get_condensation_dag(G)
        self.total_weight = self.original_graph.number_of_nodes()

        # OPTIMIZATION: Pre-compute static adjacency and initial in-degrees once.
        # We don't need to rebuild these for every retry.
        self.dag_adj = {u: list(self.dag.successors(u)) for u in self.dag.nodes()}
        self.dag_initial_in_degree = {u: 0 for u in self.dag.nodes()}
        for u in self.dag_adj:
            for v in self.dag_adj[u]:
                self.dag_initial_in_degree[v] += 1

    def _get_condensation_dag(self, G: nx.DiGraph) -> Tuple[nx.DiGraph, Dict[int, Set[int]]]:
        """
        Condenses G into a DAG. Returns the DAG and a mapping from 
        supernode_id -> set of original nodes.
        """
        scc_list = list(nx.strongly_connected_components(G))
        C = nx.condensation(G, scc=scc_list)
        
        mapping = {}
        for n in C.nodes():
            members = set(C.nodes[n]['members'])
            C.nodes[n]['weight'] = len(members)
            mapping[n] = members
            
        return C, mapping

    def solve_randomized_top_down(self, k: int, max_retries: int = 20) -> Tuple[bool, Optional[Set[int]], Dict]:
        """
        Randomized Top-Down Reduction (High Performance).
        Uses O(1) Swap-and-Pop for source management and Integer Counters for in-degrees.
        """
        start_time = time.perf_counter()
        
        # If requested k is larger than the whole graph, return the whole graph
        if k >= self.total_weight:
            all_nodes = set()
            for members in self.scc_mapping.values():
                all_nodes.update(members)
            return True, all_nodes, {
                "time": time.perf_counter() - start_time, 
                "attempts": 0,
                "final_weight": self.total_weight,
                "target_k": k
            }
        
        best_closure = None
        best_weight = -1
        
        for attempt in range(max_retries):
            # 1. Fast Initialization (Copying dict of ints is fast)
            current_nodes = set(self.dag.nodes())
            current_weight = self.total_weight
            
            # Use integer counters instead of sets of predecessors!
            in_degree = self.dag_initial_in_degree.copy()
            
            # Identify initial sources (in-degree 0)
            sources = [u for u in current_nodes if in_degree[u] == 0]
            
            # --- REDUCTION LOOP ---
            while current_weight > k:
                if not sources:
                    break 
                
                # OPTIMIZATION: O(1) Random Selection & Removal
                # 1. Pick a random index
                idx = random.randrange(len(sources))
                node_to_remove = sources[idx]
                
                # 2. Swap with the last element and pop (avoids O(N) shift)
                sources[idx] = sources[-1]
                sources.pop()
                
                # Remove node
                current_nodes.remove(node_to_remove)
                current_weight -= self.dag.nodes[node_to_remove]['weight']
                
                # Update Neighbors (Successors)
                # We simply decrement their in-degree count. 
                for v in self.dag_adj[node_to_remove]:
                    # Only process if v is still in the graph (it should be, in a DAG)
                    if v in current_nodes:
                        in_degree[v] -= 1
                        if in_degree[v] == 0:
                            sources.append(v)
            
            # 3. Check solution quality
            if current_weight <= k:
                if current_weight > best_weight:
                    best_weight = current_weight
                    best_closure = current_nodes.copy()
                
                if current_weight == k:
                    break

        # Reconstruct solution in original graph terms
        final_nodes = set()
        if best_closure:
            for supernode in best_closure:
                final_nodes.update(self.scc_mapping[supernode])

        return True, final_nodes, {
            "time": time.perf_counter() - start_time, 
            "attempts": attempt + 1,
            "final_weight": best_weight,
            "target_k": k
        }

    def verify_closure(self, C: Set[int]) -> bool:
        """Verifies if the set C is truly a closure in the original graph."""
        for u in C:
            for v in self.original_graph.successors(u):
                if v not in C:
                    return False
        return True