# Synthetic Formation-Process Benchmark Preregistration

## Status

Frozen before scheduled outcome generation on 17 September 2026. The
machine-readable design is
[formation_process_benchmark_preregistration.json](../data/formation_process_benchmark_preregistration.json).

## Question

Does one local depositional-patch automaton produce different graph closure
structure from a node-and-edge-count-matched forward-DAG control?

The directional hypothesis is that mean closure amplification is higher for
the automaton. Closure amplification is the number of reachable ordered context
pairs divided by the number of direct relations. The hypothesis is supported
on the fixed schedule if the mean paired automaton-minus-control difference is
greater than zero, and falsified otherwise.

## Automaton

The grid has 16 horizontal columns. The first synthetic event covers all
columns. Each later event begins at one seeded column and undergoes four
synchronous opportunities to spread to adjacent columns with probability
0.55. It is then deposited over the current top context in every occupied
column. Distinct contacts become directed earlier-to-later graph relations.

This is a deliberately minimal local-growth rule. It has no sediment physics,
erosion, redeposition, dating, material properties, or human activity model.
Calling it an automaton describes the computation, not archaeological realism.

## Matched control

Each of 100 trials has 12 contexts. Its control has exactly the same number of
direct relations as that trial's automaton graph. The control first gives every
noninitial context a randomly selected earlier predecessor, then samples
remaining forward edges without replacement. It is acyclic by construction.

The control matches node and edge count, but not degree distribution, path
length, or spatial footprint. Any result is conditional on that limited null.

## Reporting

All trials and fixed seeds will be retained. The primary outcome is the mean
paired closure-amplification difference. Median, sample standard deviation,
minimum, maximum, derived relation count, redundant direct relations, and
longest path are secondary descriptions.

No p-value or inferential confidence interval will be reported because the
fixed seed schedule is not a sample from a defined archaeological population.
The result cannot establish formation-process validity or archaeological
importance.