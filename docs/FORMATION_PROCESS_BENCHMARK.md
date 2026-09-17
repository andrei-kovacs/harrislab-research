# Synthetic Formation-Process Benchmark Result

## Outcome

The preregistered directional hypothesis was supported on the fixed 100-trial
schedule. Mean closure amplification was 2.3581 for the depositional-patch
automaton and 1.9755 for the node-and-edge-count-matched forward-DAG control,
a mean paired difference of +0.3826.

The result was not universal: 82 trials favored the automaton, 5 tied, and 13
favored the control. Paired differences ranged from -0.6842 to +1.4211.

| Metric, trial mean | Automaton | Matched control |
|---|---:|---:|
| Direct relations | 20.37 | 20.37 |
| Derived relations | 27.62 | 19.80 |
| Closure relations | 47.99 | 40.17 |
| Closure amplification | 2.3581 | 1.9755 |
| Redundant direct relations | 7.51 | 6.46 |
| Longest path | 7.06 | 5.46 |

The primary paired-difference median was +0.3842 and sample standard deviation
was 0.3856. These are descriptive summaries of a fixed computational schedule,
not estimates for an archaeological population.

## Provenance

The design was frozen and published at commit
[`6f4d807`](https://github.com/andrei-kovacs/harrislab-research/commit/6f4d807)
before the scheduled result was generated. The result artifact records the
canonical SHA-256 of that manifest:
`a2a8a1c1e9765e888cc0d78343af50f5079c2ce130804cdf0467e83b73028022`.

- [Frozen preregistration](FORMATION_PROCESS_PREREGISTRATION.md)
- [Machine-readable result](../data/formation_process_benchmark.json)

## Interpretation limit

This benchmark shows that one local patch-growth rule produces more
chronological reachability per direct edge than one matched random control on
the fixed schedule. It does not show that the automaton models real site
formation, that its graphs are archaeologically plausible, or that closure
amplification is a measure of archaeological quality.

The control matches context and direct-edge counts, but not degree
distribution, path length, or spatial footprint. Independent archaeological
review and comparison against additional generators and field datasets remain
necessary.

## Reproduction

```powershell
python scripts/benchmark_formation_process.py
```

The committed result retains all 100 trial records, seeds, metrics, and
automaton footprints, including trials contrary to the directional hypothesis.