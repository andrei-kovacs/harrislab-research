# Sampled-Ranking Disagreement Analysis

Assessment date: 2026-09-02. This analysis uses generated DAGs and establishes
software behavior only.

## Purpose

The initial sampled-order calibration reported endpoint-level top-choice
agreement. That metric counts a sampled choice as wrong whenever it differs
from the deterministic first exact choice, even if both candidates have the
same maximum exact score.

The tie-aware analysis therefore distinguishes:

- `endpoint agreement`: sampled and exact deterministic endpoints match;
- `tie-compatible mismatch`: endpoints differ, but the sampled candidate has
  the maximum exact order-reduction score; and
- `genuine score error`: the sampled candidate has a lower exact score.

## Recorded experiment

The analysis repeated the original 200-case calibration with seed `20260902`,
seven contexts, accepted-edge probability 0.3, four candidates, 5,000 retained
samples, 5,000 burn-in transitions, and thinning of five.

| Outcome | Cases | Rate |
|---|---:|---:|
| Exact endpoint match | 183 | 91.5% |
| Tie-compatible endpoint mismatch | 13 | 6.5% |
| Genuine score error | 4 | 2.0% |
| Sampled choice belongs to exact optimum set | 196 | 98.0% |

Thus, 13 of the previously reported 17 mismatches were artifacts of deterministic
tie-breaking rather than selection of a lower-scoring candidate.

## Genuine-error features

The four genuine errors occurred at graph seeds `20260932`, `20260959`,
`20260965`, and `20261083`.

| Feature | Observation |
|---|---:|
| Exact normalized top margin, median | 0.0319 |
| Exact normalized top margin, maximum | 0.0367 |
| Mean incomparable pairs in error cases | 15.5 |
| Mean incomparable pairs across all cases | 14.315 |
| Error cases where closure gain preferred the exact choice | 0 of 4 |

These cases are sparse, relatively wide partial orders with close top scores.
The closure-gain features either tied or favored the sampled choice, so closure
gain does not provide a correction for this subset.

## Increased-sample follow-up

Each genuine-error graph was rerun with 50,000 retained samples, 20,000 burn-in
transitions, thinning of five, and an independent seed block. All four runs then
selected the exact top candidate.

| Graph seed | 5,000-sample result | 50,000-sample result |
|---|---|---|
| `20260932` | Lower exact score | Exact top selected |
| `20260959` | Lower exact score | Exact top selected |
| `20260965` | Lower exact score | Exact top selected |
| `20261083` | Lower exact score | Exact top selected |

This supports a finite-sample explanation for the observed errors, but it does
not prove the absence of slow-mixing graph motifs. The follow-up was selected
after inspecting errors and is diagnostic, not an independent validation set.

## Recorded structural fields

The reproducible case record retains graph seed, exact and sampled choices,
exact optimum tie size, normalized exact top margin, valid-order count,
accepted-edge count, closure size, incomparable-pair count, redundant-candidate
count, closure gain, predecessor count, successor count, and whether each chosen
edge was already implied.

## Decision

Future calibration reports should use tie-aware exact-optimum selection as the
primary top-rank metric and retain endpoint agreement as a reproducibility
detail. Close-score cases should trigger larger multi-chain sample budgets or an
explicitly unresolved ranking rather than forced selection.

A sequential stopping rule based on multi-chain uncertainty in the difference
between the top two candidates was subsequently evaluated on a fresh seed block.
See [`SURROGATE_CALIBRATION.md`](SURROGATE_CALIBRATION.md#sequential-stopping-rule)
for its protocol, selective-accuracy result, and statistical limitations.