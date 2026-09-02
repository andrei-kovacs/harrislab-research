"""Controlled hidden-relation recovery experiments."""

from dataclasses import dataclass, replace
from enum import StrEnum
from random import Random

from .analysis import accepted_graph, candidate_impacts
from .model import Relation, RelationStatus, Stratigraphy
from .surrogate import closure_candidate_impacts, diagnose_sampled_order_chains


class RankingStrategy(StrEnum):
    IMPACT = "impact"
    CLOSURE_GAIN = "closure_gain"
    SAMPLED_ORDERS = "sampled_orders"
    LEXICOGRAPHIC = "lexicographic"
    RANDOM = "random"


@dataclass(frozen=True, slots=True)
class HiddenRelationTrial:
    observed_graph: Stratigraphy
    hidden_relations: tuple[Relation, ...]


@dataclass(frozen=True, slots=True)
class RecoveryStep:
    step: int
    revealed_relation: Relation
    impact_reduction: int | None
    closure_gain: int
    sampled_reduction_fraction: float | None
    sampled_split_r_hat: float | None
    sampled_effective_sample_size: float | None
    sampled_top_choice_consensus: float | None
    recovered_implications: int
    reference_implications: int
    chronological_orders: int | None

    @property
    def implication_recall(self) -> float:
        return self.recovered_implications / self.reference_implications


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    strategy: RankingStrategy
    seed: int | None
    hidden_relations: tuple[Relation, ...]
    reference_implications: int
    initial_recovered_implications: int
    steps: tuple[RecoveryStep, ...]
    area_under_recovery_curve: float


def prepare_hidden_relation_trial(
    reference: Stratigraphy,
    hidden_edges: tuple[tuple[str, str], ...],
) -> HiddenRelationTrial:
    """Convert selected observed reference edges into held-out candidates."""

    reference_graph = accepted_graph(reference)
    if reference_graph.contradiction_cycle() is not None:
        raise ValueError("reference graph must be acyclic")
    if not hidden_edges:
        raise ValueError("at least one hidden edge is required")
    if len(hidden_edges) != len(set(hidden_edges)):
        raise ValueError("hidden edge list contains duplicates")

    observed_by_edge: dict[tuple[str, str], Relation] = {}
    duplicate_edges: set[tuple[str, str]] = set()
    for relation in reference_graph.relations:
        edge = (relation.earlier, relation.later)
        if edge in observed_by_edge:
            duplicate_edges.add(edge)
        observed_by_edge[edge] = relation
    if duplicate_edges:
        formatted = ", ".join(
            f"{earlier} -> {later}" for earlier, later in sorted(duplicate_edges)
        )
        raise ValueError(f"reference contains duplicate edges: {formatted}")

    hidden: list[Relation] = []
    hidden_keys = set(hidden_edges)
    for edge in hidden_edges:
        relation = observed_by_edge.get(edge)
        if relation is None:
            raise ValueError(f"hidden edge is not in the reference: {edge[0]} -> {edge[1]}")
        if relation.status is not RelationStatus.OBSERVED:
            raise ValueError(
                f"hidden edge is not observed: {relation.earlier} -> {relation.later}"
            )
        hidden.append(relation)

    visible = [
        relation
        for relation in reference_graph.relations
        if (relation.earlier, relation.later) not in hidden_keys
    ]
    candidates = [
        replace(relation, status=RelationStatus.DISPUTED) for relation in hidden
    ]
    trial_graph = Stratigraphy(
        contexts=reference.contexts.copy(),
        evidence=reference.evidence.copy(),
        relations=[*visible, *candidates],
    )
    return HiddenRelationTrial(trial_graph, tuple(hidden))


