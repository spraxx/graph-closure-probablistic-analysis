import networkx as nx
import random
import time
from typing import Tuple, Set, Dict, Optional

class ClosureSolver:
    def __init__(self, G: nx.DiGraph):
        self.original_graph = G
        # Pre-compute Condensation DAG (Handling Cycles/SCCs)
        # Each node in DAG represents an SCC. 'weight' = size of SCC.
        self.dag, self.scc_mapping = self._get_condensation_dag(G)
        self.total_weight = self.original_graph.number_of_nodes()

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

    def solve_randomized_top_down(self, k: int, max_retries: int = 100) -> Tuple[bool, Optional[Set[int]], Dict]:
        """
        Randomized Top-Down Reduction:
        Starts with the full graph (valid closure). Randomly removes 'Source' nodes 
        (nodes with in-degree 0 in the current set) until size <= k.
        """
        start_time = time.perf_counter()
        
        if k > self.total_weight:
            return False, None, {"time": 0, "error": "k > N"}
        
        for attempt in range(max_retries):
            # 1. Initialize with all supernodes
            current_nodes = set(self.dag.nodes())
            current_weight = self.total_weight
            
            # Fast lookup for graph structure
            # adj[u] = list of successors of u
            adj = {u: list(self.dag.successors(u)) for u in self.dag.nodes()}
            # rev_adj[u] = set of predecessors of u (to track in-degrees efficiently)
            rev_adj = {u: set(self.dag.predecessors(u)) for u in self.dag.nodes()}
            
            # 2. Identify initial candidate sources (in-degree 0)
            sources = [u for u in current_nodes if len(rev_adj[u]) == 0]
            
            steps = 0
            while current_weight > k:
                if not sources:
                    break # Should not happen in a DAG unless empty
                
                # --- RANDOMIZED SELECTION ---
                node_to_remove = random.choice(sources)
                
                # Remove node
                current_nodes.remove(node_to_remove)
                current_weight -= self.dag.nodes[node_to_remove]['weight']
                
                # Remove from sources list (it's gone)
                # Note: list.remove is O(N), for optimization use a set or swap-pop
                sources.remove(node_to_remove) 
                
                # Update Neighbors: If we remove u, successors v might become sources
                for v in adj[node_to_remove]:
                    if v in current_nodes:
                        rev_adj[v].remove(node_to_remove)
                        if len(rev_adj[v]) == 0:
                            sources.append(v)
                steps += 1
            
            # 3. Check solution
            if current_weight == k:
                # Reconstruct solution in original graph terms
                final_closure = set()
                for supernode in current_nodes:
                    final_closure.update(self.scc_mapping[supernode])
                
                return True, final_closure, {
                    "time": time.perf_counter() - start_time, 
                    "attempts": attempt + 1,
                    "final_weight": current_weight
                }

        return False, None, {"time": time.perf_counter() - start_time, "attempts": max_retries}

    def verify_closure(self, C: Set[int]) -> bool:
        """Verifies if the set C is truly a closure in the original graph."""
        for u in C:
            for v in self.original_graph.successors(u):
                if v not in C:
                    return False
        return True