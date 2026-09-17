import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from benchmark_trimmis_profile19_comprehensive import generate_report


class TrimmisComprehensiveBenchmarkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.reference = ROOT / "data" / "trimmis_profile19_reference.json"
        self.preregistration = (
            ROOT / "data" / "trimmis_profile19_benchmark_preregistration.json"
        )

    def test_small_report_is_deterministic_and_complete(self) -> None:
        options = {
            "sample_count": 20,
            "burn_in": 20,
            "thinning": 2,
            "chain_count": 2,
            "order_limit": 1_000,
            "random_repetitions": 2,
        }

        first = generate_report(self.reference, self.preregistration, **options)
        second = generate_report(self.reference, self.preregistration, **options)

        self.assertEqual(first, second)
        self.assertEqual(first["aggregate"]["trial_count"], 10)
        self.assertEqual(
            sum(len(trial["hidden_edges"]) for trial in first["trials"]), 29
        )
        self.assertTrue(all(len(trial["random_runs"]) == 2 for trial in first["trials"]))

    def test_modified_assignment_fails_closed(self) -> None:
        document = json.loads(self.preregistration.read_text(encoding="utf-8"))
        modified = copy.deepcopy(document)
        modified["trials"][0]["hidden_edges"].reverse()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "modified.json"
            path.write_text(json.dumps(modified), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "deterministic assignment"):
                generate_report(self.reference, path, sample_count=20)

    def test_committed_report_matches_generator(self) -> None:
        committed = json.loads(
            (
                ROOT / "data" / "trimmis_profile19_comprehensive_benchmark.json"
            ).read_text(encoding="utf-8")
        )

        self.assert_report_equal(
            committed,
            generate_report(self.reference, self.preregistration),
        )

    def assert_report_equal(self, expected, actual) -> None:
        if isinstance(expected, float):
            self.assertAlmostEqual(expected, actual, places=4)
        elif isinstance(expected, dict):
            self.assertEqual(expected.keys(), actual.keys())
            for key in expected:
                with self.subTest(key=key):
                    self.assert_report_equal(expected[key], actual[key])
        elif isinstance(expected, list):
            self.assertEqual(len(expected), len(actual))
            for index, (expected_item, actual_item) in enumerate(zip(expected, actual)):
                with self.subTest(index=index):
                    self.assert_report_equal(expected_item, actual_item)
        else:
            self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()