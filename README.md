# Mini-Courier Planner

**Course:** Design & Analysis of Algorithms (ETCCDA302)  
**Program:** B.Tech Computer Science & Engineering  
**University:** K.R. Mangalam University  
**Capstone Type:** Algorithmic Implementation, Performance Benchmarking, and System Integration  

---

## 1. Project Overview

The **Mini-Courier Planner** is an algorithmic courier dispatch and route planning engine implemented in Python 3. The system solves the logistics challenge of dispatching a delivery vehicle from a central depot by systematically answering four core algorithmic questions:

1. **Which parcels should be prioritized?**  
   Sorted using **Merge Sort** ($O(N \log N)$) based on urgency, deadline, and parcel ID.
2. **Which parcels should be loaded onto the vehicle for maximum benefit?**  
   Optimized using **0/1 Knapsack Dynamic Programming** ($O(N \cdot W)$) to pack the highest value of goods within the vehicle's payload capacity.
3. **What is the true shortest travel path between any two locations?**  
   Computed via **Dijkstra's Algorithm** with a binary min-heap ($O((V + E) \log V)$) on a weighted non-negative road network.
4. **In what order should the driver visit the chosen customer stops?**  
   Sequenced using the **Nearest Neighbor TSP Approximation Heuristic** ($O(K^2)$), utilizing the Dijkstra distance matrix and expanding the tour into actual road segments.

---

## 2. Project Architecture & Directory Structure

```
Mini-Courier-Planner/
│
├── main.py                     # Primary CLI application entry point
├── README.md                   # Comprehensive project documentation
├── requirements.txt            # Python dependencies (matplotlib)
│
├── data/                       # Sample datasets (JSON format)
│   ├── locations.json          # 8 City sectors & Central Distribution Hub
│   ├── parcels.json            # 10 Multi-attribute sample parcels
│   └── roads.json              # 14 Weighted road network edges (in km)
│
├── algorithms/                 # Core DAA algorithm implementations
│   ├── __init__.py
│   ├── sorting.py              # Divide-and-Conquer Merge Sort
│   ├── knapsack.py             # 0/1 Knapsack Dynamic Programming
│   ├── dijkstra.py             # Dijkstra Single-Source & All-Pairs Shortest Paths
│   └── tsp.py                  # Nearest Neighbor TSP Tour & Path Expansion
│
├── utils/                      # Helper utilities and data modeling
│   ├── __init__.py
│   ├── models.py               # Dataclasses: Location, Parcel, RoadEdge, RoadGraph
│   ├── validation.py           # Robust input checking and domain constraint enforcement
│   ├── data_loader.py          # JSON loader, serializer, and graph builder
│   └── performance.py          # Benchmarking engine across N=10 to N=500
│
├── results/                    # Performance outputs and execution records
│   ├── performance_results.csv # Empirical timing measurements across 5 dataset sizes
│   ├── runtime_chart.png       # Matplotlib visualization of algorithmic scaling curves
│   └── screenshots/
│       ├── execution_trace.txt # Full console trace of main application execution
│       └── benchmark_trace.txt # Full console trace of performance benchmarking
│
├── docs/                       # Academic documentation & viva preparation
│   ├── design.md               # System design & Phase 1-5 specification mapping
│   ├── complexity_analysis.md  # Detailed time/space complexity proofs and master theorem
│   ├── test_cases.md           # 40-test verification matrix covering all edge cases
│   └── viva_questions.md       # Comprehensive viva voce exam preparation guide
│
└── tests/                      # Automated unit and integration test suite
    ├── test_validation.py      # Input integrity, negative weights, missing references
    ├── test_sorting.py         # Merge sort edge cases, stability, tie-breaking
    ├── test_knapsack.py        # 0/1 Knapsack capacity boundaries and decimal weights
    ├── test_dijkstra.py        # Shortest paths, unreachable components, zero edges
    ├── test_tsp.py             # NN approximation, return-to-depot, suboptimality proof
    └── test_integration.py     # End-to-end pipeline invariants and constraints
```

---

## 3. Algorithm Implementation Details

### A. Parcel Prioritization — Merge Sort
- **File:** `algorithms/sorting.py`
- **Paradigm:** Divide-and-Conquer
- **Time Complexity:** $\Theta(N \log N)$ (Best, Average, Worst)
- **Space Complexity:** $O(N)$ auxiliary space
- **Comparator Priority:**
  1. Priority level descending (e.g., 5 is more urgent than 4).
  2. Deadline ascending (earlier delivery window first).
  3. Parcel ID ascending (alphabetical tie-breaker for deterministic output).

