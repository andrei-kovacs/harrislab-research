"""Generate the retrospective Trimmis Profile 19 benchmark artifact."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harrislab.approval import file_sha256
from harrislab.benchmark import RankingStrategy, run_hidden_relation_benchmark
from harrislab.io import load_stratigraphy

EXPERIMENT_ID = "trimmis-profile19-retrospective-v1"
HIDDEN_EDGES = (("156", "150"), ("30", "241"), ("23", "235"))
RANDOM_SEED = 20260917
SAMPLED_SEED = 20260917


def generate_report(
    reference_path: Path,
    *,
    sample_count: int = 2_000,
    burn_in: int = 2_000,
    thinning: int = 10,
    chain_count: int = 4,
    order_limit: int = 100_000,
) -> dict[str, Any]:
    reference = load_stratigraphy(reference_path)
    settings = {
        "order_limit": order_limit,
        "sample_count_per_chain": sample_count,
        "burn_in": burn_in,
        "thinning": thinning,
        "chain_count": chain_count,
    }
    runs = []
    for strategy in RankingStrategy:
        seed = (
            SAMPLED_SEED
            if strategy is RankingStrategy.SAMPLED_ORDERS
            else RANDOM_SEED
        )
        result = run_hidden_relation_benchmark(
            reference,
            HIDDEN_EDGES,
            strategy,
            seed=seed,
            order_limit=order_limit,
            sample_count=sample_count,
            burn_in=burn_in,
            thinning=thinning,
            chain_count=chain_count,
        )
        runs.append(_serialize_result(result))

    return {
        "schema": "harrislab.hidden-relation-benchmark.v1",
        "experiment_id": EXPERIMENT_ID,
        "design": "retrospective demonstration",
        "reference": {
            "path": reference_path.name,
            "sha256": file_sha256(reference_path),
            "context_count": len(reference.contexts),
            "direct_relation_count": len(reference.relations),
        },
        "hidden_edges": [list(edge) for edge in HIDDEN_EDGES],
        "selection_note": (
            "These three edges were published in the app prototype before the "
            "benchmark was run; they were not selected from benchmark outcomes."
        ),
        "settings": settings,
        "runs": runs,
    }


def _serialize_result(result: Any) -> dict[str, Any]:
    steps = []
    for step in result.steps:
        item = asdict(step)
        relation = item.pop("revealed_relation")
        item["edge"] = [relation["earlier"], relation["later"]]
        item["implication_recall"] = step.implication_recall
        steps.append(item)
    return {
        "strategy": result.strategy.value,
        "seed": result.seed,
        "reference_implications": result.reference_implications,
        "initial_recovered_implications": result.initial_recovered_implications,
        "area_under_recovery_curve": result.area_under_recovery_curve,
        "steps": steps,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reference",
        type=Path,
        default=Path("data/trimmis_profile19_reference.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/trimmis_profile19_benchmark.json"),
    )
    arguments = parser.parse_args()
    report = generate_report(arguments.reference)
    arguments.output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {arguments.output}")


if __name__ == "__main__":
    main()