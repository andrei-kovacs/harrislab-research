# Dataset Qualification Sprint

Assessment date: 2026-09-02. One real dataset is approved for pilot extraction,
but no extracted reference graph is approved for benchmarking yet.

This record separates publication access from data reuse permission. An open or
CC-licensed article does not establish a licence for its underlying excavation
records.

## Decision rules

Each gate is assigned one of four states:

- `PASS`: direct evidence satisfies the gate.
- `FAIL`: direct evidence shows that the candidate cannot satisfy the gate.
- `HOLD`: the gate might be satisfiable, but direct evidence is unavailable.
- `N/A`: the gate does not apply to that candidate.

A candidate is `APPROVED` only when every mandatory gate passes. One `FAIL`
rejects it. Any `HOLD` keeps it unapproved.

## Mandatory gates

| Gate | Pass condition | Evidence to retain |
|---|---|---|
| Stable identity | Dataset has a DOI, accession, or versioned repository identifier. | Landing page and version or access date. |
| Data licence | Licence explicitly covers the downloaded records and permits research reuse and derivatives. | Dataset rights statement, not the article licence. |
| Context identity | Approximately 20-100 archaeological contexts have stable identifiers and descriptions. | Context table or API response. |
| Direct relations | Explicit context-to-context stratigraphic relations can be imported without inferring them from phase labels. | Relation table, graph, or documented fields. |
| Reference interpretation | A published or archaeologist-reviewed sequence identifies the expected relations or graph. | Harris matrix, signed review, or versioned reference graph. |
| Provenance | Imported contexts and relations can be traced to source records. | Source identifiers, citations, and field definitions. |
| Reproducibility | A fixed subset can be redistributed, or a scripted import can retrieve a stable version. | Redistribution terms or deterministic retrieval procedure. |
| Attribution | Required citation and notices are explicit. | Citation and attribution statement. |

## Candidate matrix

| Candidate | Identity | Licence | Contexts | Relations | Reference | Provenance | Reproducibility | Attribution | Decision |
|---|---|---|---|---|---|---|---|---|---|
| Kaymakci Archaeological Project data used by Nobles and Roosevelt (2021) | `HOLD` | `HOLD` | `HOLD` | `HOLD` | `HOLD` | `HOLD` | `HOLD` | `HOLD` | **HOLD** |
| ARIADNEplus excavation-modelling report, Zenodo 7377910 | `PASS` | `PASS` | `FAIL` | `FAIL` | `FAIL` | `N/A` | `PASS` | `PASS` | **REJECT AS DATASET** |
| ARIADNE catalogue excavation collections | `HOLD` | `HOLD` | `HOLD` | `HOLD` | `HOLD` | `HOLD` | `HOLD` | `HOLD` | **HOLD** |
| Trimmis late Iron Age settlement supplementary data, Zenodo 4461075 | `PASS` | `PASS` | `PASS` | `PASS` | `PASS` | `PASS` | `PASS` | `PASS` | **APPROVED FOR PILOT EXTRACTION** |

## Trimmis assessment