### B. Vehicle Packing — 0/1 Knapsack (Dynamic Programming)
- **File:** `algorithms/knapsack.py`
- **Paradigm:** Dynamic Programming (Tabulation)
- **Time Complexity:** $O(N \cdot W)$ (where $W$ is scaled vehicle capacity)
- **Space Complexity:** $O(N \cdot W)$
- **Recurrence Formulation:**
  $$DP[i][w] = \begin{cases} DP[i-1][w] & \text{if } w_i > w \\ \max(DP[i-1][w], DP[i-1][w - w_i] + v_i) & \text{if } w_i \le w \end{cases}$$
- **Reconstruction:** Backtracks from $DP[N][W]$ down to $DP[0][0]$ to extract the optimal parcel subset. Handles fractional/decimal weights via configurable scaling factor.

### C. Shortest Path Routing — Dijkstra's Algorithm
- **File:** `algorithms/dijkstra.py`
- **Paradigm:** Greedy with Min-Heap Priority Queue
- **Time Complexity:** $O((V + E) \log V)$
- **Space Complexity:** $O(V)$
- **Capability:** Computes shortest path distance and predecessor tracking; handles disconnected/unreachable nodes returning distance $\infty$. Rejects negative edge weights.

### D. Delivery Route Sequencing — Nearest Neighbor TSP
- **File:** `algorithms/tsp.py`
- **Paradigm:** Greedy Approximation Heuristic
- **Time Complexity:** $O(K^2)$ (where $K$ is the number of distinct delivery stops)
- **Space Complexity:** $O(K)$
- **Capability:** Traverses from the depot through all required delivery destinations and returns to the depot. Uses Dijkstra's shortest paths as the underlying metric, and stitches multi-hop road segments into a complete expanded route.

---

## 4. Setup and Installation

### Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Standard library modules: `json`, `heapq`, `dataclasses`, `typing`, `time`, `csv`, `random`, `unittest`, `argparse`
- Third-party library for plotting: `matplotlib`

### Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 5. Execution Guide

### Launch the Interactive Web Dashboard (Streamlit)
Launch the interactive web UI with real-time visual road network graph, vehicle capacity sliders, dynamic knapsack packing, and route tour animations:
```bash
streamlit run app.py
```

### Run the CLI Pipeline (Terminal Output)
Executes the full pipeline on sample data (`data/`), showing all phases in terminal:
```bash
python main.py
```

### Verbose Mode (Displays DP Table Snippets & Dijkstra Route Matrices)
```bash
python main.py --verbose
```

### Custom Vehicle Capacity & Configurable Depot
```bash
python main.py --depot DEPOT --capacity 30.0
```

### One-Way Trip (Do Not Return to Depot)
```bash
python main.py --no-return
```

### Run Performance Benchmarking Suite
Runs benchmark tests across $N \in \{10, 50, 100, 250, 500\}$, updates `results/performance_results.csv`, and renders `results/runtime_chart.png`:
```bash
python main.py --benchmark
# Or run directly:
python utils/performance.py
```

---

## 6. Sample Execution Output

