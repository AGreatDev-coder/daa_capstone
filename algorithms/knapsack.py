"""Vehicle packing using 0/1 Knapsack Dynamic Programming."""

from dataclasses import dataclass, field
from typing import List, Tuple
from utils.models import Parcel


@dataclass
class KnapsackResult:
    """Stores the outcome of the 0/1 Knapsack dynamic programming packing algorithm."""
    selected_parcels: List[Parcel]
    total_weight: float
    total_value: float
    capacity: float
    dp_table: List[List[float]]
    weight_scale: int

    @property
    def capacity_utilization_pct(self) -> float:
        if self.capacity <= 0:
            return 0.0
        return (self.total_weight / self.capacity) * 100.0

    def format_table_summary(self, max_cols: int = 15) -> str:
        """
        Generates a human-readable string representation of the DP table.
        For large tables, columns are sampled to maintain terminal readability.
        """
        if not self.dp_table:
            return "DP Table: Empty"

        num_rows = len(self.dp_table)
        num_cols = len(self.dp_table[0])

        step = max(1, num_cols // max_cols)
        col_indices = list(range(0, num_cols, step))
        if (num_cols - 1) not in col_indices:
            col_indices.append(num_cols - 1)

        lines = []
        # Header
        col_headers = [f"w={c / self.weight_scale:.1f}" for c in col_indices]
        header = f"{'Item':<8} | " + " | ".join(f"{h:>8}" for h in col_headers)
        lines.append(header)
        lines.append("-" * len(header))

        for i, row in enumerate(self.dp_table):
            label = "Base (0)" if i == 0 else f"Item {i}"
            row_vals = [f"{row[c]:.1f}" for c in col_indices]
            lines.append(f"{label:<8} | " + " | ".join(f"{val:>8}" for val in row_vals))

        return "\n".join(lines)


def knapsack_01(parcels: List[Parcel], capacity: float, weight_scale: int = 10) -> KnapsackResult:
    """
    Solves the 0/1 Knapsack problem for parcel vehicle packing using Dynamic Programming.
    
    Mathematical Formulation:
    - State: DP[i][w] = Maximum delivery value achievable using a subset of the 
      first i parcels with total weight at most w (scaled).
    - Base Cases:
      DP[0][w] = 0 for all w in [0, W_scaled]
      DP[i][0] = 0 for all i in [0, N]
    - Recurrence Relation:
      If w_i > w:
          DP[i][w] = DP[i-1][w]
      If w_i <= w:
          DP[i][w] = max(DP[i-1][w], DP[i-1][w - w_i] + v_i)
    
    Time Complexity: O(N * W_scaled)
    Space Complexity: O(N * W_scaled) auxiliary space for the DP table.
    
    Parameters:
    - parcels: Prioritized input parcels list.
    - capacity: Maximum vehicle carrying weight in kg.
    - weight_scale: Integer scaling factor for decimal weight precision (default 10 -> 0.1 kg resolution).
    
    Returns:
    - KnapsackResult containing chosen parcels, total weight, total value, and DP table.
    """
    if capacity <= 0 or not parcels:
        return KnapsackResult(
            selected_parcels=[],
            total_weight=0.0,
            total_value=0.0,
            capacity=capacity,
            dp_table=[[0.0]],
            weight_scale=weight_scale
        )

    w_scaled_cap = int(round(capacity * weight_scale))
    n = len(parcels)

    # Initialize (n + 1) x (w_scaled_cap + 1) table with zeros
    dp = [[0.0] * (w_scaled_cap + 1) for _ in range(n + 1)]

    # Populate DP Table
    for i in range(1, n + 1):
        p = parcels[i - 1]
        p_w_scaled = int(round(p.weight * weight_scale))
        p_v = float(p.value)

        for w in range(w_scaled_cap + 1):
            if p_w_scaled > w:
                # Item i cannot fit into capacity w
                dp[i][w] = dp[i - 1][w]
            else:
                # Option 1: Do not include item i
                without_item = dp[i - 1][w]
                # Option 2: Include item i
                with_item = dp[i - 1][w - p_w_scaled] + p_v
                dp[i][w] = max(without_item, with_item)

    # Reconstruct optimal parcel subset by backtracking
    selected: List[Parcel] = []
    current_w = w_scaled_cap

    for i in range(n, 0, -1):
        # If the value differs from the previous row, item i was selected
        if dp[i][current_w] != dp[i - 1][current_w]:
            p = parcels[i - 1]
            selected.append(p)
            current_w -= int(round(p.weight * weight_scale))

    # Reverse to maintain original prioritized order
    selected.reverse()

    total_weight = sum(p.weight for p in selected)
    total_value = sum(p.value for p in selected)

    return KnapsackResult(
        selected_parcels=selected,
        total_weight=total_weight,
        total_value=total_value,
        capacity=capacity,
        dp_table=dp,
        weight_scale=weight_scale
    )

