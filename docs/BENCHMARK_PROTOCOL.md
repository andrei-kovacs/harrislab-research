# Hidden-Relation Benchmark Protocol

Status on 2026-09-18: implemented, validated on synthetic software fixtures,
run on the independently reviewed Trimmis Profile 19 reference, and validated
against the direct-relation ADS Harp Inn reference.

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

The comprehensive Trimmis design was frozen in
[`trimmis_profile19_benchmark_preregistration.json`](../data/trimmis_profile19_benchmark_preregistration.json)
and published at commit `d1b0045` before outcome generation. Its complete
results, including all truncations and diagnostic warnings, are reported in
[`TRIMMIS_COMPREHENSIVE_BENCHMARK.md`](TRIMMIS_COMPREHENSIVE_BENCHMARK.md).
The primary exact comparison was inconclusive because only one of ten exact
trials completed below the declared bound.

The second-dataset Harp Inn design was frozen locally before execution, but was
not publicly preregistered. It covers all 26 eligible evidenced precedence
edges once across nine deterministic trials. Exact impact truncated in every
trial at the unchanged 100,000-order limit. Closure gain achieved mean AURC
0.9179, versus 0.8887 lexicographic and 0.8919 across repeated random controls.
Sampled orders achieved 0.8997, but 15 of 26 selected steps exceeded the split
$\hat R$ warning threshold. Full results and authority limits are in
[`HARP_INN_BENCHMARK.md`](HARP_INN_BENCHMARK.md).

## Trimmis retrospective demonstration

The first real-data run uses the corrected 26-context, 29-relation Trimmis
Profile 19 reference with canonical SHA-256
`4ccd723d9c53a96524b22bf8fa607df59607b1ed3a5467cde2fdf7e73737216a`.
It hides `156 -> 150`, `30 -> 241`, and `23 -> 235`. These relations appeared
in the public app prototype before the benchmark was run, preventing selection
from the observed benchmark outcomes. This is nevertheless retrospective and
must not be described as preregistered.

Exact impact, closure gain, and sampled-order ranking selected the same order:

1. `156 -> 150`, restoring 16 implications.
2. `30 -> 241`, restoring 13 implications.
3. `23 -> 235`, restoring 2 implications.

All three achieved AURC 0.9661, compared with 0.9547 for the lexicographic
control and 0.9630 for the single seeded random control. Exact enumeration
completed below the 100,000-order bound. The sampled run used four chains,
2,000 retained samples per chain, burn-in 2,000, thinning 10, and seed
20260917. All chains agreed on the top choice at each step, but the second
selected relation had ESS 116.5, below the protocol's 400 warning threshold.
The exact result is therefore primary; the sampled agreement is not presented
as a convergence claim.

Reproduce the committed machine-readable artifact with:

```powershell
python scripts/benchmark_trimmis_profile19.py
```

Results are stored in
[`trimmis_profile19_benchmark.json`](../data/trimmis_profile19_benchmark.json).
This single, deliberately small held-out set demonstrates the workflow. It
does not validate general archaeological usefulness or estimate performance
across sites.

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