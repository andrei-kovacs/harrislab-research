import json
import statistics
import unittest
from pathlib import Path

from harrislab.approval import file_sha256


class FormationBenchmarkArtifactTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).parents[1]
        self.preregistration_path = (
            self.root / "data" / "formation_process_benchmark_preregistration.json"
        )
        self.result = json.loads(
            (self.root / "data" / "formation_process_benchmark.json").read_text(
                encoding="utf-8"
            )
        )

    def test_result_is_bound_to_frozen_preregistration(self) -> None:
        self.assertEqual(
            self.result["preregistration"]["sha256"],
            file_sha256(self.preregistration_path),
        )
        self.assertEqual(self.result["summary"]["trial_count"], 100)

    def test_trials_follow_matching_and_seed_schedule(self) -> None:
        for expected_trial, trial in enumerate(self.result["trials"], start=1):
            self.assertEqual(trial["trial"], expected_trial)
            self.assertEqual(trial["automaton_seed"], 202609170000 + expected_trial)
            self.assertEqual(trial["control_seed"], 202609180000 + expected_trial)
            self.assertEqual(
                trial["automaton"]["context_count"],
                trial["control"]["context_count"],
            )
            self.assertEqual(
                trial["automaton"]["direct_relation_count"],
                trial["control"]["direct_relation_count"],
            )

    def test_primary_summary_recomputes_from_trials(self) -> None:
        differences = [
            trial["automaton"]["closure_amplification"]
            - trial["control"]["closure_amplification"]
            for trial in self.result["trials"]
        ]

        self.assertEqual(
            differences,
            [
                trial["paired_closure_amplification_difference"]
                for trial in self.result["trials"]
            ],
        )
        self.assertAlmostEqual(
            statistics.mean(differences),
            self.result["summary"][
                "mean_paired_closure_amplification_difference"
            ],
        )
        self.assertEqual(
            self.result["summary"]["directional_hypothesis_outcome"],
            "supported_on_fixed_schedule",
        )


if __name__ == "__main__":
    unittest.main()