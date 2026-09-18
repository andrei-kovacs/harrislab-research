# HarrisLab 0.2.0 Provenance Release

## Scope

Version 0.2.0 strengthens the boundary between evidence review and accepted
chronology. It adds operational drawing-review artifacts, a separately labelled
AI-assisted screen, machine-readable audit provenance, and an exact release
reproduction gate. It does not claim autonomous archaeological interpretation.

## Added

- A fail-closed, SHA-256-bound JSON and CSV workflow for 27 P19 drawing checks.
- A public Drawing Review panel with the complete pending relation register.
- A non-authoritative AI visual screen recording 23 visually consistent and
  four indeterminate relations, with zero visibly contradicted relations.
- A deterministic audit provenance manifest containing release, source,
  authority, component-hash, and byte-size metadata.
- A top-level `provenance` object in app audit exports.
- A non-destructive release validator that reproduces nine committed artifacts
  from checksum-bound sources and frozen protocols before running all tests.

## Authority boundary

The AI screen does not complete the formal drawing review, create a reviewer
identity, or alter chronology. All 27 relations retain
`awaiting_drawing_review` status. The accepted 26-context, 29-relation graph is
unchanged from the independently reviewed and corrected reference released
after 0.1.0.

## Validation

```powershell
python scripts/validate_release.py
```

For this release, the command reproduced the candidate, published reference,
corrected reference, drawing comparison, profile image, text proposals, two
Trimmis benchmarks, and formation benchmark exactly. The manifest check and
complete unit suite also passed.

## Known limits

- The drawing screen is AI triage, not qualified archaeological review.
- Four relations around lateral discontinuities or the central profile
  interruption remain visually indeterminate.
- The comprehensive exact-impact benchmark remains inconclusive because nine
  of ten trials exceed its preregistered bound.
- Validation establishes software and artifact reproducibility, not the
  archaeological truth of an interpretation or generality beyond Trimmis P19.