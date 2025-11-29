import os
import time
import pandas as pd
from src.data_loader import GraphLoader
from src.solvers import ClosureSolver

# --- Configuration ---
DATA_FILES = ["data/SWtinyG.txt", "data/SWmediumG.txt", "data/SWlargeG.txt"]
RESULTS_FILE = "experiment_results.csv"

def run_experiments():
    results = []
    
    print(f"{'='*60}")
    print(f"Starting Experiments on {len(DATA_FILES)} files...")
    print(f"{'='*60}\n")

    for filename in DATA_FILES:
        filepath = os.path.join(os.getcwd(), filename)
        
        if not os.path.exists(filepath):
            print(f"[WARNING] File not found: {filename}. Skipping.")
            continue
            
        print(f"Loading {filename}...")
        try:
            # 1. Load Graph
            G = GraphLoader.load_graph(filepath)
            n = G.number_of_nodes()
            m = G.number_of_edges()
            print(f" -> Loaded: {n} vertices, {m} edges.")

            # 2. Initialize Solver (Preprocessing SCCs happens here)
            print(f" -> Preprocessing (Condensing SCCs)...")
            start_prep = time.perf_counter()
            solver = ClosureSolver(G)
            prep_time = time.perf_counter() - start_prep
            print(f" -> Preprocessing complete in {prep_time:.4f}s")
            
            # 3. Define Targets (Test different sizes of k)
            # Testing 25%, 50%, 75% of N
            fractions = [0.25, 0.50, 0.75]
            
            for frac in fractions:
                k = int(n * frac)
                print(f"    -> Running Solver for k={k} ({int(frac*100)}%)...", end="", flush=True)
                
                # Run the Randomized Top-Down Algorithm
                # For SWlargeG, we might want fewer retries if it's slow, 
                # but this algorithm is O(N) per retry so 50 is fine.
                found, closure, stats = solver.solve_randomized_top_down(k=k, max_retries=50)
                
                status = "SUCCESS" if found else "FAILURE"
                print(f" {status} in {stats['time']:.4f}s ({stats.get('attempts', 0)} attempts)")
                
                # Log Data
                results.append({
                    "dataset": filename,
                    "vertices": n,
                    "edges": m,
                    "k_target": k,
                    "found": found,
                    "time_sec": stats['time'],
                    "attempts": stats.get('attempts', 0),
                    "prep_time_sec": prep_time,
                    "closure_size": len(closure) if closure else 0
                })
                
        except Exception as e:
            print(f"\n[ERROR] Processing {filename} failed: {e}")
        
        print("-" * 60)

    # 4. Save Results
    df = pd.DataFrame(results)
    df.to_csv(RESULTS_FILE, index=False)
    print(f"\nExperiments completed. Results saved to {RESULTS_FILE}")
    print(df)

if __name__ == "__main__":
    run_experiments()

