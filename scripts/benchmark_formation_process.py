"""Execute the frozen synthetic formation-process benchmark."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from statistics import mean, median, stdev
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harrislab.approval import file_sha256
from harrislab.formation import (
    formation_metrics,
    generate_depositional_patch_sequence,
    generate_edge_matched_forward_dag,
)


def run_benchmark(preregistration_path: Path) -> dict[str, Any]:
    manifest = json.loads(preregistration_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "harrislab.formation-process-preregistration.v1":
        raise ValueError("unsupported formation benchmark manifest schema")
    if manifest.get("status") != "frozen-before-outcome-generation":
        raise ValueError("benchmark manifest is not frozen")
    settings = manifest["settings"]
    if settings["repetitions"] < 2:
        raise ValueError("benchmark requires at least two repetitions")
    trial_results = []
    differences = []
    for trial in range(1, settings["repetitions"] + 1):
        automaton = generate_depositional_patch_sequence(
            context_count=settings["context_count"],
            width=settings["width"],
            growth_steps=settings["growth_steps"],
            spread_probability=settings["spread_probability"],
            seed=settings["automaton_seed_base"] + trial,
        )
        automaton_metrics = formation_metrics(automaton.graph)
        control = generate_edge_matched_forward_dag(
            context_count=settings["context_count"],
            edge_count=automaton_metrics.direct_relation_count,
            seed=settings["control_seed_base"] + trial,
        )
        control_metrics = formation_metrics(control.graph)
        if (
            automaton_metrics.context_count != control_metrics.context_count
            or automaton_metrics.direct_relation_count
            != control_metrics.direct_relation_count
        ):
            raise AssertionError("control is not node-and-edge-count matched")
        difference = (
            automaton_metrics.closure_amplification
            - control_metrics.closure_amplification
        )
        differences.append(difference)
        trial_results.append(
            {
                "trial": trial,
                "automaton_seed": automaton.seed,
                "control_seed": control.seed,
                "automaton": asdict(automaton_metrics),
                "control": asdict(control_metrics),
                "paired_closure_amplification_difference": difference,
                "automaton_footprints": [list(item) for item in automaton.footprints],
            }
        )

    mean_difference = mean(differences)
    return {
        "schema": "harrislab.formation-process-benchmark.v1",
        "title": "Synthetic depositional-patch automaton benchmark",
        "preregistration": {
            "path": preregistration_path.name,
            "sha256": file_sha256(preregistration_path),
        },
        "summary": {
            "trial_count": len(trial_results),
            "mean_paired_closure_amplification_difference": mean_difference,
            "median_paired_closure_amplification_difference": median(differences),
            "sample_standard_deviation": stdev(differences),
            "minimum_paired_difference": min(differences),
            "maximum_paired_difference": max(differences),
            "directional_hypothesis_outcome": (
                "supported_on_fixed_schedule"
                if mean_difference > 0
                else "falsified_on_fixed_schedule"
            ),
        },
        "interpretation_limit": manifest["interpretation_limit"],
        "trials": trial_results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--preregistration",
        type=Path,
        default=Path("data/formation_process_benchmark_preregistration.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/formation_process_benchmark.json"),
    )
    arguments = parser.parse_args()
    result = run_benchmark(arguments.preregistration)
    arguments.output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()