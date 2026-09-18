"""Prepare and run the Harp Inn Group 1 cross-dataset benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from dataclasses import asdict
from pathlib import Path
from statistics import mean
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harrislab.approval import file_sha256
from harrislab.benchmark import RankingStrategy, run_hidden_relation_benchmark
from harrislab.io import load_stratigraphy

EXPERIMENT_ID = "harp-inn-group1-cross-dataset-v1"
GENERATED_ON = "2026-09-18"


def build_design(reference_path: Path) -> dict[str, Any]:
    document = json.loads(reference_path.read_text(encoding="utf-8"))
    reference_hash = file_sha256(reference_path)
    edges = [
        (relation["earlier"], relation["later"])
        for relation in document["relations"]
        if relation.get("status", "observed") == "observed"
        and relation.get("evidence_ids")
    ]
    ordered = sorted(
        edges,
        key=lambda edge: hashlib.sha256(
            f"{reference_hash}:{edge[0]}->{edge[1]}".encode("ascii")
        ).hexdigest(),
    )
    trials = [
        {
            "id": f"harp-{index // 3 + 1:02d}",
            "hidden_edges": [list(edge) for edge in ordered[index : index + 3]],
        }
        for index in range(0, len(ordered), 3)
    ]
    return {
        "schema": "harrislab.hidden-relation-design.v1",
        "experiment_id": EXPERIMENT_ID,
        "status": "frozen_before_local_execution_not_publicly_preregistered",
        "reference": {
            "path": reference_path.name,
            "sha256": reference_hash,
            "context_count": len(document["contexts"]),
            "direct_relation_count": len(document["relations"]),
            "typed_non_precedence_relation_count": len(document["typed_relations"]),
        },
        "eligibility": "Every unique observed precedence relation with source evidence",
        "assignment": "SHA-256(reference hash + edge), ascending, groups of three",
        "settings": {
            "order_limit": 100_000,
            "sample_count_per_chain": 500,
            "burn_in": 500,
            "thinning": 5,
            "chain_count": 4,
            "random_repetitions_per_trial": 20,
            "seed_base": 2026091800,
        },
        "trials": trials,
    }


def generate_report(
    reference_path: Path,
    design_path: Path,
    *,
    sample_count: int | None = None,
    burn_in: int | None = None,
    thinning: int | None = None,
    chain_count: int | None = None,
    order_limit: int | None = None,
    random_repetitions: int | None = None,
) -> dict[str, Any]:
    design = json.loads(design_path.read_text(encoding="utf-8"))
    reference = load_stratigraphy(reference_path)
    _validate_design(reference_path, design)
    declared = design["settings"]
    settings = {
        "order_limit": order_limit or declared["order_limit"],
        "sample_count_per_chain": sample_count or declared["sample_count_per_chain"],
        "burn_in": burn_in if burn_in is not None else declared["burn_in"],
        "thinning": thinning or declared["thinning"],
        "chain_count": chain_count or declared["chain_count"],
        "random_repetitions_per_trial": random_repetitions
        or declared["random_repetitions_per_trial"],
        "seed_base": declared["seed_base"],
    }
    trials = []
    for trial_number, trial in enumerate(design["trials"], 1):
        hidden_edges = tuple(tuple(edge) for edge in trial["hidden_edges"])
        runs = {}
        for strategy in (
            RankingStrategy.IMPACT,
            RankingStrategy.CLOSURE_GAIN,
            RankingStrategy.SAMPLED_ORDERS,
            RankingStrategy.LEXICOGRAPHIC,
        ):
            try:
                result = run_hidden_relation_benchmark(
                    reference,
                    hidden_edges,
                    strategy,
                    seed=settings["seed_base"] + trial_number,
                    order_limit=settings["order_limit"],
                    sample_count=settings["sample_count_per_chain"],
                    burn_in=settings["burn_in"],
                    thinning=settings["thinning"],
                    chain_count=settings["chain_count"],
                )
                runs[strategy.value] = _serialize(result)
            except ValueError as error:
                if strategy is not RankingStrategy.IMPACT or "truncated" not in str(error):
                    raise
                runs[strategy.value] = {"status": "truncated", "error": str(error)}

        random_runs = []
        for repetition in range(settings["random_repetitions_per_trial"]):
            seed = settings["seed_base"] * 100 + trial_number * 100 + repetition
            result = run_hidden_relation_benchmark(
                reference,
                hidden_edges,
                RankingStrategy.RANDOM,
                seed=seed,
                order_limit=settings["order_limit"],
            )
            random_runs.append(
                {
                    "seed": seed,
                    "area_under_recovery_curve": result.area_under_recovery_curve,
                    "edge_order": [
                        [step.revealed_relation.earlier, step.revealed_relation.later]
                        for step in result.steps
                    ],
                }
            )
        trials.append(
            {
                "id": trial["id"],
                "hidden_edges": trial["hidden_edges"],
                "runs": runs,
                "random_runs": random_runs,
                "random_mean_area_under_recovery_curve": mean(
                    run["area_under_recovery_curve"] for run in random_runs
                ),
            }
        )
    return _json_safe({
        "schema": "harrislab.cross-dataset-benchmark.v1",
        "experiment_id": design["experiment_id"],
        "design": design["status"],
        "generated_on": GENERATED_ON,
        "protocol": {"path": design_path.name, "sha256": file_sha256(design_path)},
        "reference": design["reference"],
        "settings": settings,
        "trials": trials,
        "aggregate": _aggregate(trials),
    })


def _json_safe(value: Any) -> Any:
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def _validate_design(reference_path: Path, design: dict[str, Any]) -> None:
    expected = build_design(reference_path)
    if design != expected:
        raise ValueError("benchmark design does not match deterministic assignment")


def _serialize(result: Any) -> dict[str, Any]:
    steps = []
    for step in result.steps:
        item = asdict(step)
        relation = item.pop("revealed_relation")
        item["edge"] = [relation["earlier"], relation["later"]]
        item["implication_recall"] = step.implication_recall
        steps.append(item)
    return {
        "status": "complete",
        "seed": result.seed,
        "reference_implications": result.reference_implications,
        "initial_recovered_implications": result.initial_recovered_implications,
        "area_under_recovery_curve": result.area_under_recovery_curve,
        "steps": steps,
    }


def _aggregate(trials: list[dict[str, Any]]) -> dict[str, Any]:
    exact = [trial for trial in trials if trial["runs"]["impact"]["status"] == "complete"]
    sampled_steps = [
        step
        for trial in trials
        for step in trial["runs"]["sampled_orders"]["steps"]
    ]
    means = {
        strategy: mean(
            trial["runs"][strategy]["area_under_recovery_curve"] for trial in trials
        )
        for strategy in ("closure_gain", "sampled_orders", "lexicographic")
    }
    means["random"] = mean(
        trial["random_mean_area_under_recovery_curve"] for trial in trials
    )
    means["impact_completed_trials_only"] = (
        mean(trial["runs"]["impact"]["area_under_recovery_curve"] for trial in exact)
        if exact
        else None
    )
    return {
        "trial_count": len(trials),
        "hidden_edge_count": sum(len(trial["hidden_edges"]) for trial in trials),
        "exact_completed_trial_count": len(exact),
        "exact_truncated_trial_count": len(trials) - len(exact),
        "mean_area_under_recovery_curve": means,
        "closure_minus_lexicographic": means["closure_gain"] - means["lexicographic"],
        "closure_minus_random": means["closure_gain"] - means["random"],
        "sampled_minus_lexicographic": means["sampled_orders"] - means["lexicographic"],
        "sampled_minus_random": means["sampled_orders"] - means["random"],
        "sampling_warnings": {
            "selected_step_count": len(sampled_steps),
            "split_r_hat_above_1_05": sum(
                step["sampled_split_r_hat"] is None
                or step["sampled_split_r_hat"] > 1.05
                for step in sampled_steps
            ),
            "effective_sample_size_below_400": sum(
                step["sampled_effective_sample_size"] < 400 for step in sampled_steps
            ),
            "top_choice_consensus_below_0_75": sum(
                step["sampled_top_choice_consensus"] < 0.75 for step in sampled_steps
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reference",
        type=Path,
        default=Path("data/harp_inn_group1_reference.json"),
    )
    parser.add_argument(
        "--design",
        type=Path,
        default=Path("data/harp_inn_group1_benchmark_design.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/harp_inn_group1_benchmark.json"),
    )
    parser.add_argument("--prepare", action="store_true")
    arguments = parser.parse_args()
    if arguments.prepare:
        arguments.design.write_text(
            json.dumps(build_design(arguments.reference), indent=2, ensure_ascii=True)
            + "\n",
            encoding="ascii",
        )
        print(f"Wrote {arguments.design}")
        return
    report = generate_report(arguments.reference, arguments.design)
    arguments.output.write_text(
        json.dumps(report, indent=2, ensure_ascii=True) + "\n",
        encoding="ascii",
    )
    print(f"Wrote {arguments.output}")


if __name__ == "__main__":
    main()