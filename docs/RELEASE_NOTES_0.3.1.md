# HarrisLab 0.3.1 Strict-JSON and Prototype Release

## Scope

Version 0.3.1 repairs the browser compatibility of the Harp Inn benchmark
artifact and makes the second archaeological reference inspectable in the
static prototype. It does not change benchmark assignments, AURC outcomes, or
the accepted archaeological graph.

## Fixed

- Non-finite split $\hat R$ is serialized as JSON `null` instead of Python's
  non-standard `Infinity` token.
- Recomputed aggregate diagnostics treat that `null` as a convergence warning,
  preserving the reported 15 of 26 warning count.
- Tests require strict JSON serialization and parsing for generated and
  committed Harp benchmark reports.
- Versioned artifact URLs prevent browsers from reusing the incompatible
  pre-fix response.

## Prototype

The static workbench now offers a Trimmis Profile 19 and ADS Harp Inn selector.
The Harp view renders its 36 contexts and 26 precedence relations, source-bound
context records, all nine benchmark trials, exact truncations, and sampling
warnings. Trimmis-only drawing, text, formation, and scenario controls are
disabled in the Harp view so their evidence cannot be misattributed.

`CONTEMPORARY` remains reported as ten typed source relations outside the
precedence DAG. The prototype does not convert those records into graph edges.

## Validation

```powershell
python scripts/validate_release.py
```

The complete release gate reproduces both archaeological artifact chains,
checks the v0.3.1 manifest, strictly validates the Harp report, and runs the
full test suite. Browser checks cover both dataset modes at desktop and mobile
viewports.