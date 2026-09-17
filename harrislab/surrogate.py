"""Scalable candidate ranking and calibration against exact order reduction."""

from dataclasses import dataclass
from itertools import combinations
from math import sqrt
from random import Random
from statistics import NormalDist, mean, variance

from .analysis import CANDIDATE_STATUSES, accepted_graph, candidate_impacts
from .model import Context, Relation, RelationStatus, Stratigraphy


@dataclass(frozen=True, slots=True)
class ClosureImpact:
    relation: Relation
    new_implications: int
    creates_contradiction: bool


@dataclass(frozen=True, slots=True)
class SampledOrderImpact:
    relation: Relation
    estimated_reduction_fraction: float
    naive_standard_error: float
    sample_count: int
    creates_contradiction: bool


@dataclass(frozen=True, slots=True)
class CandidateChainDiagnostic:
    relation: Relation
    chain_estimates: tuple[float, ...]
    split_r_hat: float
    effective_sample_size: float


@dataclass(frozen=True, slots=True)
class MultiChainSamplingResult:
    impacts: tuple[SampledOrderImpact, ...]
    diagnostics: tuple[CandidateChainDiagnostic, ...]
    chain_top_choices: tuple[tuple[str, str], ...]
    chain_count: int
    samples_per_chain: int
    burn_in: int
    thinning: int
    seed: int

    @property
    def top_choice_consensus(self) -> float:
        return (
            max(self.chain_top_choices.count(edge) for edge in self.chain_top_choices)
            / self.chain_count
        )

    def meets_thresholds(
        self,
        max_r_hat: float = 1.05,
        min_effective_sample_size: float = 400,
        min_top_choice_consensus: float = 0.75,
    ) -> bool:
        return (
            self.top_choice_consensus >= min_top_choice_consensus
            and all(
                item.split_r_hat <= max_r_hat
                and item.effective_sample_size >= min_effective_sample_size
                for item in self.diagnostics
            )
        )


@dataclass(frozen=True, slots=True)
class SequentialSamplingStage:
    sampling: MultiChainSamplingResult
    top_edge: tuple[str, str]
    runner_up_edge: tuple[str, str]
    estimated_difference: float
    difference_standard_error: float
    confidence_interval: tuple[float, float]
    resolved: bool


@dataclass(frozen=True, slots=True)
class SequentialSamplingResult:
    stages: tuple[SequentialSamplingStage, ...]

    @property
    def resolved(self) -> bool:
        return self.stages[-1].resolved

    @property
    def selected_edge(self) -> tuple[str, str] | None:
        return self.stages[-1].top_edge if self.resolved else None

    @property
    def total_samples(self) -> int:
        final = self.stages[-1].sampling
        return final.chain_count * final.samples_per_chain


@dataclass(frozen=True, slots=True)
class CalibrationResult:
    candidate_count: int
    top_choice_agrees: bool
    pairwise_agreement: float
    exact_order: tuple[tuple[str, str], ...]
    surrogate_order: tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class CalibrationSummary:
    cases: tuple[CalibrationResult, ...]

    @property
    def top_choice_agreement_rate(self) -> float:
        return sum(case.top_choice_agrees for case in self.cases) / len(self.cases)

    @property
    def mean_pairwise_agreement(self) -> float:
        return sum(case.pairwise_agreement for case in self.cases) / len(self.cases)


