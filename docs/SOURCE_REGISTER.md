# Sprint 1 Source Register

Searches in this register began on 2026-09-02 and were extended through
2026-09-18. This is a reproducible rapid screen, not a systematic review.
`Metadata` means that bibliographic metadata
and an abstract or indexed summary were inspected. `Full text` means that an
open article page or PDF was available for inspection. An absence in a
metadata screen is not evidence that a capability is absent from the full work.

## Search log

| Source | Query | Scope | Result used |
|---|---|---|---|
| OpenAlex | `Harris matrix archaeology` | First 20 relevance-ranked records | Established Harris-matrix, digital matrix, and 3D/GIS systems |
| OpenAlex | `automatic Harris matrix archaeology` | First 20 relevance-ranked records | Extraction, spatiotemporal management, and qualitative reasoning systems |
| OpenAlex | `archaeological stratigraphy uncertainty graph` | First 20 relevance-ranked records | Uncertainty and chronological context; search precision was low |
| OpenAlex | `archaeological knowledge graph excavation CRMarchaeo` | First 20 of 53 records | Semantic models, ARIADNE, CRMarchaeo, and excavation-data roadmaps |
| OpenAlex | `archaeological excavation open dataset contexts stratigraphy` | First 20 relevance-ranked records | Candidate case studies and data sources; search precision was low |
| Zenodo API | `"Harris matrix" AND resource_type.type:dataset` | All seven matching dataset records returned on 2026-09-02 | Identified three CC BY 4.0 Ulm-Eggingen graph deposits and excluded archaeogaming datasets |
| GitHub CLI | `hmdp archaeology stratigraphy`; `Harris matrix archaeology`; `archaeological stratigraphy dataset` | Exact repository searches on 2026-09-02 | No archaeological HMDP or Harris dataset repository found; broader HMDP results were unrelated software |
| S15 backward citation trace | Crossref references for DOI `10.1007/s41982-023-00155-x` | All DOI-bearing references, followed through Zenodo API and the linked versioned GitHub tree | Identified and rejected Virtual Poeymau v0.3 as spatial software without deposited context relations or a reproducible data loader |
| Cambridge repository artifact inspection | Catalhoyuk Appendix A matrices | Workbook cells, merged ranges, timestep labels, prose, and embedded connector images | Rejected direct edge import; the apparent 960 assertions were keyword matches in prose, not relation records |
| Archaeology Data Service | Harris Matrix CSV | Collection metadata, rights, category download pages, and six deposited Harris CSVs | Identified Harp Inn collection 1005042 and qualified a checksum-bound 36-context Group 1 component |

The screen used stable identifiers to merge obvious duplicates. It did not
cover Scopus, Web of Science, JSTOR, dissertations, patents, or non-English
literature. Forward and backward citation chaining remains outstanding.

## Included sources

