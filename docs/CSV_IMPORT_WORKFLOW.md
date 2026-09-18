# CSV Pair Import

## Files

HarrisLab accepts two local CSV files:

1. A context register with one row per context.
2. A direct-relation register with one evidenced `earlier -> later` relation
   per row.

Use the [context template](../data/import_contexts_template.csv) and
[relation template](../data/import_relations_template.csv) as working examples.
Headers do not need to match the templates because the import dialog requires
explicit column mapping.

## Required mappings

The context file maps context ID and label. A source-record column is optional.
The relation file maps earlier context, later context, evidence ID, evidence
kind, evidence description, and evidence source.

Repeated evidence IDs are allowed only when their kind, description, and source
are identical. The first release supports one evidence ID per direct-relation
row. Add another relation row when distinct source assertions must remain
separately auditable.

## Validation and binding

CSV values are not silently trimmed or rewritten. After conversion, the result
passes the same strict checks as JSON import, including unique identifiers,
known endpoints, known evidence, observed-only status, and acyclicity.

The import SHA-256 binds:

- both exact source filenames and file contents;
- project title, source, and licence; and
- every selected column mapping.

Changing a source byte, metadata value, or mapping creates a different review
workspace. File contents remain in the browser.

## Output

**Export audit** includes the validated HarrisLab reference, the combined
source SHA-256, source filenames, mappings, and review history. It does not
claim that HarrisLab qualified the archaeological interpretation.