import json
import re
import unittest
from pathlib import Path

from harrislab.approval import file_sha256


class TrimmisArtifactTests(unittest.TestCase):
    def test_profile19_candidate_matches_pending_review_package(self) -> None:
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
        audit = (root / "docs" / "TRIMMIS_PROFILE19_AUDIT.md").read_text(
            encoding="utf-8"
        )
        checklist_edges = {
            (int(path_index), earlier, later)
            for path_index, earlier, later in re.findall(
                r"\| (\d+) \| (\d+) \| (\d+) \| PENDING \|", audit
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
        self.assertEqual(review["direction_confirmation"], "pending")
        self.assertEqual(checklist_edges, candidate_edges)
        self.assertEqual(
            candidate["source_profile_comparison"]["profile_only_labels"],
            ["199"],
        )
        self.assertEqual(
            candidate["source_profile_comparison"]["matrix_only_labels"], []
        )
        self.assertTrue((root / "docs" / "trimmis_profile19_overlay.png").is_file())


if __name__ == "__main__":
    unittest.main()