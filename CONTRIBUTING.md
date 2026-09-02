# Contributing

HarrisLab is an early research prototype. Bug reports, reproducibility checks,
source corrections, and methodological criticism are welcome.

## Before proposing a change

1. Open an issue describing the observation, source, and expected behavior.
2. Keep observed, derived, disputed, and AI-proposed relations distinct.
3. Do not change an accepted archaeological relation without source evidence and
   a recorded review decision.
4. Do not commit downloaded source packages, credentials, personal
   correspondence, or review-outreach material.

## Development check

Create a Python 3.11 or newer environment, then run:

```powershell
python -m pip install -e ".[acquisition]"
python -m unittest discover -s tests -v
```

New behavior should include focused tests. Archaeological dataset changes must
also update provenance, checksums where applicable, and the independent review
manifest.

By contributing code, you agree that it may be distributed under the MIT
License. Original documentation contributions may be distributed under CC BY
4.0. Source-derived material remains subject to its source license.