def closure_candidate_impacts(graph: Stratigraphy) -> tuple[ClosureImpact, ...]:
    """Rank candidates by new reachability implications without order counting."""

    baseline = accepted_graph(graph)
    if baseline.contradiction_cycle() is not None:
        raise ValueError("accepted graph must be acyclic")
    closure = {
        (relation.earlier, relation.later)
        for relation in [*baseline.relations, *baseline.derived_relations()]
    }
    successors = {identifier: set() for identifier in baseline.contexts}
    predecessors = {identifier: set() for identifier in baseline.contexts}
    for earlier, later in closure:
        successors[earlier].add(later)
        predecessors[later].add(earlier)

    seen: set[tuple[str, str]] = set()
    impacts: list[ClosureImpact] = []
    for relation in graph.relations:
        if relation.status not in CANDIDATE_STATUSES:
            continue
        edge = (relation.earlier, relation.later)
        if edge in seen:
            raise ValueError(
                f"ambiguous duplicate candidate: {relation.earlier} -> {relation.later}"
            )
        seen.add(edge)
        contradiction = (
            relation.earlier == relation.later
            or relation.earlier in successors[relation.later]
        )
        new_implications = 0
        if not contradiction:
            possible = {
                (earlier, later)
                for earlier in predecessors[relation.earlier] | {relation.earlier}
                for later in successors[relation.later] | {relation.later}
                if earlier != later
            }
            new_implications = len(possible - closure)
        impacts.append(
            ClosureImpact(
                relation=relation,
                new_implications=new_implications,
                creates_contradiction=contradiction,
            )
        )

    return tuple(
        sorted(
            impacts,
            key=lambda item: (
                -int(item.creates_contradiction),
                -item.new_implications,
                item.relation.earlier,
                item.relation.later,
            ),
        )
    )


def sampled_order_candidate_impacts(
    graph: Stratigraphy,
    sample_count: int = 1_000,
    burn_in: int = 1_000,
    thinning: int = 10,
    *,
    seed: int = 0,
) -> tuple[SampledOrderImpact, ...]:
    """Estimate each candidate's eliminated fraction of sampled valid orders."""

    if sample_count < 1:
        raise ValueError("sample count must be positive")
    if burn_in < 0:
        raise ValueError("burn-in must not be negative")
    if thinning < 1:
        raise ValueError("thinning must be positive")
    baseline = accepted_graph(graph)
    if baseline.contradiction_cycle() is not None:
        raise ValueError("accepted graph must be acyclic")
    candidates = _candidate_relations(graph)
    if not candidates:
        return ()

    closure = {
        (relation.earlier, relation.later)
        for relation in [*baseline.relations, *baseline.derived_relations()]
    }
    order = _deterministic_topological_order(baseline)
    random = Random(seed)

    def transition() -> None:
        if len(order) < 2 or random.random() < 0.5:
            return
        index = random.randrange(len(order) - 1)
        left, right = order[index], order[index + 1]
        if (left, right) not in closure and (right, left) not in closure:
            order[index], order[index + 1] = right, left

    for _ in range(burn_in):
        transition()
    violations = {_edge(relation): 0 for relation in candidates}
    for _ in range(sample_count):
        for _ in range(thinning):
            transition()
        positions = {identifier: index for index, identifier in enumerate(order)}
        for relation in candidates:
            if (
                relation.earlier == relation.later
                or positions[relation.earlier] > positions[relation.later]
            ):
                violations[_edge(relation)] += 1

    impacts: list[SampledOrderImpact] = []
    for relation in candidates:
        fraction = violations[_edge(relation)] / sample_count
        impacts.append(
            SampledOrderImpact(
                relation=relation,
                estimated_reduction_fraction=fraction,
                naive_standard_error=sqrt(fraction * (1 - fraction) / sample_count),
                sample_count=sample_count,
                creates_contradiction=(
                    relation.earlier == relation.later
                    or (relation.later, relation.earlier) in closure
                ),
            )
        )
    return tuple(
        sorted(
            impacts,
            key=lambda item: (
                -int(item.creates_contradiction),
                -item.estimated_reduction_fraction,
                item.relation.earlier,
                item.relation.later,
            ),
        )
    )


