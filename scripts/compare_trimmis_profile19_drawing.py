"""Generate a provenance-safe comparison of P19 and the reviewed matrix graph."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import fitz

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harrislab.approval import file_sha256

PROFILE_MD5 = "53ccf16a523e986ead69a30fc3f8dc24"
SOURCE_DOI = "10.5281/zenodo.4461075"
PROFILE_CLIP = fitz.Rect(50, 165, 380, 315)


def generate_comparison(
    profile_path: Path,
    reference_path: Path,
    published_reference_path: Path,
    corrections_path: Path,
) -> dict[str, Any]:
    if _md5(profile_path) != PROFILE_MD5:
        raise ValueError("P19 source checksum mismatch")

    reference = _read_json(reference_path)
    published = _read_json(published_reference_path)
    corrections = _read_json(corrections_path)
    if corrections["base_sha256"] != file_sha256(published_reference_path):
        raise ValueError("correction manifest does not match published reference")

    context_ids = {context["id"] for context in reference["contexts"]}
    occurrences = _label_occurrences(profile_path, context_ids)
    observed_ids = {occurrence["id"] for occurrence in occurrences}
    if observed_ids != context_ids:
        missing = sorted(context_ids - observed_ids)
        unexpected = sorted(observed_ids - context_ids)
        raise ValueError(
            f"profile/reference label mismatch; missing={missing}, unexpected={unexpected}"
        )

    published_edges = {
        (relation["earlier"], relation["later"]): relation
        for relation in published["relations"]
    }
    active_edges = {
        (relation["earlier"], relation["later"]): relation
        for relation in reference["relations"]
    }
    removed_edges = {
        (item["earlier"], item["later"])
        for item in corrections["remove_relations"]
    }
    added_edges = {
        (item["earlier"], item["later"])
        for item in corrections["add_relations"]
    }
    if set(published_edges) - removed_edges | added_edges != set(active_edges):
        raise ValueError("active reference does not match declared correction edges")

    relations = []
    for edge in sorted(set(published_edges) | added_edges):
        if edge in removed_edges:
            status = "superseded_matrix_relation"
            basis = "Published matrix relation replaced by the confirmed P19 correction."
        elif edge in added_edges:
            status = "confirmed_profile_correction"
            basis = "Source-author confirmation associated with P19; private correspondence is not published."
        else:
            status = "awaiting_drawing_review"
            basis = "Reviewed matrix relation; P19 geometry has not been interpreted automatically."
        relations.append(
            {
                "earlier": edge[0],
                "later": edge[1],
                "status": status,
                "basis": basis,
            }
        )

    return {
        "schema": "harrislab.drawing-comparison.v1",
        "title": "Trimmis Profile 19 drawing comparison",
        "source": {
            "doi": SOURCE_DOI,
            "file": profile_path.name,
            "md5": PROFILE_MD5,
            "license": "CC-BY-3.0",
        },
        "reference": {
            "path": reference_path.name,
            "sha256": file_sha256(reference_path),
        },
        "published_matrix_reference": {
            "path": published_reference_path.name,
            "sha256": file_sha256(published_reference_path),
        },
        "correction_manifest": {
            "path": corrections_path.name,
            "sha256": file_sha256(corrections_path),
        },
        "method": {
            "label_extraction": "Digit-only PDF text tokens restricted to active reference context identifiers.",
            "relation_policy": "No relation is inferred from vertical position or vector proximity. P19 mixes deposit boundaries, cuts, fills, and label leaders without semantic tags.",
            "review_unit": "Each active matrix relation remains awaiting drawing review unless covered by the confirmed correction manifest.",
        },
        "summary": {
            "reference_contexts": len(context_ids),
            "contexts_present_in_profile": len(observed_ids),
            "label_occurrences": len(occurrences),
            "confirmed_profile_corrections": len(added_edges),
            "superseded_matrix_relations": len(removed_edges),
            "relations_awaiting_drawing_review": sum(
                relation["status"] == "awaiting_drawing_review"
                for relation in relations
            ),
            "ai_proposed_relations": 0,
        },
        "label_occurrences": occurrences,
        "relation_comparison": relations,
    }


def render_profile_crop(profile_path: Path, output_path: Path) -> None:
    with fitz.open(profile_path) as document:
        pixmap = document[0].get_pixmap(
            matrix=fitz.Matrix(4, 4),
            clip=PROFILE_CLIP,
            alpha=False,
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pixmap.save(output_path)


def _label_occurrences(
    profile_path: Path, context_ids: set[str]
) -> list[dict[str, Any]]:
    with fitz.open(profile_path) as document:
        page = document[0]
        occurrences = [
            {
                "id": word[4],
                "page": 1,
                "rectangle": [round(value, 3) for value in word[:4]],
            }
            for word in page.get_text("words")
            if word[4] in context_ids
        ]
    return sorted(
        occurrences,
        key=lambda item: (
            item["id"],
            item["rectangle"][1],
            item["rectangle"][0],
        ),
    )


def _md5(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_directory", type=Path)
    parser.add_argument(
        "--reference",
        type=Path,
        default=Path("data/trimmis_profile19_reference.json"),
    )
    parser.add_argument(
        "--published-reference",
        type=Path,
        default=Path("data/trimmis_profile19_published_reference.json"),
    )
    parser.add_argument(
        "--corrections",
        type=Path,
        default=Path("data/trimmis_profile19_corrections.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/trimmis_profile19_drawing_comparison.json"),
    )
    parser.add_argument(
        "--image",
        type=Path,
        default=Path("docs/trimmis_profile19_source_profile.png"),
    )
    arguments = parser.parse_args()
    profile_path = arguments.source_directory / "P19.pdf"
    result = generate_comparison(
        profile_path,
        arguments.reference,
        arguments.published_reference,
        arguments.corrections,
    )
    arguments.output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    render_profile_crop(profile_path, arguments.image)
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()