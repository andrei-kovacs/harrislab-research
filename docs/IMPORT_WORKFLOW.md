# Local Dataset Import

## Purpose

Local import lets an archaeologist review a project sequence without sending
the file to HarrisLab or adding it to the public repository. The browser checks
the complete file before replacing the active workspace and binds review events
to the SHA-256 of the exact imported bytes.

Start with [`import_reference_template.json`](../data/import_reference_template.json).

## Required structure

The root schema must be `harrislab.reference.v1` and contain:

- `dataset`: non-empty `title`, `source`, and `license` strings;
- `contexts`: 2-500 unique records with string `id` and `label`;
- `evidence`: one or more unique records with `id`, supported `kind`,
  `description`, and `source`; and
- `relations`: 1-2,000 direct `observed` relations with `earlier`, `later`, and
  at least one known `evidence_id`.

Supported evidence kinds are `context_sheet`, `drawing`, `photograph`,
`sample`, `specialist_report`, and `other`.

Relation direction is always older to younger: `earlier -> later`.

## Fail-closed checks

Import is rejected without changing the current workspace when the file has:

- malformed JSON or the wrong schema;
- missing dataset identity or rights information;
- duplicate or whitespace-normalized identifiers;
- unknown relation endpoints or evidence identifiers;
- self-relations, duplicate relations, or non-observed statuses; or
- a cycle in the accepted precedence graph.

Rejected data is not partially loaded.

## Local authority boundary

An imported file is not a qualified HarrisLab reference and receives no
benchmark result or source-review badge. Source-specific Trimmis and Harp panels
remain disabled. The matrix and review queue operate locally, and the source
button is enabled only when `dataset.source` is an HTTP or HTTPS URL.

Use **Export audit** to retain the imported reference, exact source filename and
SHA-256, and append-only review events. Browser storage is not an archival or
multi-user database.