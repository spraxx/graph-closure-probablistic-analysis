import os
import pandas as pd
from src.data_loader import GraphLoader
from src.solvers import ClosureSolver
from src.legacy_solvers import LegacyGreedySolver

# We compare on Medium because Large would take too long for the Old (Legacy) solver
TARGET_FILE = "SWmediumG.txt"

def main():
    if not os.path.exists(TARGET_FILE):
        print(f"File {TARGET_FILE} not found.")
        return

    print(f"--- COMPARISON EXPERIMENT: Project 1 vs Project 2 ---")
    print(f"Loading {TARGET_FILE}...")
    G = GraphLoader.load_graph(TARGET_FILE)
    n = G.number_of_nodes()
    k = n // 2  # Target 50% closure
    
    results = []

    # 1. Run Project 1 (Old Greedy)
    print(f"Running Project 1 (Legacy Greedy)...")
    p1_found, _, p1_stats = LegacyGreedySolver.solve(G, k)
    p1_status = "SUCCESS" if p1_found else "FAILED"
    print(f" -> Result: {p1_status}")
    print(f" -> Time: {p1_stats['time']:.4f}s")
    print(f" -> Reason: {p1_stats.get('status', 'N/A')}")

    # 2. Run Project 2 (New Randomized)
    print(f"\nRunning Project 2 (Randomized Condensation)...")
    solver = ClosureSolver(G) # Preprocessing happens here
    p2_found, _, p2_stats = solver.solve_randomized_top_down(k=k, max_retries=10)
    p2_status = "SUCCESS" if p2_found else "FAILED"
    print(f" -> Result: {p2_status}")
    print(f" -> Time: {p2_stats['time']:.4f}s")

    # 3. Save Data for Report
    comparison_data = [
        {"Algorithm": "Project 1 (Greedy)", "Success": p1_found, "Time": p1_stats['time'], "Notes": p1_stats.get('status')},
        {"Algorithm": "Project 2 (Randomized)", "Success": p2_found, "Time": p2_stats['time'], "Notes": "Handled Cycles via DAG"}
    ]
    
    pd.DataFrame(comparison_data).to_csv("comparison_results.csv", index=False)
    print("\nComparison saved to comparison_results.csv")

if __name__ == "__main__":
    main()