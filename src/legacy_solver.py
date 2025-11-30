import networkx as nx
import time

class LegacyGreedySolver:
    """
    Implementation of the Greedy Heuristic from Project 1.
    This algorithm iteratively removes nodes with in-degree 0.
    It is expected to FAIL on graphs with cycles (Strongly Connected Components).
    """
    
    @staticmethod
    def solve(G: nx.DiGraph, k: int):
        start_time = time.perf_counter()
        
        # Working copy of the set of nodes
        C = set(G.nodes())
        
        # Stats
        basic_ops = 0
        
        # Optimization: Track the graph view
        # In Project 1, we often re-calculated degrees which is O(N^2) or O(N*M)
        
        while len(C) > k:
            # Logic from Project 1: Find a node in C with in-degree 0 
            # *relative to other nodes in C*
            
            node_to_remove = None
            
            # Create subgraph to check degrees (Expensive operation!)
            subgraph = G.subgraph(C)
            basic_ops += len(C) # Subgraph creation cost approximation
            
            # Linear scan for a sink/source node to remove
            for u in C:
                basic_ops += 1
                if subgraph.in_degree(u) == 0:
                    node_to_remove = u
                    break # Found one, greedy choice
            
            if node_to_remove is not None:
                C.remove(node_to_remove)
            else:
                # STUCK! The graph has a cycle (SCC) and no node has in-degree 0.
                return False, C, {
                    "time": time.perf_counter() - start_time, 
                    "status": "STUCK_ON_CYCLE",
                    "basic_ops": basic_ops
                }

        # If we exit loop, we reached size k
        return True, C, {
            "time": time.perf_counter() - start_time, 
            "status": "SUCCESS",
            "basic_ops": basic_ops
        }