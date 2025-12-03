import os
import time
import pandas as pd
from src.data_loader import GraphLoader
from src.solvers import ClosureSolver

# [REQ 3c] Import Project 1 Solver for Comparison
# We wrap this in try-except in case the file name varies slightly
try:
    from src.legacy_solver import LegacyGreedySolver
    HAS_LEGACY = True
except ImportError:
    HAS_LEGACY = False
    print("[WARNING] 'src/legacy_solver.py' not found or class name mismatch.")
    print("Comparison column will be empty.")

# Configuration
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
    print(f"Starting Experiments (Project 2 vs Project 1 Comparison)...")
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
            
            # 2. Preprocess (Project 2)
            start_prep = time.perf_counter()
            solver = ClosureSolver(G)
            prep_time = time.perf_counter() - start_prep
            
            # Analyze Structure
            scc_sizes = [d['weight'] for n, d in solver.dag.nodes(data=True)]
            largest_scc = max(scc_sizes) if scc_sizes else 0
            
            # 3. Define Targets
            targets = [int(n * p) for p in [0.25, 0.50, 0.75]]
            if largest_scc > 0 and largest_scc < n:
                smart_k = int(largest_scc * 1.05)
                if smart_k < n and smart_k not in targets:
                    targets.append(smart_k)
            targets = sorted(list(set([t for t in targets if t > 0])))

            for k in targets:
                print(f"    -> Target k={k}...", end="", flush=True)
                
                # --- A. PROJECT 2 (Randomized) ---
                found, closure, stats = solver.solve_randomized_top_down(k=k, max_retries=20)
                p2_size = len(closure) if closure else 0
                
                # --- B. PROJECT 1 (Legacy Greedy) ---
                p1_size = "N/A"
                p1_status = "Skipped"
                l_closure = None  # Initialize variable
                
                if HAS_LEGACY and n < 3000: 
                    try:
                        l_found, l_closure, l_stats = LegacyGreedySolver.solve(G, k)
                        if l_found:
                            p1_size = len(l_closure)
                            p1_status = "Success"
                        else:
                            p1_size = 0
                            p1_status = "Failed (Cycles?)"
                    except Exception as e:
                        p1_status = "Error"
                elif n >= 3000:
                    p1_status = "Too Slow"

                # --- C. CALCULATE SIMILARITY (New Code) ---
                similarity_score = "N/A"
                if p1_status == "Success" and l_closure and closure:
                    set_p1 = set(l_closure)
                    set_p2 = set(closure)
                    intersection = len(set_p1.intersection(set_p2))
                    union = len(set_p1.union(set_p2))
                    if union > 0:
                        similarity_score = intersection / union

                print(f" P2: {p2_size} | P1: {p1_size} | Sim: {similarity_score}")
                
                results.append({
                    "dataset": filename,
                    "k_target": k,
                    "P2_Randomized_Size": p2_size,
                    "P1_Legacy_Size": p1_size,
                    "P1_Status": p1_status,
                    "ops_count": stats['ops'],
                    "time_sec": stats['time'],
                    "Similarity_Score": similarity_score  # <--- Saved here
                })
                
        except Exception as e:
            print(f"\n[ERROR] {filename}: {e}")
            import traceback
            traceback.print_exc()
        
        print("-" * 60)

    # Save
    df = pd.DataFrame(results)
    df.to_csv(RESULTS_FILE, index=False)
    print(f"\nExperiments completed. Results saved to {RESULTS_FILE}")

if __name__ == "__main__":
    run_experiments()