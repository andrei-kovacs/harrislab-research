import unittest
from pathlib import Path

from harrislab.io import load_stratigraphy


class JsonInputTests(unittest.TestCase):
    def test_loads_sample_dataset_with_provenance(self) -> None:
        sample = Path(__file__).parents[1] / "data" / "synthetic_building.json"

        graph = load_stratigraphy(sample)

        self.assertEqual(len(graph.contexts), 7)
        self.assertEqual(len(graph.evidence), 3)
        self.assertIsNone(graph.contradiction_cycle())
        self.assertEqual(graph.count_chronological_orders(), (1, False))


if __name__ == "__main__":
    unittest.main()
