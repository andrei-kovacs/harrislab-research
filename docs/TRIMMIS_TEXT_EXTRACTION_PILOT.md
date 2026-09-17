# Trimmis Profile 19 Text-Extraction Pilot

## Result

A deterministic scan of the catalogue descriptions attached to all 26 active
Profile 19 contexts found two explicit relational mentions. Because one source
row has two active aliases, those mentions produce three candidate edge
options. Every option refers to a context outside the active P19 reference, so
none is eligible for evaluation or insertion.

| Outcome | Count |
|---|---:|
| Active contexts with catalogue records | 26 / 26 |
| Explicit relation mentions | 2 |
| Candidate edge options | 3 |
| Candidate pairs wholly inside the active reference | 0 |
| Accepted graph mutations | 0 |
| AI-proposed relations | 0 |

This is an audited negative result for the active graph. It does not measure
recall or extraction accuracy because there are no benchmark-eligible pairs.

## Extracted spans

Catalogue row 102, context 104:

> Grasnarbe **über Kiesbett (103)**.

This produces pending option `103 -> 104`. Context 103 is outside the active
P19 reference.

Catalogue row 149, notation `(153) = (50)`:

> Steinpackung **in Einschnitt (154)**.

This produces pending options `154 -> 50` and `154 -> 153`. The two options
preserve the catalogue alias ambiguity rather than choosing an endpoint.
Context 154 is outside the active P19 reference.

## Method and boundary

The extractor uses two narrow phrase rules: `über ... (context)` and
`in Einschnitt (context)`. It stores the literal matched span, catalogue row,
notation, description, alias set, proposed direction, and scope status.

All outputs have status `pending_human_review`. A reviewer must confirm that a
phrase expresses stratigraphic rather than merely spatial containment, resolve
aliases, confirm older-to-younger direction, and establish out-of-scope
contexts through a separately reviewed source workflow. The accepted graph is
not modified.

## Reproduction

```powershell
python scripts/extract_trimmis_profile19_text_relations.py .local-data/trimmis-source
```

The generator verifies the source catalogue MD5 and binds the result to the
canonical SHA-256 of the active reference.

- [Machine-readable proposals](../data/trimmis_profile19_text_relation_proposals.json)
- [Active corrected reference](../data/trimmis_profile19_reference.json)
- [Project charter](PROJECT_CHARTER.md)