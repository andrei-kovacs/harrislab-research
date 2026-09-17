"""Fail-closed review workflow for drawing evidence comparisons."""

from __future__ import annotations

import csv
import io
import json
from datetime import date
from pathlib import Path
from typing import Any

from .approval import file_sha256


REVIEW_DECISIONS = {
    "corroborated",
    "contradicted",
    "indeterminate",
    "not_visible",
}
NOTE_REQUIRED_DECISIONS = REVIEW_DECISIONS - {"corroborated"}
CSV_FIELDS = ("item_type", "item_key", "earlier", "later", "decision", "note", "value")


def create_drawing_review_template(
    comparison_path: str | Path,
) -> dict[str, Any]:
    comparison_file = Path(comparison_path)
    comparison = json.loads(comparison_file.read_text(encoding="utf-8"))
    pending = _pending_relations(comparison)
    return {
        "schema": "harrislab.drawing-evidence-review.v1",
        "comparison_sha256": file_sha256(comparison_file),
        "reviewer": {
            "public_label": "",
            "reviewed_at": "",
            "qualified_for_drawing_review": False,
            "independent_from_matrix_extraction": False,
        },
        "direction_confirmation": "pending",
        "relation_reviews": [
            {
                "earlier": relation["earlier"],
                "later": relation["later"],
                "decision": "pending",
                "note": "",
            }
            for relation in pending
        ],
        "publication_policy": (
            "Use a non-identifying public label. Keep names, affiliations, "
            "email addresses, and correspondence outside this artifact."
        ),
    }


def validate_drawing_review(
    comparison_path: str | Path,
    review_path: str | Path,
) -> dict[str, Any]:
    review = json.loads(Path(review_path).read_text(encoding="utf-8"))
    return validate_drawing_review_document(comparison_path, review)


def validate_drawing_review_document(
    comparison_path: str | Path,
    review: dict[str, Any],
) -> dict[str, Any]:
    comparison_file = Path(comparison_path)
    comparison = json.loads(comparison_file.read_text(encoding="utf-8"))
    if review.get("schema") != "harrislab.drawing-evidence-review.v1":
        raise ValueError("unsupported drawing review schema")
    if review.get("comparison_sha256") != file_sha256(comparison_file):
        raise ValueError("review does not match drawing comparison SHA-256")

    reviewer = review.get("reviewer", {})
    if not reviewer.get("public_label", "").strip():
        raise ValueError("non-identifying reviewer public label is required")
    if not reviewer.get("qualified_for_drawing_review"):
        raise ValueError("drawing-review qualification must be confirmed")
    if not reviewer.get("independent_from_matrix_extraction"):
        raise ValueError("reviewer independence must be confirmed")
    try:
        date.fromisoformat(reviewer.get("reviewed_at", ""))
    except (TypeError, ValueError) as error:
        raise ValueError("review date must use ISO format YYYY-MM-DD") from error
    if review.get("direction_confirmation") != "older_to_younger_confirmed":
        raise ValueError("older-to-younger direction must be confirmed")

    expected = {
        (relation["earlier"], relation["later"])
        for relation in _pending_relations(comparison)
    }
    relation_reviews = review.get("relation_reviews")
    if not isinstance(relation_reviews, list):
        raise ValueError("relation reviews are required")
    actual = [
        (item.get("earlier"), item.get("later"))
        for item in relation_reviews
        if isinstance(item, dict)
    ]
    if len(actual) != len(set(actual)):
        raise ValueError("duplicate drawing relation review")
    if set(actual) != expected:
        raise ValueError("drawing relation reviews do not match comparison")

    counts = {decision: 0 for decision in sorted(REVIEW_DECISIONS)}
    for item in relation_reviews:
        decision = item.get("decision")
        edge = f"{item.get('earlier')} -> {item.get('later')}"
        if decision not in REVIEW_DECISIONS:
            raise ValueError(f"invalid or pending decision for {edge}")
        if decision in NOTE_REQUIRED_DECISIONS and not item.get("note", "").strip():
            raise ValueError(f"review note is required for {edge}")
        counts[decision] += 1

    return {
        "schema": "harrislab.drawing-evidence-review-summary.v1",
        "comparison_sha256": review["comparison_sha256"],
        "reviewer": reviewer,
        "direction_confirmation": review["direction_confirmation"],
        "relation_count": len(relation_reviews),
        "decision_counts": counts,
        "relation_reviews": relation_reviews,
        "accepted_graph_mutations": [],
        "interpretation_limit": (
            "This summary classifies drawing evidence only. It does not alter "
            "the accepted graph or promote a relation to observed status."
        ),
    }


