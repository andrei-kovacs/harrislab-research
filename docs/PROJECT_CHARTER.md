# HarrisLab Project Charter

## Purpose

Investigate whether a Harris matrix can become an auditable computational
reasoning environment without obscuring the distinction between archaeological
observation, logical derivation, disputed interpretation, and AI proposal.

## Research questions

1. Can explicit provenance and relation status make stratigraphic conclusions
   more reproducible than an unannotated matrix?
2. Can competing valid graph scenarios quantify how unresolved relationships
   affect phasing and chronological conclusions?
3. Can information-gain ranking identify the unresolved relationship whose
   verification would reduce interpretive uncertainty most?

## Candidate contribution

The candidate contribution is the combination of edge-level provenance,
scenario comparison, dependency tracing, and information-value ranking in a
Harris-matrix workbench. This is a hypothesis about novelty, not a novelty
claim. It must survive the review protocol in `LITERATURE_MAP.md`.

## Principles

- AI may propose, extract, compare, and explain, but does not silently alter an
  accepted interpretation.
- Every accepted relationship should be traceable to evidence or explicitly
  identified as a logical derivation.
- Confidence labels are not treated as numerical probabilities without a
  calibrated statistical model.
- Contradiction checks and graph derivations remain deterministic and testable.
- Alternative interpretations are preserved instead of overwritten.

## Initial experiment

Encode a small published or openly licensed excavation sequence, then create
controlled variants by hiding or disputing selected relations. Measure:

- cycle-detection accuracy;
- recovery of logically implied relations;
- number of valid total orders;
- sensitivity of phase conclusions to each disputed edge;
- agreement between information-value ranking and archaeologist judgement.

The synthetic dataset in `data/` validates software behaviour but cannot
support archaeological conclusions.

## Boundaries

The first release will not infer relationships from images, assign dates, or
claim autonomous archaeological interpretation. LLM extraction and formation
process simulation begin only after the deterministic graph model and an open
evaluation dataset are established.

## Milestones

1. Formal model and deterministic command-line audit.
2. Scenario model for optional and mutually exclusive relations.
3. Information-gain experiment on a documented dataset.
4. Interactive matrix and evidence viewer.
5. Human-reviewed extraction of candidate relations from text.
6. Synthetic formation-process benchmark, with cellular automata evaluated as
   one possible generator rather than assumed to be archaeologically valid.
