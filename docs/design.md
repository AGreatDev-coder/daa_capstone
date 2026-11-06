# System Architecture and Design Specification

**Course:** Design & Analysis of Algorithms (ETCCDA302)  
**University:** K.R. Mangalam University  
**Project:** Mini-Courier Planner  

---

## 1. Problem Formulation & Academic Scope
The Mini-Courier Planner is a modular algorithmic decision system designed to solve a multi-stage logistics dispatch problem:
1. **Parcel Prioritization**: Sorting incoming parcels by operational urgency and delivery deadline.
2. **Vehicle Packing**: Selecting the highest-value subset of parcels subject to a rigid vehicle payload limit (0/1 Knapsack).
3. **Shortest Path Computation**: Computing true minimum-distance traversal trajectories between depots and customer stops (Dijkstra's Algorithm).
4. **Complete Delivery Routing**: Ordering delivery stops and constructing a closed courier tour starting and ending at the depot (Nearest Neighbor TSP heuristic).

```
+-------------------------------------------------------------------------+
|                              INPUT DATA                                 |
|  - parcels.json (ID, destination, weight, value, priority, deadline)   |
|  - locations.json (ID, name, is_depot)                                 |
|  - roads.json (u, v, distance_km >= 0)                                 |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                  [STAGE 1] VALIDATION & INTEGRITY CHECK                 |
|  - Positive weights/capacity, non-negative edges, valid references      |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|             [STAGE 2] PARCEL PRIORITIZATION (MERGE SORT)                |
|  - Stable divide-and-conquer sorting                                    |
|  - Rule: Priority DESC -> Deadline ASC -> ID ASC                        |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|            [STAGE 3] VEHICLE PACKING (0/1 KNAPSACK DP)                  |
|  - Maximize profit subject to total weight <= vehicle capacity          |
|  - Table DP[i][w] = max(without, with)                                  |
|  - Backtracking reconstruction                                          |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|             [STAGE 4] DESTINATION EXTRACTION & DEDUPLICATION            |
|  - Filter destinations of chosen parcels; deduplicate multi-parcel stops|
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|               [STAGE 5] SHORTEST PATHS (DIJKSTRA'S ALGORITHM)           |
|  - Min-heap priority queue single-source shortest path calculations     |
|  - Computes all-pairs shortest paths & predecessor road segments        |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|            [STAGE 6] DELIVERY TOUR (NEAREST NEIGHBOR TSP)               |
|  - Greedy tour sequencing over Dijkstra distance matrix                 |
|  - Stitches multi-hop road segments into continuous expanded route      |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|             [STAGE 7] DISPATCH MANIFEST & PERFORMANCE BENCHMARK         |
|  - Final manifest with payload % and kilometers                         |
|  - CSV timing log & matplotlib runtime scaling curves                   |
+-------------------------------------------------------------------------+
```

---

## 2. Phase-by-Phase Requirement Mapping

### Phase 1: Courier Problem Design and Planning
- **Input Data Model**: Stored in clean JSON files (`data/locations.json`, `data/parcels.json`, `data/roads.json`).
- **Validation**: Enforced via `utils/validation.py`. Rejects negative road distances, non-existent node references, duplicate IDs, and invalid vehicle capacities before algorithmic processing.
- **Graph Representation**: `RoadGraph` uses an adjacency list structure `Dict[str, Dict[str, float]]` ensuring space efficiency $O(V + E)$ and fast neighbor iteration for Dijkstra.

### Phase 2: Package Prioritization and Vehicle Packing
- **Algorithm 1 - Merge Sort (`algorithms/sorting.py`)**:
  - Implements recursive divide-and-conquer without Python standard library shortcuts.
  - Multi-tier deterministic comparison key:
    $$\text{Priority } p_1 > p_2 \implies p_1 \prec p_2$$
    $$\text{If } p_1 = p_2 \land \text{Deadline } d_1 < d_2 \implies p_1 \prec p_2$$
    $$\text{If } p_1 = p_2 \land d_1 = d_2 \land \text{ID } id_1 < id_2 \implies p_1 \prec p_2$$
- **Algorithm 2 - 0/1 Knapsack Dynamic Programming (`algorithms/knapsack.py`)**:
  - Prioritized parcels are fed into the DP state machine.
  - Integer weight discretization with configurable scaling factor ($S = 10$) enables exact dynamic programming with decimal parcel weights (e.g., $1.5\text{ kg} \rightarrow 15\text{ units}$).
  - Table construction: $(N + 1) \times (W \cdot S + 1)$ dimensions.
  - Reconstruction backtrack traces which items were packed to deliver the optimal total value.

### Phase 3: Route Maker and Graph Processing
- **Algorithm 3 - Dijkstra's Shortest Path (`algorithms/dijkstra.py`)**:
  - Employs a binary min-heap (`heapq`) achieving $O((V + E)\log V)$ runtime.
  - Reconstructs intermediate road sequences using a predecessor map.
  - Precomputes shortest pairwise paths for all delivery stops plus the depot.
- **Algorithm 4 - Nearest Neighbor TSP Approximation (`algorithms/tsp.py`)**:
  - Solves the NP-hard TSP tour using a greedy heuristic.
  - At each stop, queries the Dijkstra distance matrix to travel to the closest unvisited location.
  - Automatically completes the round-trip tour back to the warehouse.
  - Stitches individual road segments into the full expanded route (e.g., `DEPOT -> LOC_B -> LOC_C -> LOC_E`).

### Phase 4: Performance Testing and Optimization
- Evaluates algorithm scalability across 5 input sizes: $N \in \{10, 50, 100, 250, 500\}$.
- Isolated timings using high-resolution monotonic timer `time.perf_counter()`.
- Automated export to `results/performance_results.csv` and visualization via `results/runtime_chart.png`.

### Phase 5: Final Demonstration and Reporting
- Standalone execution from command line with verbose diagnostics and dispatch manifest.
- Comprehensive unit and integration test suite (40 test cases) ensuring 100% correctness across edge cases.

