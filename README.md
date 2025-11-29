# Randomized Algorithms for the k-Vertex Closure Problem

This project implements randomized algorithms to solve the **k-Vertex Closure Problem** in directed graphs. It is designed to handle large datasets efficiently by leveraging graph condensation and randomized greedy heuristics.

## 📌 Problem Description
**Goal:** Given a directed graph $G(V, E)$, find a subset of vertices $C \subseteq V$ with size $|C| = k$ such that $C$ is a **closure**.

A set $C$ is a closure if there are **no edges leaving $C$** (i.e., for every edge $(u, v)$, if $u \in C$, then $v \in C$).

## 🚀 Algorithm Approach
To solve this efficiently for large graphs (up to millions of nodes), this project uses a **Randomized Top-Down Greedy Strategy** on a Condensed Graph:

1.  **Condensation (Pre-processing):**
    The graph is condensed into a **Directed Acyclic Graph (DAG)** of its Strongly Connected Components (SCCs). Each node in the DAG represents an SCC and has a weight equal to the number of vertices in that SCC. This handles cycles naturally, which often trap standard greedy algorithms.

2.  **Randomized Greedy Reduction:**
    -   Start with the full graph (which is a valid closure).
    -   Identify "Source" nodes in the DAG (nodes with in-degree 0 within the current active set). Removing a source node preserves the closure property of the remaining set.
    -   **Random Step:** Randomly select one of the available source nodes to remove.
    -   Repeat until the total weight of the remaining nodes equals $k$.
    -   If the algorithm gets stuck or misses the target $k$, it restarts (Random Restart).

## 📂 Project Structure

```text
graph-closure-randomized/
├── src/
│   ├── __init__.py
│   ├── data_loader.py    # Parsers for SW*.txt and .gml formats
│   └── solvers.py        # Implementation of the Randomized Closure Solver
├── tests/
│   ├── __init__.py
│   └── test_solvers.py   # Unit tests to ensure algorithm correctness
├── main.py               # Entry point to run experiments on all datasets
├── SWtinyG.txt           # Benchmark dataset (Small)
├── SWmediumG.txt         # Benchmark dataset (Medium)
├── SWlargeG.txt          # Benchmark dataset (Large)
└── README.md             # Project documentation
```

## 🛠️ Installation

This project is managed using modern Python tooling. You can set it up using `uv` (recommended for speed and lock-file consistency) or standard `pip`.

### Prerequisites
* Python 3.9+
* Git

### Option 1: Using `uv` (Recommended)
This project includes a `uv.lock` file to ensure deterministic builds.

1. **Install uv** (if not already installed):
```bash
    pip install uv
```
2. **Sync dependencies and environment:**
```bash
    uv sync
```
3. **Run the project:**
```bash
    uv run main.py
```
### Option 2: Using standard `pip`
If you prefer a traditional virtual environment:

1. **Create and activate a virtual environment:**
```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
```
2. **Install dependencies:**
```bash
    pip install -e .
    # Or manually: pip install networkx matplotlib numpy pandas notebook
```
## 💻 Usage

### Running Experiments
The core experimental logic is contained in `main.py`. This script loads the graph datasets from the `data/` folder, runs the randomized closure algorithm for various values of $k$, and logs the performance.
```bash
    # If using uv
    uv run main.py

    # If using standard python
    python main.py
```
### Interactive Demo
To visualize the graph structures and step through the algorithm logic interactively, use the provided Jupyter Notebook:

    jupyter notebook project2_demo.ipynb

## 🧪 Testing

Unit tests are located in the `tests/` directory. These ensure that the graph condensation logic and the greedy solver adhere to the closure properties.

To run the tests:

    python -m unittest discover tests

## 📊 Results

When running `main.py`, the experiment data is exported to `experiment_results.csv`. This file contains the following metrics for each run:

* **Graph Name:** The dataset used (e.g., `SWtinyG`).
* **Target Size ($k$):** The desired number of vertices in the closure.
* **Success:** Whether the algorithm successfully found a closure of size $k$.
* **Iterations/Time:** Efficiency metrics for the randomized approach.

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).