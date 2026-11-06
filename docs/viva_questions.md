# Viva Voce Examination Guide

**Course:** Design & Analysis of Algorithms (ETCCDA302)  
**University:** K.R. Mangalam University  
**Project:** Mini-Courier Planner  

---

### Q1: How does your parcel prioritization sorting algorithm work?
**Answer:**  
We implemented **Merge Sort**, a classic divide-and-conquer algorithm.
1. **Divide**: The parcel array is recursively halved until sublists of length 1 or 0 remain (base cases).
2. **Conquer & Combine**: Sublists are merged back in sorted order by comparing elements at the front of each sublist using a multi-criteria comparator:
   - Primary: Higher priority value comes first (e.g., Priority 5 before Priority 4).
   - Secondary: Earlier delivery deadline comes first (e.g., 1.5 hrs before 3.0 hrs).
   - Tertiary: Alphabetical parcel ID as a deterministic tie-breaker.
Because Merge Sort is **stable**, parcels with identical keys retain their relative relative arrival order.

---

### Q2: Why was Merge Sort selected instead of Quick Sort or Bubble Sort?
**Answer:**
1. **Guaranteed Worst-Case Performance**: Merge Sort guarantees $O(N \log N)$ time in the worst case, unlike Quick Sort which degrades to $O(N^2)$ when pivots are poorly chosen (e.g., already sorted data).
2. **Stability**: Preserving the relative order of equal-priority parcels is important in dispatching systems.
3. **Bubble Sort Inefficiency**: Bubble Sort is $O(N^2)$, which is unfeasible for large parcel batches.

---

### Q3: What is Dynamic Programming, and what properties must a problem have to use it?
**Answer:**  
Dynamic Programming (DP) is an algorithm design paradigm that solves complex problems by breaking them into overlapping subproblems, solving each subproblem once, and storing their solutions in a table (memoization or tabulation) to prevent redundant recalculation.  
Two key properties required:
1. **Optimal Substructure**: An optimal solution to the problem contains optimal solutions to its subproblems.
2. **Overlapping Subproblems**: The recursive space contains repeated subproblems rather than generating new subproblems at each step.

---

### Q4: Explain the 0/1 Knapsack state, recurrence relation, and table construction.
**Answer:**
- **State Definition**: $DP[i][w]$ represents the maximum delivery benefit/value achievable using a subset of the first $i$ parcels with total weight at most $w$.
- **Base Cases**:
  - $DP[0][w] = 0$ for all $0 \le w \le W$ (0 items yield 0 value).
  - $DP[i][0] = 0$ for all $0 \le i \le N$ (0 capacity holds 0 value).
- **Recurrence Relation**:
  - If $w_i > w$: Item $i$ exceeds current weight limit:
    $$DP[i][w] = DP[i-1][w]$$
  - If $w_i \le w$: Choose maximum between excluding item $i$ and including item $i$:
    $$DP[i][w] = \max(DP[i-1][w], DP[i-1][w - w_i] + v_i)$$
- **Table Construction**: The table is populated row by row from $i=1$ to $N$ and column by column from $w=0$ to $W$.

---

### Q5: Why cannot a parcel be selected more than once in this model?
**Answer:**  
In physical courier logistics, each parcel is a distinct physical package with a unique tracking ID. Once loaded onto the delivery van, it cannot be duplicated. Mathematically, this is modeled by the **0/1 Knapsack** restriction ($x_i \in \{0, 1\}$), where the state transition looks at $DP[i-1][w - w_i]$ (the previous row) rather than $DP[i][w - w_i]$ (which would permit unbounded/fractional repetitions).

---

### Q6: How does Dijkstra's algorithm work?
**Answer:**  
Dijkstra's algorithm finds the shortest path from a single source node to all other nodes in a weighted graph with non-negative edge weights using a greedy strategy:
1. Initialize distance to source as 0, and all other nodes as $\infty$.
2. Maintain a min-priority queue (min-heap) of tentative distances.
3. In each step, extract node $u$ with minimum tentative distance.
4. Relax all outgoing edges $(u, v)$ with weight $w$:
   $$\text{If } \text{dist}[u] + w < \text{dist}[v]: \quad \text{dist}[v] \leftarrow \text{dist}[u] + w, \quad \text{pred}[v] \leftarrow u$$
