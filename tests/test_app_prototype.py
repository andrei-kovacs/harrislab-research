import unittest
from pathlib import Path


class AppPrototypeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).parents[1]
        cls.document = (root / "docs" / "app-prototype.html").read_text(
            encoding="utf-8"
        )

    def test_harp_dataset_contract_is_explicit(self) -> None:
        for required in (
            'option value="harp"',
            "harp_inn_group1_reference.json?v=0.3.1",
            "harp_inn_group1_benchmark.json?v=0.3.1",
            "function renderHarpQuestions",
            "CONTEMPORARY remains typed evidence outside the DAG",
        ):
            self.assertIn(required, self.document)

    def test_trimmis_only_panels_are_marked(self) -> None:
        self.assertEqual(self.document.count("data-trimmis-only"), 9)
        self.assertIn(
            'document.querySelectorAll("[data-trimmis-only]")', self.document
        )

    def test_review_queue_is_an_immutable_audit_overlay(self) -> None:
        for required in (
            "harrislab.review-event.v1",
            "harrislab.review-log.v1",
            "human_decision_overlay_reference_unchanged",
            "reference_sha256",
            "activeReferenceBinding",
            "Add a decision note before recording the decision",
            "function relationConsequence",
            "function renderReviewQueue",
            "Accepting this direction would create a chronological cycle",
        ):
            self.assertIn(required, self.document)


if __name__ == "__main__":
    unittest.main()