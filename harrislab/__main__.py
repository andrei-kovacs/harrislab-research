"""Command-line audit report for a HarrisLab dataset."""

import argparse
import json

from .analysis import accepted_graph, candidate_impacts
from .io import load_stratigraphy


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", help="Path to a HarrisLab JSON dataset")
    parser.add_argument(
        "--order-limit",
        type=int,
        default=100_000,
        help="Stop counting chronological orders at this bound",
    )
    args = parser.parse_args()

    graph = load_stratigraphy(args.dataset)
    accepted = accepted_graph(graph)
    cycle = accepted.contradiction_cycle()
    order_count, order_count_truncated = accepted.count_chronological_orders(
        args.order_limit
    )
    impacts = candidate_impacts(graph, args.order_limit)
    report = {
        "contexts": len(graph.contexts),
        "evidence_items": len(graph.evidence),
        "accepted_relations": len(accepted.relations),
        "unresolved_relations": len(graph.relations) - len(accepted.relations),
        "derived_relations": len(accepted.derived_relations()),
        "contradiction_cycle": cycle,
        "chronological_orders": order_count,
        "order_count_truncated": order_count_truncated,
        "candidate_impacts": [
            {
                "earlier": impact.relation.earlier,
                "later": impact.relation.later,
                "status": impact.relation.status,
                "orders_without": impact.orders_without,
                "orders_with": impact.orders_with,
                "reduction": impact.reduction,
                "creates_contradiction": impact.creates_contradiction,
                "count_truncated": impact.count_truncated,
            }
            for impact in impacts
        ],
    }
    print(json.dumps(report, indent=2))
    return 1 if cycle else 0


if __name__ == "__main__":
    raise SystemExit(main())
