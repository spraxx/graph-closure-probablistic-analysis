import os
import time
import traceback
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any

from src.data_loader import GraphLoader
from src.solvers import ClosureSolver

try:
    from src.legacy_solver import LegacyGreedySolver

    HAS_LEGACY: bool = True
except ImportError:
    HAS_LEGACY = False
    print("[WARNING] 'src/legacy_solver.py' not found. Comparison skipped.")

BASE_DIR: Path = Path(__file__).parent
DATA_DIR: Path = BASE_DIR / "data"
RESULTS_FILE: Path = BASE_DIR / "experiment_results.csv"

DATA_FILENAMES: List[str] = [
    "SWtinyG.txt",
    "SWmediumG.txt",
    "SWlargeG.txt",
    "web-Google.txt",
]


def run_experiments() -> None:
    """
    Run comparative experiments between Project 2 (ClosureSolver) and Project 1 (LegacyGreedySolver).

    For each dataset and target k value, this function:
    - Loads the graph and prepares the ClosureSolver
    - Runs the randomized top-down solver (Project 2)
    - Runs the legacy greedy solver on compatible datasets (Project 1)
    - Computes similarity scores between solutions
    - Saves all results to a CSV file

    Skips Project 1 execution if the legacy solver is unavailable or if the graph
    has more than 3000 nodes (performance limitation).

    Results are saved to: experiment_results.csv
    """
    results: List[Dict[str, Any]] = []

    print(f"{'=' * 60}")
    print(f"Starting Experiments (Project 2 vs Project 1 Comparison)")
    print(f"{'=' * 60}\n")

    if not DATA_DIR.exists():
        print(f"[ERROR] Data directory not found at: {DATA_DIR}")
        return

    for filename in DATA_FILENAMES:
        filepath: Path = DATA_DIR / filename

        if not filepath.exists():
            print(f"[WARNING] File not found: {filename}. Skipping.")
            continue

        print(f"Loading {filename}...")
        try:
            G = GraphLoader.load_graph(str(filepath))
            n: int = G.number_of_nodes()

            start_prep: float = time.perf_counter()
            solver: ClosureSolver = ClosureSolver(G)
            prep_time: float = time.perf_counter() - start_prep

            scc_sizes: List[int] = [d["weight"] for n, d in solver.dag.nodes(data=True)]
            largest_scc: int = max(scc_sizes) if scc_sizes else 0

            targets: List[int] = [int(n * p) for p in [0.25, 0.50, 0.75]]

            if 0 < largest_scc < n:
                smart_k: int = int(largest_scc * 1.05)
                if smart_k < n and smart_k not in targets:
                    targets.append(smart_k)

            targets = sorted(list(set([t for t in targets if t > 0])))

            for k in targets:
                print(f"    -> Target k={k:<5} | ", end="", flush=True)

                found: bool
                closure: set | None
                stats: Dict[str, Any]
                found, closure, stats = solver.solve_randomized_top_down(
                    k=k, max_retries=20
                )
                p2_size: int = len(closure) if closure else 0

                p1_size: int | str = "N/A"
                p1_status: str = "Skipped"
                l_closure: set | None = None

                if HAS_LEGACY and n < 3000:
                    try:
                        l_found: bool
                        l_stats: Dict[str, Any]
                        l_found, l_closure, l_stats = LegacyGreedySolver.solve(G, k)
                        if l_found:
                            p1_size = len(l_closure)
                            p1_status = "Success"
                        else:
                            p1_size = 0
                            p1_status = "Failed"
                    except Exception:
                        p1_status = "Error"
                elif n >= 3000:
                    p1_status = "Too Slow"

                # Compute similarity score (Jaccard index)
                similarity_score: float | str = "N/A"
                if p1_status == "Success" and l_closure and closure:
                    set_p1: set = set(l_closure)
                    set_p2: set = set(closure)
                    intersection: int = len(set_p1.intersection(set_p2))
                    union: int = len(set_p1.union(set_p2))
                    if union > 0:
                        similarity_score = round(intersection / union, 4)

                print(
                    f"P2 Size: {p2_size:<5} | P1 Size: {p1_size:<5} | Sim: {similarity_score}"
                )

                # Append result record
                results.append(
                    {
                        "dataset": filename,
                        "k_target": k,
                        "P2_Randomized_Size": p2_size,
                        "P1_Legacy_Size": p1_size,
                        "P1_Status": p1_status,
                        "ops_count": stats.get("ops", 0),
                        "time_sec": stats.get("time", 0),
                        "prep_time_sec": prep_time,
                        "similarity_score": similarity_score,
                    }
                )

        except Exception as e:
            print(f"\n[ERROR] Processing {filename}: {e}")
            traceback.print_exc()

        print("-" * 60)

    if results:
        df: pd.DataFrame = pd.DataFrame(results)
        df.to_csv(RESULTS_FILE, index=False)
        print(f"\nExperiments completed. Results saved to {RESULTS_FILE}")
    else:
        print("\nNo results generated.")


if __name__ == "__main__":
    run_experiments()
