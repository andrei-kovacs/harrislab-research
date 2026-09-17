# Trimmis Profile 19 Extraction Audit

Status: **REVIEWED; SOURCE-AUTHOR CORRECTION INCORPORATED**. Extracted
2026-09-02 and independently reviewed 2026-09-17 from the checksum-verified
files in Zenodo dataset
[10.5281/zenodo.4461075](https://doi.org/10.5281/zenodo.4461075), licensed
CC BY 3.0.

## Scope

The published-matrix candidate contains 25 nodes and 28 direct relations from
the rightmost Profile 19 column of the published synoptic Harris matrix.
Relations use the HarrisLab `older -> younger` direction. The geometry extractor
passed its checks for unique labels, catalog matches, unambiguous connector
endpoints, connectivity, duplicate edges, and acyclicity. Independent review
confirmed all 25 nodes, all 28 relations, and the direction convention.

The standalone profile and matrix share all 25 matrix identifiers. Position
`199`, cataloged as a furrow-like depression or plough marks, appears only in
the profile drawing. The review confirmed that this was an omission in the
published P19 matrix and supplied the corrected position: `26 -> 199 -> 170`,
where 26 is older and 170 is younger. The approved active reference incorporates
that correction and contains 26 contexts and 29 direct relations. The unchanged
published-matrix extraction is retained separately for auditability.

## Artifacts

- [Audit candidate JSON](../data/trimmis_profile19_audit_candidate.json)
- [Completed review manifest](../data/trimmis_profile19_review.json)
- [Reviewed published-matrix reference](../data/trimmis_profile19_published_reference.json)
- [Confirmed correction manifest](../data/trimmis_profile19_corrections.json)
- [Active corrected reference](../data/trimmis_profile19_reference.json)
- [P19 drawing comparison](TRIMMIS_DRAWING_COMPARISON.md)
- [Drawing comparison JSON](../data/trimmis_profile19_drawing_comparison.json)
- [Catalogue text-extraction pilot](TRIMMIS_TEXT_EXTRACTION_PILOT.md)
- [Text proposal JSON](../data/trimmis_profile19_text_relation_proposals.json)
- [Geometry overlay](trimmis_profile19_overlay.png)
- Source matrix MD5: `9ece18c188763350f16e164f441a927e`
- Source catalog MD5: `75983db690194fb562ba0378ebd627a3`
- Source P19 drawing MD5: `53ccf16a523e986ead69a30fc3f8dc24`

Blue rectangles in the overlay identify extracted nodes. Magenta paths identify
extracted direct connectors; small magenta numbers are source PDF path indices.

## Edge Checklist

The geometry overlay was inspected during extraction and every highlighted path
coincided with a printed connector. Independent source review subsequently
confirmed every listed node and relation.

| PDF path | Older | Younger | Independent review |
|---:|---:|---:|---|
| 34 | 102 | 104 | PASS |
| 35 | 164 | 165 | PASS |
| 36 | 165 | 98 | PASS |
| 37 | 222 | 228 | PASS |
| 38 | 223 | 222 | PASS |
| 39 | 224 | 223 | PASS |
| 40 | 228 | 99 | PASS |
| 41 | 98 | 224 | PASS |
| 42 | 99 | 102 | PASS |
| 136 | 22 | 23 | PASS |
| 137 | 23 | 235 | PASS |
| 138 | 23 | 240 | PASS |
| 139 | 235 | 26 | PASS |
| 140 | 240 | 26 | PASS |
| 213 | 170 | 156 | PASS |
| 214 | 26 | 170 | PASS |
| 319 | 150 | 153 | PASS |
| 320 | 150 | 50 | PASS |
| 321 | 156 | 150 | PASS |
| 322 | 156 | 267 | PASS |
| 323 | 267 | 153 | PASS |
| 440 | 153 | 30 | PASS |
| 441 | 30 | 155 | PASS |
| 442 | 30 | 241 | PASS |
| 443 | 50 | 30 | PASS |
| 512 | 155 | 3 | PASS |
| 513 | 241 | 3 | PASS |
| 514 | 3 | 164 | PASS |

## Approval And Correction

Approval required all 25 node labels and all 28 edges to pass independent
review, confirmation of the direction convention, reviewer identity and date,
and a SHA-256 binding to the reviewed candidate. The completed review satisfies
that gate.

The context 199 correction is applied only after approval through a separate
manifest bound to the approved reference hash. The correction step removes the
direct `26 -> 170` relation and adds `26 -> 199` and `199 -> 170`. Both the
source extraction and corrected reference therefore remain reproducible.

The separate drawing-comparison layer confirms identifier coverage and records
the correction provenance without deriving chronology from raw vertical
position. The other 27 matrix relations remain explicitly awaiting qualified
drawing review.

The catalogue text-extraction layer surfaces two literal relation mentions as
three alias-aware review options. All reference contexts outside the active P19
graph, so the pilot changes no accepted relation and supports no extraction
accuracy claim.

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
	data/trimmis_profile19_published_reference.json
```

Apply the confirmed correction with:

```powershell
python scripts/review_trimmis_profile19.py correct `
	data/trimmis_profile19_published_reference.json `
	data/trimmis_profile19_corrections.json `
	data/trimmis_profile19_reference.json
```

The commands reject hash drift, incomplete review, unknown or duplicate graph
items, and corrections that introduce a chronological cycle.