def diagnose_sampled_order_chains(
    graph: Stratigraphy,
    chain_count: int = 4,
    samples_per_chain: int = 1_000,
    burn_in: int = 1_000,
    thinning: int = 10,
    *,
    seed: int = 0,
) -> MultiChainSamplingResult:
    """Run independent chains and report rank, split-R-hat, and ESS diagnostics."""

    if chain_count < 2:
        raise ValueError("chain count must be at least two")
    if samples_per_chain < 4:
        raise ValueError("samples per chain must be at least four")
    if burn_in < 0:
        raise ValueError("burn-in must not be negative")
    if thinning < 1:
        raise ValueError("thinning must be positive")
    baseline = accepted_graph(graph)
    if baseline.contradiction_cycle() is not None:
        raise ValueError("accepted graph must be acyclic")
    candidates = _candidate_relations(graph)
    if not candidates:
        raise ValueError("diagnostics require at least one candidate")
    closure = {
        (relation.earlier, relation.later)
        for relation in [*baseline.relations, *baseline.derived_relations()]
    }

    traces_by_edge: dict[tuple[str, str], list[list[int]]] = {
        _edge(relation): [] for relation in candidates
    }
    chain_top_choices: list[tuple[str, str]] = []
    for chain_index in range(chain_count):
        traces = _sample_violation_traces(
            baseline,
            candidates,
            closure,
            samples_per_chain,
            burn_in,
            thinning,
            seed + chain_index,
        )
        for edge, trace in traces.items():
            traces_by_edge[edge].append(trace)
        chain_top_choices.append(
            min(
                traces,
                key=lambda edge: (
                    -sum(traces[edge]) / samples_per_chain,
                    edge,
                ),
            )
        )

    relation_by_edge = {_edge(relation): relation for relation in candidates}
    diagnostics: list[CandidateChainDiagnostic] = []
    impacts: list[SampledOrderImpact] = []
    for edge, chains in traces_by_edge.items():
        relation = relation_by_edge[edge]
        chain_estimates = tuple(mean(chain) for chain in chains)
        pooled_count = sum(sum(chain) for chain in chains)
        total_samples = chain_count * samples_per_chain
        fraction = pooled_count / total_samples
        contradiction = (
            relation.earlier == relation.later
            or (relation.later, relation.earlier) in closure
        )
        impacts.append(
            SampledOrderImpact(
                relation=relation,
                estimated_reduction_fraction=fraction,
                naive_standard_error=sqrt(fraction * (1 - fraction) / total_samples),
                sample_count=total_samples,
                creates_contradiction=contradiction,
            )
        )
        diagnostics.append(
            CandidateChainDiagnostic(
                relation=relation,
                chain_estimates=chain_estimates,
                split_r_hat=_split_r_hat(chains),
                effective_sample_size=sum(
                    _effective_sample_size(chain) for chain in chains
                ),
            )
        )

    impacts.sort(
        key=lambda item: (
            -int(item.creates_contradiction),
            -item.estimated_reduction_fraction,
            item.relation.earlier,
            item.relation.later,
        )
    )
    diagnostic_by_edge = {_edge(item.relation): item for item in diagnostics}
    return MultiChainSamplingResult(
        impacts=tuple(impacts),
        diagnostics=tuple(diagnostic_by_edge[_edge(item.relation)] for item in impacts),
        chain_top_choices=tuple(chain_top_choices),
        chain_count=chain_count,
        samples_per_chain=samples_per_chain,
        burn_in=burn_in,
        thinning=thinning,
        seed=seed,
    )


