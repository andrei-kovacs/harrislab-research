# Trimmis Profile 19 Comprehensive Benchmark

## Status

The design was frozen and published at commit `d1b0045` before outcome
generation. The machine-readable preregistration binds the corrected reference
SHA-256, all 29 eligible direct relations, deterministic trial assignment,
seeds, strategies, limits, and truncation policy.

This is a benchmark of software behavior on one reviewed graph. It does not
measure archaeological importance, correctness probability, investigation
cost, or performance across sites.

## Primary outcome

The preregistered primary comparison could not be evaluated adequately. Exact
impact enumeration completed for 1 of 10 trials and reached the declared
1,000,000-order bound in the other nine. The single completed trial favored
exact impact by 0.0313 AURC over lexical order and 0.0172 over the mean of 20
seeded random orders, but one trial cannot support a general conclusion.

## Descriptive secondary results

Across all ten trials, mean AURC was:

| Strategy | Mean AURC |
|---|---:|
| Closure gain | 0.8483 |
| Sampled orders | 0.8494 |
| Lexicographic control | 0.7638 |
| Seeded random control | 0.7612 |

Closure gain equaled or exceeded the lexical control in 10 of 10 trials and
exceeded each trial's 20-seed random mean in 10 of 10 trials. Its mean paired
difference was +0.0845 AURC against lexical order and +0.0871 against random.
These are descriptive outcomes specified as secondary measures, not an
inferential validation of the method.

## Every trial

| Trial | Exact AURC | Closure AURC | Sampled AURC | Lexical AURC | Random mean AURC |
|---|---:|---:|---:|---:|---:|
| T01 | truncated | 0.8328 | 0.8328 | 0.7964 | 0.7339 |
| T02 | truncated | 0.8922 | 0.8922 | 0.8870 | 0.8414 |
| T03 | truncated | 0.7370 | 0.7057 | 0.4891 | 0.5846 |
| T04 | truncated | 0.7755 | 0.8182 | 0.7755 | 0.7733 |
| T05 | truncated | 0.8927 | 0.8927 | 0.6198 | 0.7826 |
| T06 | truncated | 0.8797 | 0.8797 | 0.8797 | 0.7955 |
| T07 | truncated | 0.7531 | 0.7531 | 0.7531 | 0.6633 |
| T08 | truncated | 0.8937 | 0.8937 | 0.6427 | 0.7661 |
| T09 | truncated | 0.8823 | 0.8823 | 0.8823 | 0.7445 |
| T10 | 0.9437 | 0.9437 | 0.9437 | 0.9125 | 0.9266 |

The sampled strategy selected 29 edges across the ten adaptive trials. Five
selected steps had split R-hat above 1.05 and nine had effective sample size
below 400. No step had top-choice consensus below 0.75. These diagnostics are
warnings, and sampled AURC should not be read as a convergence guarantee.

## Reproduction

```powershell
python scripts/benchmark_trimmis_profile19_comprehensive.py
python -m unittest tests.test_trimmis_comprehensive_benchmark -v
```

- [Frozen preregistration](../data/trimmis_profile19_benchmark_preregistration.json)
- [Complete result artifact](../data/trimmis_profile19_comprehensive_benchmark.json)
- [Benchmark protocol](BENCHMARK_PROTOCOL.md)

The generator fails closed if the reference hash or deterministic trial
assignment differs from the preregistration. Sample initialization is sorted
explicitly and regression-tested across Python hash seeds.