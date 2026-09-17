"""Synthetic graph generators for formation-process software benchmarks."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random

from .model import Context, Evidence, EvidenceKind, Relation, Stratigraphy


@dataclass(frozen=True, slots=True)
class FormationSequence:
    graph: Stratigraphy
    generator: str
    seed: int
    width: int
    footprints: tuple[tuple[int, ...], ...]


@dataclass(frozen=True, slots=True)
class FormationMetrics:
    context_count: int
    direct_relation_count: int
    derived_relation_count: int
    closure_relation_count: int
    closure_amplification: float
    redundant_direct_relation_count: int
    longest_path_length: int


def generate_depositional_patch_sequence(
    *,
    context_count: int,
    width: int,
    growth_steps: int,
    spread_probability: float,
    seed: int,
) -> FormationSequence:
    """Grow local one-dimensional patches and stack them over existing tops."""
    if context_count < 2:
        raise ValueError("context_count must be at least two")
    if width < 2:
        raise ValueError("width must be at least two")
    if growth_steps < 0:
        raise ValueError("growth_steps must not be negative")
    if not 0 <= spread_probability <= 1:
        raise ValueError("spread_probability must be between zero and one")

    random = Random(seed)
    graph = _empty_synthetic_graph("depositional-patch-automaton", context_count)
    tops: list[str | None] = [None] * width
    footprints: list[tuple[int, ...]] = []

    for index in range(context_count):
        identifier = f"F{index:02d}"
        if index == 0:
            footprint = set(range(width))
        else:
            footprint = {random.randrange(width)}
            for _ in range(growth_steps):
                frontier = sorted(
                    {
                        neighbour
                        for column in footprint
                        for neighbour in (column - 1, column + 1)
                        if 0 <= neighbour < width and neighbour not in footprint
                    }
                )
                footprint.update(
                    column
                    for column in frontier
                    if random.random() < spread_probability
                )

        predecessors = sorted(
            {tops[column] for column in footprint if tops[column] is not None}
        )
        for predecessor in predecessors:
            graph.add_relation(
                Relation(predecessor, identifier, evidence_ids=("synthetic-rule",))
            )
        for column in footprint:
            tops[column] = identifier
        footprints.append(tuple(sorted(footprint)))

    if graph.contradiction_cycle() is not None:
        raise AssertionError("depositional patch generator produced a cycle")
    return FormationSequence(
        graph=graph,
        generator="depositional_patch_automaton",
        seed=seed,
        width=width,
        footprints=tuple(footprints),
    )


def generate_edge_matched_forward_dag(
    *, context_count: int, edge_count: int, seed: int
) -> FormationSequence:
    """Generate a connected forward DAG with an exact requested edge count."""
    if context_count < 2:
        raise ValueError("context_count must be at least two")
    minimum_edges = context_count - 1
    maximum_edges = context_count * (context_count - 1) // 2
    if not minimum_edges <= edge_count <= maximum_edges:
        raise ValueError(
            f"edge_count must be between {minimum_edges} and {maximum_edges}"
        )

    random = Random(seed)
    graph = _empty_synthetic_graph("edge-count-matched-forward-dag", context_count)
    pairs = {
        (f"F{random.randrange(later):02d}", f"F{later:02d}")
        for later in range(1, context_count)
    }
    available = [
        (f"F{earlier:02d}", f"F{later:02d}")
        for later in range(1, context_count)
        for earlier in range(later)
        if (f"F{earlier:02d}", f"F{later:02d}") not in pairs
    ]
    random.shuffle(available)
    pairs.update(available[: edge_count - len(pairs)])
    for earlier, later in sorted(pairs):
        graph.add_relation(
            Relation(earlier, later, evidence_ids=("synthetic-rule",))
        )
    return FormationSequence(
        graph=graph,
        generator="edge_count_matched_forward_dag",
        seed=seed,
        width=0,
        footprints=(),
    )


def formation_metrics(graph: Stratigraphy) -> FormationMetrics:
    if graph.contradiction_cycle() is not None:
        raise ValueError("formation metrics require an acyclic graph")
    direct_count = len(graph.relations)
    if direct_count == 0:
        raise ValueError("formation metrics require at least one relation")
    derived_count = len(graph.derived_relations())
    closure_count = direct_count + derived_count
    redundant_count = sum(
        _is_reachable_without(graph, relation.earlier, relation.later, index)
        for index, relation in enumerate(graph.relations)
    )
    return FormationMetrics(
        context_count=len(graph.contexts),
        direct_relation_count=direct_count,
        derived_relation_count=derived_count,
        closure_relation_count=closure_count,
        closure_amplification=closure_count / direct_count,
        redundant_direct_relation_count=redundant_count,
        longest_path_length=_longest_path_length(graph),
    )


def _empty_synthetic_graph(generator: str, context_count: int) -> Stratigraphy:
    graph = Stratigraphy()
    graph.add_evidence(
        Evidence(
            "synthetic-rule",
            EvidenceKind.OTHER,
            "Computational construction, not archaeological evidence",
            generator,
        )
    )
    for index in range(context_count):
        graph.add_context(Context(f"F{index:02d}", f"Synthetic event {index}"))
    return graph


def _is_reachable_without(
    graph: Stratigraphy, earlier: str, later: str, ignored_index: int
) -> bool:
    adjacency = {identifier: set() for identifier in graph.contexts}
    for index, relation in enumerate(graph.relations):
        if index != ignored_index:
            adjacency[relation.earlier].add(relation.later)
    pending = list(adjacency[earlier])
    visited: set[str] = set()
    while pending:
        current = pending.pop()
        if current == later:
            return True
        if current not in visited:
            visited.add(current)
            pending.extend(adjacency[current] - visited)
    return False


def _longest_path_length(graph: Stratigraphy) -> int:
    incoming = {identifier: set() for identifier in graph.contexts}
    outgoing = {identifier: set() for identifier in graph.contexts}
    for relation in graph.relations:
        incoming[relation.later].add(relation.earlier)
        outgoing[relation.earlier].add(relation.later)
    available = sorted(
        identifier for identifier, predecessors in incoming.items() if not predecessors
    )
    distances = {identifier: 0 for identifier in graph.contexts}
    while available:
        current = available.pop(0)
        for later in sorted(outgoing[current]):
            distances[later] = max(distances[later], distances[current] + 1)
            incoming[later].remove(current)
            if not incoming[later]:
                available.append(later)
                available.sort()
    return max(distances.values())