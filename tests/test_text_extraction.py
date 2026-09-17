import json
import unittest
from pathlib import Path

from harrislab.approval import file_sha256
from harrislab.text_extraction import extract_relation_candidates


class TextExtractionTests(unittest.TestCase):
    def setUp(self) -> None:
        shared_cut_record = {
            "catalog_row": 149,
            "catalog_notation": "(153) = (50):",
            "description_de": "Steinpackung in Einschnitt (154).",
        }
        self.catalog = {
            "50": shared_cut_record,
            "104": {
                "catalog_row": 102,
                "catalog_notation": "(104):",
                "description_de": "Grasnarbe über Kiesbett (103).",
            },
            "153": shared_cut_record,
            "156": {
                "catalog_row": 276,
                "catalog_notation": "(284) =(90) = (156):",
                "description_de": "Steinige, dunkel humose Schicht mit Holzkohlestücken.",
            },
        }
        self.active_ids = {"50", "104", "153", "156"}

    def test_extracts_literal_directional_mentions_as_pending(self) -> None:
        candidates = extract_relation_candidates(self.catalog, self.active_ids)

        self.assertEqual(
            [(item["earlier"], item["later"]) for item in candidates],
            [("103", "104"), ("154", "50"), ("154", "153")],
        )
        self.assertTrue(
            all(item["status"] == "pending_human_review" for item in candidates)
        )
        self.assertTrue(
            all(
                item["scope_status"]
                == "referenced_context_outside_active_reference"
                for item in candidates
            )
        )

    def test_preserves_literal_span_and_aliases(self) -> None:
        candidates = extract_relation_candidates(self.catalog, self.active_ids)
        cut_candidate = candidates[1]

        self.assertEqual(
            cut_candidate["source"]["matched_text"], "in Einschnitt (154)"
        )
        self.assertEqual(cut_candidate["source"]["subject_aliases"], ["50", "153"])
        start, end = cut_candidate["source"]["character_span"]
        self.assertEqual(
            cut_candidate["source"]["description_de"][start:end],
            cut_candidate["source"]["matched_text"],
        )

    def test_does_not_extract_material_descriptions(self) -> None:
        candidates = extract_relation_candidates(self.catalog, self.active_ids)

        self.assertNotIn("156", {item["later"] for item in candidates})

    def test_marks_existing_active_pair_without_accepting_it(self) -> None:
        active_catalog = {
            **self.catalog,
            "103": {
                "catalog_row": 101,
                "catalog_notation": "(103):",
                "description_de": "Kiesbett.",
            },
        }
        candidates = extract_relation_candidates(
            active_catalog,
            {*self.active_ids, "103"},
            accepted_relations=[("103", "104")],
        )

        candidate = next(item for item in candidates if item["later"] == "104")
        self.assertEqual(candidate["scope_status"], "active_reference_pair")
        self.assertTrue(candidate["already_in_accepted_graph"])
        self.assertEqual(candidate["status"], "pending_human_review")

    def test_conflicting_alias_records_fail_closed(self) -> None:
        catalog = {
            "50": self.catalog["50"],
            "153": {**self.catalog["153"], "description_de": "Different text."},
        }

        with self.assertRaisesRegex(ValueError, "conflicting catalogue records"):
            extract_relation_candidates(catalog, {"50", "153"})

    def test_published_pilot_is_bound_and_does_not_mutate_graph(self) -> None:
        root = Path(__file__).parents[1]
        artifact = json.loads(
            (root / "data" / "trimmis_profile19_text_relation_proposals.json")
            .read_text(encoding="utf-8")
        )

        self.assertEqual(
            artifact["reference"]["sha256"],
            file_sha256(root / "data" / "trimmis_profile19_reference.json"),
        )
        self.assertEqual(artifact["summary"]["explicit_relation_mentions"], 2)
        self.assertEqual(artifact["summary"]["proposed_relation_options"], 3)
        self.assertEqual(artifact["summary"]["active_reference_pair_proposals"], 0)
        self.assertEqual(artifact["summary"]["accepted_graph_mutations"], 0)
        self.assertEqual(artifact["accepted_graph_mutations"], [])
        self.assertTrue(
            all(
                candidate["status"] == "pending_human_review"
                and candidate["scope_status"]
                == "referenced_context_outside_active_reference"
                for candidate in artifact["candidates"]
            )
        )


if __name__ == "__main__":
    unittest.main()