def sequential_sampled_order_ranking(
    graph: Stratigraphy,
    chain_count: int = 4,
    initial_samples_per_chain: int = 1_000,
    max_samples_per_chain: int = 16_000,
    burn_in: int = 1_000,
    thinning: int = 10,
    growth_factor: int = 2,
    confidence_level: float = 0.95,
    max_r_hat: float = 1.05,
    min_effective_sample_size: float = 400,
    min_top_choice_consensus: float = 0.75,
    *,
    seed: int = 0,
) -> SequentialSamplingResult:
    """Increase a multi-chain budget until the leading pair is distinguishable."""

    if initial_samples_per_chain < 4:
        raise ValueError("initial samples per chain must be at least four")
    if max_samples_per_chain < initial_samples_per_chain:
        raise ValueError("maximum samples must not be below the initial samples")
    if growth_factor < 2:
        raise ValueError("growth factor must be at least two")
    if not 0 < confidence_level < 1:
        raise ValueError("confidence level must be between zero and one")

    candidates = _candidate_relations(graph)
    if len(candidates) < 2:
        raise ValueError("sequential ranking requires at least two candidates")
    baseline = accepted_graph(graph)
    if baseline.contradiction_cycle() is not None:
        raise ValueError("accepted graph must be acyclic")
    closure = {
        (relation.earlier, relation.later)
        for relation in [*baseline.relations, *baseline.derived_relations()]
    }
    critical_value = NormalDist().inv_cdf(0.5 + confidence_level / 2)
    stages: list[SequentialSamplingStage] = []
    samples_per_chain = initial_samples_per_chain

    while True:
        sampling = diagnose_sampled_order_chains(
            graph,
            chain_count,
            samples_per_chain,
            burn_in,
            thinning,
            seed=seed,
        )
        top_edge = _edge(sampling.impacts[0].relation)
        runner_up_edge = _edge(sampling.impacts[1].relation)
        difference_chains: list[list[int]] = []
        for chain_index in range(chain_count):
            traces = _sample_violation_traces(
                baseline,
                candidates,
                closure,
                samples_per_chain,
                burn_in,
                thinning,
                seed + chain_index,
            )
            difference_chains.append(
                [
                    top - runner_up
                    for top, runner_up in zip(
                        traces[top_edge], traces[runner_up_edge], strict=True
                    )
                ]
            )
        difference_trace = [
            value for chain in difference_chains for value in chain
        ]
        estimated_difference = mean(difference_trace)
        effective_sample_size = sum(
            _effective_sample_size(chain) for chain in difference_chains
        )
        difference_standard_error = sqrt(
            variance(difference_trace) / effective_sample_size
        )
        interval = (
            estimated_difference - critical_value * difference_standard_error,
            estimated_difference + critical_value * difference_standard_error,
        )
        resolved = (
            interval[0] > 0
            and sampling.meets_thresholds(
                max_r_hat,
                min_effective_sample_size,
                min_top_choice_consensus,
            )
        )
        stages.append(
            SequentialSamplingStage(
                sampling=sampling,
                top_edge=top_edge,
                runner_up_edge=runner_up_edge,
                estimated_difference=estimated_difference,
                difference_standard_error=difference_standard_error,
                confidence_interval=interval,
                resolved=resolved,
            )
        )
        if resolved or samples_per_chain == max_samples_per_chain:
            return SequentialSamplingResult(tuple(stages))
        samples_per_chain = min(
            samples_per_chain * growth_factor, max_samples_per_chain
        )


def calibrate_closure_surrogate(
    graph: Stratigraphy, order_limit: int = 100_000
) -> CalibrationResult:
    """Compare closure-gain ranking with exact order-reduction ranking."""

    exact = candidate_impacts(graph, order_limit)
    if not exact:
        raise ValueError("calibration requires at least one candidate")
    if any(impact.count_truncated for impact in exact):
        raise ValueError("exact order count truncated during calibration")
    surrogate = closure_candidate_impacts(graph)
    exact_scores = {
        _edge(impact.relation): impact.reduction for impact in exact
    }
    surrogate_scores = {
        _edge(impact.relation): (
            int(impact.creates_contradiction),
            impact.new_implications,
        )
        for impact in surrogate
    }
    agreements = [
        _compare(exact_scores[left], exact_scores[right])
        == _compare(surrogate_scores[left], surrogate_scores[right])
        for left, right in combinations(sorted(exact_scores), 2)
    ]
    exact_order = tuple(_edge(impact.relation) for impact in exact)
    surrogate_order = tuple(_edge(impact.relation) for impact in surrogate)
    return CalibrationResult(
        candidate_count=len(exact),
        top_choice_agrees=exact_order[0] == surrogate_order[0],
        pairwise_agreement=(sum(agreements) / len(agreements) if agreements else 1.0),
        exact_order=exact_order,
        surrogate_order=surrogate_order,
    )


