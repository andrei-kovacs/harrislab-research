# HarrisLab Research

[![Tests](https://github.com/andrei-kovacs/harrislab-research/actions/workflows/tests.yml/badge.svg)](https://github.com/andrei-kovacs/harrislab-research/actions/workflows/tests.yml)

[Open the live HarrisLab prototype](https://andrei-kovacs.github.io/harrislab-research/)

HarrisLab is an early computational-archaeology research project exploring a
provenance-aware, uncertainty-conscious extension of the Harris matrix. Its
first principle is that software and AI proposals must remain distinguishable
from observations made by archaeologists.

This repository is a research seed, not a field-ready recording system. It
contains a synthetic software-validation dataset, an independently reviewed
Trimmis Profile 19 reference graph, and a direct relation-table reference from
ADS Harp Inn. The active Trimmis reference incorporates a
source-author correction for context 199 while retaining the original matrix
extraction as an auditable source snapshot. All novelty claims remain
provisional pending a systematic literature review.

> **Research status:** The Trimmis extraction passed independent source review
> on 17 September 2026. A publicly preregistered benchmark now covers every
> eligible direct relation in ten fixed trials. The exact primary analysis was
> inconclusive because nine trials exceeded its bound; scalable strategies have
> descriptive results only. A locally frozen cross-dataset validation now
> covers all 26 Harp Inn precedence edges in nine trials. Exact impact
> truncated throughout; closure gain led the descriptive scalable controls.
> HarrisLab is an independent personal
> research project and is not affiliated with, sponsored by, or endorsed by
> Microsoft or the source-data authors and institutions.

> **Drawing screen status:** An AI-assisted visual screen found 23 relations
> visually consistent and four indeterminate, with none visibly contradicted.
> This is non-authoritative triage. All 27 drawing relations remain pending
> qualified review, and the screen makes zero accepted graph changes.

> **Synthetic benchmark status:** The preregistered depositional-patch
> automaton comparison is complete. Its directional graph-structure hypothesis
> was supported on the fixed schedule, with 13 of 100 trials favoring the
> matched control. This is software validation, not a claim about real site
> formation.

## Current capabilities

- Represent contexts, temporal constraints, evidence, and relation status.
- Reject references to unknown contexts or evidence.
- Detect a temporal contradiction and return its cycle.
- Derive constraints implied by longer paths.
- Count valid total chronological orders up to a configurable bound.
- Keep disputed and AI-proposed edges outside the accepted interpretation.
- Rank unresolved edges by exact reduction of valid chronological orders when
	every bounded count completes.
- Rank larger or truncated cases with closure gain as a scalable baseline, not
	an exact substitute.
- Approximate order reduction with reproducible linear-extension sampling;
	finite-run convergence is not established.
- Report split R-hat, ESS, and consensus as operational sampling warnings, not
	proof of convergence.
- Evaluate named interpretations with accepted, rejected, and undecided edges.
- Compare contradictions, order counts, and implied relations across scenarios.
- Trace chronological conclusions through supporting relations to evidence.
- Benchmark hidden-relation recovery against deterministic and seeded controls.
- Compare matrix and source-drawing provenance without auto-accepting inferred edges.
- Validate hash-bound archaeological drawing reviews without mutating the accepted graph.
- Preserve AI-assisted drawing observations as non-authoritative screening evidence.
- Surface literal catalogue relation mentions as review-only proposals.
- Preregister synthetic formation-process comparisons against matched controls.
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
python scripts/benchmark_formation_process.py
```

Reproduce the locally frozen ADS Harp Inn cross-dataset validation:

```powershell
python scripts/qualify_harp_inn.py .local-data/harp-inn-source
python scripts/benchmark_harp_inn_group1.py
```

Reproduce the qualification screen for the first approved pilot dataset:

```powershell
python -m pip install -e ".[acquisition]"
python scripts/qualify_trimmis.py .local-data/trimmis-source
python scripts/compare_trimmis_profile19_drawing.py .local-data/trimmis-source
python scripts/extract_trimmis_profile19_text_relations.py .local-data/trimmis-source
```

The downloaded source artifacts are checksum-verified and should remain outside
version control. Qualification does not approve an extracted relation graph;
that graph requires a separate geometry-conversion and visual-audit step.

Create the public blank P19 drawing-review checklist, or validate a completed
copy returned by a qualified independent reviewer:

```powershell
python scripts/drawing_review_workflow.py
python scripts/drawing_review_workflow.py --validate path/to/completed_checklist.csv
```

Validation is bound to the comparison SHA-256 and fails on missing, duplicate,
unknown, or pending decisions. Its output classifies drawing evidence only and
never mutates the accepted chronology.

Reproduce the complete 0.3.0 artifact chain and run the release gate:

```powershell
python scripts/validate_release.py
```

The browser audit export includes a machine-readable provenance manifest with
component hashes, source identity, and authority boundaries.

## Research documents

- [Project charter](docs/PROJECT_CHARTER.md)
- [Formal data model](docs/DATA_MODEL.md)
- [Release reproducibility](docs/REPRODUCIBILITY.md)
- [Preliminary literature map](docs/LITERATURE_MAP.md)
- [Sprint 1 source register](docs/SOURCE_REGISTER.md)
- [Sprint 1 novelty screen](docs/NOVELTY_SCREEN.md)
- [Dataset qualification sprint](docs/DATASET_QUALIFICATION.md)
- [Trimmis Profile 19 extraction audit](docs/TRIMMIS_PROFILE19_AUDIT.md)
- [Trimmis Profile 19 drawing comparison](docs/TRIMMIS_DRAWING_COMPARISON.md)
- [Trimmis Profile 19 drawing-review workflow](docs/DRAWING_REVIEW_WORKFLOW.md)
- [Trimmis Profile 19 AI-assisted drawing screen](docs/TRIMMIS_AI_DRAWING_SCREEN.md)
- [Trimmis Profile 19 text-extraction pilot](docs/TRIMMIS_TEXT_EXTRACTION_PILOT.md)
- [Synthetic formation-process benchmark preregistration](docs/FORMATION_PROCESS_PREREGISTRATION.md)
- [Synthetic formation-process benchmark result](docs/FORMATION_PROCESS_BENCHMARK.md)
- [Hidden-relation benchmark protocol](docs/BENCHMARK_PROTOCOL.md)
- [Comprehensive Trimmis benchmark results](docs/TRIMMIS_COMPREHENSIVE_BENCHMARK.md)
- [ADS Harp Inn cross-dataset benchmark](docs/HARP_INN_BENCHMARK.md)
- [Closure-gain surrogate calibration](docs/SURROGATE_CALIBRATION.md)
- [Exact-impact and scalable-ranking limits](docs/EXACT_IMPACT_LIMITATIONS.md)
- [Sampled-ranking disagreement analysis](docs/DISAGREEMENT_ANALYSIS.md)
- [Version 0.1.0 research-seed release notes](docs/RELEASE_NOTES_0.1.0.md)
- [Version 0.2.0 provenance release notes](docs/RELEASE_NOTES_0.2.0.md)
- [Version 0.3.0 cross-dataset release notes](docs/RELEASE_NOTES_0.3.0.md)
