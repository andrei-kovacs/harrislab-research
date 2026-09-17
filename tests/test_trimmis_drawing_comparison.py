import json
import unittest
from pathlib import Path

from harrislab.approval import file_sha256


class TrimmisDrawingComparisonTests(unittest.TestCase):
    def test_committed_comparison_preserves_provenance_boundaries(self) -> None:
        root = Path(__file__).resolve().parents[1]
        comparison = json.loads(
            (root / "data" / "trimmis_profile19_drawing_comparison.json").read_text(
                encoding="utf-8"
            )
        )
        reference = json.loads(
            (root / "data" / "trimmis_profile19_reference.json").read_text(
                encoding="utf-8"
            )
        )
        relations = {
            (item["earlier"], item["later"]): item["status"]
            for item in comparison["relation_comparison"]
        }

        self.assertEqual(
            comparison["reference"]["sha256"],
            file_sha256(root / "data" / "trimmis_profile19_reference.json"),
        )
        self.assertEqual(comparison["summary"]["reference_contexts"], 26)
        self.assertEqual(comparison["summary"]["contexts_present_in_profile"], 26)
        self.assertEqual(comparison["summary"]["confirmed_profile_corrections"], 2)
        self.assertEqual(comparison["summary"]["superseded_matrix_relations"], 1)
        self.assertEqual(comparison["summary"]["relations_awaiting_drawing_review"], 27)
        self.assertEqual(comparison["summary"]["ai_proposed_relations"], 0)
        self.assertEqual(relations[("26", "170")], "superseded_matrix_relation")
        self.assertEqual(relations[("26", "199")], "confirmed_profile_correction")
        self.assertEqual(relations[("199", "170")], "confirmed_profile_correction")
        self.assertEqual(
            {item["id"] for item in comparison["label_occurrences"]},
            {context["id"] for context in reference["contexts"]},
        )
        self.assertTrue(
            (root / "docs" / "trimmis_profile19_source_profile.png").is_file()
        )


if __name__ == "__main__":
    unittest.main()