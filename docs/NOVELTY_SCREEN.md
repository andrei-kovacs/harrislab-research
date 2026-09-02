# Sprint 1 Novelty Screen

Status on 2026-09-02: **provisional gap identified, novelty not established**.
This screen compares reported capabilities, mostly at abstract level. It is a
falsification tool for candidate claims, not an originality opinion.

## Capability overlap

| Capability | Known overlap | HarrisLab implication | Confidence |
|---|---|---|---|
| Draw or manage a Harris Matrix digitally | S04, S05, S07, S08, S09, S19 | Not novel and must not be a contribution claim. | High |
| Integrate stratigraphy with GIS, 3D, 4D, or spatiotemporal data | S03-S09, S14, S17 | Not novel; treat spatial integration as interoperability work. | High |
| Represent excavation data semantically | S10-S13, S16-S18 | Not novel; align with CRMarchaeo rather than creating a competing ontology. | High |
| Connect evidence to virtual reconstruction | S06 and the Extended Matrix literature | Provenance alone is too broad a claim. HarrisLab must specify relation-level audit semantics and measurable benefits. | Medium-high |
| Revise field units during post-excavation analysis | S15 | Alternative interpretations are archaeologically motivated, but scenario-preserving computation still requires verification. | Medium-high |
| Derive or reason over stratigraphic relations | S08 and S10 report interval relations or semantic deductions; qualitative-constraint-network work also appeared in the search | Generic inference is not novel. Any claim must concern explicit dependency witnesses, accepted/disputed separation, or evaluation. | Medium |
| Preserve simultaneous competing graph interpretations | No included abstract clearly reports executable, mutually exclusive Harris-matrix scenarios | Candidate gap, subject to full-text and citation-chain review. | Low-medium |
| Return a deterministic minimal or human-auditable contradiction witness | Cycle and consistency concerns are known, but no included abstract clearly reports witness extraction tied to evidence provenance | Candidate gap, subject to algorithm and software review. | Low-medium |
| Rank unresolved relations by expected reduction in interpretive uncertainty | No direct match in the included screen | Strongest candidate gap, but active-learning and value-of-information literature outside archaeology must be reviewed. | Low-medium |
| Benchmark hidden-relation recovery against a licensed reference sequence | Reproducibility and open-data work exists, but no included source clearly reports this benchmark design | Candidate methodological contribution, not yet a domain novelty claim. | Low-medium |

## Claims ruled out

HarrisLab must not claim to be:

- the first digital Harris Matrix;
- the first integration of Harris matrices with spatial or 3D data;
- the first semantic model of excavation data;
- the first provenance-aware archaeological reconstruction workflow;
- a replacement for CRMarchaeo, ARIADNE, or Bayesian chronology;
- autonomous archaeological interpretation.

## Surviving candidate contribution

The narrow candidate is an **auditable constraint workbench for uncertain
stratigraphic interpretation** that combines:

1. explicit separation of observed, accepted, inferred, disputed, and
   AI-proposed relations;
2. executable alternative scenarios without overwriting the accepted graph;
3. deterministic contradiction and dependency witnesses tied to source
   evidence;
4. value-of-information ranking of unresolved relations; and
5. reproducible evaluation by hiding or disputing relations in a licensed,
   expert-reviewed sequence.

The combination, not any individual feature, is the candidate contribution.
It survives this rapid screen, but confidence remains low to medium until the
full-text review and non-archaeological constraint-reasoning review are done.

## Falsification tests

Reject or narrow the candidate contribution if prior art is found that:

1. stores mutually exclusive or optional stratigraphic relations as executable
   scenarios and compares their chronological consequences;
2. traces every inferred relation and contradiction witness to relation-level
   evidence;
3. ranks field checks using a calibrated value-of-information objective; or
4. evaluates those capabilities on reusable excavation data with hidden-edge
   or disputed-edge recovery metrics.

## Sprint decision

Proceed to a real-data pilot only after one dataset passes the acceptance gate
in `SOURCE_REGISTER.md`. In parallel, prioritize full-text checks for S08, S10,
S11, S15, and qualitative temporal-constraint-network systems. Those sources
are the most likely to falsify the surviving claims.
