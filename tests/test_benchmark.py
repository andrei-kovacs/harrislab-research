import unittest

from harrislab import Context, Relation, Stratigraphy
from harrislab.benchmark import (
    RankingStrategy,
    prepare_hidden_relation_trial,
    run_hidden_relation_benchmark,
)


class HiddenRelationBenchmarkTests(unittest.TestCase):
    def test_trial_preserves_source_relation_and_marks_copy_disputed(self) -> None:
        reference = self._bridge_graph()

        trial = prepare_hidden_relation_trial(reference, (("2", "3"),))

        self.assertEqual(trial.hidden_relations, (reference.relations[1],))
        candidate = trial.observed_graph.relations[-1]
        self.assertEqual(candidate.status, "disputed")
        self.assertEqual(reference.relations[1].status, "observed")

    def test_impact_ranking_recovers_closure_before_lexicographic_baseline(self) -> None:
        reference = self._bridge_graph()
        hidden = (("2", "3"), ("1", "3"))

        impact = run_hidden_relation_benchmark(reference, hidden)
        baseline = run_hidden_relation_benchmark(
            reference, hidden, RankingStrategy.LEXICOGRAPHIC
        )

        self.assertEqual(
            (impact.steps[0].revealed_relation.earlier, impact.steps[0].revealed_relation.later),
            ("2", "3"),
        )
        self.assertEqual(impact.steps[0].implication_recall, 1.0)
        self.assertGreater(
            impact.area_under_recovery_curve, baseline.area_under_recovery_curve
        )

    def test_seeded_random_baseline_is_reproducible(self) -> None:
        reference = self._bridge_graph()
        hidden = (("2", "3"), ("1", "3"))

        first = run_hidden_relation_benchmark(
            reference, hidden, RankingStrategy.RANDOM, seed=17
        )
        second = run_hidden_relation_benchmark(
            reference, hidden, RankingStrategy.RANDOM, seed=17
        )

        self.assertEqual(first.steps, second.steps)
        self.assertEqual(first.area_under_recovery_curve, second.area_under_recovery_curve)

    def test_benchmark_rejects_truncated_impact_counts(self) -> None:
        reference = self._bridge_graph()

        with self.assertRaisesRegex(ValueError, "order count truncated"):
            run_hidden_relation_benchmark(reference, (("2", "3"),), order_limit=1)

    def test_trial_requires_a_hidden_edge(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least one hidden edge"):
            prepare_hidden_relation_trial(self._bridge_graph(), ())

    def test_closure_gain_strategy_does_not_enumerate_orders(self) -> None:
        reference = Stratigraphy()
        for index in range(20):
            identifier = str(index)
            reference.add_context(Context(identifier, f"Context {identifier}"))
        for index in range(19):
            reference.add_relation(Relation(str(index), str(index + 1)))
        hidden = tuple((str(index), str(index + 1)) for index in range(0, 10, 2))

        result = run_hidden_relation_benchmark(
            reference,
            hidden,
            RankingStrategy.CLOSURE_GAIN,
            order_limit=1,
        )

        self.assertEqual(len(result.steps), len(hidden))
        self.assertTrue(all(step.chronological_orders is None for step in result.steps))
        self.assertTrue(all(step.impact_reduction is None for step in result.steps))

    def test_sampled_order_strategy_is_reproducible_and_avoids_enumeration(self) -> None:
        reference = self._bridge_graph()
        hidden = (("2", "3"), ("1", "3"))

        first = run_hidden_relation_benchmark(
            reference,
            hidden,
            RankingStrategy.SAMPLED_ORDERS,
            seed=29,
            order_limit=1,
            sample_count=500,
        )
        second = run_hidden_relation_benchmark(
            reference,
            hidden,
            RankingStrategy.SAMPLED_ORDERS,
            seed=29,
            order_limit=1,
            sample_count=500,
        )

        self.assertEqual(first, second)
        self.assertTrue(all(step.chronological_orders is None for step in first.steps))
        self.assertTrue(
            all(step.sampled_reduction_fraction is not None for step in first.steps)
        )
        self.assertTrue(
            all(step.sampled_split_r_hat is not None for step in first.steps)
        )
        self.assertTrue(
            all(step.sampled_effective_sample_size is not None for step in first.steps)
        )
        self.assertTrue(
            all(step.sampled_top_choice_consensus is not None for step in first.steps)
        )

    @staticmethod
    def _bridge_graph() -> Stratigraphy:
        graph = Stratigraphy()
        for identifier in ("1", "2", "3", "4"):
            graph.add_context(Context(identifier, f"Context {identifier}"))
        graph.add_relation(Relation("1", "2"))
        graph.add_relation(Relation("2", "3"))
        graph.add_relation(Relation("3", "4"))
        graph.add_relation(Relation("1", "3"))
        return graph


if __name__ == "__main__":
    unittest.main()