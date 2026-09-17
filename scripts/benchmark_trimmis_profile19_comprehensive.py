"""Run the preregistered comprehensive Trimmis Profile 19 benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
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


def generate_report(
    reference_path: Path,
    preregistration_path: Path,
    *,
    sample_count: int | None = None,
    burn_in: int | None = None,
    thinning: int | None = None,
    chain_count: int | None = None,
    order_limit: int | None = None,
    random_repetitions: int | None = None,
) -> dict[str, Any]:
    preregistration = json.loads(preregistration_path.read_text(encoding="utf-8"))
    reference = load_stratigraphy(reference_path)
    _validate_preregistration(reference_path, preregistration)
    declared = preregistration["settings"]
    settings = {
        "order_limit": order_limit or declared["order_limit"],
        "sample_count_per_chain": sample_count
        or declared["sample_count_per_chain"],
        "burn_in": burn_in if burn_in is not None else declared["burn_in"],
        "thinning": thinning or declared["thinning"],
        "chain_count": chain_count or declared["chain_count"],
        "random_repetitions_per_trial": random_repetitions
        or declared["random_repetitions_per_trial"],
    }
    trials = []
    for trial_number, trial in enumerate(preregistration["trials"], start=1):
        hidden_edges = tuple(tuple(edge) for edge in trial["hidden_edges"])
        runs: dict[str, Any] = {}
        for strategy in (
            RankingStrategy.IMPACT,
            RankingStrategy.CLOSURE_GAIN,
            RankingStrategy.SAMPLED_ORDERS,
            RankingStrategy.LEXICOGRAPHIC,
        ):
            seed = 2026091700 + trial_number
            try:
                result = run_hidden_relation_benchmark(
                    reference,
                    hidden_edges,
                    strategy,
                    seed=seed,
                    order_limit=settings["order_limit"],
                    sample_count=settings["sample_count_per_chain"],
                    burn_in=settings["burn_in"],
                    thinning=settings["thinning"],
                    chain_count=settings["chain_count"],
                )
                runs[strategy.value] = _serialize_result(result)
            except ValueError as error:
                if strategy is not RankingStrategy.IMPACT or "truncated" not in str(error):
                    raise
                runs[strategy.value] = {"status": "truncated", "error": str(error)}

        random_runs = []
        for repetition in range(settings["random_repetitions_per_trial"]):
            seed = 202609170000 + 100 * trial_number + repetition
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

    return {
        "schema": "harrislab.comprehensive-benchmark.v1",
        "experiment_id": preregistration["experiment_id"],
        "design": "preregistered comprehensive edge-partition benchmark",
        "generated_on": "2026-09-17",
        "preregistration": {
            "path": preregistration_path.name,
            "sha256": file_sha256(preregistration_path),
        },
        "reference": preregistration["reference"],
        "settings": settings,
        "trials": trials,
        "aggregate": _aggregate(trials),
    }


def _validate_preregistration(reference_path: Path, document: dict[str, Any]) -> None:
    reference_hash = file_sha256(reference_path)
    if document["reference"]["sha256"] != reference_hash:
        raise ValueError("preregistration does not match reference SHA-256")
    raw_reference = json.loads(reference_path.read_text(encoding="utf-8"))
    eligible = [
        (relation["earlier"], relation["later"])
        for relation in raw_reference["relations"]
        if relation.get("status", "observed") == "observed"
        and relation.get("evidence_ids")
    ]
    if len(eligible) != len(set(eligible)):
        raise ValueError("eligible reference relations are not unique")
    expected = sorted(
        eligible,
        key=lambda edge: hashlib.sha256(
            f"{reference_hash}:{edge[0]}->{edge[1]}".encode()
        ).hexdigest(),
    )
    declared = [
        tuple(edge)
        for trial in document["trials"]
        for edge in trial["hidden_edges"]
    ]
    if declared != expected:
        raise ValueError("preregistered trials do not match deterministic assignment")


def _serialize_result(result: Any) -> dict[str, Any]:
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
    exact_trials = [trial for trial in trials if trial["runs"]["impact"]["status"] == "complete"]
    strategy_means = {
        strategy: mean(
            trial["runs"][strategy]["area_under_recovery_curve"]
            for trial in trials
        )
        for strategy in ("closure_gain", "sampled_orders", "lexicographic")
    }
    if exact_trials:
        strategy_means["impact"] = mean(
            trial["runs"]["impact"]["area_under_recovery_curve"]
            for trial in exact_trials
        )
    random_mean = mean(
        trial["random_mean_area_under_recovery_curve"] for trial in trials
    )
    exact_orders = [
        [step["edge"] for step in trial["runs"]["impact"]["steps"]]
        for trial in exact_trials
    ]
    closure_orders = [
        [step["edge"] for step in trial["runs"]["closure_gain"]["steps"]]
        for trial in exact_trials
    ]
    sampled_orders = [
        [step["edge"] for step in trial["runs"]["sampled_orders"]["steps"]]
        for trial in exact_trials
    ]
    sampled_steps = [
        step
        for trial in trials
        for step in trial["runs"]["sampled_orders"]["steps"]
    ]
    return {
        "trial_count": len(trials),
        "exact_completed_trial_count": len(exact_trials),
        "exact_truncated_trial_count": len(trials) - len(exact_trials),
        "mean_area_under_recovery_curve": {
            **strategy_means,
            "random": random_mean,
        },
        "mean_paired_impact_minus_lexicographic": mean(
            trial["runs"]["impact"]["area_under_recovery_curve"]
            - trial["runs"]["lexicographic"]["area_under_recovery_curve"]
            for trial in exact_trials
        )
        if exact_trials
        else None,
        "mean_paired_impact_minus_random": mean(
            trial["runs"]["impact"]["area_under_recovery_curve"]
            - trial["random_mean_area_under_recovery_curve"]
            for trial in exact_trials
        )
        if exact_trials
        else None,
        "descriptive_secondary_comparisons": {
            "mean_paired_closure_minus_lexicographic": mean(
                trial["runs"]["closure_gain"]["area_under_recovery_curve"]
                - trial["runs"]["lexicographic"]["area_under_recovery_curve"]
                for trial in trials
            ),
            "mean_paired_closure_minus_random": mean(
                trial["runs"]["closure_gain"]["area_under_recovery_curve"]
                - trial["random_mean_area_under_recovery_curve"]
                for trial in trials
            ),
            "closure_at_least_lexicographic_trial_count": sum(
                trial["runs"]["closure_gain"]["area_under_recovery_curve"]
                >= trial["runs"]["lexicographic"]["area_under_recovery_curve"]
                for trial in trials
            ),
            "closure_above_random_mean_trial_count": sum(
                trial["runs"]["closure_gain"]["area_under_recovery_curve"]
                > trial["random_mean_area_under_recovery_curve"]
                for trial in trials
            ),
            "mean_paired_sampled_minus_lexicographic": mean(
                trial["runs"]["sampled_orders"]["area_under_recovery_curve"]
                - trial["runs"]["lexicographic"]["area_under_recovery_curve"]
                for trial in trials
            ),
            "mean_paired_sampled_minus_random": mean(
                trial["runs"]["sampled_orders"]["area_under_recovery_curve"]
                - trial["random_mean_area_under_recovery_curve"]
                for trial in trials
            ),
        },
        "exact_closure_full_order_agreement_rate": sum(
            exact == closure for exact, closure in zip(exact_orders, closure_orders)
        )
        / len(exact_trials)
        if exact_trials
        else None,
        "exact_sampled_full_order_agreement_rate": sum(
            exact == sampled for exact, sampled in zip(exact_orders, sampled_orders)
        )
        / len(exact_trials)
        if exact_trials
        else None,
        "sampling_diagnostics": {
            "selected_step_count": len(sampled_steps),
            "split_r_hat_above_1_05": sum(
                step["sampled_split_r_hat"] > 1.05 for step in sampled_steps
            ),
            "effective_sample_size_below_400": sum(
                step["sampled_effective_sample_size"] < 400
                for step in sampled_steps
            ),
            "top_choice_consensus_below_0_75": sum(
                step["sampled_top_choice_consensus"] < 0.75
                for step in sampled_steps
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reference",
        type=Path,
        default=Path("data/trimmis_profile19_reference.json"),
    )
    parser.add_argument(
        "--preregistration",
        type=Path,
        default=Path("data/trimmis_profile19_benchmark_preregistration.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/trimmis_profile19_comprehensive_benchmark.json"),
    )
    arguments = parser.parse_args()
    report = generate_report(arguments.reference, arguments.preregistration)
    arguments.output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {arguments.output}")


if __name__ == "__main__":
    main()