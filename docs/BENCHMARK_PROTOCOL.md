# Hidden-Relation Benchmark Protocol

Status on 2026-09-02: implemented and validated on synthetic software fixtures.
It has not been run on archaeological evaluation data.

## Question

Given several known direct relations hidden from an otherwise accepted
reference sequence, does adaptive constraint-impact ranking restore the
reference's chronological implications earlier than control orderings?

This tests a deterministic ranking heuristic. It does not estimate expected
information gain, fieldwork cost, correctness probability, or archaeological
importance.

## Inputs

The experiment requires:

1. An acyclic expert-reviewed reference graph.
2. A declared set of direct `observed` relations to hide.
3. An order-count bound high enough to avoid truncation.
4. A fixed strategy and, for random ordering, a recorded seed.

Sampled-order runs additionally require a sample count, burn-in length,
transitions between retained samples, and sampler seed.
For reported results, run multiple independent chains and retain per-candidate
split $\hat R$, effective sample size, and top-choice consensus.

Preparing a trial removes each selected relation from the accepted graph and
adds a `disputed` copy with the same endpoints and evidence links. The reference
graph is not mutated. Derived relations cannot be selected as hidden source
observations.

## Ranking strategies

| Strategy | Selection rule | Purpose |
|---|---|---|
| `impact` | Adaptively select the candidate causing the largest reduction in valid total chronological orders. Ties use endpoint order. | Current HarrisLab heuristic. |
| `closure_gain` | Adaptively select the candidate producing the most new reachability implications. | Scalable surrogate baseline. |
| `sampled_orders` | Estimate the fraction of sampled linear extensions eliminated by each candidate using a lazy adjacent-swap chain. | Approximation to exact order reduction. |
| `lexicographic` | Select the remaining endpoint pair in lexical order. | Deterministic non-informative control. |
| `random` | Select from a once-shuffled candidate order using a recorded seed. | Reproducible random control. |

Impact, closure gain, or sampled-order impact is recomputed after every reveal.
If bounded order enumeration truncates, an `impact` run fails instead of
treating capped values as a valid ranking. Other strategies do not enumerate or
report order counts.

## Outcomes

Let $C_R$ be the transitive chronological closure of the reference and $C_k$
the closure after $k$ reveals. Closure recall is:

$$
R_k = \frac{|C_k \cap C_R|}{|C_R|}.
$$

The primary software metric is area under the recovery curve, using trapezoids
over the initial state and every reveal:

$$
AURC = \frac{1}{n}\sum_{k=0}^{n-1}\frac{R_k + R_{k+1}}{2}.
$$

Higher AURC means the strategy restores reference implications earlier. Each
step records the revealed source relation, closure gain, and closure-recovery
count. Exact-impact steps also record order reduction and remaining valid-order
count. Sampled-order steps record the estimated eliminated-order fraction.
They also retain split $\hat R$, effective sample size, and top-choice consensus
for the selected relation. `sample_count` is interpreted as samples per chain;
the default sampled strategy runs four chains.

A redundant hidden direct edge may remain unrevealed after closure recall
reaches 1.0. This is intentional: the metric scores recovery of chronological
conclusions, not verbatim reconstruction of every recorded edge.

## Synthetic acceptance test

The test fixture hides a bridge relation `2 -> 3` and a redundant direct
relation `1 -> 3`. Adaptive impact ranking must reveal the bridge first and
restore the complete reference closure in one step. A lexicographic control
reveals the redundant edge first and therefore has lower AURC.

This establishes implementation behavior only. It is not evidence that the
heuristic identifies archaeologically valuable investigations.

## Real-data preregistration

Before running against a qualified dataset, freeze:

1. Dataset version, imported subset, and reference graph hash.
2. Eligibility rules for hiding relations.
3. Random seeds and number of repeated trials.
4. Single-edge and multi-edge hiding rates.
5. Order-count limit and a policy for trials that exceed it.
6. Primary AURC comparison and secondary order-count outcomes.
7. Archaeologist ranking procedure and disagreement handling.

Report every eligible trial, including failures and truncations. Do not tune
hiding patterns or seeds after observing comparative results.

## Known limitations

- Exact-impact ranking uses exponential total-order enumeration and will
  probably truncate near the 20-100-context dataset target. Closure gain avoids
  that enumeration but is only a calibrated baseline.
- Sampled-order estimates depend on burn-in and thinning. The current
  implementation provides classical split $\hat R$ and a positive-sequence ESS,
  but these are warning diagnostics rather than a convergence guarantee.
- Closure recall weights every implied relation equally.
- Held-out reference edges are treated as true and costless to verify.
- AURC is a recovery metric, not calibrated value of information.
- One expert reference sequence cannot represent all defensible interpretations.

The initial surrogate calibration is recorded in
[`SURROGATE_CALIBRATION.md`](SURROGATE_CALIBRATION.md). Its top-choice agreement
is not high enough to treat closure gain and exact impact as interchangeable.