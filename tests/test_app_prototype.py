import json
import unittest
from pathlib import Path

from harrislab.io import load_stratigraphy


class AppPrototypeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).parents[1]
        cls.document = (cls.root / "docs" / "app-prototype.html").read_text(
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

    def test_local_import_is_fail_closed_and_hash_bound(self) -> None:
        for required in (
            "function validateImportedReference",
            "function isAcyclic",
            'crypto.subtle.digest("SHA-256"',
            "only observed relations may be imported",
            "relation evidence is missing or unknown",
            "No file content is uploaded",
        ):
            self.assertIn(required, self.document)

        template_path = self.root / "data" / "import_reference_template.json"
        template = json.loads(template_path.read_text(encoding="utf-8"))
        graph = load_stratigraphy(template_path)
        self.assertEqual(template["schema"], "harrislab.reference.v1")
        self.assertEqual(len(graph.contexts), 4)
        self.assertEqual(len(graph.relations), 3)
        self.assertIsNone(graph.contradiction_cycle())

    def test_csv_pair_import_has_mapping_and_provenance_contract(self) -> None:
        for required in (
            "papaparse@5.5.3",
            "function prepareCsvMappings",
            "function importCsvPair",
            "Column mapping",
            'format: "csv-pair-v1"',
            "conflicting evidence metadata",
        ):
            self.assertIn(required, self.document)

        contexts = (self.root / "data" / "import_contexts_template.csv").read_text(
            encoding="utf-8"
        )
        relations = (
            self.root / "data" / "import_relations_template.csv"
        ).read_text(encoding="utf-8")
        self.assertIn("context_id,label,record_source", contexts)
        self.assertIn(
            "earlier,later,evidence_id,evidence_kind,evidence_description,evidence_source",
            relations,
        )

    def test_review_branches_attachments_and_exchange_are_hash_bound(self) -> None:
        for required in (
            "harrislab.review-bundle.v1",
            "function effectiveBranchEdges",
            "function renderBranchComparison",
            "function fingerprintFiles",
            "file.arrayBuffer()",
            "Each evidence file must be 25 MB or smaller",
            "review bundle does not match the active reference SHA-256",
            "human_decision_overlay_reference_unchanged",
        ):
            self.assertIn(required, self.document)


if __name__ == "__main__":
    unittest.main()