# ADS Harp Inn Cross-Dataset Benchmark

Run date: 2026-09-18. Status: complete descriptive validation under a protocol
frozen locally before execution, but not publicly preregistered.

## Dataset and design

The reference is the 36-context Group 1 component imported from version 1 of
the ADS Harp Inn dataset, [DOI 10.5284/1133013](https://doi.org/10.5284/1133013).
It contains 26 direct, evidenced precedence relations and 10 contemporary
typed relations that never enter the precedence DAG. The reference SHA-256 is
`7572111181087d9d31ca484d64d2bf3d7742a33d4bc81cdd768f8fab44e8455c`.

Every eligible precedence edge appears exactly once. SHA-256 ordering assigned
the 26 edges to nine fixed trials of at most three hidden relations. Each trial
used an exact-order limit of 100,000, four sampled-order chains with 500
retained samples per chain, burn-in 500, thinning 5, and 20 fixed-seed random
repetitions.

## Results

| Strategy | Mean AURC | Difference from lexicographic | Difference from random |
|---|---:|---:|---:|
| Closure gain | 0.9179 | +0.0292 | +0.0261 |
| Sampled orders | 0.8997 | +0.0110 | +0.0078 |
| Lexicographic | 0.8887 | - | -0.0031 |
| Random mean | 0.8919 | +0.0031 | - |

Exact impact truncated in all nine trials at the declared bound, so there is
no exact cross-dataset comparison. This failure was retained as an outcome;
the limit was not raised after observing results.

Closure gain had the highest mean AURC and exceeded the random mean in seven of
nine trials. These are descriptive results from one selected component, not a
claim that closure gain estimates exact impact or archaeological value.

The sampled strategy had no selected step below ESS 400, but 15 of 26 selected
steps had split $\hat R > 1.05$ and four had top-choice consensus below 0.75.
Its aggregate result must therefore be read with a convergence warning, not as
a validated approximation to exact ranking.

## Reproduction and authority

```powershell
python scripts/benchmark_harp_inn_group1.py --prepare
python scripts/benchmark_harp_inn_group1.py
```

The first command deterministically rebuilds the frozen design. The runner
rejects any design that differs from that assignment. The committed report is
hash-bound to both the design and source reference, retains every trial and
random repetition, and can be audited with:

```powershell
python -m unittest tests.test_harp_inn_benchmark -v
```

No AI-generated relation is accepted into the reference. `CONTEMPORARY` links
remain source evidence outside precedence, and no hierarchy, phase, layer,
coordinate, or sentinel record is used to manufacture chronological edges.