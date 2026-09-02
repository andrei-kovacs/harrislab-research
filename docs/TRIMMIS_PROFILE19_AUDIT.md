# Trimmis Profile 19 Extraction Audit

Status: **PENDING INDEPENDENT REVIEW**. Generated 2026-09-02 from the
checksum-verified files in Zenodo dataset
[10.5281/zenodo.4461075](https://doi.org/10.5281/zenodo.4461075), licensed
CC BY 3.0.

## Scope

The candidate contains 25 nodes and 28 direct relations from the rightmost
Profile 19 column of the published synoptic Harris matrix. Relations use the
HarrisLab `older -> younger` direction. The geometry extractor passed its
checks for unique labels, catalog matches, unambiguous connector endpoints,
connectivity, duplicate edges, and acyclicity.

The standalone profile and matrix share all 25 matrix identifiers. Position
`199`, cataloged as furrow-like depression or plough marks, appears only in the
profile drawing. It is recorded as a discrepancy and excluded because the
expert synoptic matrix does not assign it a graph node or relations.

## Artifacts

- [Audit candidate JSON](../data/trimmis_profile19_audit_candidate.json)
- [Independent review manifest](../data/trimmis_profile19_review.json)
- [Geometry overlay](trimmis_profile19_overlay.png)
- Source matrix MD5: `9ece18c188763350f16e164f441a927e`
- Source catalog MD5: `75983db690194fb562ba0378ebd627a3`
- Source P19 drawing MD5: `53ccf16a523e986ead69a30fc3f8dc24`

Blue rectangles in the overlay identify extracted nodes. Magenta paths identify
extracted direct connectors; small magenta numbers are source PDF path indices.

## Edge Checklist

The geometry overlay was inspected once during extraction and every highlighted
path coincided with a printed connector. An independent reviewer must compare
the table with the overlay and mark each relation `PASS` or `FAIL` before graph
approval.

| PDF path | Older | Younger | Independent review |
|---:|---:|---:|---|
| 34 | 102 | 104 | PENDING |
| 35 | 164 | 165 | PENDING |
| 36 | 165 | 98 | PENDING |
| 37 | 222 | 228 | PENDING |
| 38 | 223 | 222 | PENDING |
| 39 | 224 | 223 | PENDING |
| 40 | 228 | 99 | PENDING |
| 41 | 98 | 224 | PENDING |
| 42 | 99 | 102 | PENDING |
| 136 | 22 | 23 | PENDING |
| 137 | 23 | 235 | PENDING |
| 138 | 23 | 240 | PENDING |
| 139 | 235 | 26 | PENDING |
| 140 | 240 | 26 | PENDING |
| 213 | 170 | 156 | PENDING |
| 214 | 26 | 170 | PENDING |
| 319 | 150 | 153 | PENDING |
| 320 | 150 | 50 | PENDING |
| 321 | 156 | 150 | PENDING |
| 322 | 156 | 267 | PENDING |
| 323 | 267 | 153 | PENDING |
| 440 | 153 | 30 | PENDING |
| 441 | 30 | 155 | PENDING |
| 442 | 30 | 241 | PENDING |
| 443 | 50 | 30 | PENDING |
| 512 | 155 | 3 | PENDING |
| 513 | 241 | 3 | PENDING |
| 514 | 3 | 164 | PENDING |

## Approval Rule

Approval requires all 25 node labels and all 28 edges to pass independent
review, confirmation that downward matrix order means earlier under the source
convention, reviewer identity and date, and a SHA-256 hash of the approved edge
list. Any failed edge returns the candidate to extraction; it must not be
silently corrected in the derived JSON.

The hidden-relation benchmark remains blocked until this checklist is complete.

Generate a fresh manifest if the candidate changes:

```powershell
python scripts/review_trimmis_profile19.py template `
	data/trimmis_profile19_audit_candidate.json `
	data/trimmis_profile19_review.json
```

After an independent reviewer completes the manifest, apply the gate with:

```powershell
python scripts/review_trimmis_profile19.py approve `
	data/trimmis_profile19_audit_candidate.json `
	data/trimmis_profile19_review.json `
	data/trimmis_profile19_reference.json
```

The command rejects hash drift, missing reviewer identity or date, unconfirmed
independence or direction, missing or duplicate review items, and every status
other than `pass`. On success it prints the approved file's SHA-256.