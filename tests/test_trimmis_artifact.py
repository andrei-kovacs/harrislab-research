import json
import re
import unittest
from pathlib import Path

from harrislab.approval import file_sha256


class TrimmisArtifactTests(unittest.TestCase):
    def test_profile19_review_and_correction_artifacts_are_consistent(self) -> None:
        root = Path(__file__).parents[1]
        candidate = json.loads(
            (root / "data" / "trimmis_profile19_audit_candidate.json").read_text(
                encoding="utf-8"
            )
        )
        review = json.loads(
            (root / "data" / "trimmis_profile19_review.json").read_text(
                encoding="utf-8"
            )
        )
        published_reference = json.loads(
            (root / "data" / "trimmis_profile19_published_reference.json").read_text(
                encoding="utf-8"
            )
        )
        corrections = json.loads(
            (root / "data" / "trimmis_profile19_corrections.json").read_text(
                encoding="utf-8"
            )
        )
        corrected_reference = json.loads(
            (root / "data" / "trimmis_profile19_reference.json").read_text(
                encoding="utf-8"
            )
        )
        audit = (root / "docs" / "TRIMMIS_PROFILE19_AUDIT.md").read_text(
            encoding="utf-8"
        )
        checklist_edges = {
            (int(path_index), earlier, later)
            for path_index, earlier, later in re.findall(
                r"\| (\d+) \| (\d+) \| (\d+) \| PASS \|", audit
            )
        }
        candidate_edges = {
            (edge["pdf_path_index"], edge["earlier"], edge["later"])
            for edge in candidate["edges"]
        }

        self.assertEqual(candidate["approval_status"], "pending_visual_review")
        self.assertEqual(candidate["node_count"], 25)
        self.assertEqual(candidate["edge_count"], 28)
        self.assertEqual(
            review["candidate_sha256"],
            file_sha256(root / "data" / "trimmis_profile19_audit_candidate.json"),
        )
        self.assertEqual(review["direction_confirmation"], "pass")
        self.assertTrue(review["reviewer"]["independent_from_extraction"])
        self.assertTrue(
            all(item["status"] == "pass" for item in review["node_reviews"])
        )
        self.assertTrue(
            all(item["status"] == "pass" for item in review["edge_reviews"])
        )
        self.assertEqual(checklist_edges, candidate_edges)
        self.assertEqual(
            candidate["source_profile_comparison"]["profile_only_labels"],
            ["199"],
        )
        self.assertEqual(
            candidate["source_profile_comparison"]["matrix_only_labels"], []
        )
        self.assertEqual(len(published_reference["contexts"]), 25)
        self.assertEqual(len(published_reference["relations"]), 28)
        self.assertEqual(
            corrections["base_sha256"],
            file_sha256(root / "data" / "trimmis_profile19_published_reference.json"),
        )
        corrected_pairs = {
            (relation["earlier"], relation["later"])
            for relation in corrected_reference["relations"]
        }
        self.assertEqual(len(corrected_reference["contexts"]), 26)
        self.assertEqual(len(corrected_reference["relations"]), 29)
        self.assertIn(("26", "199"), corrected_pairs)
        self.assertIn(("199", "170"), corrected_pairs)
        self.assertNotIn(("26", "170"), corrected_pairs)
        self.assertTrue((root / "docs" / "trimmis_profile19_overlay.png").is_file())


if __name__ == "__main__":
    unittest.main()