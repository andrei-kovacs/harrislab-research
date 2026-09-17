# Trimmis Profile 19 Drawing-Review Workflow

This workflow lets a qualified archaeologist review the 27 relations marked
`awaiting_drawing_review` in the canonical P19 comparison. It records whether
the drawing corroborates a matrix relation. It does not approve, reject, add,
or remove graph relations.

## Prepare the checklist

Run:

```powershell
python scripts/drawing_review_workflow.py
```

This regenerates the hash-bound blank templates:

- `data/trimmis_profile19_drawing_review_template.json`
- `docs/trimmis_profile19_drawing_review_checklist.csv`

Give the reviewer a private copy of the CSV and the P19 source drawing. Keep
names, affiliations, email addresses, and correspondence outside the CSV. The
`public_label` must be non-identifying.

## Complete the checklist

Set the metadata values as follows:

- `public_label`: a non-identifying label, such as `Independent reviewer 1`
- `reviewed_at`: an ISO date in `YYYY-MM-DD` format
- `qualified_for_drawing_review`: `true`
- `independent_from_matrix_extraction`: `true`
- `direction_confirmation`: `older_to_younger_confirmed`

Each relation requires one decision:

| Decision | Meaning |
|---|---|
| `corroborated` | The drawing supports the stated relation and direction. |
| `contradicted` | The drawing appears inconsistent with the relation or direction. |
| `indeterminate` | The available drawing does not support a confident decision. |
| `not_visible` | The relevant contact or evidence is not visible. |

A note is mandatory for every decision except `corroborated`. Do not alter the
relation identifiers or comparison hash.

## Validate the return

Run:

```powershell
python scripts/drawing_review_workflow.py --validate path/to/completed_checklist.csv
```

On success, the command writes `drawing_review_summary.json`. It fails closed
for a stale hash, missing or duplicate relation, incomplete declaration,
pending or unknown decision, or missing required rationale. The summary always
contains an empty `accepted_graph_mutations` list. Any later graph correction
requires its own evidence, authority, and approval workflow.