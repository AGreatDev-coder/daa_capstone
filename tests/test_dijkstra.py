"""Unit tests for shortest path calculation using Dijkstra's algorithm."""

import unittest
from utils.models import RoadGraph
from algorithms.dijkstra import dijkstra, reconstruct_path, get_shortest_path, compute_all_pairs_shortest_paths


class TestDijkstra(unittest.TestCase):

    def test_single_node_graph(self):
        """Single node graph has distance 0 to itself and empty neighbors."""
        g = RoadGraph()
        g.add_node("DEPOT")
        distances, predecessors = dijkstra(g, "DEPOT")
        self.assertEqual(distances["DEPOT"], 0.0)
        self.assertIsNone(predecessors["DEPOT"])
        dist, path = get_shortest_path(g, "DEPOT", "DEPOT")
        self.assertEqual(dist, 0.0)
        self.assertEqual(path, ["DEPOT"])

    def test_simple_connected_graph(self):
        """Test simple 3-node linear graph."""
        g = RoadGraph()
        g.add_edge("A", "B", 4.0)
        g.add_edge("B", "C", 2.0)
        dist, path = get_shortest_path(g, "A", "C")
        self.assertEqual(dist, 6.0)
        self.assertEqual(path, ["A", "B", "C"])

    def test_multiple_paths_chooses_minimum(self):
        """
        Diamond graph with multiple paths:
        A -> B (5), B -> D (5)  => path len 10
        A -> C (2), C -> D (3)  => path len 5
        Dijkstra must pick A -> C -> D.
        """
        g = RoadGraph()
        g.add_edge("A", "B", 5.0)
        g.add_edge("B", "D", 5.0)
        g.add_edge("A", "C", 2.0)
        g.add_edge("C", "D", 3.0)

        dist, path = get_shortest_path(g, "A", "D")
        self.assertEqual(dist, 5.0)
        self.assertEqual(path, ["A", "C", "D"])

    def test_zero_weight_edge(self):
        """Zero weight edges should be validly traversed."""
        g = RoadGraph()
        g.add_edge("A", "B", 0.0)
        g.add_edge("B", "C", 3.0)
        dist, path = get_shortest_path(g, "A", "C")
        self.assertEqual(dist, 3.0)
        self.assertEqual(path, ["A", "B", "C"])

    def test_unreachable_node(self):
        """Nodes in an isolated component should have inf distance and empty path."""
        g = RoadGraph()
        g.add_edge("A", "B", 2.0)
        g.add_node("ISOLATED")

        dist, path = get_shortest_path(g, "A", "ISOLATED")
        self.assertEqual(dist, float("inf"))
        self.assertEqual(path, [])

    def test_negative_edge_rejected(self):
        """RoadGraph add_edge or Dijkstra should reject negative edge weights."""
        g = RoadGraph()
        with self.assertRaises(ValueError):
            g.add_edge("A", "B", -2.0)

    def test_compute_all_pairs_subset(self):
        """Test pairwise shortest path calculation for a subset of locations."""
        g = RoadGraph()
        g.add_edge("DEPOT", "LOC_A", 2.0)
        g.add_edge("LOC_A", "LOC_B", 3.0)
        g.add_edge("DEPOT", "LOC_B", 7.0)

        subset = {"DEPOT", "LOC_A", "LOC_B"}
        pair_dists, pair_paths = compute_all_pairs_shortest_paths(g, subset)

        self.assertEqual(pair_dists[("DEPOT", "LOC_B")], 5.0)
        self.assertEqual(pair_paths[("DEPOT", "LOC_B")], ["DEPOT", "LOC_A", "LOC_B"])
        self.assertEqual(pair_dists[("LOC_B", "DEPOT")], 5.0)


if __name__ == "__main__":
    unittest.main()

