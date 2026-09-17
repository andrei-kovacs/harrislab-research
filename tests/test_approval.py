import json
import tempfile
import unittest
from pathlib import Path

from harrislab.approval import (
    apply_confirmed_corrections,
    approve_candidate,
    create_review_template,
    file_sha256,
)
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
        self.assertEqual(approved["schema"], "harrislab.reference.v1")
        self.assertIn("matrix_rectangle", approved["contexts"][0])
        self.assertIn("catalog_notation", approved["contexts"][0])
        self.assertIsNone(graph.contradiction_cycle())
        self.assertTrue(
            all(
                relation.status is RelationStatus.OBSERVED
                for relation in graph.relations
            )
        )

    def test_confirmed_correction_replaces_direct_relation_with_context(self) -> None:
        review = self._approved_review()
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            review_path = directory_path / "review.json"
            reference_path = directory_path / "reference.json"
            corrections_path = directory_path / "corrections.json"
            corrected_path = directory_path / "corrected.json"
            review_path.write_text(json.dumps(review), encoding="utf-8")
            reference_path.write_text(
                json.dumps(approve_candidate(self.candidate, review_path)),
                encoding="utf-8",
            )
            corrections_path.write_text(
                json.dumps(self._confirmed_corrections(reference_path)),
                encoding="utf-8",
            )

            corrected = apply_confirmed_corrections(
                reference_path, corrections_path
            )
            corrected_path.write_text(json.dumps(corrected), encoding="utf-8")
            graph = load_stratigraphy(corrected_path)

        pairs = {(relation.earlier, relation.later) for relation in graph.relations}
        self.assertEqual(len(graph.contexts), 26)
        self.assertEqual(len(graph.relations), 29)
        self.assertEqual(len(graph.evidence), 4)
        self.assertEqual(
            corrected["schema"], "harrislab.corrected-reference.v1"
        )
        self.assertNotIn(("26", "170"), pairs)
        self.assertIn(("26", "199"), pairs)
        self.assertIn(("199", "170"), pairs)
        self.assertIsNone(graph.contradiction_cycle())

    def test_correction_is_bound_to_reference_hash(self) -> None:
        review = self._approved_review()
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            review_path = directory_path / "review.json"
            reference_path = directory_path / "reference.json"
            corrections_path = directory_path / "corrections.json"
            review_path.write_text(json.dumps(review), encoding="utf-8")
            reference_path.write_text(
                json.dumps(approve_candidate(self.candidate, review_path)),
                encoding="utf-8",
            )
            corrections = self._confirmed_corrections(reference_path)
            corrections["base_sha256"] = "0" * 64
            corrections_path.write_text(json.dumps(corrections), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "do not match"):
                apply_confirmed_corrections(reference_path, corrections_path)

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

    def _confirmed_corrections(self, reference_path: Path) -> dict[str, object]:
        return {
            "schema": "harrislab.confirmed-corrections.v1",
            "base_sha256": file_sha256(reference_path),
            "status": "confirmed",
            "reviewed_at": "2026-09-17",
            "title": "Trimmis Profile 19 corrected reference graph",
            "description": "Source-author-corrected Profile 19 reference graph.",
            "summary": "Insert context 199 between contexts 26 and 170.",
            "evidence": {
                "id": "trimmis-author-correction-2026-09-17",
                "kind": "other",
                "description": "Source-author correction for context 199",
                "source": "Private correspondence, 2026-09-17",
            },
            "add_contexts": [
                {
                    "id": "199",
                    "label": "Furrow-like depression or plough marks",
                }
            ],
            "remove_relations": [{"earlier": "26", "later": "170"}],
            "add_relations": [
                {"earlier": "26", "later": "199"},
                {"earlier": "199", "later": "170"},
            ],
        }


if __name__ == "__main__":
    unittest.main()