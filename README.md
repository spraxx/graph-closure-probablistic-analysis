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