Dataset: Johannes Reich, "Die spaeteisenzeitliche Siedlung von Trimmis GR im
Alpenrheintal - Ergaenzende Daten," version 1,
[DOI 10.5281/zenodo.4461075](https://doi.org/10.5281/zenodo.4461075).

Directly verified from the Zenodo record and checksum-matched files:

- The record is a versioned dataset with concept DOI `10.5281/zenodo.4461074`.
- The deposited records are licensed CC BY 3.0.
- `Katalog_Positionen.xlsx` contains one 308-row sheet of stable position
  identifiers and German descriptions.
- `Harris_Matrix.pdf` is the published synoptic Harris matrix and phase
  structure. It is a one-page Illustrator vector document with selectable node
  labels, 175 text blocks, 550 vector paths, and 843 vector items.
- The deposit also contains source profile drawings `P19.pdf`, `P25.pdf`, and
  `P27.pdf`, allowing a profile-bounded pilot to retain source-level provenance.
- The matrix and catalog MD5 checksums match the values published by Zenodo.
- The required attribution is the dataset citation and CC BY 3.0 notice.

The pilot will use a connected subset from a deposited profile, initially
Profile 19, rather than treating all 308 catalog positions as one graph. The
matrix encodes relations graphically rather than as a relation table. This
satisfies the direct-relations source gate, but the derived edge list remains
unapproved until vector geometry is converted deterministically and every edge
is visually audited against the deposited matrix.

The first deterministic extraction found 25 matrix nodes and 28 direct edges.
All connector overlays coincide with printed matrix paths. The standalone P19
section and synoptic matrix share those 25 identifiers. Identifier `199` occurs
only in the section; catalog row 206 describes it as a furrow-like depression
or plough marks. Because the expert synoptic matrix omits it, the pilot records
the discrepancy but does not invent relations for `199`.

The candidate JSON, highlighted matrix, and independent edge checklist are in
[`TRIMMIS_PROFILE19_AUDIT.md`](TRIMMIS_PROFILE19_AUDIT.md). The benchmark stays
blocked while that checklist is pending.

Reproduce the machine-checkable portion with:

```powershell
python -m pip install -e ".[acquisition]"
python scripts/qualify_trimmis.py .local-data/trimmis-source
```

The script verifies DOI, licence identifier, file checksums, workbook row
counts, and matrix text/vector structure. Raw artifacts are intentionally not
committed to this repository.

## Kaymakci assessment

Primary research article: Gary R. Nobles and Christopher H. Roosevelt,
"Filling the Void in Archaeological Excavations: 2D Point Clouds to 3D
Volumes," [DOI 10.1515/opar-2020-0149](https://doi.org/10.1515/opar-2020-0149).

Verified:

- The article is an open-access publication and OpenAlex identifies its
  published version as CC BY.
- The abstract states that the method draws on contextual point-cloud datasets
  from the Kaymakci Archaeological Project.
- The article therefore establishes relevance to excavation-unit data and 3D
  reconstruction.

Not verified:

- a stable public dataset record for the records used in the article;
- a licence explicitly covering those underlying records;
- a downloadable context table and direct stratigraphic relation table;
- a published Harris matrix or other expert reference sequence; and
- redistribution and attribution terms for an evaluation subset.

Publisher, institutional-repository, and Open Context pages could not provide
machine-readable evidence for these missing gates during this sprint. This is
an absence of verification, not evidence that the data do not exist.

Promotion from `HOLD` requires a direct dataset landing page or a written reply
from the data owner that identifies the version, licence, context fields,
relation fields, reference interpretation, and permitted redistribution.

## ARIADNEplus report assessment

The [Archaeological Excavation Modelling Working Group report](https://doi.org/10.5281/zenodo.7377910)
has a stable DOI, four downloadable report files, and a CC BY 4.0 licence. Its
Zenodo resource type is `Report`. The deposited files are the final report and
annexes, not context and relation records. It is useful for modelling guidance
but fails the data-content gates and is rejected as the evaluation dataset.

The wider ARIADNE catalogue remains a discovery route, not a single qualified
candidate. A specific catalogue record must be assessed independently against
all mandatory gates.

## Next extraction action

Extract the Profile 19 graph from the checksum-verified matrix while preserving
the following evidence for every derived record:

1. Source record DOI, version, file name, and MD5.
2. Matrix page and node/connector PDF coordinates.
3. Original printed label and normalized catalog identifier.
4. Relation direction under the older-to-younger HarrisLab convention.
5. A visual-audit disposition for every node and edge.
6. A hash of the final approved reference graph.

Do not run the hidden-relation benchmark on an automatically extracted graph.
Preserve the raw source unchanged, record the field mapping, and import only the
visually approved edge list into a separate derived JSON fixture.

## Planned evaluation after approval

1. Import the full reference sequence and verify acyclicity and relation count.
2. Hide known direct relations under a fixed random seed and declared sampling
   protocol.
3. Rank the hidden relations using the current order-reduction baseline.
4. Reveal relations in ranked order and measure recovery of the reference
   sequence and declared archaeological conclusions.
5. Compare the ranking with random order, a simple graph heuristic, and an
   archaeologist's ranking.

Scenario modelling can proceed against synthetic fixtures while acquisition is
blocked, but no archaeological-performance claim may use those fixtures.