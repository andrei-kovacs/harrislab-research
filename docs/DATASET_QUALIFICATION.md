# Dataset Qualification Sprint

Initial assessment date: 2026-09-02. Updated 2026-09-18 after qualifying a
second real-data reference from ADS Harp Inn.

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
| Ulm-Eggingen Linear Pottery models, Zenodo 4744471, 5534232, and 5534261 | `PASS` | `PASS` | `HOLD` | `PASS` | `PASS` | `PASS` | `PASS` | `PASS` | **HOLD** |
| Virtual Poeymau software, Zenodo 7391905 | `PASS` | `HOLD` | `FAIL` | `FAIL` | `FAIL` | `HOLD` | `FAIL` | `HOLD` | **REJECT AS BENCHMARK** |
| Cambridge Catalhoyuk Appendix A matrices | `HOLD` | `HOLD` | `PASS` | `FAIL` | `PASS` | `HOLD` | `FAIL` | `HOLD` | **REJECT FOR DIRECT-RELATION IMPORT** |
| ADS Harp Inn, collection 1005042, version 1 | `PASS` | `PASS` | `PASS` | `PASS` | `PASS` | `PASS` | `PASS` | `PASS` | **APPROVED** |

## ADS Harp Inn assessment

Dataset: High Speed Two Ltd. and Connect Archaeology, "Data from
Archaeological Recording Work at Harp Inn," version 1,
[DOI 10.5284/1133013](https://doi.org/10.5284/1133013), distributed by the
Archaeology Data Service in 2025.

Directly verified from the ADS metadata, rights statement, and deposited
semicolon-delimited Harris CSV:

- ADS collection `1005042`, version 1, has a stable DOI and is licensed under
  the Open Government Licence.
- `1C20HINAR_harris_matrix_phase_1_phase_2.csv` has frozen SHA-256
  `d754dfb14250dc66b2741c4d65d6cb08ef376775e4903bdbdc4554d00a948467`.
- The selected Group 1 component contains 36 stable, described contexts. It is
  connected by explicit `ABOVE`, `LATER`, or `CONTEMPORARY` source records.
- The import maps `ABOVE(source,target)` and `LATER(source,target)` to
  `target earlier -> source later`. The resulting 26 evidenced precedence
  relations are acyclic.
- Ten explicit `CONTEMPORARY` records are preserved as symmetric typed source
  evidence. They are used only to delimit the source component and never enter
  the precedence DAG.
- Sentinels `T`, `G`, `U`, `1000`, `1001`, `Matrix*`, hierarchy, phase
  membership, and layer values are excluded from benchmark connectivity.
- Each accepted precedence relation cites its exact CSV record. The importer
  fails on source checksum, component counts, canonical node or edge hashes,
  or acyclicity changes. AI contributes zero accepted graph mutations.

Reproduce the live qualification with:

```powershell
python scripts/qualify_harp_inn.py .local-data/harp-inn-source
```

## Cambridge Catalhoyuk Appendix A assessment

The inspected Appendix A workbook is a visual publication artifact, not an
explicit relation table. Its matrices depend on merged cells, timestep labels,
and embedded connector images. A preliminary count of 960 apparent assertions
was a prose keyword-search false positive; it must not be reported as a count
of stratigraphic relations. Recovering edges from worksheet geometry would
require an additional interpretation and review workflow rather than a direct,
source-record import. The artifact is therefore rejected for the direct-
relation benchmark, without implying that the published interpretation lacks
archaeological value.

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

The pilot uses a connected subset from Profile 19 rather than treating all 308
catalog positions as one graph. The matrix encodes relations graphically rather
than as a relation table. The deterministic extraction was independently
reviewed against the deposited matrix on 17 September 2026.

The deterministic extraction found 25 matrix nodes and 28 direct edges, all of
which passed source-author review. The standalone P19 section and synoptic
matrix share those 25 identifiers. Identifier `199` occurs only in the section;
catalog row 206 describes it as a furrow-like depression or plough marks. The
review confirmed that its omission from the P19 matrix was a source error and
placed it between context 26 (older) and context 170 (younger). The active
reference therefore contains 26 contexts and 29 direct relations, while the
unaltered 25/28 extraction remains available as a provenance snapshot.

The candidate JSON, highlighted matrix, completed review manifest, correction
manifest, and generated references are documented in
[`TRIMMIS_PROFILE19_AUDIT.md`](TRIMMIS_PROFILE19_AUDIT.md).

Reproduce the machine-checkable portion with:

```powershell
python -m pip install -e ".[acquisition]"
python scripts/qualify_trimmis.py .local-data/trimmis-source
```

The script verifies DOI, licence identifier, file checksums, workbook row
counts, and matrix text/vector structure. Raw artifacts are intentionally not
committed to this repository.

## Ulm-Eggingen assessment

Datasets: Eva Rosenstock, supplementary data to Figures 7, 8, and 9 of
*Linear Pottery and Harris* (2022),
[DOI 10.5281/zenodo.4744471](https://doi.org/10.5281/zenodo.4744471),
[DOI 10.5281/zenodo.5534232](https://doi.org/10.5281/zenodo.5534232), and
[DOI 10.5281/zenodo.5534261](https://doi.org/10.5281/zenodo.5534261).

Directly verified from the Zenodo records and deposited CSV and GraphML files:

- All three records are versioned datasets licensed CC BY 4.0. Each provides
  DOI-stable CSV, GraphML, HMCX, PDF, and image representations with published
  file checksums.
- The uncollapsed CSV files contain 107 `DEPOSIT` records, 36
  `PHASE_GROUP` records, and either three or eight `PERIOD_GROUP` records,
  plus top-surface, geology, and unexcavated sentinels.
- The `ABOVE` and `BELOW` fields explicitly encode 36 unique, acyclic
  deposit-to-deposit superpositions. These relations can be imported without
  deriving them from phase labels.
- Only 60 of the 107 deposits have a non-empty description in the deposited
  CSV. The context-identity gate therefore remains on hold pending a stable
  source for descriptions of the other 47 deposits or a justified bounded
  context table.
- The direct deposit graph is highly disconnected. Its largest weakly
  connected component has six deposits; the remaining components have four or
  fewer deposits or are isolated. No connected 20-100-context pilot can be
  selected from direct deposit relations alone.
- The complete GraphML combines superpositions with building, fence, period,
  contemporaneity, spatial, yard-model, and ceramic-analysis interpretations.
  It has 149 or 154 nested nodes and 218 directed edges and is cyclic when all
  edge classes are treated as precedence. The full graph must not be imported
  as a Harris precedence DAG without a documented relation-class mapping.
- Figures 7-9 and their versioned graph files are published expert reference
  interpretations based on Claus-Joachim Kind's 1989 excavation publication.
  They satisfy the reference gate but do not convert model-derived edges into
  direct stratigraphic observations.

This candidate remains `HOLD`. It is suitable for testing typed-relation
import and authority separation, but not for the preregistered hidden-direct-
relation benchmark. Promoting it would require complete context descriptions
and a defensible 20-100-context evaluation unit that does not gain connectivity
from interpretive phase or spatial-model edges.

## Virtual Poeymau assessment

Software: Sebastien Plutniak, "Virtual Poeymau: a web application to explore
the archaeological data from the excavation archives of the Poeymau cave
(France)," version 0.3,
[DOI 10.5281/zenodo.7391905](https://doi.org/10.5281/zenodo.7391905).

Directly verified from the Zenodo API and the complete Git tree at tag `v0.3`:

- The software has a version DOI, concept DOI `10.5281/zenodo.4765692`, and a
  22,759-byte archive with published MD5
  `8a2202a696196e4c2587a3bebc550e3c`.
- Zenodo classifies the deposit as software and records its licence only as
  `other-open`. The linked repository contains an AGPL-3.0 licence for the
  program, but no statement explicitly licensing the museum-derived
  archaeological records for reuse and derivatives.
- The complete tagged tree contains only `LICENSE`, `NEWS.md`, `README.md`,
  `app.R`, `server.R`, and `ui.R`. It contains no deposited data table.
- `server.R` calls `source("data-preprocessing.R")`, but that file is absent
  from the tag and Zenodo archive. The published artifact therefore cannot
  reproduce the application or retrieve a fixed dataset independently.
- The application describes about 15,000 object records extracted from field
  notes. Exposed fields include object ID, square, coordinates or coordinate
  ranges, field layer and sublayer, localisation method, object description,
  alteration, class, and material. These are object observations rather than
  a bounded table of 20-100 archaeological contexts with stable descriptions.
- No explicit context-to-context `above`, `below`, `earlier`, `later`, `cuts`,
  `fills`, `overlies`, or `underlies` relation table is present. Layer order is
  hard-coded for display, and modelled surfaces and convex hulls are computed
  from object coordinates; neither is direct stratigraphic ground truth.
- No deposited Harris matrix or archaeologist-reviewed reference graph is
  included.

This candidate is rejected for HarrisLab benchmarking because the context,
direct-relations, reference, and reproducibility gates fail. It remains a useful
methodological example of spatial post-excavation exploration, but its object
layers must not be converted into direct Harris relations.

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