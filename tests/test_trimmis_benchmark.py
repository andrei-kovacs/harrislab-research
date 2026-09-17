import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from benchmark_trimmis_profile19 import generate_report


class TrimmisBenchmarkReportTests(unittest.TestCase):
    def test_report_is_deterministic_and_bound_to_reference(self) -> None:
        reference = ROOT / "data" / "trimmis_profile19_reference.json"
        options = {
            "sample_count": 20,
            "burn_in": 20,
            "thinning": 2,
            "chain_count": 2,
        }

        first = generate_report(reference, **options)
        second = generate_report(reference, **options)

        self.assertEqual(first, second)
        self.assertEqual(first["reference"]["context_count"], 26)
        self.assertEqual(first["reference"]["direct_relation_count"], 29)
        self.assertEqual(len(first["reference"]["sha256"]), 64)
        self.assertEqual(
            {run["strategy"] for run in first["runs"]},
            {"impact", "closure_gain", "sampled_orders", "lexicographic", "random"},
        )
        self.assertTrue(
            all(len(run["steps"]) == len(first["hidden_edges"]) for run in first["runs"])
        )

    def test_committed_report_matches_generator(self) -> None:
        reference = ROOT / "data" / "trimmis_profile19_reference.json"
        committed = json.loads(
            (ROOT / "data" / "trimmis_profile19_benchmark.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(committed, generate_report(reference))


if __name__ == "__main__":
    unittest.main()