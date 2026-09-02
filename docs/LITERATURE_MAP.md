# Preliminary Literature and Prior-Art Map

This is a scoped starting map, not a systematic review. Pages were checked on
2026-09-02. No originality claim should be made from this document alone.

Sprint 1 evidence is recorded in the [source register](SOURCE_REGISTER.md) and
[novelty screen](NOVELTY_SCREEN.md). Those documents preserve search scope,
evidence depth, overlap decisions, and confidence separately from this map.

## Verified starting points

| Area | Starting source | Relevance |
|---|---|---|
| Archaeological stratigraphy | [Harris Matrix project](https://www.harrismatrix.com/) | Primary starting point for Harris's principles, terminology, and the history of the matrix. |
| Matrix software | [Harris Matrix Composer](https://www.harrismatrixcomposer.com/) | Existing matrix construction software. Capabilities and publications require deeper review because the page was not machine-readable during this initial check. |
| Semantic excavation data | [CRMarchaeo](https://www.cidoc-crm.org/crmarchaeo/) | CIDOC CRM extension for excavation entities, activities, observations, stratigraphy, integration, and exchange. HarrisLab should map to it rather than invent an incompatible ontology. |
| Chronological modelling | [OxCal](https://c14.arch.ox.ac.uk/oxcal.html) | Established radiocarbon calibration and archaeological chronological modelling. HarrisLab should not present graph ordering as a replacement for Bayesian chronology. |

## Review clusters

The formal review should search scholarly databases for:

1. Harris matrix generation, validation, transitive reduction, and digital
   excavation recording.
2. Uncertain temporal graphs, alternative stratigraphic interpretations, and
   probabilistic or fuzzy stratigraphy.
3. CRMarchaeo, CIDOC CRM, archaeological knowledge graphs, and provenance
   standards such as PROV-O.
4. Bayesian chronology and the integration of stratigraphic constraints with
   scientific dating.
5. NLP and computer vision applied to context sheets, excavation reports,
   section drawings, and legacy archives.
6. Active learning, value of information, and decision support in fieldwork.
7. Agent-based and cellular-automata models of archaeological site formation.

## Candidate overlap tests

For every discovered system or paper, record whether it supports:

- evidence provenance per relation;
- observed versus inferred edge status;
- simultaneous competing interpretations;
- deterministic contradiction explanations;
- dependency tracing from conclusions to evidence;
- ranking unresolved relations by expected information gain;
- reproducible evaluation against a known formation history.

The project is only distinct if a meaningful combination remains after this
comparison. Merely using an LLM to extract or draw a matrix is not sufficient.

## Search protocol

- Search Scopus, Web of Science, Google Scholar, JSTOR, ADS, Zenodo, and GitHub.
- Use forward and backward citation chaining from Harris, CRMarchaeo, digital
  matrix systems, and archaeological chronology literature.
- Record query, date, database, inclusion decision, and stable identifier.
- Ask at least two practising field archaeologists to identify software and
  terminology absent from the academic literature.
- Publish the resulting source register and overlap table before describing any
  feature as novel.