| ID | Source | Evidence checked | Why included |
|---|---|---|---|
| S01 | Edward C. Harris, *Principles of Archaeological Stratigraphy* (first edition 1979); [bibliographic record](https://doi.org/10.2307/3888021) | Metadata | Foundation of the Harris Matrix and the representation of relative stratigraphic sequence. |
| S02 | Patricia Paice, "Extensions to the Harris Matrix System to Illustrate Stratigraphic Discussion of an Archaeological Site" (1991), [DOI](https://doi.org/10.1179/009346991791548753) | Metadata and abstract | Early explicit extension of the matrix for stratigraphic discussion. |
| S03 | Jeroen De Reu et al., "Integrating geomatics in archaeological research at the site of Thorikos" (2014), [DOI](https://doi.org/10.1016/j.jas.2014.02.018) | Metadata | Integrated excavation recording, geomatics, metadata, and digital workflows. |
| S04 | Jeroen De Reu et al., "Spatiotemporal data as the foundation of an archaeological stratigraphy extraction and management system" (2016), [DOI](https://doi.org/10.1016/j.culher.2015.12.001) | Metadata and abstract | Direct prior art for extracting and managing archaeological stratigraphy from spatiotemporal data. |
| S05 | Wolfgang Neubauer et al., "Integrated Spatio-temporal Documentation and Analysis of Archaeological Stratifications Using the Harris Matrix" (2018), [DOI](https://doi.org/10.2312/gch.20181369) | Metadata and abstract | Direct prior art for integrated Harris-matrix documentation and analysis. |
| S06 | Emanuel Demetrescu et al., "From Field Archaeology to Virtual Reconstruction: A Five Steps Method Using the Extended Matrix" (2021), [DOI](https://doi.org/10.3390/app11115206) | Metadata and abstract | Extended Matrix workflow with traceable, transparent virtual reconstruction. |
| S07 | Lidia Ortega et al., "Integrated and interactive 4D system for archaeological stratigraphy" (2022), [DOI](https://doi.org/10.1007/s12520-022-01667-3) | Metadata and abstract | Combines drawings, profiles, plans, Harris matrices, and digitized files in a 4D record. |
| S08 | Michael Doneus et al., "Stratigraphy from Topography I" (2022), [DOI](https://doi.org/10.1553/archaeologia106s203) | Metadata and abstract | Extends matrix creation with Allen interval relations, GIS, periods, phases, and an absolute timeline. |
| S09 | Michael Doneus et al., "Stratigraphy from Topography II" (2022), [DOI](https://doi.org/10.1553/archaeologia106s223) | Metadata and abstract | Practical GIS-based spatiotemporal use of the Harris Matrix on topographic data. |
| S10 | Keith May, "The Matrix: Connecting Time and Space in archaeological stratigraphic records and archives" (2020), [DOI](https://doi.org/10.11141/ia.55.8) | Full text available; abstract screened | Direct discussion of reusable stratigraphic relations, conceptual modelling, and semantically enriched deductions. |
| S11 | Markos Katsianis et al., "Semantic Modelling of Archaeological Excavation Data" (2023), [DOI](https://doi.org/10.11141/ia.64.12) | Full text available; abstract screened | State-of-the-art review and roadmap for granular excavation data, CIDOC CRM extensions, and CRMarchaeo. |
| S12 | Franco Niccolucci, Achille Felicetti, and Sorin Hermon, "Populating the Data Space for Cultural Heritage with Heritage Digital Twins" (2022), [DOI](https://doi.org/10.3390/data7080105) | Metadata and abstract | Adjacent semantic infrastructure based on interoperable Heritage Digital Twins; not an excavation-specific model. |
| S13 | ARIADNE consortium, "Enabling European Archaeological Research: The ARIADNE E-Infrastructure" (2017), [DOI](https://doi.org/10.11141/ia.43.11) | Metadata and abstract | Existing infrastructure for discovery, integration, and reuse of archaeological datasets. |
| S14 | Gary R. Nobles and Christopher H. Roosevelt, "Filling the Void in Archaeological Excavations" (2021), [DOI](https://doi.org/10.1515/opar-2020-0149) | Full text available; abstract screened | Programmatic construction of volumetric excavation units from contextual point-cloud data; names the Kaymakci Archaeological Project as a case. |
| S15 | Emmanuel Discamps et al., "Breaking Free from Field Layers" (2023), [DOI](https://doi.org/10.1007/s41982-023-00155-x) | Full text available; abstract screened | Post-excavation stratigraphies that revise field layers to improve reliability and chronological resolution. |
| S16 | ARIADNEplus Archaeological Excavation Modelling Working Group report (2022), [DOI](https://doi.org/10.5281/zenodo.7377910) | Metadata | Open, CC BY working-group output focused specifically on excavation-data modelling. |
| S17 | "A data model for the spatialized integration of archaeological excavation information from prehistoric sites" (2026), [DOI](https://doi.org/10.1038/s40494-026-02316-x) | Metadata and abstract | Recent direct overlap: spatialized integration of fragmented excavation information and GIS for prehistoric sites. |
| S18 | CRMarchaeo, [official specification page](https://www.cidoc-crm.org/crmarchaeo/) | Official project page | Domain ontology for archaeological excavation observations, activities, entities, and stratigraphic relations. |
| S19 | Harris Matrix Composer, [project site](https://www.harrismatrixcomposer.com/) | Project page only | Existing matrix-construction software; detailed capability verification is still required. |
| S20 | OxCal, [official project site](https://c14.arch.ox.ac.uk/oxcal.html) | Official project page | Established Bayesian chronological modelling; prevents overclaiming graph order as chronological inference. |
| S21 | Johannes Reich, "Die spaeteisenzeitliche Siedlung von Trimmis GR im Alpenrheintal - Ergaenzende Daten" (2021), [DOI](https://doi.org/10.5281/zenodo.4461075) | Dataset landing page, API metadata, XLSX catalog, and vector Harris matrix inspected; published MD5 checksums reproduced | First candidate with an explicit data licence, stable context catalog, deposited source profiles, and an expert reference matrix. |
| S22 | Eva Rosenstock, supplementary data to Figures 7-9 of *Linear Pottery and Harris* (2022), [Figure 7](https://doi.org/10.5281/zenodo.4744471), [Figure 8](https://doi.org/10.5281/zenodo.5534232), and [Figure 9](https://doi.org/10.5281/zenodo.5534261) | Dataset landing pages, API metadata, and all deposited CSV and GraphML files inspected | CC BY 4.0 expert models with explicit direct superpositions, but incomplete context descriptions and no 20-context connected direct-relation component. |
| S23 | Sebastien Plutniak, "Virtual Poeymau" v0.3 (2022), [version DOI](https://doi.org/10.5281/zenodo.7391905) | Zenodo API metadata, archive checksum, complete Git tree at `v0.3`, and all six tagged source files inspected | Spatial exploration software cited by S15; rejected as a benchmark because the archaeological table and preprocessing file are absent, data rights are not explicit, and no direct context relations or reference graph are deposited. |
| S24 | High Speed Two Ltd. and Connect Archaeology, "Data from Archaeological Recording Work at Harp Inn" (2025), [DOI](https://doi.org/10.5284/1133013) | ADS collection 1005042 metadata, version 1 rights statement, citation, category downloads, and checksum-frozen Harris CSV inspected | Open Government Licence source with stable context records and explicit `ABOVE`, `LATER`, and `CONTEMPORARY` relations. A deterministic import yields 36 contexts, 26 precedence relations, and 10 typed non-precedence relations. |

## Candidate evaluation data

| Candidate | Current evidence | Decision before use |
|---|---|---|
| Kaymakci Archaeological Project contextual point clouds | S14 demonstrates programmatic excavation-unit reconstruction from project data. The article is open access, but an article licence does not license the underlying records. | **HOLD:** no stable dataset record, data licence, relation table, or reference sequence was directly verified. |
| ARIADNEplus report, Zenodo 7377910 | S16 is a CC BY 4.0 report with report and annex files. | **REJECT AS DATASET:** it contains modelling documentation, not context and relation records. Retain it as guidance. |
| ARIADNE catalogue excavation collections | S11, S13, and S16 establish discovery infrastructure and modelling work. | **HOLD:** identify a specific catalogue record containing licensed context-level data, explicit stratigraphic relations, and a reference interpretation. |
| Published Post-excavation Stratigraphy cases | S15 provides a strong methodological comparator between field and revised units. | Verify whether machine-readable unit and relation tables are deposited under a reusable license. |
| Trimmis late Iron Age settlement supplementary data | S21 is a CC BY 3.0 Zenodo dataset with a 308-row position catalog, deposited profile drawings, and a vector synoptic Harris matrix. | **APPROVED FOR PILOT EXTRACTION:** use a profile-bounded subset; visually audit the geometry-derived edge list before benchmarking. |
| Ulm-Eggingen Linear Pottery models | S22 provides three CC BY 4.0, DOI-stable expert graphs. The uncollapsed files contain 107 deposits and 36 direct deposit superpositions, but only 60 deposit descriptions; the largest direct-relation component has six deposits. | **HOLD:** useful for typed-relation import tests, but do not use phase, spatial, yard-model, or ceramic edges to manufacture a connected benchmark. |
| Virtual Poeymau | S23 is DOI-stable AGPL-3.0 application code for exploring about 15,000 museum-derived object records. The fixed artifact omits its data preprocessing dependency and data, has no explicit data licence, and exposes no context-relation table or reference graph. | **REJECT AS BENCHMARK:** retain as a methodological spatial-visualisation source; do not infer direct relations from its hard-coded layer display order or modelled surfaces. |
| Cambridge Catalhoyuk Appendix A matrices | The inspected XLSX matrices use merged cells, timestep labels, and embedded connector images. Prose keyword matching produced an invalid apparent count of 960 assertions. | **REJECT FOR DIRECT-RELATION IMPORT:** worksheet geometry is not an explicit edge table and requires a separate reviewed extraction workflow. |
| ADS Harp Inn | S24 is DOI-stable version 1 data under the Open Government Licence. The frozen Group 1 CSV component has 36 contexts, 26 evidenced precedence edges, and 10 explicit contemporary links. | **APPROVED:** import only explicit `ABOVE` and `LATER` records as precedence. Preserve `CONTEMPORARY` as typed non-precedence evidence and exclude sentinels, hierarchy, phase, layer, and coordinates from manufactured connectivity. |
| HarrisLab synthetic building | Repository-owned and deterministic. | Retain only for software validation; never use it as evidence for archaeological performance. |

Trimmis and ADS Harp Inn now provide two independently sourced real-data
references. Harp Inn is the first direct relation-table import; its benchmark
results remain descriptive validation rather than archaeological-performance
proof. The acceptance gate is: stable identifier,
explicit license, context identifiers, relation ground truth or expert-reviewed
reference interpretation, and sufficient provenance to score reconstruction.
The full gate definitions and evidence audit are in
[`DATASET_QUALIFICATION.md`](DATASET_QUALIFICATION.md).

## Next search actions

1. Read S04-S17 in full and record page-level evidence for each overlap field.
2. Run forward and backward citation chaining from S04, S05, S10, S11, and S15.
3. Search Scopus, Web of Science, Google Scholar, JSTOR, Zenodo, ADS, and GitHub
   using the logged queries and synonyms for `ambiguous`, `alternative`,
   `inconsistent`, `constraint`, and `value of information`.
4. Ask two field archaeologists to review both the terminology and the software
   list before any originality statement is submitted.
