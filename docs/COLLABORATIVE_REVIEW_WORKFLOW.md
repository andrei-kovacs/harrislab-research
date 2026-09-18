# Collaborative Review Exchange

## Scope

HarrisLab review remains local-first. Collaboration uses portable JSON bundles,
not a server account or an opaque shared database. A reviewer exports one named
interpretation branch and sends that file through the project's approved
collaboration channel.

## Interpretation branches

Every dataset starts with `main`. Additional named branches begin from the
immutable source reference and retain independent append-only review events.
The branch comparison reports latest decision counts and the chronological
conclusions gained or unsupported relative to the reference.

Accepting a candidate is blocked when it would create a cycle with other
accepted decisions in that branch. Decisions in one branch do not affect any
other branch or the source reference.

## Evidence attachments

Review questions may select up to 20 local files, each no larger than 25 MB.
HarrisLab records filename, media type, byte size, and SHA-256. File contents
are neither stored in browser persistence nor included in exports. Teams must
retain the original files in their controlled archive and use the fingerprint
to verify identity.

## Export and import

**Export this branch** creates `harrislab.review-bundle.v1` with:

- immutable reference path and SHA-256;
- dataset and branch identity;
- export timestamp; and
- append-only review events, including attachment fingerprints.

Import is fail-closed. HarrisLab rejects a bundle if its reference SHA-256 does
not match the active dataset, its event structure is invalid, its relation uses
unknown contexts, or its decisions fall outside the controlled vocabulary.
Known event IDs are deduplicated. A bundle named `main` is imported into a new
dated shared branch to avoid silently merging another reviewer's main line.

Portable exchange provides auditable asynchronous review. It is not concurrent
editing, identity authentication, access control, or archival storage.