```text
================================================================================
                    MINI-COURIER PLANNER (DAA CAPSTONE)
              Algorithmic Parcel Dispatch and Route Optimization
================================================================================

--------------------------------------------------------------------------------
 [PHASE 1] DATA LOADING & INTEGRITY VERIFICATION
--------------------------------------------------------------------------------
[*] Depot Location         : DEPOT
[*] Total Locations Loaded : 8
[*] Total Road Nodes       : 8
[*] Total Parcels Loaded   : 10

Parcel ID  | Destination | Weight (kg)  | Value (Rs)   | Priority   | Deadline (hrs)
------------------------------------------------------------------------------
P01        | LOC_A      | 3.0          | 45.0         | 4          | 2.0           
P02        | LOC_B      | 5.0          | 80.0         | 5          | 1.5           
...

--------------------------------------------------------------------------------
 [PHASE 2A] PARCEL PRIORITIZATION (ALGORITHM: MERGE SORT)
 Rule: Higher Priority -> Earlier Deadline -> Deterministic ID Tie-breaker
--------------------------------------------------------------------------------
[+] Total Divide-and-Conquer Comparisons Performed: 23

Rank   | Parcel ID  | Destination | Priority   | Deadline   | Weight   | Value   
--------------------------------------------------------------------------
1      | P09        | LOC_A      | 5          | 1.0        | 1.5      | 30.0    
2      | P02        | LOC_B      | 5          | 1.5        | 5.0      | 80.0    
3      | P05        | LOC_E      | 5          | 2.5        | 6.0      | 95.0    
4      | P01        | LOC_A      | 4          | 2.0        | 3.0      | 45.0    
5      | P06        | LOC_B      | 4          | 3.0        | 3.5      | 60.0    
6      | P07        | LOC_F      | 4          | 3.5        | 7.0      | 110.0   
...

--------------------------------------------------------------------------------
 [PHASE 2B] VEHICLE PACKING (ALGORITHM: 0/1 KNAPSACK DYNAMIC PROGRAMMING)
 Vehicle Maximum Weight Capacity: 25.0 kg
--------------------------------------------------------------------------------
[+] Optimal Subset Selected   : ['P09', 'P02', 'P05', 'P06', 'P07', 'P04']
[+] Total Packed Weight        : 25.0 / 25.0 kg (100.0% capacity utilized)
[+] Total Delivery Value Earned: Rs. 410.00

--------------------------------------------------------------------------------
 [PHASE 3C] DELIVERY TOUR SEQUENCING (ALGORITHM: NEAREST NEIGHBOR TSP)
 Approximation heuristic with Dijkstra distance matrix
--------------------------------------------------------------------------------
[*] Planned Stop Order : DEPOT -> LOC_A -> LOC_B -> LOC_E -> LOC_F -> LOC_D -> DEPOT
[*] Expanded Road Path : DEPOT -> LOC_A -> LOC_B -> LOC_C -> LOC_E -> LOC_F -> LOC_E -> LOC_D -> LOC_A -> DEPOT
[*] Total Trip Distance: 33.00 km
[*] Returned to Depot  : True

=================================================================================
                           FINAL COURIER DISPATCH MANIFEST
=================================================================================
 Vehicle Capacity       : 25.0 kg
 Total Weight Loaded    : 25.0 kg (100.0% utilized)
 Total Parcels Loaded   : 6
 Total Delivery Revenue : Rs. 410.00
 Total Travel Distance  : 33.00 km
 Planned Tour Sequence  : DEPOT -> LOC_A -> LOC_B -> LOC_E -> LOC_F -> LOC_D -> DEPOT
 Expanded Road Segments : DEPOT -> LOC_A -> LOC_B -> LOC_C -> LOC_E -> LOC_F -> LOC_E -> LOC_D -> LOC_A -> DEPOT
=================================================================================
```

---

## 7. Testing & Verification

Run all **40 automated test cases**:
```bash
python -m unittest discover -s tests -p "test_*.py"
```

To run individual modules:
```bash
python -m unittest tests/test_validation.py
python -m unittest tests/test_sorting.py
python -m unittest tests/test_knapsack.py
python -m unittest tests/test_dijkstra.py
python -m unittest tests/test_tsp.py
python -m unittest tests/test_integration.py
```

All 40 tests pass with 0 failures and 0 errors, validating:
- Empty and single-element edge cases.
- Negative edge and invalid reference detection.
- Vehicle payload bound enforcement.
- Proof of suboptimal cases in Nearest Neighbor heuristic.
- Continuity of multi-hop road reconstructions.

---

## 8. Academic Deliverables Mapping

| Capstone Requirement Phase | Corresponding Artifacts & Source Code |
| :--- | :--- |
| **Phase 1: Problem Design & Planning** | `data/*.json`, `utils/models.py`, `utils/validation.py`, `docs/design.md` |
| **Phase 2: Parcel Prioritization & Packing** | `algorithms/sorting.py`, `algorithms/knapsack.py`, `tests/test_sorting.py`, `tests/test_knapsack.py` |
| **Phase 3: Route Maker & Graph Processing** | `algorithms/dijkstra.py`, `algorithms/tsp.py`, `tests/test_dijkstra.py`, `tests/test_tsp.py` |
| **Phase 4: Performance Testing** | `utils/performance.py`, `results/performance_results.csv`, `results/runtime_chart.png`, `docs/complexity_analysis.md` |
| **Phase 5: Final Report & Viva Defense** | `main.py`, `README.md`, `docs/viva_questions.md`, `results/screenshots/execution_trace.txt` |

---

## 9. Limitations & Future Improvements

1. **Greedy TSP Suboptimality**: Nearest Neighbor is a greedy heuristic that can produce suboptimal tours under certain network geometries. Future extensions could implement **2-Opt local search refinement** or **Christofides 1.5-approximation**.
2. **Dynamic Delivery Windows**: The current model filters deadlines during sorting; incorporating a hard-constraint **Vehicle Routing Problem with Time Windows (VRPTW)** would represent time-sensitive delivery contracts more strictly.
3. **Multi-Vehicle Fleet**: The current implementation solves single-trip dispatch for one vehicle; scaling to a fleet of heterogeneous vehicles can be formulated as a Capacitated Vehicle Routing Problem (CVRP).

