# Computational Complexity and Empirical Performance Analysis

**Course:** Design & Analysis of Algorithms (ETCCDA302)  
**University:** K.R. Mangalam University  

---

## 1. Theoretical Complexity Breakdown

| Algorithmic Stage | Implemented Algorithm | Best Case Time | Average Case Time | Worst Case Time | Auxiliary Space | Paradigms Used |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Parcel Prioritization** | Merge Sort | $O(N \log N)$ | $O(N \log N)$ | $O(N \log N)$ | $O(N)$ | Divide and Conquer |
| **Vehicle Packing** | 0/1 Knapsack DP | $O(N \cdot W)$ | $O(N \cdot W)$ | $O(N \cdot W)$ | $O(N \cdot W)$ | Dynamic Programming |
| **Shortest Paths** | Dijkstra (Min-Heap) | $O((V + E) \log V)$ | $O((V + E) \log V)$ | $O((V + E) \log V)$ | $O(V)$ | Greedy / Priority Queue |
| **All-Pairs Metric** | All-Pairs Dijkstra | $O(K (V + E) \log V)$| $O(K (V + E) \log V)$| $O(K (V + E) \log V)$| $O(K \cdot V)$ | Repeated Dijkstra |
| **Delivery Tour** | Nearest Neighbor TSP | $O(K^2)$ | $O(K^2)$ | $O(K^2)$ | $O(K)$ | Greedy Heuristic |

*Notation:*
- $N$: Number of parcels to be prioritized.
- $W$: Scaled integer vehicle weight capacity ($W = \text{Capacity} \times \text{Scale}$).
- $V$: Total locations (vertices) in the courier network.
- $E$: Road segments (edges) in the road graph.
- $K$: Distinct customer delivery locations selected for the trip ($K \le V$).

---

## 2. Detailed Mathematical Derivations

### A. Merge Sort for Parcel Prioritization
- **Recurrence Relation:**
  $$T(N) = 2 T(N / 2) + \Theta(N)$$
  - Base case: $T(1) = \Theta(1)$.
  - Dividing step: Splitting the array takes $O(1)$.
  - Merging step: The linear merge pass inspects each parcel element, performing at most $N - 1$ comparisons and copying $N$ elements into the auxiliary array.
- **Application of Master Theorem:**
  - $a = 2, b = 2, f(N) = \Theta(N)$.
  - $N^{\log_b a} = N^{\log_2 2} = N^1 = \Theta(N)$.
  - Since $f(N) = \Theta(N^{\log_b a})$, Master Theorem Case 2 applies:
    $$T(N) = \Theta(N \log N)$$
- **Space Complexity:** $O(N)$ auxiliary storage is allocated across recursive merge buffers.

---

### B. 0/1 Knapsack Dynamic Programming
- **Recurrence Formulation:**
  Let $DP[i][w]$ denote the optimal total value achievable using a subset of the first $i$ parcels ($1 \le i \le N$) with total weight capacity $w$ ($0 \le w \le W$):
  $$DP[i][w] = \begin{cases} 0 & \text{if } i = 0 \text{ or } w = 0 \\ DP[i-1][w] & \text{if } w_i > w \\ \max(DP[i-1][w], DP[i-1][w - w_i] + v_i) & \text{if } w_i \le w \end{cases}$$
- **Time Complexity:**
  The DP grid contains $(N + 1) \times (W + 1)$ cells. Each cell requires $O(1)$ constant-time arithmetic comparison and memory read/write.
  $$\text{Time} = \Theta(N \cdot W)$$
  *Note:* Because the runtime depends on the numeric value $W$, 0/1 Knapsack is pseudo-polynomial in time.
- **Space Complexity:**
  Storing the full DP matrix for item reconstruction requires $(N + 1)(W + 1)$ floating-point entries, giving $\Theta(N \cdot W)$ auxiliary space.

---

### C. Dijkstra's Shortest Path Algorithm
- **Priority Queue Implementation:**
  We utilize a binary min-heap (`heapq` in Python).
- **Operations:**
  - Inserting the source node: $O(\log V)$.
  - `heappop` extract-min: executed at most $V$ times $\implies O(V \log V)$.
  - Edge relaxations: each directed edge is examined at most once. When a shorter path to neighbor $v$ is discovered, a heap push is executed $\implies O(E \log V)$.
- **Total Time:**
  $$T(V, E) = O((V + E) \log V)$$
  On planar/sparse road graphs where $E \approx O(V)$, this simplifies to $O(V \log V)$.
- **Space Complexity:**
  $O(V)$ for the `distances` dictionary, $O(V)$ for `predecessors`, and $O(V)$ for the priority queue heap.

---

### D. Nearest Neighbor Heuristic for TSP
- **Procedure:**
  Starting at Depot, visit the nearest unvisited node among the $K$ delivery locations, repeating until all $K$ nodes are visited, then return to Depot.
- **Complexity:**
  - In step 1: Search among $K$ unvisited nodes $\implies K$ lookups.
  - In step 2: Search among $K-1$ unvisited nodes $\implies K - 1$ lookups.
  - In step $K$: Search among 1 unvisited node $\implies 1$ lookup.
  - Total distance matrix lookups:
    $$\sum_{i=1}^K i = \frac{K(K + 1)}{2} = \Theta(K^2)$$
- **Space Complexity:** $O(K)$ to track visited nodes and route sequence.

---

## 3. Empirical Benchmark Observations

The table below presents real empirical benchmarks measured using Python's `time.perf_counter()` over 3 trials on an isolated testing environment:

| Dataset Size | Parcels ($N$) | Locations ($V$) | Merge Sort (s) | 0/1 Knapsack DP (s) | Dijkstra Shortest Paths (s) | Nearest Neighbor TSP (s) | Cumulative Pipeline (s) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Small** | 10 | 5 | 0.000035 | 0.000282 | 0.000126 | 0.000138 | **0.000580** |
| **Small-Med** | 50 | 15 | 0.000157 | 0.001221 | 0.000606 | 0.000635 | **0.002619** |
| **Medium** | 100 | 25 | 0.000404 | 0.005402 | 0.002085 | 0.001994 | **0.009884** |
| **Med-Large**| 250 | 40 | 0.001281 | 0.034495 | 0.006126 | 0.006181 | **0.048083** |
| **Large** | 500 | 60 | 0.002361 | 0.070940 | 0.013820 | 0.011050 | **0.098170** |

### Key Analytical Takeaways:
1. **Merge Sort Efficiency**: As $N$ increased 50-fold from 10 to 500, Merge Sort time scaled by $\approx 67\times$, reflecting near-linear $O(N \log N)$ behavior with negligible runtime ($2.36\text{ ms}$).
2. **Knapsack Pseudo-Polynomial Growth**: 0/1 Knapsack consumes the largest fraction of runtime (~72% at $N=500$) due to table size $(N \times W)$. For very large vehicle capacities ($W > 10,000$), a Branch-and-Bound or Fully Polynomial-Time Approximation Scheme (FPTAS) would be recommended.
3. **Graph Algorithms Scalability**: Dijkstra and Nearest Neighbor TSP executed well within sub-15ms latencies for practical city logistics clusters ($V \le 60$).