def calibrate_sampled_order_surrogate(
    graph: Stratigraphy,
    sample_count: int = 1_000,
    burn_in: int = 1_000,
    thinning: int = 10,
    *,
    seed: int = 0,
    order_limit: int = 100_000,
) -> CalibrationResult:
    """Compare sampled eliminated-order fractions with exact order reduction."""

    exact = candidate_impacts(graph, order_limit)
    if not exact:
        raise ValueError("calibration requires at least one candidate")
    if any(impact.count_truncated for impact in exact):
        raise ValueError("exact order count truncated during calibration")
    sampled = sampled_order_candidate_impacts(
        graph,
        sample_count,
        burn_in,
        thinning,
        seed=seed,
    )
    exact_scores = {_edge(impact.relation): impact.reduction for impact in exact}
    sampled_scores = {
        _edge(impact.relation): (
            int(impact.creates_contradiction),
            impact.estimated_reduction_fraction,
        )
        for impact in sampled
    }
    agreements = [
        _compare(exact_scores[left], exact_scores[right])
        == _compare(sampled_scores[left], sampled_scores[right])
        for left, right in combinations(sorted(exact_scores), 2)
    ]
    exact_order = tuple(_edge(impact.relation) for impact in exact)
    sampled_order = tuple(_edge(impact.relation) for impact in sampled)
    return CalibrationResult(
        candidate_count=len(exact),
        top_choice_agrees=exact_order[0] == sampled_order[0],
        pairwise_agreement=(sum(agreements) / len(agreements) if agreements else 1.0),
        exact_order=exact_order,
        surrogate_order=sampled_order,
    )


def generate_calibration_graph(
    context_count: int = 7,
    accepted_probability: float = 0.3,
    candidate_count: int = 4,
    *,
    seed: int = 0,
) -> Stratigraphy:
    """Generate a reproducible DAG with forward-only unresolved candidates."""

    if context_count < 2:
        raise ValueError("context count must be at least two")
    if not 0 <= accepted_probability <= 1:
        raise ValueError("accepted probability must be between zero and one")
    possible_edges = [
        (str(earlier), str(later))
        for earlier in range(context_count)
        for later in range(earlier + 1, context_count)
    ]
    if not 1 <= candidate_count <= len(possible_edges):
        raise ValueError("candidate count is outside the available edge range")

    random = Random(seed)
    random.shuffle(possible_edges)
    candidate_edges = possible_edges[:candidate_count]
    graph = Stratigraphy()
    for index in range(context_count):
        identifier = str(index)
        graph.add_context(Context(identifier, f"Context {identifier}"))
    for earlier, later in possible_edges[candidate_count:]:
        if random.random() < accepted_probability:
            graph.add_relation(Relation(earlier, later))
    for earlier, later in candidate_edges:
        graph.add_relation(
            Relation(earlier, later, status=RelationStatus.AI_PROPOSED)
        )
    return graph


def calibrate_generated_dags(
    case_count: int = 25,
    context_count: int = 7,
    accepted_probability: float = 0.3,
    candidate_count: int = 4,
    *,
    seed: int = 0,
    order_limit: int = 100_000,
) -> CalibrationSummary:
    if case_count < 1:
        raise ValueError("case count must be positive")
    cases = tuple(
        calibrate_closure_surrogate(
            generate_calibration_graph(
                context_count,
                accepted_probability,
                candidate_count,
                seed=seed + case_index,
            ),
            order_limit,
        )
        for case_index in range(case_count)
    )
    return CalibrationSummary(cases)


def calibrate_generated_dags_sampled(
    case_count: int = 25,
    context_count: int = 7,
    accepted_probability: float = 0.3,
    candidate_count: int = 4,
    sample_count: int = 1_000,
    burn_in: int = 1_000,
    thinning: int = 10,
    *,
    seed: int = 0,
    order_limit: int = 100_000,
) -> CalibrationSummary:
    if case_count < 1:
        raise ValueError("case count must be positive")
    cases = tuple(
        calibrate_sampled_order_surrogate(
            generate_calibration_graph(
                context_count,
                accepted_probability,
                candidate_count,
                seed=seed + case_index,
            ),
            sample_count,
            burn_in,
            thinning,
            seed=seed + 1_000_000 + case_index,
            order_limit=order_limit,
        )
        for case_index in range(case_count)
    )
    return CalibrationSummary(cases)


def _candidate_relations(graph: Stratigraphy) -> tuple[Relation, ...]:
    candidates: list[Relation] = []
    seen: set[tuple[str, str]] = set()
    for relation in graph.relations:
        if relation.status not in CANDIDATE_STATUSES:
            continue
        edge = _edge(relation)
        if edge in seen:
            raise ValueError(
                f"ambiguous duplicate candidate: {relation.earlier} -> {relation.later}"
            )
        seen.add(edge)
        candidates.append(relation)
    return tuple(candidates)


