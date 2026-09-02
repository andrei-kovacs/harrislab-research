"""JSON input for reproducible stratigraphic datasets."""

import json
from pathlib import Path

from .model import (
    Context,
    Evidence,
    EvidenceKind,
    Relation,
    RelationStatus,
    Stratigraphy,
)


def load_stratigraphy(path: str | Path) -> Stratigraphy:
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    graph = Stratigraphy()

    for item in document.get("evidence", []):
        graph.add_evidence(
            Evidence(
                identifier=item["id"],
                kind=EvidenceKind(item["kind"]),
                description=item["description"],
                source=item["source"],
            )
        )
    for item in document["contexts"]:
        graph.add_context(Context(identifier=item["id"], label=item["label"]))
    for item in document["relations"]:
        graph.add_relation(
            Relation(
                earlier=item["earlier"],
                later=item["later"],
                status=RelationStatus(item.get("status", "observed")),
                evidence_ids=tuple(item.get("evidence_ids", [])),
            )
        )
    return graph
