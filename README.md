# HarrisLab Research

[![Tests](https://github.com/andrei-kovacs/harrislab-research/actions/workflows/tests.yml/badge.svg)](https://github.com/andrei-kovacs/harrislab-research/actions/workflows/tests.yml)

[Open the live HarrisLab prototype](https://andrei-kovacs.github.io/harrislab-research/)

HarrisLab is an early computational-archaeology research project exploring a
provenance-aware, uncertainty-conscious extension of the Harris matrix. Its
first principle is that software and AI proposals must remain distinguishable
from observations made by archaeologists.

This repository is a research seed, not a field-ready recording system. It
contains a synthetic software-validation dataset and an independently reviewed
Trimmis Profile 19 reference graph. The active reference incorporates a
source-author correction for context 199 while retaining the original matrix
extraction as an auditable source snapshot. All novelty claims remain
provisional pending a systematic literature review.

> **Research status:** The Trimmis extraction passed independent source review
> on 17 September 2026. A publicly preregistered benchmark now covers every
> eligible direct relation in ten fixed trials. The exact primary analysis was
> inconclusive because nine trials exceeded its bound; scalable strategies have
> descriptive results only. HarrisLab is an independent personal
> research project and is not affiliated with, sponsored by, or endorsed by
> Microsoft or the source-data authors and institutions.

## Current capabilities

- Represent contexts, temporal constraints, evidence, and relation status.
- Reject references to unknown contexts or evidence.
- Detect a temporal contradiction and return its cycle.
- Derive constraints implied by longer paths.
- Count valid total chronological orders up to a configurable bound.
- Keep disputed and AI-proposed edges outside the accepted interpretation.
- Rank unresolved edges by their reduction of valid chronological orders.
- Rank larger graphs with a calibrated closure-gain surrogate baseline.
- Approximate order reduction with reproducible linear-extension sampling.
- Diagnose sampled rankings across chains with split R-hat, ESS, and consensus.
- Evaluate named interpretations with accepted, rejected, and undecided edges.
- Compare contradictions, order counts, and implied relations across scenarios.
- Trace chronological conclusions through supporting relations to evidence.
- Benchmark hidden-relation recovery against deterministic and seeded controls.
- Load a reproducible JSON dataset and emit a command-line audit report.

## Run

From this directory:

```powershell
python -m unittest discover -s tests -v
python -m harrislab data/synthetic_building.json
```

Expected sample result: seven contexts, seven accepted relations, one unresolved
relation, two valid total orders before that proposal is accepted, and one after.

Launch the interactive Trimmis Profile 19 visual prototype:

```powershell
python -m http.server 8765
```

Then open [the HarrisLab app prototype](http://localhost:8765/docs/app-prototype.html).
It renders the reviewed 26-context reference graph, context provenance,
scenario comparison, and a retrospective hidden-relation ranking
demonstration. The reference includes the confirmed insertion of context 199
between older context 26 and younger context 170. The investigation queue loads
generated exact-impact results and benchmark diagnostics from a committed JSON
artifact. Held-out relations are known reference edges, not field disputes.

Reproduce that artifact:

```powershell
python scripts/benchmark_trimmis_profile19.py
```

Reproduce the preregistered comprehensive benchmark:

```powershell
python scripts/benchmark_trimmis_profile19_comprehensive.py
```

Reproduce the qualification screen for the first approved pilot dataset:

```powershell
python -m pip install -e ".[acquisition]"
python scripts/qualify_trimmis.py .local-data/trimmis-source
```

The downloaded source artifacts are checksum-verified and should remain outside
version control. Qualification does not approve an extracted relation graph;
that graph requires a separate geometry-conversion and visual-audit step.

## Research documents

- [Project charter](docs/PROJECT_CHARTER.md)
- [Formal data model](docs/DATA_MODEL.md)
- [Preliminary literature map](docs/LITERATURE_MAP.md)
- [Sprint 1 source register](docs/SOURCE_REGISTER.md)
- [Sprint 1 novelty screen](docs/NOVELTY_SCREEN.md)
- [Dataset qualification sprint](docs/DATASET_QUALIFICATION.md)
- [Trimmis Profile 19 extraction audit](docs/TRIMMIS_PROFILE19_AUDIT.md)
- [Hidden-relation benchmark protocol](docs/BENCHMARK_PROTOCOL.md)
- [Comprehensive Trimmis benchmark results](docs/TRIMMIS_COMPREHENSIVE_BENCHMARK.md)
- [Closure-gain surrogate calibration](docs/SURROGATE_CALIBRATION.md)
- [Sampled-ranking disagreement analysis](docs/DISAGREEMENT_ANALYSIS.md)
