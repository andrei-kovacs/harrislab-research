import json
import tempfile
import unittest
from pathlib import Path

from harrislab.drawing_review import (
    create_drawing_review_template,
    drawing_review_csv,
    drawing_review_from_csv,
    validate_drawing_review,
)


class DrawingReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.comparison = (
            Path(__file__).parents[1]
            / "data"
            / "trimmis_profile19_drawing_comparison.json"
        )

    def test_template_contains_exactly_pending_relations(self) -> None:
        template = create_drawing_review_template(self.comparison)

        self.assertEqual(len(template["relation_reviews"]), 27)
        self.assertTrue(
            all(item["decision"] == "pending" for item in template["relation_reviews"])
        )
        self.assertNotIn("name", template["reviewer"])
        self.assertNotIn("email", template["reviewer"])

    def test_complete_review_emits_summary_without_graph_mutation(self) -> None:
        review = self._complete_review()
        review["relation_reviews"][0]["decision"] = "contradicted"
        review["relation_reviews"][0]["note"] = "Boundary contact is not visible."

        summary = self._validate(review)

        self.assertEqual(summary["relation_count"], 27)
        self.assertEqual(summary["decision_counts"]["corroborated"], 26)
        self.assertEqual(summary["decision_counts"]["contradicted"], 1)
        self.assertEqual(summary["accepted_graph_mutations"], [])

    def test_stale_hash_fails_closed(self) -> None:
        review = self._complete_review()
        review["comparison_sha256"] = "0" * 64

        with self.assertRaisesRegex(ValueError, "does not match"):
            self._validate(review)

    def test_missing_relation_fails_closed(self) -> None:
        review = self._complete_review()
        review["relation_reviews"].pop()

        with self.assertRaisesRegex(ValueError, "do not match"):
            self._validate(review)

    def test_pending_decision_fails_closed(self) -> None:
        review = self._complete_review()
        review["relation_reviews"][0]["decision"] = "pending"

        with self.assertRaisesRegex(ValueError, "invalid or pending"):
            self._validate(review)

    def test_noncorroborating_decision_requires_note(self) -> None:
        review = self._complete_review()
        review["relation_reviews"][0]["decision"] = "indeterminate"

        with self.assertRaisesRegex(ValueError, "note is required"):
            self._validate(review)

    def test_csv_round_trip_preserves_review(self) -> None:
        review = self._complete_review()
        review["relation_reviews"][0]["decision"] = "not_visible"
        review["relation_reviews"][0]["note"] = "Contact is outside the crop."
        csv_text = drawing_review_csv(review)
        csv_text = csv_text.replace(
            "qualified_for_drawing_review,,,,,false",
            "qualified_for_drawing_review,,,,,true",
        ).replace(
            "independent_from_matrix_extraction,,,,,false",
            "independent_from_matrix_extraction,,,,,true",
        )
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "review.csv"
            json_path = Path(directory) / "review.json"
            csv_path.write_text(csv_text, encoding="utf-8")
            converted = drawing_review_from_csv(csv_path)
            json_path.write_text(json.dumps(converted), encoding="utf-8")
            summary = validate_drawing_review(self.comparison, json_path)

        self.assertEqual(summary["decision_counts"]["not_visible"], 1)
        self.assertEqual(summary["accepted_graph_mutations"], [])

    def test_csv_rejects_invalid_boolean(self) -> None:
        csv_text = drawing_review_csv(create_drawing_review_template(self.comparison))
        csv_text = csv_text.replace(
            "qualified_for_drawing_review,,,,,false",
            "qualified_for_drawing_review,,,,,yes",
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "review.csv"
            path.write_text(csv_text, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "true or false"):
                drawing_review_from_csv(path)

    def _complete_review(self) -> dict[str, object]:
        review = create_drawing_review_template(self.comparison)
        review["reviewer"] = {
            "public_label": "Independent drawing reviewer 1",
            "reviewed_at": "2026-09-17",
            "qualified_for_drawing_review": True,
            "independent_from_matrix_extraction": True,
        }
        review["direction_confirmation"] = "older_to_younger_confirmed"
        for item in review["relation_reviews"]:
            item["decision"] = "corroborated"
        return review

    def _validate(self, review: dict[str, object]) -> dict[str, object]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "review.json"
            path.write_text(json.dumps(review), encoding="utf-8")
            return validate_drawing_review(self.comparison, path)


if __name__ == "__main__":
    unittest.main()