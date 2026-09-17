import json
import os
import subprocess
import sys
from pathlib import Path

import unittest

from harrislab import Context, Relation, RelationStatus, Stratigraphy
from harrislab.surrogate import (
    calibrate_closure_surrogate,
    calibrate_generated_dags,
    calibrate_generated_dags_sampled,
    calibrate_sampled_order_surrogate,
    closure_candidate_impacts,
    diagnose_sampled_order_chains,
    generate_calibration_graph,
    sampled_order_candidate_impacts,
    sequential_sampled_order_ranking,
)


class ClosureSurrogateTests(unittest.TestCase):
    def test_sampled_ranking_is_independent_of_python_hash_seed(self) -> None:
        root = Path(__file__).resolve().parents[1]
        code = """
import json
from harrislab.io import load_stratigraphy
from harrislab.benchmark import RankingStrategy, run_hidden_relation_benchmark
result = run_hidden_relation_benchmark(
    load_stratigraphy('data/trimmis_profile19_reference.json'),
    (('30', '241'), ('99', '102'), ('170', '156')),
    RankingStrategy.SAMPLED_ORDERS,
    seed=2026091701,
    sample_count=20,
    burn_in=20,
    thinning=2,
    chain_count=2,
)
print(json.dumps([(step.revealed_relation.earlier, step.revealed_relation.later, step.sampled_reduction_fraction) for step in result.steps]))
"""
        outputs = []
        for hash_seed in ("1", "2"):
            environment = os.environ.copy()
            environment["PYTHONHASHSEED"] = hash_seed
            outputs.append(
                subprocess.check_output(
                    [sys.executable, "-c", code],
                    cwd=root,
                    env=environment,
                    text=True,
                ).strip()
            )

        self.assertEqual(json.loads(outputs[0]), json.loads(outputs[1]))

    def test_bridge_candidate_ranks_above_redundant_candidate(self) -> None:
        graph = self._candidate_graph()

        impacts = closure_candidate_impacts(graph)

        self.assertEqual(self._edge(impacts[0].relation), ("2", "3"))
        self.assertGreater(impacts[0].new_implications, impacts[1].new_implications)

    def test_calibration_agrees_on_bridge_top_choice(self) -> None:
        calibration = calibrate_closure_surrogate(self._candidate_graph())

        self.assertTrue(calibration.top_choice_agrees)
        self.assertEqual(calibration.exact_order[0], ("2", "3"))
        self.assertEqual(calibration.surrogate_order[0], ("2", "3"))

    def test_seeded_generated_calibration_is_reproducible(self) -> None:
        first = calibrate_generated_dags(case_count=5, seed=41)
        second = calibrate_generated_dags(case_count=5, seed=41)

        self.assertEqual(first, second)
        self.assertGreaterEqual(first.top_choice_agreement_rate, 0.0)
        self.assertLessEqual(first.top_choice_agreement_rate, 1.0)
        self.assertGreaterEqual(first.mean_pairwise_agreement, 0.0)
        self.assertLessEqual(first.mean_pairwise_agreement, 1.0)

    def test_surrogate_handles_graph_too_large_for_exact_default_bound(self) -> None:
        graph = generate_calibration_graph(
            context_count=20,
            accepted_probability=0.05,
            candidate_count=4,
            seed=7,
        )

        impacts = closure_candidate_impacts(graph)

        self.assertEqual(len(impacts), 4)

    def test_sampled_fraction_is_near_half_for_unconstrained_pair(self) -> None:
        graph = Stratigraphy()
        graph.add_context(Context("1", "Context 1"))
        graph.add_context(Context("2", "Context 2"))
        graph.add_relation(Relation("1", "2", RelationStatus.DISPUTED))

        impact = sampled_order_candidate_impacts(
            graph, sample_count=4_000, burn_in=500, thinning=2, seed=17
        )[0]

        self.assertGreater(impact.estimated_reduction_fraction, 0.45)
        self.assertLess(impact.estimated_reduction_fraction, 0.55)

    def test_sampled_calibration_agrees_on_bridge_top_choice(self) -> None:
        calibration = calibrate_sampled_order_surrogate(
            self._candidate_graph(), sample_count=2_000, seed=23
        )

        self.assertTrue(calibration.top_choice_agrees)
        self.assertEqual(calibration.surrogate_order[0], ("2", "3"))

    def test_seeded_sampled_calibration_is_reproducible(self) -> None:
        first = calibrate_generated_dags_sampled(
            case_count=5, sample_count=300, burn_in=300, thinning=3, seed=41
        )
        second = calibrate_generated_dags_sampled(
            case_count=5, sample_count=300, burn_in=300, thinning=3, seed=41
        )

        self.assertEqual(first, second)

    def test_multichain_diagnostics_for_unconstrained_pair(self) -> None:
        graph = Stratigraphy()
        graph.add_context(Context("1", "Context 1"))
        graph.add_context(Context("2", "Context 2"))
        graph.add_relation(Relation("1", "2", RelationStatus.DISPUTED))

        result = diagnose_sampled_order_chains(
            graph,
            chain_count=4,
            samples_per_chain=1_000,
            burn_in=500,
            thinning=2,
            seed=71,
        )

        impact = result.impacts[0]
        diagnostic = result.diagnostics[0]
        self.assertGreater(impact.estimated_reduction_fraction, 0.45)
        self.assertLess(impact.estimated_reduction_fraction, 0.55)
        self.assertLess(diagnostic.split_r_hat, 1.05)
        self.assertGreater(diagnostic.effective_sample_size, 100)
        self.assertLess(diagnostic.effective_sample_size, impact.sample_count)
        self.assertEqual(result.top_choice_consensus, 1.0)
        self.assertTrue(result.meets_thresholds())
        self.assertFalse(result.meets_thresholds(min_top_choice_consensus=1.1))

    def test_multichain_diagnostics_are_reproducible(self) -> None:
        first = diagnose_sampled_order_chains(
            self._candidate_graph(), samples_per_chain=200, seed=83
        )
        second = diagnose_sampled_order_chains(
            self._candidate_graph(), samples_per_chain=200, seed=83
        )

        self.assertEqual(first, second)

    def test_sequential_ranking_resolves_bridge_fixture(self) -> None:
        result = sequential_sampled_order_ranking(
            self._candidate_graph(),
            initial_samples_per_chain=500,
            max_samples_per_chain=2_000,
            burn_in=500,
            thinning=2,
            min_effective_sample_size=100,
            seed=97,
        )

        self.assertTrue(result.resolved)
        self.assertEqual(result.selected_edge, ("2", "3"))
        self.assertGreater(result.stages[-1].confidence_interval[0], 0)

    def test_sequential_ranking_leaves_exact_tie_unresolved(self) -> None:
        graph = Stratigraphy()
        for identifier in ("1", "2", "3"):
            graph.add_context(Context(identifier, f"Context {identifier}"))
        graph.add_relation(Relation("1", "2", RelationStatus.DISPUTED))
        graph.add_relation(Relation("1", "3", RelationStatus.DISPUTED))

        result = sequential_sampled_order_ranking(
            graph,
            initial_samples_per_chain=500,
            max_samples_per_chain=2_000,
            burn_in=500,
            thinning=2,
            min_effective_sample_size=100,
            confidence_level=0.99,
            seed=101,
        )

        self.assertFalse(result.resolved)
        self.assertIsNone(result.selected_edge)
        self.assertEqual(result.total_samples, 8_000)
        lower, upper = result.stages[-1].confidence_interval
        self.assertLessEqual(lower, 0)
        self.assertGreaterEqual(upper, 0)

    @staticmethod
    def _candidate_graph() -> Stratigraphy:
        graph = Stratigraphy()
        for identifier in ("1", "2", "3", "4"):
            graph.add_context(Context(identifier, f"Context {identifier}"))
        graph.add_relation(Relation("1", "2"))
        graph.add_relation(Relation("3", "4"))
        graph.add_relation(Relation("2", "3", RelationStatus.DISPUTED))
        graph.add_relation(Relation("1", "3", RelationStatus.DISPUTED))
        return graph

    @staticmethod
    def _edge(relation: Relation) -> tuple[str, str]:
        return relation.earlier, relation.later


if __name__ == "__main__":
    unittest.main()