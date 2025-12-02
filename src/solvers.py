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
        
        # Pre-compute structure for speed
        self.dag_adj = {u: list(self.dag.successors(u)) for u in self.dag.nodes()}
        self.dag_initial_in_degree = {u: 0 for u in self.dag.nodes()}
        for u in self.dag_adj:
            for v in self.dag_adj[u]:
                self.dag_initial_in_degree[v] += 1

    def _get_condensation_dag(self, G: nx.DiGraph) -> Tuple[nx.DiGraph, Dict[int, Set[int]]]:
        scc_list = list(nx.strongly_connected_components(G))
        C = nx.condensation(G, scc=scc_list)
        mapping = {}
        for n in C.nodes():
            members = set(C.nodes[n]['members'])
            C.nodes[n]['weight'] = len(members)
            mapping[n] = members
        return C, mapping

    def solve_randomized_top_down(self, k: int, max_retries: int = 50, max_time_sec: float = 60.) -> Tuple[bool, Optional[Set[int]], Dict]:
        """
        Randomized Solver that meets Project Requirements:
        1. Tracks 'ops' (Requirement 3b)
        2. Checks 'visited_states' (Requirement 1) and returns 'unique_tested'
        """
        start_time = time.perf_counter()
        
        # [REQ 1] Set to ensure we don't test the same solution twice
        visited_states = set()
        
        # [REQ 3b] Counter for basic operations
        op_count = 0
        
        # EARLY EXIT: If k is larger than graph, return everything
        if k >= self.total_weight:
            all_nodes = set()
            for members in self.scc_mapping.values():
                all_nodes.update(members)
            # MUST RETURN 'unique_tested' HERE TOO
            return True, all_nodes, {
                "time": 0, 
                "ops": 0, 
                "unique_tested": 0,
                "attempts": 0,
                "final_weight": self.total_weight
            }
        
        best_closure = None
        best_weight = -1
        
        for attempt in range(max_retries):
            if (time.perf_counter() - start_time) > max_time_sec:
                break
            # Fast Init
            current_nodes = set(self.dag.nodes())
            current_weight = self.total_weight
            in_degree = self.dag_initial_in_degree.copy()
            
            # Initial Sources
            sources = [u for u in current_nodes if in_degree[u] == 0]
            
            # Trace path for hashing
            removed_sequence = []

            while current_weight > k:
                if not sources:
                    break 
                
                op_count += 1 # Decision op
                
                # --- OPTIMIZATION: Swap-and-Pop (O(1) removal) ---
                idx = random.randrange(len(sources))
                node_to_remove = sources[idx]
                sources[idx] = sources[-1]
                sources.pop()
                
                # Logic
                current_nodes.remove(node_to_remove)
                current_weight -= self.dag.nodes[node_to_remove]['weight']
                removed_sequence.append(node_to_remove)
                
                # Update Neighbors
                for v in self.dag_adj[node_to_remove]:
                    op_count += 1 # Traversal op
                    if v in current_nodes:
                        in_degree[v] -= 1
                        if in_degree[v] == 0:
                            sources.append(v)

            # [REQ 1] Check Visited
            # Hash the frozen set of removed nodes to identify the solution state
            state_hash = hash(frozenset(removed_sequence))
            
            if state_hash in visited_states:
                # We have tested this exact solution before. Skip.
                continue
            
            visited_states.add(state_hash)

            # Update Best
            if current_weight <= k:
                if current_weight > best_weight:
                    best_weight = current_weight
                    best_closure = current_nodes.copy()
                if current_weight == k:
                    break

        # Reconstruct
        final_nodes = set()
        if best_closure:
            for supernode in best_closure:
                final_nodes.update(self.scc_mapping[supernode])

        return True, final_nodes, {
            "time": time.perf_counter() - start_time, 
            "attempts": attempt + 1,
            "final_weight": best_weight,
            "ops": op_count,         # [REQ 3b]
            "unique_tested": len(visited_states) # [FIXED: This key was missing]
        }