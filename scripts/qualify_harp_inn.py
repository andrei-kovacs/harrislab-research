"""Qualify and import the ADS Harp Inn Group 1 Harris-matrix component."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DOI = "10.5284/1133013"
COLLECTION_VERSION = "1"
LICENSE = "Open Government Licence"
METADATA_URL = (
    "https://archaeologydataservice.ac.uk/archives/collections/"
    "view/1005042/metadata.cfm"
)
SOURCE_NAME = "1C20HINAR_harris_matrix_phase_1_phase_2.csv"
SOURCE_URL = (
    "https://archaeologydataservice.ac.uk/catalogue/adsdata/arch-5042-1/"
    f"dissemination/1C20HINAR_Harris_Matrix_CSVs/{SOURCE_NAME}"
)
SOURCE_SHA256 = "d754dfb14250dc66b2741c4d65d6cb08ef376775e4903bdbdc4554d00a948467"
EXPECTED_NODE_HASH = "560782b7d88d23d0f5cca72539cf28bf6815f1c04b5d46a0e9f3f99c79910394"
EXPECTED_PRECEDENCE_HASH = "44a59ec95109b06157ebfeda7f08dbfa5400dcb823f9397d3c0983a3de4edb1b"
EXPECTED_CONTEMPORARY_HASH = "7a1fc51fce2d944f5dc23c7b27087b920c8b2109e3fb90abdae8ee897fdf5524"
EXCLUDED_IDS = {"1000", "1001", "G", "T", "U"}


def _normalize(value: str) -> str:
    return " ".join(value.split())


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _open(url: str):
    request = Request(url, headers={"User-Agent": "HarrisLab/0.2 dataset screen"})
    last_error: HTTPError | URLError | None = None
    for _ in range(3):
        try:
            return urlopen(request, timeout=60)
        except (HTTPError, URLError) as error:
            last_error = error
    assert last_error is not None
    raise last_error


def _download(url: str, destination: Path) -> None:
    with _open(url) as response:
        destination.write_bytes(response.read())


def _parse(path: Path) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]], dict[str, set[str]]]:
    units: dict[str, dict[str, Any]] = {}
    relations: list[dict[str, Any]] = []
    parents: dict[str, set[str]] = defaultdict(set)
    header: list[str] = []
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        for record_number, row in enumerate(csv.reader(source, delimiter=";"), 1):
            if not row:
                continue
            tag = _normalize(row[0]).upper()
            if tag == "HEADER":
                header = [_normalize(field).upper() for field in row[1:]]
                continue
            record = {
                field: row[index + 1] if index + 1 < len(row) else ""
                for index, field in enumerate(header)
            }
            if tag == "UNIT" and "ID" in record:
                identifier = _normalize(record["ID"])
                if identifier in units:
                    raise ValueError(f"duplicate normalized context identifier: {identifier}")
                units[identifier] = {
                    "id": identifier,
                    "type": _normalize(record.get("TYPE", "")).upper(),
                    "name": _normalize(record.get("NAME", "")),
                    "description": _normalize(record.get("DESCRIPTION", "")),
                    "source_row": record_number,
                }
            elif tag == "RELATION" and "SOURCE" in record:
                relations.append(
                    {
                        "type": _normalize(record.get("TYPE", "")).upper(),
                        "source": _normalize(record["SOURCE"]),
                        "target": _normalize(record.get("TARGET", "")),
                        "source_row": record_number,
                    }
                )
            elif tag == "HIERARCHY" and "PARENT" in record:
                parents[_normalize(record.get("CHILD", ""))].add(
                    _normalize(record["PARENT"])
                )
    return units, relations, parents


def _components(nodes: set[str], edges: set[tuple[str, str]]) -> list[set[str]]:
    adjacency = {node: set() for node in nodes}
    for left, right in edges:
        if left in adjacency and right in adjacency:
            adjacency[left].add(right)
            adjacency[right].add(left)
    result = []
    unseen = set(nodes)
    while unseen:
        pending = [min(unseen)]
        unseen.remove(pending[0])
        component = set()
        while pending:
            node = pending.pop()
            component.add(node)
            for neighbor in adjacency[node] & unseen:
                unseen.remove(neighbor)
                pending.append(neighbor)
        result.append(component)
    return sorted(result, key=lambda item: (-len(item), sorted(item)))


def _is_dag(nodes: set[str], edges: set[tuple[str, str]]) -> bool:
    adjacency = {node: set() for node in nodes}
    indegree = {node: 0 for node in nodes}
    for earlier, later in edges:
        if earlier == later:
            return False
        if later not in adjacency[earlier]:
            adjacency[earlier].add(later)
            indegree[later] += 1
    pending = [node for node, degree in indegree.items() if degree == 0]
    visited = 0
    while pending:
        node = pending.pop()
        visited += 1
        for later in adjacency[node]:
            indegree[later] -= 1
            if indegree[later] == 0:
                pending.append(later)
    return visited == len(nodes)


def import_group1(path: Path) -> dict[str, Any]:
    if _sha256(path) != SOURCE_SHA256:
        raise ValueError(f"checksum mismatch for {SOURCE_NAME}: {_sha256(path)}")
    units, source_relations, parents = _parse(path)
    group_nodes = {
        identifier
        for identifier, unit in units.items()
        if unit["type"] in {"SURFACE", "DEPOSIT"}
        and identifier not in EXCLUDED_IDS
        and not identifier.startswith("Matrix")
        and "Group 1" in parents[identifier]
    }
    precedence_rows: dict[tuple[str, str], dict[str, Any]] = {}
    contemporary_rows: dict[tuple[str, str], dict[str, Any]] = {}
    for relation in source_relations:
        source = relation["source"]
        target = relation["target"]
        if source not in group_nodes or target not in group_nodes:
            continue
        if relation["type"] in {"ABOVE", "LATER"}:
            precedence_rows[(target, source)] = relation
        elif relation["type"] == "CONTEMPORARY":
            contemporary_rows[tuple(sorted((source, target)))] = relation

    components = _components(
        group_nodes,
        set(precedence_rows) | set(contemporary_rows),
    )
    eligible = [component for component in components if 20 <= len(component) <= 100]
    if not eligible:
        raise ValueError("no relation-connected Group 1 component has 20-100 contexts")
    selected = eligible[0]
    precedence_rows = {
        edge: row
        for edge, row in precedence_rows.items()
        if edge[0] in selected and edge[1] in selected
    }
    contemporary_rows = {
        edge: row
        for edge, row in contemporary_rows.items()
        if edge[0] in selected and edge[1] in selected
    }
    node_records = [units[identifier] for identifier in sorted(selected)]
    precedence_edges = sorted(precedence_rows)
    contemporary_edges = sorted(contemporary_rows)
    checks = {
        "context_count": len(selected),
        "precedence_relation_count": len(precedence_edges),
        "contemporary_relation_count": len(contemporary_edges),
        "node_records_sha256": _canonical_hash(node_records),
        "precedence_edges_sha256": _canonical_hash(precedence_edges),
        "contemporary_edges_sha256": _canonical_hash(contemporary_edges),
    }
    expected = {
        "context_count": 36,
        "precedence_relation_count": 26,
        "contemporary_relation_count": 10,
        "node_records_sha256": EXPECTED_NODE_HASH,
        "precedence_edges_sha256": EXPECTED_PRECEDENCE_HASH,
        "contemporary_edges_sha256": EXPECTED_CONTEMPORARY_HASH,
    }
    if checks != expected:
        raise ValueError(f"selected component does not match frozen reference: {checks}")
    if not _is_dag(selected, set(precedence_edges)):
        raise ValueError("selected precedence relations contain a cycle")

    evidence = []
    relations = []
    for earlier, later in precedence_edges:
        source_row = precedence_rows[(earlier, later)]["source_row"]
        evidence_id = f"harp-inn-relation-record-{source_row}"
        evidence.append(
            {
                "id": evidence_id,
                "kind": "other",
                "description": f"Explicit ADS Harris-matrix relation at CSV record {source_row}",
                "source": f"{SOURCE_URL}#record={source_row}",
            }
        )
        relations.append(
            {
                "earlier": earlier,
                "later": later,
                "status": "observed",
                "evidence_ids": [evidence_id],
                "source_relation": precedence_rows[(earlier, later)]["type"],
                "source_record": source_row,
            }
        )

    contexts = []
    for item in node_records:
        label = item["name"]
        if item["description"] and item["description"] != item["name"]:
            label = f"{label}: {item['description']}" if label else item["description"]
        contexts.append(
            {
                "id": item["id"],
                "label": label,
                "source_type": item["type"],
                "source_name": item["name"],
                "source_description": item["description"],
                "source_record": item["source_row"],
            }
        )

    typed_relations = [
        {
            "type": "contemporary",
            "contexts": list(edge),
            "status": "observed_typed_non_precedence",
            "source_record": contemporary_rows[edge]["source_row"],
        }
        for edge in contemporary_edges
    ]
    return {
        "schema": "harrislab.reference.v1",
        "dataset": {
            "title": "Data from Archaeological Recording Work at Harp Inn",
            "doi": DOI,
            "version": COLLECTION_VERSION,
            "license": LICENSE,
            "source_file": SOURCE_NAME,
            "source_url": SOURCE_URL,
            "source_sha256": SOURCE_SHA256,
            "selection": "Largest 20-100-context component in Group 1 connected by explicit ABOVE, LATER, or CONTEMPORARY relations",
            "direction_mapping": "ABOVE/LATER(source,target) -> target earlier, source later",
            "excluded_from_connectivity": sorted(EXCLUDED_IDS) + ["Matrix*", "hierarchy", "layer"],
        },
        "qualification": checks | {"precedence_is_dag": True},
        "contexts": contexts,
        "evidence": evidence,
        "relations": relations,
        "typed_relations": typed_relations,
        "authority": {
            "accepted_precedence_source": "explicit ADS ABOVE/LATER records only",
            "contemporary_treatment": "preserved as typed source evidence; not added to the precedence DAG",
            "accepted_graph_mutations_from_ai": 0,
        },
    }


def qualify(destination: Path) -> dict[str, Any]:
    destination.mkdir(parents=True, exist_ok=True)
    metadata_path = destination / "metadata.html"
    source_path = destination / SOURCE_NAME
    _download(METADATA_URL, metadata_path)
    metadata = metadata_path.read_text(encoding="utf-8", errors="replace")
    required_metadata = (DOI, "Version", COLLECTION_VERSION, LICENSE)
    missing = [value for value in required_metadata if value not in metadata]
    if missing:
        raise ValueError(f"ADS metadata is missing required value(s): {', '.join(missing)}")
    _download(SOURCE_URL, source_path)
    document = import_group1(source_path)
    document["retrieval"] = {
        "metadata_url": METADATA_URL,
        "metadata_sha256": _sha256(metadata_path),
        "source_sha256": _sha256(source_path),
    }
    return document


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/harp_inn_group1_reference.json"),
    )
    arguments = parser.parse_args()
    document = qualify(arguments.destination)
    arguments.output.write_text(
        json.dumps(document, indent=2, ensure_ascii=True) + "\n",
        encoding="ascii",
    )
    print(
        f"Qualified {len(document['contexts'])} contexts and "
        f"{len(document['relations'])} precedence relations into {arguments.output}"
    )


if __name__ == "__main__":
    main()