import os
import time
import pandas as pd
from src.data_loader import GraphLoader
from src.solvers import ClosureSolver

# --- Configuration ---
# Add your new dataset here once downloaded (e.g., 'data/cit-HepTh.txt')
DATA_FILES = [
    "data/SWtinyG.txt", 
    "data/SWmediumG.txt", 
    "data/SWlargeG.txt",
    "data/web-Google.txt"
]
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

            # 2. Initialize Solver & Analyze Structure
            print(f" -> Preprocessing (Condensing SCCs)...")
            start_prep = time.perf_counter()
            solver = ClosureSolver(G)
            prep_time = time.perf_counter() - start_prep
            
            # Find Giant Component size
            scc_sizes = [d['weight'] for n, d in solver.dag.nodes(data=True)]
            largest_scc = max(scc_sizes) if scc_sizes else 0
            print(f" -> Preprocessing complete in {prep_time:.4f}s")
            print(f" -> Largest SCC: {largest_scc} nodes ({largest_scc/n:.1%} of graph)")
            
            # 3. Define Targets
            # We include standard targets AND targets specifically around the Giant SCC
            targets = []
            
            # Standard percentages
            for p in [0.25, 0.50, 0.75]:
                targets.append(int(n * p))
            
            # "Smart" targets: Try to get just slightly more than the Giant SCC
            # (This tests if we can add small components TO the giant one)
            if largest_scc < n:
                smart_k = int(largest_scc * 1.05) # Giant + 5%
                if smart_k < n and smart_k not in targets:
                    targets.append(smart_k)
            
            targets = sorted(list(set(targets))) # Remove duplicates and sort

            for k in targets:
                print(f"    -> Target k={k} ({k/n:.1%})...", end="", flush=True)
                
                # Run the Randomized Top-Down Algorithm (Best Effort)
                found, closure, stats = solver.solve_randomized_top_down(k=k, max_retries=20)
                
                final_size = len(closure) if closure else 0
                gap = final_size - k
                
                # Check if we got close
                status = "EXACT" if final_size == k else f"CLOSE ({gap})"
                print(f" Found size {final_size} in {stats['time']:.4f}s")
                
                # Log Data
                results.append({
                    "dataset": filename,
                    "vertices": n,
                    "edges": m,
                    "largest_scc": largest_scc,
                    "k_target": k,
                    "k_achieved": final_size,
                    "gap": gap,
                    "time_sec": stats['time'],
                    "attempts": stats.get('attempts', 0),
                    "prep_time_sec": prep_time
                })
                
        except Exception as e:
            print(f"\n[ERROR] Processing {filename} failed: {e}")
            import traceback
            traceback.print_exc()
        
        print("-" * 60)

    # 4. Save Results
    df = pd.DataFrame(results)
    df.to_csv(RESULTS_FILE, index=False)
    print(f"\nExperiments completed. Results saved to {RESULTS_FILE}")
    print(df[["dataset", "k_target", "k_achieved", "time_sec"]])

if __name__ == "__main__":
    run_experiments()