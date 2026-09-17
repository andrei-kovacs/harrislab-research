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
        "schema": "harrislab.reference.v1",
        "title": "Trimmis Profile 19 approved reference graph",
        "description": (
            "Independently reviewed extraction from the published synoptic Harris matrix."
        ),
        "license": source["license"],
        "source_doi": source["doi"],
        "evidence": evidence,
        "contexts": [
            {
                "id": node["id"],
                "label": node["description_de"],
                "catalog_row": node["catalog_row"],
                "catalog_notation": node["catalog_notation"],
                "matrix_page": node["matrix_page"],
                "matrix_rectangle": node["matrix_rectangle"],
                "printed_label": node["printed_label"],
            }
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


def apply_confirmed_corrections(
    reference_path: str | Path, corrections_path: str | Path
) -> dict[str, Any]:
    reference_file = Path(reference_path)
    reference = json.loads(reference_file.read_text(encoding="utf-8"))
    corrections = json.loads(Path(corrections_path).read_text(encoding="utf-8"))
    if corrections.get("base_sha256") != file_sha256(reference_file):
        raise ValueError("corrections do not match reference SHA-256")
    if corrections.get("status") != "confirmed":
        raise ValueError("corrections must be confirmed")

    contexts = {context["id"]: context for context in reference["contexts"]}
    for context in corrections.get("add_contexts", []):
        if context["id"] in contexts:
            raise ValueError(f"duplicate corrected context: {context['id']}")
        contexts[context["id"]] = context

    relations = list(reference["relations"])
    for removal in corrections.get("remove_relations", []):
        matches = [
            relation
            for relation in relations
            if relation["earlier"] == removal["earlier"]
            and relation["later"] == removal["later"]
        ]
        if len(matches) != 1:
            raise ValueError(
                "corrected relation removal must match exactly once: "
                f"{removal['earlier']} -> {removal['later']}"
            )
        relations.remove(matches[0])

    evidence = list(reference.get("evidence", []))
    correction_evidence = corrections["evidence"]
    if any(item["id"] == correction_evidence["id"] for item in evidence):
        raise ValueError(f"duplicate correction evidence: {correction_evidence['id']}")
    evidence.append(correction_evidence)

    for addition in corrections.get("add_relations", []):
        relation = {
            **addition,
            "status": addition.get("status", "observed"),
            "evidence_ids": [correction_evidence["id"]],
        }
        relations.append(relation)

    _validate_corrected_graph(contexts, relations, evidence)
    return {
        **reference,
        "schema": "harrislab.corrected-reference.v1",
        "title": corrections["title"],
        "description": corrections["description"],
        "evidence": evidence,
        "contexts": sorted(contexts.values(), key=lambda context: context["id"]),
        "relations": sorted(
            relations,
            key=lambda relation: (relation["earlier"], relation["later"]),
        ),
        "correction": {
            "manifest_sha256": file_sha256(corrections_path),
            "status": corrections["status"],
            "reviewed_at": corrections["reviewed_at"],
            "summary": corrections["summary"],
        },
    }


def _validate_corrected_graph(
    contexts: dict[str, dict[str, Any]],
    relations: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> None:
    evidence_ids = {item["id"] for item in evidence}
    relation_pairs: set[tuple[str, str]] = set()
    adjacency = {identifier: set() for identifier in contexts}
    indegree = {identifier: 0 for identifier in contexts}
    for relation in relations:
        earlier, later = relation["earlier"], relation["later"]
        if earlier not in contexts or later not in contexts:
            raise ValueError(f"corrected relation references unknown context: {earlier} -> {later}")
        pair = (earlier, later)
        if pair in relation_pairs:
            raise ValueError(f"duplicate corrected relation: {earlier} -> {later}")
        relation_pairs.add(pair)
        unknown_evidence = set(relation.get("evidence_ids", [])) - evidence_ids
        if unknown_evidence:
            raise ValueError(
                "corrected relation references unknown evidence: "
                f"{', '.join(sorted(unknown_evidence))}"
            )
        adjacency[earlier].add(later)
        indegree[later] += 1

    available = [identifier for identifier, degree in indegree.items() if degree == 0]
    visited = 0
    while available:
        identifier = available.pop()
        visited += 1
        for later in adjacency[identifier]:
            indegree[later] -= 1
            if indegree[later] == 0:
                available.append(later)
    if visited != len(contexts):
        raise ValueError("confirmed corrections introduce a chronological cycle")


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