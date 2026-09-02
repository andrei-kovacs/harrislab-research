# Scalable Surrogate Calibration

Assessment date: 2026-09-02. This is a computational calibration on generated
DAGs, not an archaeological evaluation.

## Closure-gain definition

For a candidate edge $u \rightarrow v$, let $P(u)$ contain $u$ and every
accepted predecessor of $u$. Let $S(v)$ contain $v$ and every accepted successor
of $v$. The closure-gain score is the number of pairs in $P(u) \times S(v)$ that
are not already present in the accepted graph's transitive closure.

$$
G(u,v) = |(P(u) \times S(v)) \setminus C|.
$$

Candidates that create a cycle are flagged and sorted before non-contradictory
candidates. Remaining candidates are sorted by descending $G$, then by endpoint
identifier for deterministic ties.

The accepted transitive closure is computed once. Each candidate then requires
set operations over its predecessor-successor product. The method does not
enumerate total chronological orders.

## Calibration method

The harness generates forward-only DAGs from a seeded pseudo-random process.
Candidate edges are reserved before accepted edges are sampled, preventing
overlap. For every graph it compares closure gain with exact valid-order
reduction and records:

- whether both methods select the same top candidate; and
- pairwise agreement between exact and surrogate scores, treating ties as a
  distinct outcome.

Exact calibration fails if bounded order counting truncates. Generated graphs
are software fixtures and do not model archaeological formation processes.

## Recorded run

Parameters:

| Field | Value |
|---|---:|
| Seed | `20260902` |
| Cases | 200 |
| Contexts per graph | 7 |
| Accepted-edge probability | 0.3 |
| Candidates per graph | 4 |
| Exact order limit | 100,000 |

Results:

| Metric | Result |
|---|---:|
| Top-choice agreement | 0.7400 |
| Mean pairwise agreement | 0.7008 |
| Cases with different top choices | 52 of 200 |

A separate execution smoke test scored 20 candidates on a generated
100-context graph with 187 total relations in approximately 0.0012 seconds on
the development machine. This timing is descriptive, not a controlled
performance benchmark.

## Decision

Retain closure gain as a **scalable baseline**, not as a validated substitute
for exact order reduction. Agreement is materially above an uninformative
ranking but the 26% top-choice disagreement rate is too large to treat the two
objectives as interchangeable.

The hidden-relation benchmark may use `closure_gain` on graphs where exact
enumeration is unavailable. Those results must be labelled by strategy and must
not be described as exact information gain.

## Sampled-order definition

The second surrogate estimates the proportion of accepted linear extensions
that a candidate would eliminate. Starting from a deterministic topological
order, a lazy adjacent-swap Markov chain repeatedly selects neighboring
contexts. It swaps them only when neither context is constrained before the
other. The chain has the uniform distribution over linear extensions as its
stationary distribution, but finite-run convergence is not established here.

For candidate $u \rightarrow v$, the estimate is the fraction of retained
samples in which $v$ occurs before $u$. The implementation records sample
count, burn-in, thinning, seed, and a naive Bernoulli standard error. That error
does not correct for chain autocorrelation and must not be used as a confidence
interval.

## Sampled-order calibration

The sampled method used the same 200 graphs, graph-generation seed, and exact
order limit as the closure-gain run. Its additional parameters were:

| Field | Value |
|---|---:|
| Samples per graph | 5,000 |
| Burn-in transitions | 5,000 |
| Transitions between samples | 5 |
| Sampler seed rule | `20260902 + 1000000 + case index` |

Results:

| Metric | Closure gain | Sampled orders |
|---|---:|---:|
| Top-choice agreement | 0.7400 | 0.9150 |
| Mean pairwise agreement | 0.7008 | 0.9183 |
| Cases with different top choices | 52 | 17 |
| Calibration runtime | Not recorded | 4.867 seconds |

On the generated 100-context smoke-test graph, 5,000 retained samples for 20
candidates completed in approximately 0.059 seconds. These timings are
descriptive observations on the development machine.

Sampled orders are the stronger computational baseline in this calibration,
but the remaining 8.5% top-choice disagreement and missing convergence evidence
prevent treating the estimates as exact.

A subsequent tie-aware review found that 13 of 17 endpoint mismatches selected
a candidate tied for the maximum exact score. The sampled candidate belonged to
the exact optimum set in 196 of 200 cases. See
[`DISAGREEMENT_ANALYSIS.md`](DISAGREEMENT_ANALYSIS.md) for the structural audit
and increased-sample follow-up.

