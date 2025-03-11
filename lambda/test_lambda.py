import unittest
from lambda_function import compute_mst

class TestMSTAlgorithm(unittest.TestCase):
    def test_compute_mst(self):
        num_nodes = 4
        edges = [(3, 1, 2), (1, 2, 3), (4, 3, 4), (2, 1, 4)]
        total_cost, mst_edges = compute_mst(num_nodes, edges)
        self.assertEqual(total_cost, 6)
        self.assertEqual(len(mst_edges), num_nodes - 1)

if __name__ == "__main__":
    unittest.main()
