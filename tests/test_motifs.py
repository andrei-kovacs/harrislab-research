import unittest

from harrislab import Context, Relation, RelationStatus, Stratigraphy
from harrislab.motifs import (
    analyze_generated_sampled_disagreements,
    analyze_sampled_disagreement,
)


class DisagreementMotifTests(unittest.TestCase):
    def test_exact_top_tie_accepts_either_sampled_choice(self) -> None:
        graph = Stratigraphy()
        for identifier in ("1", "2", "3"):
            graph.add_context(Context(identifier, f"Context {identifier}"))
        graph.add_relation(Relation("1", "2", RelationStatus.DISPUTED))
        graph.add_relation(Relation("1", "3", RelationStatus.DISPUTED))

        case = analyze_sampled_disagreement(
            graph, sample_count=2_000, burn_in=1_000, sampler_seed=17
        )

        self.assertEqual(case.exact_top_tie_size, 2)
        self.assertTrue(case.sampled_choice_is_exact_optimum)
        self.assertEqual(case.exact_top_margin_fraction, 0.0)

    def test_bridge_fixture_has_unique_exact_optimum(self) -> None:
        graph = Stratigraphy()
        for identifier in ("1", "2", "3", "4"):
            graph.add_context(Context(identifier, f"Context {identifier}"))
        graph.add_relation(Relation("1", "2"))
        graph.add_relation(Relation("3", "4"))
        graph.add_relation(Relation("2", "3", RelationStatus.DISPUTED))
        graph.add_relation(Relation("1", "3", RelationStatus.DISPUTED))

        case = analyze_sampled_disagreement(
            graph, sample_count=2_000, burn_in=1_000, sampler_seed=23
        )

        self.assertEqual(case.exact_top_tie_size, 1)
        self.assertTrue(case.endpoint_choice_agrees)
        self.assertGreater(case.exact_top_margin_fraction, 0)
        self.assertEqual(case.exact_choice_motif.closure_gain, 4)

    def test_generated_analysis_is_reproducible(self) -> None:
        first = analyze_generated_sampled_disagreements(
            case_count=5, sample_count=300, burn_in=300, seed=41
        )
        second = analyze_generated_sampled_disagreements(
            case_count=5, sample_count=300, burn_in=300, seed=41
        )

        self.assertEqual(first, second)
        self.assertEqual(
            first.tie_compatible_mismatch_count,
            len(first.endpoint_mismatches) - len(first.genuine_score_errors),
        )


if __name__ == "__main__":
    unittest.main()