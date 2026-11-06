# Test Strategy, Verification Matrix, and Edge Cases

**Course:** Design & Analysis of Algorithms (ETCCDA302)  
**University:** K.R. Mangalam University  

---

## 1. Test Suite Summary
The test suite consists of **40 automated tests** implemented using Python's standard `unittest` framework. All tests pass with zero failures and zero errors.

To run the complete suite:
```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## 2. Comprehensive Test Verification Matrix

| Test Module | Test Method | Category | Scenario / Edge Case Tested | Expected Result | Pass / Fail |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **`test_validation.py`** | `test_valid_dataset_passes` | Normal | Standard 8-node, 10-parcel dataset | Passes without error | **PASS** |
| | `test_missing_depot_raises_error` | Error | Depot ID not present in locations | Raises `ValidationError` | **PASS** |
| | `test_empty_locations_raises_error` | Boundary | Empty locations array | Raises `ValidationError` | **PASS** |
| | `test_negative_weight_raises_error` | Boundary | Parcel with weight $< 0$ | Raises `ValidationError` | **PASS** |
| | `test_negative_value_raises_error` | Boundary | Parcel with value $< 0$ | Raises `ValidationError` | **PASS** |
| | `test_negative_road_distance_raises_error` | Algorithmic | Road with distance $< 0$ | Rejects negative edge (Dijkstra) | **PASS** |
| | `test_unregistered_destination_raises_error` | Referential | Destination not in locations | Raises `ValidationError` | **PASS** |
| | `test_duplicate_parcel_id_raises_error` | Integrity | Two parcels with identical ID | Raises `ValidationError` | **PASS** |
| | `test_load_sample_data_from_disk` | I/O | Load JSON files from `data/` | All structures parsed properly | **PASS** |
| **`test_sorting.py`** | `test_empty_list` | Edge | Empty parcel list `[]` | Returns `[]`, 0 comparisons | **PASS** |
| | `test_single_item` | Edge | Single parcel | Returns item unchanged | **PASS** |
| | `test_already_sorted_input` | Normal | Parcels already in priority order | Order preserved identically | **PASS** |
| | `test_reverse_sorted_input` | Normal | Parcels in reverse priority order | Inverted into descending order | **PASS** |
| | `test_equal_priorities_earlier_deadline_first` | Tie-break | Equal priority, different deadlines | Earlier deadline prioritized | **PASS** |
| | `test_equal_priority_and_deadline_tiebreaker` | Tie-break | Equal priority & deadline | Lexicographical ID order | **PASS** |
| | `test_multi_factor_sorting` | Integration | Mixed priorities and deadlines | Correct multi-tier ordering | **PASS** |
| **`test_knapsack.py`** | `test_empty_parcel_list` | Edge | No parcels available | Returns empty subset, 0 value | **PASS** |
| | `test_zero_capacity` | Boundary | Vehicle capacity = 0 kg | Returns empty selection | **PASS** |
| | `test_negative_capacity` | Boundary | Vehicle capacity $< 0$ | Gracefully returns empty set | **PASS** |
| | `test_parcels_heavier_than_capacity` | Boundary | Parcels $> W$ | Rejects oversized parcels | **PASS** |
| | `test_exact_capacity_fit` | Normal | Item matches exact capacity | Selected if value is highest | **PASS** |
| | `test_optimal_subset_selection` | Optimal | Classic textbook 0/1 instance | Selects true maximum profit | **PASS** |
| | `test_decimal_weight_resolution` | Real-world | Decimal weights ($1.5, 2.5, 3.5$) | Exact integer table scaling | **PASS** |
| | `test_no_duplicate_parcels` | 0/1 Constraint | Multiple similar items | Each item selected at most once | **PASS** |
| **`test_dijkstra.py`** | `test_single_node_graph` | Boundary | Graph with only 1 vertex | Distance 0, path `[node]` | **PASS** |
| | `test_simple_connected_graph` | Normal | Linear graph $A - B - C$ | Finds exact additive distance | **PASS** |
| | `test_multiple_paths_chooses_minimum` | Optimal | Diamond graph with alternate paths | Chooses strictly minimal path | **PASS** |
| | `test_zero_weight_edge` | Edge | Road with weight = 0 | Correctly traverses free edge | **PASS** |
| | `test_unreachable_node` | Disconnected | Disconnected component | Distance $\infty$, path `[]` | **PASS** |
| | `test_negative_edge_rejected` | Constraint | Negative edge inserted | Raises `ValueError` | **PASS** |
| | `test_compute_all_pairs_subset` | Integration | Subgraph pairwise calculations | Symmetric correct shortest paths| **PASS** |
| **`test_tsp.py`** | `test_single_delivery_location` | Base | 1 delivery stop + Depot | Depot $\rightarrow$ Stop $\rightarrow$ Depot | **PASS** |
| | `test_no_delivery_locations` | Base | 0 delivery stops | Tour: `[DEPOT]`, distance 0 | **PASS** |
| | `test_multiple_locations_with_intermediate_dijkstra_hops` | Multi-hop | Road without direct edge | Uses intermediate Dijkstra hops | **PASS** |
| | `test_disconnected_unreachable_location` | Disconnected | Target in disconnected island | Flags in unreachable list | **PASS** |
| | `test_return_to_depot_flag_false` | Config | `return_to_depot=False` | Courier halts at last stop | **PASS** |
| | `test_route_distance_equals_sum_of_legs` | Correctness | Sum of individual legs | Matches `total_distance` | **PASS** |
| | `test_nearest_neighbor_suboptimality` | Academic | Graph where greedy choice is suboptimal | Demonstrates heuristic limits | **PASS** |
| **`test_integration.py`** | `test_full_pipeline_sample_data` | End-to-End | Complete execution on sample data | Validates all 7 system invariants | **PASS** |
| | `test_pipeline_zero_capacity` | End-to-End | Zero capacity edge case in pipeline | Graceful empty manifest | **PASS** |

---

## 3. Invariants Verified by Integration Tests
1. **Capacity Invariant:** Total weight of loaded parcels never exceeds vehicle capacity ($\sum w_i \le W$).
2. **0/1 Item Uniqueness:** Every selected parcel ID appears at most once in the vehicle manifest.
3. **Delivery Completeness:** Every destination referenced by packed parcels is scheduled for visit in the TSP tour.
4. **Deduplication:** Multiple parcels for the same location result in exactly one delivery stop.
5. **Path Continuity:** The expanded road path is a contiguous, traversable sequence of adjacent vertices in the road network.
6. **Distance Conservation:** Total route distance is exactly equal to the sum of individual segment travel distances.