## Multi-chain diagnostics

The diagnostic API runs independently seeded chains from randomized valid
topological orders. For each candidate it reports:

- the estimated reduction fraction from each chain;
- split $\hat R$ across the chain halves;
- an autocorrelation-adjusted effective sample size, summed across chains; and
- top-choice consensus across chains.

The default adequacy check requires $\hat R \le 1.05$, effective sample size at
least 400 for every candidate, and top-choice consensus of at least 0.75. These
are operational warning thresholds, not proof of convergence.

Recorded sanity checks used four chains:

| Fixture | Retained samples | Estimate or rank | Maximum $\hat R$ | Minimum ESS | Top consensus |
|---|---:|---|---:|---:|---:|
| Unconstrained two-context pair | 4,000 | Reduction fraction 0.5050 | 1.0006 | 3,875.2 | 1.00 |
| Bridge versus redundant edge | 4,000 | Bridge ranked first | 1.0011 | 2,188.1 | 1.00 |

The ESS estimator uses the initial positive autocorrelation sequence separately
for each chain. Split $\hat R$ is the classical variance-ratio diagnostic, not
rank-normalized or folded. Constant traces, including deterministic
contradictions, report $\hat R=1$ only when every split has the same mean.

These diagnostics can expose poor mixing or unstable ranking. They cannot prove
that an adjacent-swap chain has reached the uniform stationary distribution,
and they do not correct the previously reported naive Bernoulli standard error.

## Sequential stopping rule

The sequential API starts four independently seeded chains at a fixed retained
sample budget and doubles that budget until either the ranking resolves or a
fixed maximum is reached. At each stage it:

1. identifies the top two candidates from the pooled estimates;
2. forms a paired trace by subtracting the runner-up violation indicator from
   the top-candidate indicator at every retained chain state;
3. estimates the paired difference's effective sample size using the same
   positive-sequence estimator as the candidate diagnostics; and
4. resolves only when the two-sided normal interval for the difference is
   strictly above zero and all multi-chain thresholds pass.

If the interval still includes zero at the maximum budget, the result contains
no selected edge. Every stage, interval, diagnostic, and sampling parameter is
retained for audit. This is a heuristic sequential interval, not a confidence
sequence, so repeated inspection can inflate its nominal error rate.

### Fresh-seed evaluation

The rule was fixed before evaluating a new block of 100 graph seeds beginning
at `20270000`. Graph generation retained the original seven contexts, 0.3
accepted-edge probability, and four candidates. Sampling used four chains,
500 initial and 8,000 maximum retained samples per chain, 2,000 burn-in
transitions, thinning of five, 95% intervals, maximum $\hat R$ of 1.05, minimum
ESS of 400, and minimum top-choice consensus of 0.75.

| Metric | Result |
|---|---:|
| Resolved cases | 86 of 100 |
| Coverage | 86.0% |
| Resolved choices in exact optimum set | 86 of 86 |
| Selective accuracy | 100.0% |
| Unresolved cases | 14 of 100 |
| Unresolved cases with tied exact optima | 11 of 14 |
| Mean retained samples across all chains | 13,240 |
| Median retained samples across all chains | 8,000 |
| Maximum retained samples across all chains | 32,000 |

No confidently resolved error occurred in this block. This is evidence of
useful selective behavior on generated graphs, not proof of a zero error rate.
The sample is small, the interval is not sequentially adjusted, and the graph
generator is not an archaeological formation model. Three unique-optimum cases
remained unresolved, demonstrating that the rule can abstain even when an exact
winner exists.

## Next falsification tests

1. Replace the repeated-look normal interval with a valid confidence sequence
   or alpha-spending design, then evaluate it on another untouched seed block.
2. Repeat calibration by graph size, density, width, candidate redundancy, and
   number of candidates.
3. Compare classical diagnostics with rank-normalized split $\hat R$, folded
   $\hat R$, and bulk/tail ESS implementations on non-binary chain summaries.
4. Compare against additional scalable baselines, including local degree and
   reachability centrality.
5. Report rank agreement confidence intervals across independent seed blocks.
6. Test whether any computational score agrees with archaeologist priorities
   after a dataset passes qualification.