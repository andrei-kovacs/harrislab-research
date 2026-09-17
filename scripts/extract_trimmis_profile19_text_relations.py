"""Generate pending relation proposals from Trimmis Profile 19 catalogue text."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harrislab.approval import file_sha256
from harrislab.text_extraction import extract_relation_candidates
from scripts.extract_trimmis_profile19 import (
    CATALOG_MD5,
    SOURCE_DOI,
    _catalog_records,
    _verify_source,
)


def generate_pilot(catalog_path: Path, reference_path: Path) -> dict[str, Any]:
    _verify_source(catalog_path, CATALOG_MD5)
    reference = json.loads(reference_path.read_text(encoding="utf-8"))
    context_ids = {context["id"] for context in reference["contexts"]}
    accepted_relations = {
        (relation["earlier"], relation["later"])
        for relation in reference["relations"]
    }
    catalog = _catalog_records(catalog_path)
    missing_contexts = sorted(context_ids - set(catalog), key=_identifier_key)
    if missing_contexts:
        raise ValueError(f"active contexts missing from catalogue: {missing_contexts}")

    candidates = extract_relation_candidates(
        catalog,
        context_ids,
        accepted_relations,
    )
    mention_keys = {
        (
            candidate["source"]["catalog_row"],
            *candidate["source"]["character_span"],
        )
        for candidate in candidates
    }
    active_pair_count = sum(
        candidate["scope_status"] == "active_reference_pair"
        for candidate in candidates
    )
    return {
        "schema": "harrislab.text-relation-proposals.v1",
        "title": "Trimmis Profile 19 catalogue relation proposals",
        "source": {
            "doi": SOURCE_DOI,
            "file": catalog_path.name,
            "md5": CATALOG_MD5,
            "license": "CC-BY-3.0",
        },
        "reference": {
            "path": reference_path.name,
            "sha256": file_sha256(reference_path),
        },
        "method": {
            "scope": "Descriptions attached to active Profile 19 context identifiers.",
            "rules": [
                {
                    "id": "over",
                    "phrase": "subject über referenced context",
                    "candidate_direction": "referenced context -> subject",
                },
                {
                    "id": "within_cut",
                    "phrase": "subject in Einschnitt (referenced context)",
                    "candidate_direction": "referenced cut -> subject",
                },
            ],
            "policy": "Rules surface literal mentions for human review; they do not accept relations or modify the reference graph.",
        },
        "summary": {
            "active_reference_contexts": len(context_ids),
            "contexts_with_catalog_records": len(context_ids) - len(missing_contexts),
            "explicit_relation_mentions": len(mention_keys),
            "proposed_relation_options": len(candidates),
            "active_reference_pair_proposals": active_pair_count,
            "out_of_scope_context_proposals": len(candidates) - active_pair_count,
            "already_in_accepted_graph": sum(
                candidate["already_in_accepted_graph"]
                for candidate in candidates
            ),
            "accepted_graph_mutations": 0,
            "ai_proposed_relations": 0,
        },
        "review_requirements": [
            "Confirm that the matched phrase expresses stratigraphic rather than spatial containment.",
            "Resolve catalogue aliases before selecting a graph endpoint.",
            "Confirm older-to-younger direction.",
            "Add out-of-scope contexts through a separately reviewed source workflow.",
        ],
        "candidates": candidates,
        "accepted_graph_mutations": [],
    }


def _identifier_key(identifier: str) -> tuple[int, int | str]:
    return (0, int(identifier)) if identifier.isdigit() else (1, identifier)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_directory", type=Path)
    parser.add_argument(
        "--reference",
        type=Path,
        default=Path("data/trimmis_profile19_reference.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/trimmis_profile19_text_relation_proposals.json"),
    )
    arguments = parser.parse_args()
    result = generate_pilot(
        arguments.source_directory / "Katalog_Positionen.xlsx",
        arguments.reference,
    )
    arguments.output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()