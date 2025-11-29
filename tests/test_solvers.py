import unittest
import networkx as nx
from src.solvers import ClosureSolver

class TestClosureSolver(unittest.TestCase):
    def setUp(self):
        # Create a simple test graph
        # 0 -> 1 -> 2
        # |    ^
        # v    |
        # 3 -> 4
        # SCCs: {0}, {3}, {1, 2, 4}? No.
        # 1->2, 2->?, let's make 1-2-4-1 a cycle.
        self.G = nx.DiGraph()
        self.G.add_edges_from([(0,1), (0,3), (3,4), (4,1), (1,2), (2,4)])
        # Cycle: 1->2->4->1. SCC = {1, 2, 4} (size 3)
        # Node 0 points to 1 and 3. SCC {0} (size 1)
        # Node 3 points to 4. SCC {3} (size 1)
        # DAG: {0} -> {3} -> {1,2,4}
        #           \-> {1,2,4}
        # Weights: {0}:1, {3}:1, {1,2,4}:3. Total 5.
        
        self.solver = ClosureSolver(self.G)

    def test_condensation_weights(self):
        # Check if weights were calculated correctly
        weights = [d['weight'] for n, d in self.solver.dag.nodes(data=True)]
        self.assertIn(3, weights)
        self.assertIn(1, weights)
        self.assertEqual(sum(weights), 5)

    def test_find_closure_exact_k(self):
        # We want closure of size 3. That must be {1, 2, 4}.
        # Removing {0} (src) -> Remainder {3, 1, 2, 4} (size 4). Source is {3}.
        # Remove {3} -> Remainder {1, 2, 4} (size 3).
        success, closure, _ = self.solver.solve_randomized_top_down(k=3)
        self.assertTrue(success)
        self.assertEqual(len(closure), 3)
        self.assertTrue(self.solver.verify_closure(closure))

    def test_impossible_k(self):
        # Size 2 is impossible. 
        # Closures sizes: 
        # {1,2,4} (3)
        # {3,1,2,4} (4)
        # {0,3,1,2,4} (5)
        # Empty (0)
        success, _, _ = self.solver.solve_randomized_top_down(k=2)
        self.assertFalse(success)

if __name__ == '__main__':
    unittest.main()