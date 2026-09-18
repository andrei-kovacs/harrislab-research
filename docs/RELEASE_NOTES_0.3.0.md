# HarrisLab 0.3.0 Cross-Dataset Release

## Scope

Version 0.3.0 adds a second open archaeological reference and a deterministic
cross-dataset validation while preserving the rule that AI cannot modify the
accepted graph. It does not establish general archaeological performance or
promote sampled diagnostics to authoritative inference.

## Added

- A fail-closed importer for ADS Harp Inn collection 1005042, version 1, bound
  to the Open Government Licence source CSV by SHA-256.
- A 36-context reference containing 26 explicit precedence relations and 10
  contemporary typed relations outside the precedence DAG.
- A locally frozen nine-trial design covering every evidenced precedence edge
  exactly once.
- A complete benchmark report with closure gain, sampled orders,
  lexicographic, and 20 repeated random controls per trial.
- Four tests for deterministic assignment, design tamper rejection,
  deterministic reduced execution, and committed-report integrity.
- An expanded audit manifest and release gate covering both archaeological
  datasets and all Harp benchmark artifacts.

## Results

Closure gain achieved mean AURC 0.9179, compared with 0.8887 for
lexicographic order and 0.8919 for the repeated random control. Exact impact
truncated in all nine trials at the unchanged 100,000-order bound. Sampled
orders achieved 0.8997, but 15 of 26 selected steps exceeded split
$\hat R = 1.05$; that result retains an explicit convergence warning.

These are descriptive results for one source component under a protocol frozen
locally before execution. The protocol was not publicly preregistered.

## Authority boundary

Only explicit ADS `ABOVE` and `LATER` records enter the accepted precedence
graph. `CONTEMPORARY` remains symmetric typed evidence outside precedence.
Sentinels, hierarchy, phase membership, layers, and coordinates do not create
benchmark connectivity. AI contributes zero accepted Harp Inn graph mutations.

## Validation

```powershell
python scripts/validate_release.py
```

The command reproduces all prior v0.2.0 artifacts, the Harp Inn archaeological
payload, deterministic benchmark design, and complete benchmark report. It
then checks the v0.3.0 audit manifest and runs the full test suite.

## Known limits

- The Harp Inn component can use direct contemporary links for component
  selection, although those links never become chronological constraints.
- Exact impact remains computationally unusable for these trials at the
  declared bound.
- Sampled-order warnings prevent a convergence claim.
- Cross-dataset validation across Trimmis Profile 19 and one Harp Inn component
  does not establish generality across sites, recording systems, or periods.