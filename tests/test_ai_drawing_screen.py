import json
import unittest
from pathlib import Path

from harrislab.approval import file_sha256


class AiDrawingScreenTests(unittest.TestCase):
    def test_screen_is_complete_and_has_no_graph_authority(self) -> None:
        root = Path(__file__).resolve().parents[1]
        screen = json.loads(
            (root / "data" / "trimmis_profile19_ai_drawing_screen.json").read_text(
                encoding="utf-8"
            )
        )
        comparison_path = root / "data" / "trimmis_profile19_drawing_comparison.json"
        comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
        expected = {
            (item["earlier"], item["later"])
            for item in comparison["relation_comparison"]
            if item["status"] == "awaiting_drawing_review"
        }
        actual = [
            (item["earlier"], item["later"])
            for item in screen["relation_screens"]
        ]

        self.assertEqual(
            screen["drawing_comparison_sha256"], file_sha256(comparison_path)
        )
        self.assertEqual(len(actual), 27)
        self.assertEqual(len(set(actual)), 27)
        self.assertEqual(set(actual), expected)
        self.assertEqual(
            set(item["result"] for item in screen["relation_screens"]),
            {"visually_consistent", "indeterminate"},
        )
        counts = {
            result: sum(item["result"] == result for item in screen["relation_screens"])
            for result in {"visually_consistent", "indeterminate"}
        }
        self.assertEqual(screen["summary"]["visually_consistent"], counts["visually_consistent"])
        self.assertEqual(screen["summary"]["indeterminate"], counts["indeterminate"])
        self.assertEqual(screen["summary"]["visibly_contradicted"], 0)
        self.assertEqual(screen["summary"]["accepted_graph_mutations"], 0)
        self.assertEqual(screen["accepted_graph_mutations"], [])


if __name__ == "__main__":
    unittest.main()