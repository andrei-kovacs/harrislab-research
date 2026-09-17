# Exact Impact and Scalable Ranking Limits

## Exact objective

For an unresolved relation, HarrisLab's exact impact method counts valid total
chronological orders before and after adding the candidate. Its score is the
number of orders eliminated by that relation.

The counter uses memoized dynamic programming over sets of already placed
contexts. This is exact when it completes, but the number of reachable states
depends on the graph's partial-order structure and can grow exponentially.
Context count alone is therefore not a valid availability threshold.

Every count has an explicit limit. If either the baseline or candidate count
reaches that bound, `count_truncated` is true and the resulting difference must
not be presented as exact information gain or used for exact ranking.

## Observed limit on Trimmis P19

The comprehensive Trimmis benchmark used a one-million-order bound. Exact
enumeration completed in 1 of 10 trials and truncated in 9. The preregistered
primary comparison was therefore inconclusive. This is an expected limitation
of bounded exact counting, not evidence that the surrogate results are exact.

## Scalable alternatives

### Closure gain

Closure gain counts new chronological implications without enumerating total
orders. On 200 generated seven-context calibration graphs it selected the same
top candidate as exact order reduction in 74.0% of cases. The 26.0% mismatch
rate means it is a scalable baseline, not an interchangeable substitute.

### Sampled orders

The sampled method estimates the fraction of retained linear extensions that a
candidate would eliminate. On the same generated calibration set its top
choice matched exact ranking in 91.5% of cases, and belonged to the tied exact
optimum set in 196 of 200 cases.

Finite-run convergence is not established. Split R-hat, effective sample size,
and top-choice consensus are operational warnings only. Passing them does not
prove convergence; failing them requires abstention or further sampling.

## Selection policy

1. Use exact impact only when every compared baseline and candidate count
   completes below the declared bound.
2. If any required count truncates, report exact ranking as unavailable.
3. Label closure-gain and sampled-order results by method.
4. Retain convergence diagnostics and abstentions for sampled results.
5. Do not translate any computational rank into archaeological importance,
   correctness probability, or investigation priority without external
   validation.

- [Comprehensive Trimmis benchmark](TRIMMIS_COMPREHENSIVE_BENCHMARK.md)
- [Surrogate calibration](SURROGATE_CALIBRATION.md)
- [Sampled-ranking disagreement analysis](DISAGREEMENT_ANALYSIS.md)