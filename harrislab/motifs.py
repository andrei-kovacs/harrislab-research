"""Structural analysis of surrogate-versus-exact ranking disagreements."""

from dataclasses import dataclass

from .analysis import accepted_graph, candidate_impacts
from .model import Relation, Stratigraphy
from .surrogate import (
    closure_candidate_impacts,
    generate_calibration_graph,
    sampled_order_candidate_impacts,
)


@dataclass(frozen=True, slots=True)
class CandidateMotif:
    edge: tuple[str, str]
    exact_reduction: int
    exact_reduction_fraction: float
    closure_gain: int
    predecessor_count: int
    successor_count: int
    already_implied: bool


@dataclass(frozen=True, slots=True)
class DisagreementCase:
    graph_seed: int
    exact_choice: tuple[str, str]
    sampled_choice: tuple[str, str]
    endpoint_choice_agrees: bool
    sampled_choice_is_exact_optimum: bool
    exact_top_tie_size: int
    exact_top_margin_fraction: float
    valid_order_count: int
    accepted_relation_count: int
    closure_size: int
    incomparable_pair_count: int
    redundant_candidate_count: int
    exact_choice_motif: CandidateMotif
    sampled_choice_motif: CandidateMotif


@dataclass(frozen=True, slots=True)
class DisagreementSummary:
    cases: tuple[DisagreementCase, ...]

    @property
    def endpoint_agreement_rate(self) -> float:
        return sum(case.endpoint_choice_agrees for case in self.cases) / len(self.cases)

    @property
    def exact_optimum_rate(self) -> float:
        return sum(case.sampled_choice_is_exact_optimum for case in self.cases) / len(self.cases)

    @property
    def endpoint_mismatches(self) -> tuple[DisagreementCase, ...]:
        return tuple(case for case in self.cases if not case.endpoint_choice_agrees)

    @property
    def genuine_score_errors(self) -> tuple[DisagreementCase, ...]:
        return tuple(
            case for case in self.cases if not case.sampled_choice_is_exact_optimum
        )

    @property
    def tie_compatible_mismatch_count(self) -> int:
        return len(self.endpoint_mismatches) - len(self.genuine_score_errors)


def analyze_sampled_disagreement(
    graph: Stratigraphy,
    *,
    graph_seed: int = 0,
    sample_count: int = 5_000,
    burn_in: int = 5_000,
    thinning: int = 5,
    sampler_seed: int = 1_000_000,
    order_limit: int = 100_000,
) -> DisagreementCase:
    """Compare one sampled top choice with the exact optimum set."""

    exact = candidate_impacts(graph, order_limit)
    if not exact:
        raise ValueError("disagreement analysis requires candidates")
    if any(item.count_truncated for item in exact):
        raise ValueError("exact order count truncated during disagreement analysis")
    sampled = sampled_order_candidate_impacts(
        graph,
        sample_count,
        burn_in,
        thinning,
        seed=sampler_seed,
    )
    closure_impacts = {
        _edge(item.relation): item for item in closure_candidate_impacts(graph)
    }
    exact_by_edge = {_edge(item.relation): item for item in exact}
    exact_top_score = exact[0].reduction
    exact_top_edges = {
        edge for edge, item in exact_by_edge.items() if item.reduction == exact_top_score
    }
    lower_scores = sorted(
        {item.reduction for item in exact if item.reduction < exact_top_score},
        reverse=True,
    )
    runner_up_score = lower_scores[0] if lower_scores else exact_top_score
    valid_orders = exact[0].orders_without
    exact_choice = _edge(exact[0].relation)
    sampled_choice = _edge(sampled[0].relation)

    baseline = accepted_graph(graph)
    closure = {
        (relation.earlier, relation.later)
        for relation in [*baseline.relations, *baseline.derived_relations()]
    }
    predecessors = {identifier: set() for identifier in baseline.contexts}
    successors = {identifier: set() for identifier in baseline.contexts}
    for earlier, later in closure:
        successors[earlier].add(later)
        predecessors[later].add(earlier)
    context_count = len(baseline.contexts)
    comparable_pairs = len(closure)
    incomparable_pairs = context_count * (context_count - 1) // 2 - comparable_pairs

    def motif(edge: tuple[str, str]) -> CandidateMotif:
        relation = exact_by_edge[edge].relation
        return CandidateMotif(
            edge=edge,
            exact_reduction=exact_by_edge[edge].reduction,
            exact_reduction_fraction=(
                exact_by_edge[edge].reduction / valid_orders if valid_orders else 0.0
            ),
            closure_gain=closure_impacts[edge].new_implications,
            predecessor_count=len(predecessors[relation.earlier]),
            successor_count=len(successors[relation.later]),
            already_implied=edge in closure,
        )

    return DisagreementCase(
        graph_seed=graph_seed,
        exact_choice=exact_choice,
        sampled_choice=sampled_choice,
        endpoint_choice_agrees=exact_choice == sampled_choice,
        sampled_choice_is_exact_optimum=sampled_choice in exact_top_edges,
        exact_top_tie_size=len(exact_top_edges),
        exact_top_margin_fraction=(
            (exact_top_score - runner_up_score) / valid_orders if valid_orders else 0.0
        ),
        valid_order_count=valid_orders,
        accepted_relation_count=len(baseline.relations),
        closure_size=len(closure),
        incomparable_pair_count=incomparable_pairs,
        redundant_candidate_count=sum(
            item.reduction == 0 for item in exact
        ),
        exact_choice_motif=motif(exact_choice),
        sampled_choice_motif=motif(sampled_choice),
    )


def analyze_generated_sampled_disagreements(
    case_count: int = 200,
    context_count: int = 7,
    accepted_probability: float = 0.3,
    candidate_count: int = 4,
    sample_count: int = 5_000,
    burn_in: int = 5_000,
    thinning: int = 5,
    *,
    seed: int = 20260902,
    order_limit: int = 100_000,
) -> DisagreementSummary:
    if case_count < 1:
        raise ValueError("case count must be positive")
    return DisagreementSummary(
        tuple(
            analyze_sampled_disagreement(
                generate_calibration_graph(
                    context_count,
                    accepted_probability,
                    candidate_count,
                    seed=seed + case_index,
                ),
                graph_seed=seed + case_index,
                sample_count=sample_count,
                burn_in=burn_in,
                thinning=thinning,
                sampler_seed=seed + 1_000_000 + case_index,
                order_limit=order_limit,
            )
            for case_index in range(case_count)
        )
    )


def _edge(relation: Relation) -> tuple[str, str]:
    return relation.earlier, relation.later