def _sample_violation_traces(
    graph: Stratigraphy,
    candidates: tuple[Relation, ...],
    closure: set[tuple[str, str]],
    sample_count: int,
    burn_in: int,
    thinning: int,
    seed: int,
) -> dict[tuple[str, str], list[int]]:
    random = Random(seed)
    order = _random_topological_order(graph, random)

    def transition() -> None:
        if len(order) < 2 or random.random() < 0.5:
            return
        index = random.randrange(len(order) - 1)
        left, right = order[index], order[index + 1]
        if (left, right) not in closure and (right, left) not in closure:
            order[index], order[index + 1] = right, left

    for _ in range(burn_in):
        transition()
    traces = {_edge(relation): [] for relation in candidates}
    for _ in range(sample_count):
        for _ in range(thinning):
            transition()
        positions = {identifier: index for index, identifier in enumerate(order)}
        for relation in candidates:
            traces[_edge(relation)].append(
                int(
                    relation.earlier == relation.later
                    or positions[relation.earlier] > positions[relation.later]
                )
            )
    return traces


def _random_topological_order(graph: Stratigraphy, random: Random) -> list[str]:
    adjacency = {identifier: set() for identifier in graph.contexts}
    indegree = {identifier: 0 for identifier in graph.contexts}
    for relation in graph.relations:
        if relation.later not in adjacency[relation.earlier]:
            adjacency[relation.earlier].add(relation.later)
            indegree[relation.later] += 1
    available = sorted(
        identifier for identifier, degree in indegree.items() if degree == 0
    )
    order: list[str] = []
    while available:
        index = random.randrange(len(available))
        identifier = available.pop(index)
        order.append(identifier)
        for later in sorted(adjacency[identifier]):
            indegree[later] -= 1
            if indegree[later] == 0:
                available.append(later)
    if len(order) != len(graph.contexts):
        raise ValueError("accepted graph must be acyclic")
    return order


def _split_r_hat(chains: list[list[int]]) -> float:
    half_length = len(chains[0]) // 2
    split_chains = [
        segment
        for chain in chains
        for segment in (chain[:half_length], chain[-half_length:])
    ]
    chain_means = [mean(chain) for chain in split_chains]
    within = mean(variance(chain) for chain in split_chains)
    if within == 0:
        return 1.0 if len(set(chain_means)) == 1 else float("inf")
    between = half_length * variance(chain_means)
    variance_estimate = (
        ((half_length - 1) / half_length) * within + between / half_length
    )
    return sqrt(variance_estimate / within)


def _effective_sample_size(trace: list[int]) -> float:
    sample_count = len(trace)
    average = mean(trace)
    variance_sum = sum((value - average) ** 2 for value in trace)
    if variance_sum == 0:
        return float(sample_count)
    positive_autocorrelation = 0.0
    for lag in range(1, sample_count):
        covariance = sum(
            (trace[index] - average) * (trace[index + lag] - average)
            for index in range(sample_count - lag)
        )
        autocorrelation = covariance / variance_sum
        if autocorrelation <= 0:
            break
        positive_autocorrelation += autocorrelation
    return sample_count / (1 + 2 * positive_autocorrelation)


def _deterministic_topological_order(graph: Stratigraphy) -> list[str]:
    adjacency = {identifier: set() for identifier in graph.contexts}
    indegree = {identifier: 0 for identifier in graph.contexts}
    for relation in graph.relations:
        if relation.later not in adjacency[relation.earlier]:
            adjacency[relation.earlier].add(relation.later)
            indegree[relation.later] += 1
    available = sorted(
        identifier for identifier, degree in indegree.items() if degree == 0
    )
    order: list[str] = []
    while available:
        identifier = available.pop(0)
        order.append(identifier)
        for later in sorted(adjacency[identifier]):
            indegree[later] -= 1
            if indegree[later] == 0:
                available.append(later)
                available.sort()
    if len(order) != len(graph.contexts):
        raise ValueError("accepted graph must be acyclic")
    return order


def _edge(relation: Relation) -> tuple[str, str]:
    return relation.earlier, relation.later


def _compare(left: object, right: object) -> int:
    return (left > right) - (left < right)