"""Scenario analysis for unresolved stratigraphic relationships."""

from dataclasses import dataclass
from enum import StrEnum

from .model import DependencyWitness, Relation, RelationStatus, Stratigraphy


ACCEPTED_STATUSES = frozenset({RelationStatus.OBSERVED, RelationStatus.DERIVED})
CANDIDATE_STATUSES = frozenset(
    {RelationStatus.DISPUTED, RelationStatus.AI_PROPOSED}
)


@dataclass(frozen=True, slots=True)
class CandidateImpact:
    relation: Relation
    orders_without: int
    orders_with: int
    reduction: int
    creates_contradiction: bool
    count_truncated: bool


class ScenarioDecision(StrEnum):
    ACCEPT = "accept"
    REJECT = "reject"
    UNDECIDED = "undecided"


@dataclass(frozen=True, slots=True)
class RelationDecision:
    earlier: str
    later: str
    decision: ScenarioDecision


@dataclass(frozen=True, slots=True)
class Interpretation:
    name: str
    decisions: tuple[RelationDecision, ...] = ()


@dataclass(frozen=True, slots=True)
class InterpretationResult:
    interpretation: Interpretation
    accepted: tuple[Relation, ...]
    rejected: tuple[Relation, ...]
    undecided: tuple[Relation, ...]
    contradiction_cycle: tuple[str, ...] | None
    chronological_orders: int
    count_truncated: bool
    implied_relations: frozenset[tuple[str, str]]


@dataclass(frozen=True, slots=True)
class InterpretationComparison:
    left: InterpretationResult
    right: InterpretationResult
    implied_only_by_left: frozenset[tuple[str, str]]
    implied_only_by_right: frozenset[tuple[str, str]]


def accepted_graph(graph: Stratigraphy) -> Stratigraphy:
    return _copy_with_relations(
        graph,
        [relation for relation in graph.relations if relation.status in ACCEPTED_STATUSES],
    )


def candidate_impacts(
    graph: Stratigraphy, limit: int = 100_000
) -> tuple[CandidateImpact, ...]:
    """Compare each unresolved edge with the accepted interpretation."""

    baseline = accepted_graph(graph)
    orders_without, baseline_truncated = baseline.count_chronological_orders(limit)
    impacts: list[CandidateImpact] = []

    for relation in graph.relations:
        if relation.status not in CANDIDATE_STATUSES:
            continue
        proposed = _copy_with_relations(baseline, [*baseline.relations, relation])
        cycle = proposed.contradiction_cycle()
        orders_with, proposed_truncated = proposed.count_chronological_orders(limit)
        impacts.append(
            CandidateImpact(
                relation=relation,
                orders_without=orders_without,
                orders_with=orders_with,
                reduction=orders_without - orders_with,
                creates_contradiction=cycle is not None,
                count_truncated=baseline_truncated or proposed_truncated,
            )
        )

    return tuple(
        sorted(
            impacts,
            key=lambda item: (-item.reduction, item.relation.earlier, item.relation.later),
        )
    )


def evaluate_interpretation(
    graph: Stratigraphy, interpretation: Interpretation, limit: int = 100_000
) -> InterpretationResult:
    """Apply explicit candidate decisions without changing the source graph."""

    candidates: dict[tuple[str, str], Relation] = {}
    for relation in graph.relations:
        if relation.status not in CANDIDATE_STATUSES:
            continue
        key = (relation.earlier, relation.later)
        if key in candidates:
            raise ValueError(
                f"ambiguous duplicate candidate: {relation.earlier} -> {relation.later}"
            )
        candidates[key] = relation
    decisions: dict[tuple[str, str], ScenarioDecision] = {}
    for item in interpretation.decisions:
        key = (item.earlier, item.later)
        if key in decisions:
            raise ValueError(f"duplicate scenario decision: {item.earlier} -> {item.later}")
        if key not in candidates:
            raise ValueError(f"decision is not for an unresolved relation: {item.earlier} -> {item.later}")
        decisions[key] = item.decision

    accepted: list[Relation] = []
    rejected: list[Relation] = []
    undecided: list[Relation] = []
    for key, relation in candidates.items():
        decision = decisions.get(key, ScenarioDecision.UNDECIDED)
        if decision is ScenarioDecision.ACCEPT:
            accepted.append(relation)
        elif decision is ScenarioDecision.REJECT:
            rejected.append(relation)
        else:
            undecided.append(relation)

    baseline = accepted_graph(graph)
    scenario = _copy_with_relations(baseline, [*baseline.relations, *accepted])
    cycle = scenario.contradiction_cycle()
    orders, truncated = scenario.count_chronological_orders(limit)
    implied = frozenset()
    if cycle is None:
        implied = frozenset(
            (relation.earlier, relation.later)
            for relation in [*scenario.relations, *scenario.derived_relations()]
        )

    relation_key = lambda relation: (relation.earlier, relation.later)
    return InterpretationResult(
        interpretation=interpretation,
        accepted=tuple(sorted(accepted, key=relation_key)),
        rejected=tuple(sorted(rejected, key=relation_key)),
        undecided=tuple(sorted(undecided, key=relation_key)),
        contradiction_cycle=cycle,
        chronological_orders=orders,
        count_truncated=truncated,
        implied_relations=implied,
    )


def compare_interpretations(
    graph: Stratigraphy,
    left: Interpretation,
    right: Interpretation,
    limit: int = 100_000,
) -> InterpretationComparison:
    left_result = evaluate_interpretation(graph, left, limit)
    right_result = evaluate_interpretation(graph, right, limit)
    return InterpretationComparison(
        left=left_result,
        right=right_result,
        implied_only_by_left=left_result.implied_relations - right_result.implied_relations,
        implied_only_by_right=right_result.implied_relations - left_result.implied_relations,
    )


def interpretation_dependency_witness(
    graph: Stratigraphy,
    interpretation: Interpretation,
    earlier: str,
    later: str,
) -> DependencyWitness | None:
    """Trace a chronological conclusion within one named interpretation."""

    result = evaluate_interpretation(graph, interpretation)
    if result.contradiction_cycle is not None:
        raise ValueError("cannot trace conclusions in a contradictory interpretation")
    baseline = accepted_graph(graph)
    scenario = _copy_with_relations(baseline, [*baseline.relations, *result.accepted])
    return scenario.dependency_witness(earlier, later)


def _copy_with_relations(
    graph: Stratigraphy, relations: list[Relation]
) -> Stratigraphy:
    return Stratigraphy(
        contexts=graph.contexts.copy(),
        evidence=graph.evidence.copy(),
        relations=relations.copy(),
    )