def run_hidden_relation_benchmark(
    reference: Stratigraphy,
    hidden_edges: tuple[tuple[str, str], ...],
    strategy: RankingStrategy = RankingStrategy.IMPACT,
    *,
    seed: int = 0,
    order_limit: int = 100_000,
    sample_count: int = 1_000,
    burn_in: int = 1_000,
    thinning: int = 10,
    chain_count: int = 4,
) -> BenchmarkResult:
    """Reveal held-out edges and measure recovery of reference implications."""

    trial = prepare_hidden_relation_trial(reference, hidden_edges)
    reference_graph = accepted_graph(reference)
    reference_closure = _chronological_closure(reference_graph)
    current = Stratigraphy(
        contexts=trial.observed_graph.contexts.copy(),
        evidence=trial.observed_graph.evidence.copy(),
        relations=trial.observed_graph.relations.copy(),
    )
    initial_recovered = len(
        _chronological_closure(accepted_graph(current)) & reference_closure
    )
    original_by_edge = {
        (relation.earlier, relation.later): relation
        for relation in trial.hidden_relations
    }

    random_order = list(original_by_edge)
    Random(seed).shuffle(random_order)
    steps: list[RecoveryStep] = []
    while len(steps) < len(trial.hidden_relations):
        sampled_diagnostic = None
        closure_impacts = closure_candidate_impacts(current)
        closure_by_edge = {
            (impact.relation.earlier, impact.relation.later): impact
            for impact in closure_impacts
        }
        if strategy is RankingStrategy.IMPACT:
            impacts = candidate_impacts(current, order_limit)
            if any(impact.count_truncated for impact in impacts):
                raise ValueError(
                    "order count truncated; impact ranking is not valid at this limit"
                )
            selected_impact = impacts[0]
            selected_relation = selected_impact.relation
            impact_reduction = selected_impact.reduction
        elif strategy is RankingStrategy.CLOSURE_GAIN:
            selected_relation = closure_impacts[0].relation
            impact_reduction = None
        elif strategy is RankingStrategy.SAMPLED_ORDERS:
            sampled_diagnostic = diagnose_sampled_order_chains(
                current,
                chain_count=chain_count,
                samples_per_chain=sample_count,
                burn_in=burn_in,
                thinning=thinning,
                seed=seed + len(steps),
            )
            selected_relation = sampled_diagnostic.impacts[0].relation
            impact_reduction = None
        else:
            remaining = set(closure_by_edge)
            if strategy is RankingStrategy.LEXICOGRAPHIC:
                selected_edge = min(remaining)
            elif strategy is RankingStrategy.RANDOM:
                selected_edge = next(edge for edge in random_order if edge in remaining)
            else:
                raise ValueError(f"unsupported ranking strategy: {strategy}")
            selected_relation = closure_by_edge[selected_edge].relation
            impact_reduction = None

        selected_edge = (
            selected_relation.earlier,
            selected_relation.later,
        )
        original = original_by_edge[selected_edge]
        sampled_fraction = None
        sampled_r_hat = None
        sampled_ess = None
        sampled_consensus = None
        if strategy is RankingStrategy.SAMPLED_ORDERS:
            sampled_fraction = next(
                impact.estimated_reduction_fraction
                for impact in sampled_diagnostic.impacts
                if (
                    impact.relation.earlier,
                    impact.relation.later,
                )
                == selected_edge
            )
            selected_diagnostic = next(
                item
                for item in sampled_diagnostic.diagnostics
                if (item.relation.earlier, item.relation.later) == selected_edge
            )
            sampled_r_hat = selected_diagnostic.split_r_hat
            sampled_ess = selected_diagnostic.effective_sample_size
            sampled_consensus = sampled_diagnostic.top_choice_consensus
        current.relations = [
            relation
            for relation in current.relations
            if (relation.earlier, relation.later) != selected_edge
        ]
        current.relations.append(original)
        accepted = accepted_graph(current)
        orders: int | None = None
        if strategy is RankingStrategy.IMPACT:
            orders, truncated = accepted.count_chronological_orders(order_limit)
            if truncated:
                raise ValueError("order count truncated after revealing a relation")
        recovered = len(_chronological_closure(accepted) & reference_closure)
        steps.append(
            RecoveryStep(
                step=len(steps) + 1,
                revealed_relation=original,
                impact_reduction=impact_reduction,
                closure_gain=closure_by_edge[selected_edge].new_implications,
                sampled_reduction_fraction=sampled_fraction,
                sampled_split_r_hat=sampled_r_hat,
                sampled_effective_sample_size=sampled_ess,
                sampled_top_choice_consensus=sampled_consensus,
                recovered_implications=recovered,
                reference_implications=len(reference_closure),
                chronological_orders=orders,
            )
        )

    recalls = [
        initial_recovered / len(reference_closure),
        *(step.implication_recall for step in steps),
    ]
    area = sum(
        (left + right) / 2 for left, right in zip(recalls, recalls[1:])
    ) / len(steps)
    return BenchmarkResult(
        strategy=strategy,
        seed=(
            seed
            if strategy in {RankingStrategy.RANDOM, RankingStrategy.SAMPLED_ORDERS}
            else None
        ),
        hidden_relations=trial.hidden_relations,
        reference_implications=len(reference_closure),
        initial_recovered_implications=initial_recovered,
        steps=tuple(steps),
        area_under_recovery_curve=area,
    )


def _chronological_closure(graph: Stratigraphy) -> frozenset[tuple[str, str]]:
    return frozenset(
        (relation.earlier, relation.later)
        for relation in [*graph.relations, *graph.derived_relations()]
    )