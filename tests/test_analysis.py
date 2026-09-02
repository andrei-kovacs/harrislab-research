import unittest

from harrislab import (
    Context,
    Evidence,
    EvidenceKind,
    Interpretation,
    Relation,
    RelationDecision,
    RelationStatus,
    ScenarioDecision,
    Stratigraphy,
    accepted_graph,
    candidate_impacts,
    compare_interpretations,
    evaluate_interpretation,
    interpretation_dependency_witness,
)


class CandidateAnalysisTests(unittest.TestCase):
    def test_disputed_relation_is_not_silently_accepted(self) -> None:
        graph = self._diamond_graph()
        graph.add_relation(Relation("101", "102", RelationStatus.DISPUTED))

        accepted = accepted_graph(graph)
        impact = candidate_impacts(graph)[0]

        self.assertEqual(accepted.count_chronological_orders(), (2, False))
        self.assertEqual(impact.orders_with, 1)
        self.assertEqual(impact.reduction, 1)
        self.assertFalse(impact.creates_contradiction)

    def test_candidate_that_creates_cycle_is_flagged(self) -> None:
        graph = self._diamond_graph()
        graph.add_relation(Relation("103", "100", RelationStatus.AI_PROPOSED))

        impact = candidate_impacts(graph)[0]

        self.assertTrue(impact.creates_contradiction)
        self.assertEqual(impact.orders_with, 0)

    def test_named_interpretations_preserve_opposite_consequences(self) -> None:
        graph = self._diamond_graph()
        graph.add_relation(Relation("101", "102", RelationStatus.DISPUTED))
        graph.add_relation(Relation("102", "101", RelationStatus.DISPUTED))
        interpretation_a = Interpretation(
            "A",
            (RelationDecision("101", "102", ScenarioDecision.ACCEPT),),
        )
        interpretation_b = Interpretation(
            "B",
            (RelationDecision("102", "101", ScenarioDecision.ACCEPT),),
        )

        comparison = compare_interpretations(graph, interpretation_a, interpretation_b)

        self.assertEqual(comparison.left.chronological_orders, 1)
        self.assertEqual(comparison.right.chronological_orders, 1)
        self.assertEqual(len(comparison.left.undecided), 1)
        self.assertEqual(len(comparison.right.undecided), 1)
        self.assertIn(("101", "102"), comparison.implied_only_by_left)
        self.assertIn(("102", "101"), comparison.implied_only_by_right)
        self.assertEqual(accepted_graph(graph).count_chronological_orders(), (2, False))

    def test_interpretation_rejects_unknown_candidate_decision(self) -> None:
        graph = self._diamond_graph()
        interpretation = Interpretation(
            "invalid",
            (RelationDecision("101", "102", ScenarioDecision.ACCEPT),),
        )

        with self.assertRaisesRegex(ValueError, "not for an unresolved relation"):
            evaluate_interpretation(graph, interpretation)

    def test_interpretation_rejects_duplicate_candidate_endpoints(self) -> None:
        graph = self._diamond_graph()
        graph.add_relation(Relation("101", "102", RelationStatus.DISPUTED))
        graph.add_relation(Relation("101", "102", RelationStatus.AI_PROPOSED))

        with self.assertRaisesRegex(ValueError, "ambiguous duplicate candidate"):
            evaluate_interpretation(graph, Interpretation("ambiguous"))

    def test_interpretation_witness_includes_accepted_candidate_evidence(self) -> None:
        graph = self._diamond_graph()
        graph.add_evidence(
            Evidence("E1", EvidenceKind.DRAWING, "Section", "archive/section")
        )
        candidate = Relation(
            "101", "102", RelationStatus.DISPUTED, evidence_ids=("E1",)
        )
        graph.add_relation(candidate)
        interpretation = Interpretation(
            "accept candidate",
            (RelationDecision("101", "102", ScenarioDecision.ACCEPT),),
        )

        witness = interpretation_dependency_witness(
            graph, interpretation, "101", "102"
        )

        self.assertIsNotNone(witness)
        assert witness is not None
        self.assertEqual(witness.relations, (candidate,))
        self.assertEqual([item.identifier for item in witness.evidence], ["E1"])
        self.assertIsNone(
            interpretation_dependency_witness(
                graph, Interpretation("undecided"), "101", "102"
            )
        )

    @staticmethod
    def _diamond_graph() -> Stratigraphy:
        graph = Stratigraphy()
        for identifier in ("100", "101", "102", "103"):
            graph.add_context(Context(identifier, f"Context {identifier}"))
        graph.add_relation(Relation("100", "101"))
        graph.add_relation(Relation("100", "102"))
        graph.add_relation(Relation("101", "103"))
        graph.add_relation(Relation("102", "103"))
        return graph


if __name__ == "__main__":
    unittest.main()
