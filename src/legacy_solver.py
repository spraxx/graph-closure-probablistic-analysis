import networkx as nx
import time
from typing import Tuple, Dict, Set, Any


class LegacyGreedySolver:
    """
    Implementation of the Greedy Heuristic from Project 1.
    
    This algorithm iteratively removes nodes with in-degree 0 until the graph
    is reduced to k nodes. It is expected to FAIL on graphs with cycles
    (Strongly Connected Components).
    """
    
    @staticmethod
    def solve(G: nx.DiGraph, k: int) -> Tuple[bool, Set[int], Dict[str, Any]]:
        """
        Solve the feedback vertex set problem using a greedy heuristic.
        
        Iteratively removes nodes with in-degree 0 from the graph until either:
        - The remaining graph has k or fewer nodes (success)
        - No nodes with in-degree 0 can be found (stuck on cycle)
        
        Args:
            G: A directed graph (nx.DiGraph) to reduce.
            k: The target number of nodes to retain.
        
        Returns:
            A tuple containing:
            - bool: True if the graph was successfully reduced to k nodes,
                    False if the algorithm got stuck on a cycle.
            - Set[int]: The set of remaining node identifiers.
            - Dict[str, Any]: Metadata dictionary containing:
                - "time" (float): Elapsed time in seconds.
                - "status" (str): Either "SUCCESS" or "STUCK_ON_CYCLE".
                - "basic_ops" (int): Total number of basic operations performed.
        """
        start_time: float = time.perf_counter()
        C: Set[int] = set(G.nodes())
        basic_ops: int = 0
        
        while len(C) > k:
            node_to_remove: int | None = None
            subgraph: nx.DiGraph = G.subgraph(C)
            basic_ops += len(C)
            
            for u in C:
                basic_ops += 1
                if subgraph.in_degree(u) == 0:
                    node_to_remove = u
                    break
            
            if node_to_remove is not None:
                C.remove(node_to_remove)
            else:
                return False, C, {
                    "time": time.perf_counter() - start_time,
                    "status": "STUCK_ON_CYCLE",
                    "basic_ops": basic_ops
                }
        
        return True, C, {
            "time": time.perf_counter() - start_time,
            "status": "SUCCESS",
            "basic_ops": basic_ops
        }