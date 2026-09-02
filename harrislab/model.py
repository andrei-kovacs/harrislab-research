"""Core provenance-aware stratigraphic graph model."""

from collections import deque
from dataclasses import dataclass, field
from enum import StrEnum


class RelationStatus(StrEnum):
    """How a stratigraphic relationship entered the interpretation."""

    OBSERVED = "observed"
    DERIVED = "derived"
    DISPUTED = "disputed"
    AI_PROPOSED = "ai_proposed"


class EvidenceKind(StrEnum):
    CONTEXT_SHEET = "context_sheet"
    DRAWING = "drawing"
    PHOTOGRAPH = "photograph"
    SAMPLE = "sample"
    SPECIALIST_REPORT = "specialist_report"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class Evidence:
    identifier: str
    kind: EvidenceKind
    description: str
    source: str


@dataclass(frozen=True, slots=True)
class Context:
    identifier: str
    label: str


@dataclass(frozen=True, slots=True)
class Relation:
    """A directed constraint from an earlier context to a later context."""

    earlier: str
    later: str
    status: RelationStatus = RelationStatus.OBSERVED
    evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class DependencyWitness:
    """One deterministic supporting path for a chronological conclusion."""

    earlier: str
    later: str
    relations: tuple[Relation, ...]
    evidence: tuple[Evidence, ...]
    relations_without_evidence: tuple[Relation, ...]

    @property
    def is_fully_evidenced(self) -> bool:
        return not self.relations_without_evidence


@dataclass(slots=True)
class Stratigraphy:
    contexts: dict[str, Context] = field(default_factory=dict)
    evidence: dict[str, Evidence] = field(default_factory=dict)
    relations: list[Relation] = field(default_factory=list)

    def add_context(self, context: Context) -> None:
        if context.identifier in self.contexts:
            raise ValueError(f"duplicate context: {context.identifier}")
        self.contexts[context.identifier] = context

    def add_evidence(self, item: Evidence) -> None:
        if item.identifier in self.evidence:
            raise ValueError(f"duplicate evidence: {item.identifier}")
        self.evidence[item.identifier] = item

    def add_relation(self, relation: Relation) -> None:
        missing = {
            identifier
            for identifier in (relation.earlier, relation.later)
            if identifier not in self.contexts
        }
        if missing:
            raise ValueError(f"unknown context(s): {', '.join(sorted(missing))}")
        missing_evidence = set(relation.evidence_ids) - self.evidence.keys()
        if missing_evidence:
            raise ValueError(
                f"unknown evidence: {', '.join(sorted(missing_evidence))}"
            )
        self.relations.append(relation)

    def derived_relations(self) -> tuple[Relation, ...]:
        """Return temporal constraints implied through paths of length two or more."""

        adjacency = self._adjacency()
        direct = {(relation.earlier, relation.later) for relation in self.relations}
        derived: list[Relation] = []

        for earlier in sorted(self.contexts):
            frontier = list(adjacency[earlier])
            reachable: set[str] = set()
            while frontier:
                later = frontier.pop()
                if later in reachable:
                    continue
                reachable.add(later)
                frontier.extend(adjacency[later] - reachable)

            for later in sorted(reachable):
                if (earlier, later) not in direct:
                    derived.append(
                        Relation(earlier, later, status=RelationStatus.DERIVED)
                    )
        return tuple(derived)

    def dependency_witness(
        self, earlier: str, later: str
    ) -> DependencyWitness | None:
        """Return a deterministic shortest base-relation path and its evidence."""

        missing = {
            identifier
            for identifier in (earlier, later)
            if identifier not in self.contexts
        }
        if missing:
            raise ValueError(f"unknown context(s): {', '.join(sorted(missing))}")
        if earlier == later:
            raise ValueError("dependency witness requires distinct contexts")

        outgoing: dict[str, list[Relation]] = {
            identifier: [] for identifier in self.contexts
        }
        for relation in self.relations:
            if relation.status is not RelationStatus.DERIVED:
                outgoing[relation.earlier].append(relation)
        for relations in outgoing.values():
            relations.sort(
                key=lambda relation: (
                    relation.later,
                    relation.status.value,
                    relation.evidence_ids,
                )
            )

        frontier: deque[tuple[str, tuple[Relation, ...]]] = deque([(earlier, ())])
        visited = {earlier}
        while frontier:
            current, path = frontier.popleft()
            for relation in outgoing[current]:
                next_path = (*path, relation)
                if relation.later == later:
                    return self._build_dependency_witness(earlier, later, next_path)
                if relation.later not in visited:
                    visited.add(relation.later)
                    frontier.append((relation.later, next_path))
        return None

    def _build_dependency_witness(
        self, earlier: str, later: str, relations: tuple[Relation, ...]
    ) -> DependencyWitness:
        evidence: list[Evidence] = []
        seen_evidence: set[str] = set()
        without_evidence: list[Relation] = []
        for relation in relations:
            if not relation.evidence_ids:
                without_evidence.append(relation)
            for identifier in relation.evidence_ids:
                if identifier not in seen_evidence:
                    evidence.append(self.evidence[identifier])
                    seen_evidence.add(identifier)
        return DependencyWitness(
            earlier=earlier,
            later=later,
            relations=relations,
            evidence=tuple(evidence),
            relations_without_evidence=tuple(without_evidence),
        )

    def count_chronological_orders(self, limit: int = 100_000) -> tuple[int, bool]:
        """Count valid total orders, stopping at limit for bounded analysis."""

        if limit < 1:
            raise ValueError("limit must be positive")

        adjacency = self._adjacency()
        indegree = {identifier: 0 for identifier in self.contexts}
        for later_contexts in adjacency.values():
            for later in later_contexts:
                indegree[later] += 1

        count = 0
        truncated = False

        def count_from(current_indegree: dict[str, int], placed: int) -> None:
            nonlocal count, truncated
            if count >= limit:
                truncated = True
                return
            if placed == len(self.contexts):
                count += 1
                return

            available = sorted(
                identifier
                for identifier, degree in current_indegree.items()
                if degree == 0
            )
            for identifier in available:
                next_indegree = current_indegree.copy()
                next_indegree[identifier] = -1
                for later in adjacency[identifier]:
                    next_indegree[later] -= 1
                count_from(next_indegree, placed + 1)
                if truncated:
                    return

        count_from(indegree, 0)
        return count, truncated

    def _adjacency(self) -> dict[str, set[str]]:
        adjacency = {identifier: set() for identifier in self.contexts}
        for relation in self.relations:
            adjacency[relation.earlier].add(relation.later)
        return adjacency

    def contradiction_cycle(self) -> tuple[str, ...] | None:
        """Return one closed temporal cycle, or None when the graph is valid."""

        adjacency = self._adjacency()

        visited: set[str] = set()
        active: set[str] = set()
        path: list[str] = []

        def visit(identifier: str) -> tuple[str, ...] | None:
            visited.add(identifier)
            active.add(identifier)
            path.append(identifier)

            for later in adjacency[identifier]:
                if later not in visited:
                    cycle = visit(later)
                    if cycle is not None:
                        return cycle
                elif later in active:
                    start = path.index(later)
                    return tuple(path[start:] + [later])

            path.pop()
            active.remove(identifier)
            return None

        for identifier in self.contexts:
            if identifier not in visited:
                cycle = visit(identifier)
                if cycle is not None:
                    return cycle
        return None