def drawing_review_csv(template: dict[str, Any]) -> str:
    """Render a drawing-review template as an editable CSV checklist."""
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    metadata = {
        "comparison_sha256": template["comparison_sha256"],
        "public_label": template["reviewer"]["public_label"],
        "reviewed_at": template["reviewer"]["reviewed_at"],
        "qualified_for_drawing_review": "false",
        "independent_from_matrix_extraction": "false",
        "direction_confirmation": template["direction_confirmation"],
    }
    for key, value in metadata.items():
        writer.writerow({"item_type": "metadata", "item_key": key, "value": value})
    for item in template["relation_reviews"]:
        writer.writerow(
            {
                "item_type": "relation",
                "earlier": item["earlier"],
                "later": item["later"],
                "decision": item["decision"],
                "note": item["note"],
            }
        )
    return output.getvalue()


def drawing_review_from_csv(csv_path: str | Path) -> dict[str, Any]:
    """Parse an editable checklist into the canonical review document."""
    with Path(csv_path).open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if tuple(reader.fieldnames or ()) != CSV_FIELDS:
            raise ValueError("drawing review CSV headers do not match template")
        rows = list(reader)

    metadata: dict[str, str] = {}
    relation_reviews = []
    for row in rows:
        if row["item_type"] == "metadata":
            key = row["item_key"]
            if not key or key in metadata:
                raise ValueError("duplicate or empty drawing review metadata key")
            metadata[key] = row["value"].strip()
        elif row["item_type"] == "relation":
            relation_reviews.append(
                {
                    "earlier": row["earlier"].strip(),
                    "later": row["later"].strip(),
                    "decision": row["decision"].strip(),
                    "note": row["note"].strip(),
                }
            )
        else:
            raise ValueError(f"unsupported drawing review CSV row: {row['item_type']}")

    required_metadata = {
        "comparison_sha256",
        "public_label",
        "reviewed_at",
        "qualified_for_drawing_review",
        "independent_from_matrix_extraction",
        "direction_confirmation",
    }
    if set(metadata) != required_metadata:
        raise ValueError("drawing review CSV metadata is incomplete")
    return {
        "schema": "harrislab.drawing-evidence-review.v1",
        "comparison_sha256": metadata["comparison_sha256"],
        "reviewer": {
            "public_label": metadata["public_label"],
            "reviewed_at": metadata["reviewed_at"],
            "qualified_for_drawing_review": _csv_boolean(
                metadata["qualified_for_drawing_review"]
            ),
            "independent_from_matrix_extraction": _csv_boolean(
                metadata["independent_from_matrix_extraction"]
            ),
        },
        "direction_confirmation": metadata["direction_confirmation"],
        "relation_reviews": relation_reviews,
        "publication_policy": (
            "Use a non-identifying public label. Keep names, affiliations, "
            "email addresses, and correspondence outside this artifact."
        ),
    }


def _pending_relations(comparison: dict[str, Any]) -> list[dict[str, Any]]:
    if comparison.get("schema") != "harrislab.drawing-comparison.v1":
        raise ValueError("unsupported drawing comparison schema")
    pending = [
        relation
        for relation in comparison.get("relation_comparison", [])
        if relation.get("status") == "awaiting_drawing_review"
    ]
    if len(pending) != comparison.get("summary", {}).get(
        "relations_awaiting_drawing_review"
    ):
        raise ValueError("drawing comparison pending count is inconsistent")
    return sorted(pending, key=lambda item: (item["earlier"], item["later"]))


def _csv_boolean(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized not in {"true", "false"}:
        raise ValueError("drawing review CSV booleans must be true or false")
    return normalized == "true"