5. Repeat until the priority queue is empty. Predecessors are backtracked to reconstruct shortest road paths.

---

### Q7: Why does Dijkstra require non-negative edge weights?
**Answer:**  
Dijkstra's greedy choice assumes that once a vertex is extracted from the priority queue, its shortest distance is finalized and will never decrease. If negative edges exist, this greedy property breaks down because traversing through an undiscovered negative edge later could yield a smaller path cost to an already "visited" vertex. (Graphs with negative weights require Bellman-Ford).

---

### Q8: What is the fundamental difference between the Shortest Path Problem and the Travelling Salesman Problem (TSP)?
**Answer:**
- **Shortest Path Problem**:
  - Finds the minimum cost path between two specific vertices (or one to all).
  - Vertices can be bypassed or visited as intermediate hops.
  - Can be solved in polynomial time: $O((V+E)\log V)$ via Dijkstra.
- **Travelling Salesman Problem (TSP)**:
  - Finds the minimum cost cycle that visits **every required node exactly once** and returns to the start.
  - Known to be **NP-hard**; exhaustive search is $O(n!)$ and DP (Held-Karp) is $O(n^2 2^n)$.
  - We use the polynomial-time $O(K^2)$ Nearest Neighbor heuristic to approximate the tour.

---

### Q9: How does Nearest Neighbor choose the next delivery location?
**Answer:**  
At the current location (initially the Depot), the algorithm queries the precomputed Dijkstra shortest path matrix for all remaining **unvisited** delivery destinations and greedily travels to the location that has the minimum distance:
$$v_{\text{next}} = \arg\min_{u \in \text{Unvisited}} \text{dist}(\text{current}, u)$$
It marks $v_{\text{next}}$ as visited, updates the current node, and repeats until all stops are visited.

---

### Q10: Why does the Nearest Neighbor heuristic not guarantee an optimal TSP tour?
**Answer:**  
Nearest Neighbor makes myopic, local greedy choices without considering global consequences. By greedily picking very close locations early, it can leave isolated distant vertices for the end of the tour, forcing an extremely long return edge or bridge traversing the entire map. This is proven empirically in `test_nearest_neighbor_suboptimality` in `tests/test_tsp.py`.

---

### Q11: What is the time and space complexity of every implemented algorithm?
**Answer:**
1. **Merge Sort**: Time $O(N \log N)$ (all cases), Space $O(N)$.
2. **0/1 Knapsack DP**: Time $O(N \cdot W)$, Space $O(N \cdot W)$ (pseudo-polynomial).
3. **Dijkstra**: Time $O((V + E) \log V)$ with min-heap, Space $O(V)$.
4. **Nearest Neighbor TSP**: Time $O(K^2)$ over $K$ delivery locations, Space $O(K)$.

---

### Q12: How was empirical runtime measured for the performance report?
**Answer:**  
Runtimes were measured using Python's high-resolution monotonic timer `time.perf_counter()`.
- File I/O, user interaction, and print formatting were strictly excluded from the timing windows.
- Each algorithm was measured in isolation over multiple trials (3 trials averaged) on synthetic datasets scaled from $N=10$ to $N=500$ to observe true asymptotic complexity trends.
- Outputs were recorded in `results/performance_results.csv` and plotted in `results/runtime_chart.png`.

---

### Q13: How does the system handle invalid, malformed, or unreachable data?
**Answer:**
1. **Input Validation**: `utils/validation.py` validates schema and domain constraints (positive weights, non-negative capacity, non-negative road distances, valid foreign key references). Raises descriptive `ValidationError` exceptions instead of crashing.
2. **Unreachable Locations**: If the road network is disconnected, Dijkstra sets the distance to $\infty$. The TSP solver detects this condition, flags the unreachable stops in `unreachable_locations`, and completes a safe route for the reachable subset without hanging or hallucinating paths.
3. **Zero Capacity / Empty Input**: Returns an empty selection manifest cleanly ($0\text{ kg}$, $0\text{ Rs}$, route at depot).

