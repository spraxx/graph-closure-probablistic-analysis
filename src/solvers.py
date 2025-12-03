import networkx as nx
import random
import time
from typing import Tuple, Set, Dict, Optional, List


class ClosureSolver:
    """
    Solves the closure problem on directed graphs using condensation to DAG
    and randomized top-down greedy strategy.
    
    Attributes:
        original_graph (nx.DiGraph): The input directed graph.
        dag (nx.DiGraph): Condensed DAG of strongly connected components.
        scc_mapping (Dict[int, Set[int]]): Maps DAG nodes to original graph nodes.
        total_weight (int): Total number of nodes in the original graph.
        dag_adj (Dict): Adjacency list for the DAG.
        dag_initial_in_degree (Dict): Initial in-degree of each DAG node.
    """
    
    def __init__(self, G: nx.DiGraph) -> None:
        """
        Initialize the ClosureSolver with a directed graph.
        
        Args:
            G: A directed graph (nx.DiGraph) to solve on.
        """
        self.original_graph: nx.DiGraph = G
        self.dag, self.scc_mapping = self._get_condensation_dag(G)
        self.total_weight: int = self.original_graph.number_of_nodes()

        self.dag_adj: Dict[int, List[int]] = {u: list(self.dag.successors(u)) for u in self.dag.nodes()}
        self.dag_initial_in_degree: Dict[int, int] = {u: 0 for u in self.dag.nodes()}
        for u in self.dag_adj:
            for v in self.dag_adj[u]:
                self.dag_initial_in_degree[v] += 1

    def _get_condensation_dag(self, G: nx.DiGraph) -> Tuple[nx.DiGraph, Dict[int, Set[int]]]:
        """
        Condense the graph into a DAG of strongly connected components.
        
        Computes all strongly connected components and creates a condensation graph
        where each node represents an SCC. Each condensation node stores:
        - 'members': The original nodes in that SCC
        - 'weight': The number of original nodes in that SCC
        
        Args:
            G: A directed graph (nx.DiGraph) to condense.
        
        Returns:
            A tuple containing:
            - nx.DiGraph: The condensed DAG where nodes are SCCs.
            - Dict[int, Set[int]]: Mapping from SCC node IDs to sets of original nodes.
        """
        scc_list: List[Set[int]] = list(nx.strongly_connected_components(G))
        C: nx.DiGraph = nx.condensation(G, scc=scc_list)
        mapping: Dict[int, Set[int]] = {}
        for n in C.nodes():
            members: Set[int] = set(C.nodes[n]['members'])
            C.nodes[n]['weight'] = len(members)
            mapping[n] = members
        return C, mapping

    def verify_closure(self, closure_nodes: Set[int]) -> bool:
        """
        Verify if the given set of nodes forms a valid closure in the original graph.
        
        A closure is valid if for every node in the set, all of its successors
        are also in the set.
        
        Args:
            closure_nodes: A set of node identifiers to verify.
        
        Returns:
            True if the set forms a valid closure, False otherwise.
        """
        if not closure_nodes:
            return True
            
        for u in closure_nodes:
            for v in self.original_graph.successors(u):
                if v not in closure_nodes:
                    return False
        return True

    def solve_randomized_top_down(
        self,
        k: int,
        max_retries: int = 50,
        max_time_sec: float = 60.0
    ) -> Tuple[bool, Optional[Set[int]], Dict[str, float | int]]:
        """
        Solve the closure problem using randomized top-down greedy strategy on the DAG.
        
        Performs multiple randomized attempts to find a closure with weight as close to k
        as possible without exceeding it. Each attempt removes random source nodes from
        the DAG until the target weight is reached or exceeded.
        
        Args:
            k: Target weight (maximum number of nodes in the closure).
            max_retries: Maximum number of randomized attempts (default: 50).
            max_time_sec: Maximum time allowed for solving in seconds (default: 60.0).
        
        Returns:
            A tuple containing:
            - bool: Always True (solution attempt completed).
            - Optional[Set[int]]: Set of original graph nodes in the best closure found,
                                  or None if no valid closure exists within constraints.
            - Dict[str, float | int]: Statistics dictionary containing:
                - "time" (float): Total elapsed time in seconds.
                - "attempts" (int): Number of attempts performed.
                - "final_weight" (int): Weight of the best closure found (-1 if none found).
                - "ops" (int): Total number of operations performed.
                - "unique_tested" (int): Number of unique states tested.
        """
        start_time: float = time.perf_counter()
        
        visited_states: Set[int] = set()
        op_count: int = 0

        if k >= self.total_weight:
            all_nodes: Set[int] = set(self.original_graph.nodes())
            return True, all_nodes, {
                "time": 0.0,
                "ops": 0,
                "unique_tested": 0,
                "attempts": 0,
                "final_weight": self.total_weight
            }
        
        best_closure: Optional[Set[int]] = None
        best_weight: int = -1
        attempts_done: int = 0
        
        for attempt in range(max_retries):
            attempts_done = attempt + 1
            if (time.perf_counter() - start_time) > max_time_sec:
                break

            current_nodes: Set[int] = set(self.dag.nodes())
            current_weight: int = self.total_weight
            in_degree: Dict[int, int] = self.dag_initial_in_degree.copy()

            sources: List[int] = [u for u in current_nodes if in_degree[u] == 0]

            removed_sequence: List[int] = []

            while current_weight > k:
                if not sources:
                    break
                
                op_count += 1
                
                idx: int = random.randrange(len(sources))
                node_to_remove: int = sources[idx]

                sources[idx] = sources[-1]
                sources.pop()

                current_nodes.remove(node_to_remove)
                current_weight -= self.dag.nodes[node_to_remove]['weight']
                removed_sequence.append(node_to_remove)

                for v in self.dag_adj[node_to_remove]:
                    op_count += 1  # Traversal op
                    if v in current_nodes:
                        in_degree[v] -= 1
                        if in_degree[v] == 0:
                            sources.append(v)

            state_hash: int = hash(frozenset(removed_sequence))
            
            if state_hash in visited_states:
                continue
            
            visited_states.add(state_hash)

            if current_weight <= k:
                if current_weight > best_weight:
                    best_weight = current_weight
                    best_closure = current_nodes.copy()
                if current_weight == k:
                    break

        final_nodes: Set[int] = set()
        if best_closure:
            for supernode in best_closure:
                final_nodes.update(self.scc_mapping[supernode])

        return True, final_nodes, {
            "time": time.perf_counter() - start_time,
            "attempts": attempts_done,
            "final_weight": best_weight,
            "ops": op_count,
            "unique_tested": len(visited_states)
        }