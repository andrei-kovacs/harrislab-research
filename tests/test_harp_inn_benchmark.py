import copy
import json
import unittest
from pathlib import Path

from harrislab.approval import file_sha256
from scripts.benchmark_harp_inn_group1 import (
    _aggregate,
    _validate_design,
    build_design,
    generate_report,
)


class HarpInnBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).parents[1]
        cls.reference_path = cls.root / "data" / "harp_inn_group1_reference.json"
        cls.design_path = cls.root / "data" / "harp_inn_group1_benchmark_design.json"
        cls.report_path = cls.root / "data" / "harp_inn_group1_benchmark.json"
        cls.design = json.loads(cls.design_path.read_text(encoding="utf-8"))
        cls.report = json.loads(cls.report_path.read_text(encoding="utf-8"))

    def test_design_is_deterministic_and_covers_each_edge_once(self) -> None:
        self.assertEqual(build_design(self.reference_path), self.design)
        hidden_edges = [
            tuple(edge)
            for trial in self.design["trials"]
            for edge in trial["hidden_edges"]
        ]
        reference = json.loads(self.reference_path.read_text(encoding="utf-8"))
        eligible_edges = [
            (relation["earlier"], relation["later"])
            for relation in reference["relations"]
            if relation.get("status", "observed") == "observed"
            and relation.get("evidence_ids")
        ]

        self.assertEqual(len(self.design["trials"]), 9)
        self.assertEqual(len(hidden_edges), 26)
        self.assertEqual(len(hidden_edges), len(set(hidden_edges)))
        self.assertEqual(set(hidden_edges), set(eligible_edges))

    def test_modified_design_fails_closed(self) -> None:
        modified = copy.deepcopy(self.design)
        modified["trials"][0]["hidden_edges"].reverse()

        with self.assertRaisesRegex(ValueError, "deterministic assignment"):
            _validate_design(self.reference_path, modified)

    def test_reduced_execution_is_deterministic(self) -> None:
        settings = {
            "sample_count": 8,
            "burn_in": 8,
            "thinning": 2,
            "chain_count": 2,
            "order_limit": 10,
            "random_repetitions": 2,
        }

        first = generate_report(self.reference_path, self.design_path, **settings)
        second = generate_report(self.reference_path, self.design_path, **settings)

        self.assertEqual(first, second)
        self.assertEqual(first["aggregate"]["trial_count"], 9)
        self.assertEqual(first["aggregate"]["hidden_edge_count"], 26)
        json.dumps(first, allow_nan=False)

    def test_committed_report_is_bound_and_internally_reproducible(self) -> None:
        json.loads(
            self.report_path.read_text(encoding="utf-8"),
            parse_constant=lambda value: self.fail(f"non-standard JSON value: {value}"),
        )
        self.assertEqual(
            self.report["protocol"]["sha256"], file_sha256(self.design_path)
        )
        self.assertEqual(
            self.report["reference"]["sha256"], file_sha256(self.reference_path)
        )
        _validate_design(self.reference_path, self.design)
        self.assertEqual(self.report["aggregate"], _aggregate(self.report["trials"]))
        self.assertEqual(len(self.report["trials"]), 9)
        self.assertTrue(
            all(len(trial["random_runs"]) == 20 for trial in self.report["trials"])
        )


if __name__ == "__main__":
    unittest.main()