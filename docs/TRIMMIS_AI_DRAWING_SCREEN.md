# Trimmis Profile 19 AI-Assisted Drawing Screen

## Result

The authoritative `P19.pdf` is publicly available in Johannes Reich's
[Zenodo dataset](https://doi.org/10.5281/zenodo.4461075). The local source file
has MD5 `53ccf16a523e986ead69a30fc3f8dc24`, matching the checksum published by
Zenodo. The dataset is licensed CC BY 3.0.

On 18 September 2026, a multimodal AI assistant visually screened the 27
relations awaiting drawing review against high-resolution crops rendered from
that file:

| Result | Count |
|---|---:|
| Visually consistent | 23 |
| Indeterminate | 4 |
| Visibly contradicted | 0 |

The four indeterminate relations are `150 -> 153`, `155 -> 3`, `241 -> 3`,
and `3 -> 164`. Their labels occur across lateral discontinuities or around the
central interruption, where linework alone does not establish the relevant
contact semantics confidently.

## Interpretation boundary

This is an AI-assisted screen, not a qualified archaeological review. It does
not complete the public drawing-review checklist, change any relation status,
or mutate the accepted graph. The drawing does not machine-encode the semantic
difference between deposits, cuts, fills, boundaries, and label leaders.

The result is useful as triage: a future independent reviewer can begin with
the four indeterminate relations while retaining all 27 as formally pending.
Dr Johannes Reich will not be approached for further review.

The complete relation-level observations and limitations are recorded in
[`trimmis_profile19_ai_drawing_screen.json`](../data/trimmis_profile19_ai_drawing_screen.json).