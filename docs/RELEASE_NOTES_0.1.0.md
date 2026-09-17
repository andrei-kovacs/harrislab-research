# HarrisLab 0.1.0 Research Seed

## Scope

Version 0.1.0 completes the six milestones in the project charter as a
reproducible research seed. It is not a field-ready recording system and makes
no claim of autonomous archaeological interpretation.

Included:

- provenance-aware contexts, evidence, and relation states;
- deterministic contradiction, closure, dependency, and scenario analysis;
- exact bounded order counting plus explicitly labelled scalable baselines;
- an independently reviewed Trimmis Profile 19 reference with a separate
  correction manifest;
- preregistered retrospective and comprehensive hidden-relation benchmarks;
- drawing and catalogue-text comparison layers that do not mutate the graph;
- a preregistered synthetic depositional-patch benchmark; and
- a static interactive audit viewer.

## Principal results

- Trimmis exact impact completed in only 1 of 10 comprehensive trials, making
  the primary comparison inconclusive.
- Closure gain and sampled ranking produced stronger descriptive AURC than the
  controls on the single Trimmis graph, without establishing archaeological
  validity.
- The P19 drawing contains all 26 active context identifiers; 27 matrix
  relations still await qualified drawing review.
- Catalogue text produced three pending options, none wholly inside the active
  reference, and zero graph mutations.
- The synthetic automaton's preregistered directional hypothesis was supported
  on its fixed schedule, while 13 of 100 trials favored the matched control.

## Known limits

- Novelty remains provisional pending full-text review, citation chaining, and
  external archaeological review.
- Exact order reduction is unavailable when bounded counting truncates.
- Surrogate and sampled rankings are experimental and cannot be interpreted as
  archaeological value or correctness probability.
- The formation automaton is a computational baseline, not a calibrated model
  of site formation.
- HarrisLab software is released under the MIT License. Source datasets and
  reproduced source imagery retain their stated upstream licenses.

## Reproduction

```powershell
python -m pip install -e ".[acquisition]"
python -m unittest discover -s tests -v
python -m harrislab data/synthetic_building.json
```

Source-dependent Trimmis workflows require the checksum-verified Zenodo files
outside version control. Frozen manifests, complete result artifacts, and
their generating scripts are committed in the repository.