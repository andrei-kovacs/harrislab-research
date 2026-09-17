"""Deterministic candidate extraction from stratigraphic catalogue text."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from typing import Any


_RELATION_PATTERNS = (
    (
        "over",
        re.compile(r"\büber\s+[^.;]*?\((?P<reference>\d+)\)", re.IGNORECASE),
        "A referenced deposit described below the subject may be earlier.",
    ),
    (
        "within_cut",
        re.compile(
            r"\bin\s+(?:einem\s+)?Einschnitt\s*\((?P<reference>\d+)\)",
            re.IGNORECASE,
        ),
        "A referenced cut containing the subject may be earlier than its fill.",
    ),
)


def extract_relation_candidates(
    catalog: Mapping[str, Mapping[str, Any]],
    active_context_ids: Iterable[str],
    accepted_relations: Iterable[tuple[str, str]] = (),
) -> list[dict[str, Any]]:
    """Return review-only edge candidates grounded in literal catalogue spans."""
    active_ids = {str(identifier) for identifier in active_context_ids}
    accepted_pairs = {(str(earlier), str(later)) for earlier, later in accepted_relations}
    rows: dict[int, dict[str, Any]] = {}

    for identifier, record in catalog.items():
        if str(identifier) not in active_ids:
            continue
        row = int(record["catalog_row"])
        description = str(record["description_de"])
        notation = str(record["catalog_notation"])
        if row in rows and (
            rows[row]["description_de"] != description
            or rows[row]["catalog_notation"] != notation
        ):
            raise ValueError(f"conflicting catalogue records for row {row}")
        entry = rows.setdefault(
            row,
            {
                "catalog_row": row,
                "catalog_notation": notation,
                "description_de": description,
                "subject_ids": [],
            },
        )
        entry["subject_ids"].append(str(identifier))

    candidates: list[dict[str, Any]] = []
    for row, record in sorted(rows.items()):
        description = record["description_de"]
        for rule, pattern, direction_basis in _RELATION_PATTERNS:
            for match in pattern.finditer(description):
                referenced_id = match.group("reference")
                for subject_id in sorted(record["subject_ids"], key=_identifier_key):
                    pair = (referenced_id, subject_id)
                    candidates.append(
                        {
                            "id": f"catalog-row-{row}-{rule}-{referenced_id}-{subject_id}",
                            "earlier": referenced_id,
                            "later": subject_id,
                            "status": "pending_human_review",
                            "rule": rule,
                            "direction_basis": direction_basis,
                            "scope_status": (
                                "active_reference_pair"
                                if referenced_id in active_ids
                                else "referenced_context_outside_active_reference"
                            ),
                            "already_in_accepted_graph": pair in accepted_pairs,
                            "source": {
                                "catalog_row": row,
                                "catalog_notation": record["catalog_notation"],
                                "description_de": description,
                                "matched_text": match.group(0),
                                "character_span": [match.start(), match.end()],
                                "subject_aliases": sorted(
                                    record["subject_ids"], key=_identifier_key
                                ),
                            },
                        }
                    )
    return candidates


def _identifier_key(identifier: str) -> tuple[int, int | str]:
    return (0, int(identifier)) if identifier.isdigit() else (1, identifier)