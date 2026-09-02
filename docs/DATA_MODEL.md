# Formal Data Model

## Graph convention

Let the stratigraphic graph be $G = (V, E)$, where each vertex is a context or
event and each directed edge $(u, v)$ means **u is earlier than v**. A valid
interpretation is a directed acyclic graph. Any directed cycle is therefore a
temporal contradiction.

This direction is an internal computational convention. A future interface may
display later contexts above earlier contexts in the familiar Harris layout.

## Entities

### Context

- `id`: stable identifier within a dataset.
- `label`: human-readable description.

The prototype deliberately avoids pretending that deposits, cuts, interfaces,
structures, and events are interchangeable. A controlled context-type model is
deferred until it can be aligned with established archaeological standards.

### Relation

- `earlier`: source context identifier.
- `later`: target context identifier.
- `status`: `observed`, `derived`, `disputed`, or `ai_proposed`.
- `evidence_ids`: zero or more provenance links.

`derived` means reachable through accepted edges. `disputed` and `ai_proposed`
are labels, not endorsements, and are excluded from the accepted graph. The
prototype can evaluate each unresolved edge independently or apply explicit
decisions in a named interpretation.

### Interpretation

- `name`: human-readable scenario identifier.
- `decisions`: zero or more candidate-edge decisions: `accept`, `reject`, or
	`undecided`.

Omitted candidate edges default to `undecided`. Accepting a candidate includes
its constraint only in that interpretation; it does not alter its source status
or mutate the accepted graph. Duplicate decisions, decisions for non-candidate
edges, and duplicate candidate endpoints are rejected as ambiguous. Scenario
results report accepted, rejected, and undecided candidates, contradiction
witnesses, bounded total-order counts, and implied chronological relations.
Pairwise comparison reports implications unique to either interpretation.
Any chronological implication can return one deterministic shortest supporting
path and the evidence records attached to that path. Scenario-specific witnesses
may include accepted disputed or AI-proposed relations without changing the
baseline interpretation.

Mutually exclusive groups involving more than opposite edge directions remain
future work.

### Evidence

- `id`: stable evidence identifier.
- `kind`: context sheet, drawing, photograph, sample, specialist report, other.
- `description`: concise human-readable account.
- `source`: archive reference or URI.

## Deterministic operations

- Referential-integrity validation.
- Cycle detection.
- Transitive derivation.
- Bounded enumeration of total orders consistent with the partial order.
- Candidate-edge impact measured as the change in valid total-order count.
- Named-interpretation evaluation and pairwise consequence comparison.
- Deterministic conclusion-to-relation and relation-to-evidence witnesses.

Counting total orders is exponential in the general case. The prototype uses a
hard configurable bound and reports truncation rather than presenting a lower
bound as an exact result.

## Next model extension

Add explicit phase and archaeological-claim entities, then trace those claims to
their chronological conclusions. Also add mutually exclusive decision groups.
The current total-order reduction is a deterministic constraint-impact measure,
not expected information gain. Numerical probability will remain out of scope
until priors and calibration data can be defended.
