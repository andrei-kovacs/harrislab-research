import importlib.util
import json
import unittest
from pathlib import Path

from harrislab.io import load_stratigraphy


class HarpInnArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).parents[1]
        cls.reference_path = cls.root / "data" / "harp_inn_group1_reference.json"
        cls.document = json.loads(cls.reference_path.read_text(encoding="utf-8"))

    def test_reference_is_bound_to_qualified_source(self) -> None:
        dataset = self.document["dataset"]
        qualification = self.document["qualification"]

        self.assertEqual(dataset["doi"], "10.5284/1133013")
        self.assertEqual(dataset["version"], "1")
        self.assertEqual(dataset["license"], "Open Government Licence")
        self.assertEqual(
            dataset["source_sha256"],
            "d754dfb14250dc66b2741c4d65d6cb08ef376775e4903bdbdc4554d00a948467",
        )
        self.assertEqual(qualification["context_count"], 36)
        self.assertEqual(qualification["precedence_relation_count"], 26)
        self.assertEqual(qualification["contemporary_relation_count"], 10)
        self.assertEqual(
            qualification["precedence_edges_sha256"],
            "44a59ec95109b06157ebfeda7f08dbfa5400dcb823f9397d3c0983a3de4edb1b",
        )
        self.assertTrue(qualification["precedence_is_dag"])

    def test_precedence_and_typed_relations_remain_separate(self) -> None:
        graph = load_stratigraphy(self.reference_path)

        self.assertEqual(len(graph.contexts), 36)
        self.assertEqual(len(graph.relations), 26)
        self.assertEqual(len(graph.evidence), 26)
        self.assertIsNone(graph.contradiction_cycle())
        self.assertTrue(all(relation.evidence_ids for relation in graph.relations))
        self.assertEqual(len(self.document["typed_relations"]), 10)
        self.assertTrue(
            all(
                relation["status"] == "observed_typed_non_precedence"
                for relation in self.document["typed_relations"]
            )
        )
        self.assertEqual(
            self.document["authority"]["accepted_graph_mutations_from_ai"], 0
        )

    def test_local_source_reproduces_committed_graph_when_available(self) -> None:
        source = (
            self.root
            / ".local-data"
            / "harp-inn-source"
            / "1C20HINAR_harris_matrix_phase_1_phase_2.csv"
        )
        if not source.is_file():
            self.skipTest("checksum-verified ADS source is not present")
        script_path = self.root / "scripts" / "qualify_harp_inn.py"
        specification = importlib.util.spec_from_file_location(
            "qualify_harp_inn", script_path
        )
        module = importlib.util.module_from_spec(specification)
        assert specification.loader is not None
        specification.loader.exec_module(module)

        reproduced = module.import_group1(source)

        for key in (
            "dataset",
            "qualification",
            "contexts",
            "evidence",
            "relations",
            "typed_relations",
            "authority",
        ):
            self.assertEqual(reproduced[key], self.document[key])


if __name__ == "__main__":
    unittest.main()