# Release Reproducibility

## Scope

HarrisLab 0.3.0 provides a fail-closed release gate from checksum-verified
Trimmis and ADS Harp Inn source files to the committed references, comparisons,
images, text proposals, benchmark designs, and benchmark results. Regeneration
occurs in a temporary directory and never overwrites committed results.

The validator requires canonical content equality for:

- the extracted audit candidate;
- the independently reviewed published reference;
- the corrected active reference;
- the P19 drawing comparison and rendered source crop;
- the catalogue text proposals;
- the retrospective and comprehensive Trimmis benchmarks; and
- the synthetic formation-process benchmark;
- the Harp Inn archaeological payload from its frozen source CSV;
- the deterministic Harp Inn hidden-edge design; and
- the complete Harp Inn cross-dataset benchmark report.

It then verifies the audit provenance manifest and runs the complete unit test
suite. A mismatch or missing source fails the command.

JSON line endings are normalized to LF before SHA-256 hashing and byte
counting, making the manifest stable across Git checkouts on Windows and Linux.
Binary artifacts, including the rendered profile image, retain exact-byte
comparison.

## Reproduce

Install the acquisition dependency and obtain both open source deposits:

```powershell
python -m pip install -e ".[acquisition]"
python scripts/qualify_trimmis.py .local-data/trimmis-source
python scripts/qualify_harp_inn.py .local-data/harp-inn-source
```

Run the release gate:

```powershell
python scripts/validate_release.py
```

The source directory may be supplied explicitly:

```powershell
python scripts/validate_release.py --source-directory C:\path\to\trimmis-source
```

Both source directories may be supplied explicitly:

```powershell
python scripts/validate_release.py `
	--source-directory C:\path\to\trimmis-source `
	--harp-source-directory C:\path\to\harp-inn-source
```

The authoritative online records are
[Zenodo 4461075](https://doi.org/10.5281/zenodo.4461075) and
[ADS 1133013](https://doi.org/10.5284/1133013). The validator accepts only the
source checksums encoded by the extraction workflows. Harp Inn's mutable live
retrieval receipt is checked for source-hash consistency but excluded from the
reproduced archaeological payload comparison. Private review correspondence is
neither required nor published; the frozen review and correction manifests
contain the reproducible Trimmis decisions without personal contact details.

## Audit exports

The app's **Export audit** command includes
`data/harrislab_audit_manifest.json` as its top-level `provenance` object. To
regenerate or verify that manifest independently:

```powershell
python scripts/build_audit_manifest.py
python scripts/build_audit_manifest.py --check
```

The AI drawing screen remains non-authoritative in both the manifest and the
export. All 27 drawing relations remain pending qualified review, and the
screen contributes zero accepted graph mutations. The Harp Inn graph accepts
only explicit ADS `ABOVE` or `LATER` records as precedence, preserves
`CONTEMPORARY` as typed non-precedence evidence, and includes zero AI graph
mutations.