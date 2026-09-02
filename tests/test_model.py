import unittest

from harrislab import (
    Context,
    Evidence,
    EvidenceKind,
    Relation,
    RelationStatus,
    Stratigraphy,
)


class StratigraphyTests(unittest.TestCase):
    def test_acyclic_sequence_has_no_contradiction(self) -> None:
        graph = Stratigraphy()
        for identifier in ("100", "101", "102"):
            graph.add_context(Context(identifier, f"Context {identifier}"))

        graph.add_relation(Relation("100", "101"))
        graph.add_relation(Relation("101", "102"))

        self.assertIsNone(graph.contradiction_cycle())

    def test_temporal_cycle_is_reported_with_closed_path(self) -> None:
        graph = Stratigraphy()
        for identifier in ("100", "101", "102"):
            graph.add_context(Context(identifier, f"Context {identifier}"))

        graph.add_relation(Relation("100", "101"))
        graph.add_relation(Relation("101", "102"))
        graph.add_relation(Relation("102", "100"))

        self.assertEqual(graph.contradiction_cycle(), ("100", "101", "102", "100"))

    def test_derives_only_relationships_not_already_recorded(self) -> None:
        graph = Stratigraphy()
        for identifier in ("100", "101", "102"):
            graph.add_context(Context(identifier, f"Context {identifier}"))
        graph.add_relation(Relation("100", "101"))
        graph.add_relation(Relation("101", "102"))

        derived = graph.derived_relations()

        self.assertEqual([(item.earlier, item.later) for item in derived], [("100", "102")])

    def test_counts_alternative_valid_orders(self) -> None:
        graph = Stratigraphy()
        for identifier in ("100", "101", "102", "103"):
            graph.add_context(Context(identifier, f"Context {identifier}"))
        graph.add_relation(Relation("100", "101"))
        graph.add_relation(Relation("100", "102"))
        graph.add_relation(Relation("101", "103"))
        graph.add_relation(Relation("102", "103"))

        self.assertEqual(graph.count_chronological_orders(), (2, False))

    def test_rejects_relation_with_unknown_evidence(self) -> None:
        graph = Stratigraphy()
        graph.add_context(Context("100", "Natural subsoil"))
        graph.add_context(Context("101", "Construction cut"))
        graph.add_evidence(
            Evidence("E1", EvidenceKind.CONTEXT_SHEET, "Sheet 100", "archive/100")
        )

        with self.assertRaisesRegex(ValueError, "unknown evidence: E2"):
            graph.add_relation(Relation("100", "101", evidence_ids=("E2",)))

    def test_dependency_witness_is_shortest_deterministic_and_evidence_linked(self) -> None:
        graph = Stratigraphy()
        for identifier in ("100", "101", "102", "103"):
            graph.add_context(Context(identifier, f"Context {identifier}"))
        graph.add_evidence(
            Evidence("E1", EvidenceKind.DRAWING, "Section", "archive/section")
        )
        graph.add_evidence(
            Evidence("E2", EvidenceKind.CONTEXT_SHEET, "Sheet", "archive/sheet")
        )
        graph.add_relation(Relation("100", "102", evidence_ids=("E2",)))
        graph.add_relation(Relation("102", "103", evidence_ids=("E2",)))
        graph.add_relation(Relation("100", "101", evidence_ids=("E1",)))
        graph.add_relation(Relation("101", "103", evidence_ids=("E1", "E2")))

        witness = graph.dependency_witness("100", "103")

        self.assertIsNotNone(witness)
        assert witness is not None
        self.assertEqual(
            [(relation.earlier, relation.later) for relation in witness.relations],
            [("100", "101"), ("101", "103")],
        )
        self.assertEqual([item.identifier for item in witness.evidence], ["E1", "E2"])
        self.assertTrue(witness.is_fully_evidenced)

    def test_dependency_witness_reports_provenance_gap(self) -> None:
        graph = Stratigraphy()
        graph.add_context(Context("100", "Context 100"))
        graph.add_context(Context("101", "Context 101"))
        relation = Relation("100", "101")
        graph.add_relation(relation)

        witness = graph.dependency_witness("100", "101")

        self.assertIsNotNone(witness)
        assert witness is not None
        self.assertEqual(witness.relations_without_evidence, (relation,))
        self.assertFalse(witness.is_fully_evidenced)

    def test_dependency_witness_does_not_treat_derived_edge_as_source(self) -> None:
        graph = Stratigraphy()
        graph.add_context(Context("100", "Context 100"))
        graph.add_context(Context("101", "Context 101"))
        graph.add_relation(Relation("100", "101", status=RelationStatus.DERIVED))

        self.assertIsNone(graph.dependency_witness("100", "101"))


if __name__ == "__main__":
    unittest.main()