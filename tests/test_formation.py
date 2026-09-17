import json
import tempfile
import unittest
from pathlib import Path

from harrislab.formation import (
    formation_metrics,
    generate_depositional_patch_sequence,
    generate_edge_matched_forward_dag,
)
from harrislab.model import Context, Relation, Stratigraphy
from scripts.benchmark_formation_process import run_benchmark


class FormationProcessTests(unittest.TestCase):
    def test_automaton_is_deterministic_and_acyclic(self) -> None:
        settings = {
            "context_count": 8,
            "width": 10,
            "growth_steps": 3,
            "spread_probability": 0.5,
            "seed": 42,
        }
        first = generate_depositional_patch_sequence(**settings)
        second = generate_depositional_patch_sequence(**settings)

        self.assertEqual(first.footprints, second.footprints)
        self.assertEqual(first.graph.relations, second.graph.relations)
        self.assertIsNone(first.graph.contradiction_cycle())
        self.assertEqual(first.footprints[0], tuple(range(10)))
        self.assertTrue(all(first.footprints[1:]))

    def test_control_matches_requested_nodes_and_edges(self) -> None:
        control = generate_edge_matched_forward_dag(
            context_count=8, edge_count=12, seed=42
        )

        self.assertEqual(len(control.graph.contexts), 8)
        self.assertEqual(len(control.graph.relations), 12)
        self.assertIsNone(control.graph.contradiction_cycle())
        self.assertEqual(
            {relation.later for relation in control.graph.relations},
            {f"F{index:02d}" for index in range(1, 8)},
        )

    def test_metrics_for_chain_are_exact(self) -> None:
        graph = Stratigraphy()
        for identifier in ("A", "B", "C"):
            graph.add_context(Context(identifier, identifier))
        graph.add_relation(Relation("A", "B"))
        graph.add_relation(Relation("B", "C"))

        metrics = formation_metrics(graph)

        self.assertEqual(metrics.direct_relation_count, 2)
        self.assertEqual(metrics.derived_relation_count, 1)
        self.assertEqual(metrics.closure_relation_count, 3)
        self.assertEqual(metrics.closure_amplification, 1.5)
        self.assertEqual(metrics.redundant_direct_relation_count, 0)
        self.assertEqual(metrics.longest_path_length, 2)

    def test_metrics_detect_redundant_direct_relation(self) -> None:
        graph = Stratigraphy()
        for identifier in ("A", "B", "C"):
            graph.add_context(Context(identifier, identifier))
        graph.add_relation(Relation("A", "B"))
        graph.add_relation(Relation("B", "C"))
        graph.add_relation(Relation("A", "C"))

        metrics = formation_metrics(graph)

        self.assertEqual(metrics.derived_relation_count, 0)
        self.assertEqual(metrics.redundant_direct_relation_count, 1)
        self.assertEqual(metrics.longest_path_length, 2)

    def test_invalid_generator_settings_fail(self) -> None:
        with self.assertRaisesRegex(ValueError, "context_count"):
            generate_depositional_patch_sequence(
                context_count=1,
                width=10,
                growth_steps=3,
                spread_probability=0.5,
                seed=42,
            )
        with self.assertRaisesRegex(ValueError, "edge_count"):
            generate_edge_matched_forward_dag(
                context_count=8, edge_count=6, seed=42
            )

    def test_runner_preserves_matching_on_independent_fixture(self) -> None:
        manifest = {
            "schema": "harrislab.formation-process-preregistration.v1",
            "status": "frozen-before-outcome-generation",
            "settings": {
                "repetitions": 3,
                "context_count": 6,
                "width": 8,
                "growth_steps": 2,
                "spread_probability": 0.5,
                "automaton_seed_base": 100,
                "control_seed_base": 200,
            },
            "interpretation_limit": "Test fixture only.",
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            result = run_benchmark(path)

        self.assertEqual(result["summary"]["trial_count"], 3)
        self.assertTrue(
            all(
                trial["automaton"]["direct_relation_count"]
                == trial["control"]["direct_relation_count"]
                for trial in result["trials"]
            )
        )

    def test_runner_rejects_unfrozen_manifest(self) -> None:
        manifest = {
            "schema": "harrislab.formation-process-preregistration.v1",
            "status": "draft",
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "not frozen"):
                run_benchmark(path)


if __name__ == "__main__":
    unittest.main()