"""Fail-closed approval of source-derived stratigraphic graph candidates."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


def file_sha256(path: str | Path) -> str:
    content = json.loads(Path(path).read_text(encoding="utf-8"))
    canonical = json.dumps(
        content,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def create_review_template(candidate_path: str | Path) -> dict[str, Any]:
    path = Path(candidate_path)
    candidate = json.loads(path.read_text(encoding="utf-8"))
    return {
        "schema": "harrislab.independent-review.v1",
        "candidate_sha256": file_sha256(path),
        "reviewer": {
            "name": "",
            "affiliation": "",
            "reviewed_at": "",
            "independent_from_extraction": False,
        },
        "direction_confirmation": "pending",
        "node_reviews": [
            {"id": node["id"], "status": "pending", "note": ""}
            for node in candidate["nodes"]
        ],
        "edge_reviews": [
            {"id": edge["id"], "status": "pending", "note": ""}
            for edge in candidate["edges"]
        ],
    }


def approve_candidate(
    candidate_path: str | Path, review_path: str | Path
) -> dict[str, Any]:
    candidate_file = Path(candidate_path)
    candidate = json.loads(candidate_file.read_text(encoding="utf-8"))
    review = json.loads(Path(review_path).read_text(encoding="utf-8"))
    if review.get("candidate_sha256") != file_sha256(candidate_file):
        raise ValueError("review does not match candidate SHA-256")

    reviewer = review.get("reviewer", {})
    if not reviewer.get("name", "").strip():
        raise ValueError("reviewer name is required")
    if not reviewer.get("independent_from_extraction"):
        raise ValueError("reviewer independence must be confirmed")
    try:
        date.fromisoformat(reviewer.get("reviewed_at", ""))
    except ValueError as error:
        raise ValueError("review date must use ISO format YYYY-MM-DD") from error
    if review.get("direction_confirmation") != "pass":
        raise ValueError("older-to-younger direction is not approved")

    _require_complete_reviews(
        "node", {node["id"] for node in candidate["nodes"]}, review.get("node_reviews")
    )
    _require_complete_reviews(
        "edge", {edge["id"] for edge in candidate["edges"]}, review.get("edge_reviews")
    )

    source = candidate["source"]
    evidence = [
        {
            "id": "trimmis-catalog",
            "kind": "context_sheet",
            "description": "Trimmis position catalog used for context labels",
            "source": f"https://doi.org/{source['doi']}#{source['catalog_file']}",
        },
        {
            "id": "trimmis-matrix",
            "kind": "drawing",
            "description": "Published synoptic Harris matrix for extracted relations",
            "source": f"https://doi.org/{source['doi']}#{source['matrix_file']}",
        },
        {
            "id": "trimmis-p19",
            "kind": "drawing",
            "description": "Profile P19 source drawing used for identifier comparison",
            "source": f"https://doi.org/{source['doi']}#{source['profile_file']}",
        },
    ]
    return {
        "title": "Trimmis Profile 19 approved reference graph",
        "description": (
            "Independently reviewed extraction from the published synoptic Harris matrix."
        ),
        "license": source["license"],
        "source_doi": source["doi"],
        "evidence": evidence,
        "contexts": [
            {"id": node["id"], "label": node["description_de"]}
            for node in candidate["nodes"]
        ],
        "relations": [
            {
                "earlier": edge["earlier"],
                "later": edge["later"],
                "status": "observed",
                "evidence_ids": ["trimmis-matrix"],
                "source_pdf_path_index": edge["pdf_path_index"],
            }
            for edge in candidate["edges"]
        ],
        "approval": {
            "candidate_sha256": review["candidate_sha256"],
            "reviewer": reviewer,
            "direction_confirmation": "older_to_younger",
            "profile_only_labels": candidate["source_profile_comparison"][
                "profile_only_labels"
            ],
        },
    }


def _require_complete_reviews(
    item_type: str, expected_ids: set[str], reviews: object
) -> None:
    if not isinstance(reviews, list):
        raise ValueError(f"{item_type} reviews are required")
    review_ids = [review.get("id") for review in reviews if isinstance(review, dict)]
    if len(review_ids) != len(set(review_ids)):
        raise ValueError(f"duplicate {item_type} review")
    if set(review_ids) != expected_ids:
        raise ValueError(f"{item_type} reviews do not match candidate")
    failed = [
        review["id"]
        for review in reviews
        if review.get("status") != "pass"
    ]
    if failed:
        raise ValueError(
            f"{item_type} reviews are not all approved: {', '.join(sorted(failed))}"
        )