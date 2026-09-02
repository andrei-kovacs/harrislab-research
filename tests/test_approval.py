import json
import tempfile
import unittest
from pathlib import Path

from harrislab.approval import approve_candidate, create_review_template, file_sha256
from harrislab.io import load_stratigraphy
from harrislab.model import RelationStatus


class ApprovalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.candidate = (
            Path(__file__).parents[1]
            / "data"
            / "trimmis_profile19_audit_candidate.json"
        )

    def test_pending_review_cannot_emit_reference_graph(self) -> None:
        review = create_review_template(self.candidate)
        with tempfile.TemporaryDirectory() as directory:
            review_path = Path(directory) / "review.json"
            review_path.write_text(json.dumps(review), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "reviewer name is required"):
                approve_candidate(self.candidate, review_path)

    def test_review_is_bound_to_candidate_hash(self) -> None:
        review = self._approved_review()
        review["candidate_sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as directory:
            review_path = Path(directory) / "review.json"
            review_path.write_text(json.dumps(review), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "does not match"):
                approve_candidate(self.candidate, review_path)

    def test_candidate_hash_is_independent_of_json_line_endings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            lf_path = Path(directory) / "lf.json"
            crlf_path = Path(directory) / "crlf.json"
            lf_path.write_bytes(b'{\n  "value": 1\n}\n')
            crlf_path.write_bytes(b'{\r\n  "value": 1\r\n}\r\n')

            self.assertEqual(file_sha256(lf_path), file_sha256(crlf_path))

    def test_complete_review_emits_loadable_reference_graph(self) -> None:
        review = self._approved_review()
        with tempfile.TemporaryDirectory() as directory:
            review_path = Path(directory) / "review.json"
            output_path = Path(directory) / "approved.json"
            review_path.write_text(json.dumps(review), encoding="utf-8")

            approved = approve_candidate(self.candidate, review_path)
            output_path.write_text(json.dumps(approved), encoding="utf-8")
            graph = load_stratigraphy(output_path)

        self.assertEqual(len(graph.contexts), 25)
        self.assertEqual(len(graph.relations), 28)
        self.assertEqual(len(graph.evidence), 3)
        self.assertIsNone(graph.contradiction_cycle())
        self.assertTrue(
            all(
                relation.status is RelationStatus.OBSERVED
                for relation in graph.relations
            )
        )

    def _approved_review(self) -> dict[str, object]:
        review = create_review_template(self.candidate)
        review["reviewer"] = {
            "name": "Independent Reviewer",
            "affiliation": "Test fixture",
            "reviewed_at": "2026-09-02",
            "independent_from_extraction": True,
        }
        review["direction_confirmation"] = "pass"
        for item in [*review["node_reviews"], *review["edge_reviews"]]:
            item["status"] = "pass"
        return review


if __name__ == "__main__":
    unittest.main()