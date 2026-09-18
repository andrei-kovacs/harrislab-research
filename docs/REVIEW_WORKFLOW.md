# Matrix Review Workflow

## Purpose

The Matrix Review Queue supports post-excavation reconciliation of an observed
relation or a proposed alternative direction. It answers a practical question:
what chronological conclusions would change if the reviewer accepted or
rejected this relation?

The queue is a human decision overlay. It never edits the loaded reference.

## Review procedure

1. Select Trimmis Profile 19 or ADS Harp Inn.
2. Click a matrix connector to prefill its direction and source record, or enter
   two context identifiers to test a candidate direction.
3. Record a stable reviewer identifier, evidence reference, and why the
   relation requires review.
4. Inspect the consequence preview. For an observed relation, it reports how
   many accepted chronological conclusions the rejection branch loses. For a
   candidate, it reports added conclusions or blocks acceptance if it creates a
   cycle.
5. Add a decision note and record `accept`, `reject`, or `undecided`.
6. Export the audit bundle and retain it with the reviewed project records.

Changing a decision appends another event. Earlier events remain in the log.
The current status is derived from the latest decision event for that relation.

## Audit record

Each event records:

- event schema and unique identifier;
- UTC timestamp;
- dataset and reference SHA-256;
- earlier and later context identifiers;
- reviewer identifier;
- evidence reference and opening rationale; and
- decision and decision note when applicable.

The exported `review_log` is bound to the corresponding component in
`harrislab_audit_manifest.json`. Its authority value is
`human_decision_overlay_reference_unchanged`.

## Authority and limitations

- A browser decision does not alter, correct, or supersede source archaeology.
- Cycle blocking is a structural validity check, not an archaeological ruling.
- Closure impact counts chronological implications equally; it does not measure
  fieldwork cost, evidential quality, or archaeological importance.
- Browser `localStorage` is neither shared nor an archival database. Export is
  required for retention, review exchange, or repository deposit.
- Evidence references are text links or identifiers. Binary attachments and
  reviewer authentication are not yet implemented.