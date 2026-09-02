"""Extract an auditable Profile 19 graph candidate from the Trimmis matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any
from xml.etree import ElementTree
from zipfile import ZipFile

import fitz

MATRIX_MD5 = "9ece18c188763350f16e164f441a927e"
CATALOG_MD5 = "75983db690194fb562ba0378ebd627a3"
PROFILE_MD5 = "53ccf16a523e986ead69a30fc3f8dc24"
SOURCE_DOI = "10.5281/zenodo.4461075"
PROFILE_BOUNDARY_X = 941.62
PROFILE_RIGHT_X = 1060.0
NODE_TOP_Y = 40.0
NODE_BOTTOM_Y = 790.0
ENDPOINT_TOLERANCE = 0.35
SPREADSHEET_NS = {
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "relationships": (
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    ),
}
GLYPH_LABEL_FIXES = {"532": "235", "042": "240"}


def _md5(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _verify_source(path: Path, expected_md5: str) -> None:
    actual_md5 = _md5(path)
    if actual_md5 != expected_md5:
        raise ValueError(f"checksum mismatch for {path.name}: {actual_md5}")


def _catalog_records(path: Path) -> dict[str, dict[str, Any]]:
    with ZipFile(path) as archive:
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
            shared_strings = [
                "".join(item.itertext())
                for item in root.findall("main:si", SPREADSHEET_NS)
            ]
        worksheet = ElementTree.fromstring(
            archive.read("xl/worksheets/sheet1.xml")
        )
        records: dict[str, dict[str, Any]] = {}
        for row in worksheet.findall(
            ".//main:sheetData/main:row", SPREADSHEET_NS
        ):
            values: list[str] = []
            for cell in row.findall("main:c", SPREADSHEET_NS):
                value = cell.find("main:v", SPREADSHEET_NS)
                text = "" if value is None else value.text or ""
                if cell.attrib.get("t") == "s" and text:
                    text = shared_strings[int(text)]
                values.append(text)
            if len(values) < 2:
                continue
            for identifier in re.findall(r"\(([^)]+)\)", values[0]):
                normalized = identifier.replace("_", "")
                records[normalized] = {
                    "catalog_row": int(row.attrib["r"]),
                    "catalog_notation": values[0],
                    "description_de": values[1],
                }
    return records


def _overlap_ratio(left: fitz.Rect, right: fitz.Rect) -> float:
    overlap = left & right
    if overlap.is_empty:
        return 0.0
    return overlap.get_area() / min(left.get_area(), right.get_area())


def _node_rectangles(page: fitz.Page) -> list[fitz.Rect]:
    candidates: list[fitz.Rect] = []
    for drawing in page.get_drawings():
        for item in drawing["items"]:
            if item[0] != "re":
                continue
            rectangle = item[1]
            if not (
                rectangle.x0 >= PROFILE_BOUNDARY_X
                and rectangle.x1 <= PROFILE_RIGHT_X
                and rectangle.y0 >= NODE_TOP_Y
                and rectangle.y1 <= NODE_BOTTOM_Y
                and 8 < rectangle.height < 11
                and rectangle.width > 15
            ):
                continue
            candidates.append(rectangle)

    clusters: list[list[fitz.Rect]] = []
    for rectangle in candidates:
        for cluster in clusters:
            if _overlap_ratio(rectangle, cluster[0]) >= 0.9:
                cluster.append(rectangle)
                break
        else:
            clusters.append([rectangle])
    return [min(cluster, key=lambda rectangle: rectangle.get_area()) for cluster in clusters]


def _label_for_rectangle(page: fitz.Page, rectangle: fitz.Rect) -> str:
    glyphs: list[str] = []
    for word in page.get_text("words"):
        word_rectangle = fitz.Rect(word[:4])
        overlap = word_rectangle & rectangle
        if (
            not overlap.is_empty
            and overlap.get_area() >= 0.3 * word_rectangle.get_area()
        ):
            glyphs.append(word[4])
    raw_label = "".join(glyphs)
    return GLYPH_LABEL_FIXES.get(raw_label, raw_label)


def _on_boundary(point: fitz.Point, rectangle: fitz.Rect) -> bool:
    on_vertical = (
        rectangle.y0 - ENDPOINT_TOLERANCE
        <= point.y
        <= rectangle.y1 + ENDPOINT_TOLERANCE
        and min(abs(point.x - rectangle.x0), abs(point.x - rectangle.x1))
        <= ENDPOINT_TOLERANCE
    )
    on_horizontal = (
        rectangle.x0 - ENDPOINT_TOLERANCE
        <= point.x
        <= rectangle.x1 + ENDPOINT_TOLERANCE
        and min(abs(point.y - rectangle.y0), abs(point.y - rectangle.y1))
        <= ENDPOINT_TOLERANCE
    )
    return on_vertical or on_horizontal


def _point(point: fitz.Point) -> list[float]:
    return [round(point.x, 3), round(point.y, 3)]


def _would_cycle(nodes: set[str], edges: list[tuple[str, str]]) -> bool:
    adjacency = {node: set() for node in nodes}
    indegree = {node: 0 for node in nodes}
    for earlier, later in edges:
        if later not in adjacency[earlier]:
            adjacency[earlier].add(later)
            indegree[later] += 1
    available = [node for node, degree in indegree.items() if degree == 0]
    visited = 0
    while available:
        node = available.pop()
        visited += 1
        for later in adjacency[node]:
            indegree[later] -= 1
            if indegree[later] == 0:
                available.append(later)
    return visited != len(nodes)


def _profile_labels(path: Path, catalog: dict[str, dict[str, Any]]) -> set[str]:
    with fitz.open(path) as document:
        return {
            word[4]
            for page in document
            for word in page.get_text("words")
            if word[4].isdigit() and word[4] in catalog
        }


def extract(
    matrix_path: Path, catalog_path: Path, profile_path: Path
) -> dict[str, Any]:
    _verify_source(matrix_path, MATRIX_MD5)
    _verify_source(catalog_path, CATALOG_MD5)
    _verify_source(profile_path, PROFILE_MD5)
    catalog = _catalog_records(catalog_path)
    profile_labels = _profile_labels(profile_path, catalog)

    with fitz.open(matrix_path) as document:
        if document.page_count != 1:
            raise ValueError("expected a one-page Harris matrix")
        page = document[0]
        nodes: dict[str, dict[str, Any]] = {}
        rectangles: dict[str, fitz.Rect] = {}
        for rectangle in _node_rectangles(page):
            label = _label_for_rectangle(page, rectangle)
            if not label:
                raise ValueError(f"unlabelled node rectangle: {rectangle}")
            if label in nodes:
                raise ValueError(f"duplicate node label: {label}")
            if label not in catalog:
                raise ValueError(f"node label missing from catalog: {label}")
            rectangles[label] = rectangle
            nodes[label] = {
                "id": label,
                "printed_label": label,
                "matrix_page": 1,
                "matrix_rectangle": [round(value, 3) for value in rectangle],
                **catalog[label],
                "audit_status": "pending_visual_review",
            }

        edges: list[dict[str, Any]] = []
        endpoint_failures: list[dict[str, Any]] = []
        for path_index, drawing in enumerate(page.get_drawings()):
            if drawing.get("fill") is not None or drawing.get("dashes") != "[] 0":
                continue
            segments = [item for item in drawing["items"] if item[0] == "l"]
            if not segments:
                continue
            start, end = segments[0][1], segments[-1][2]
            start_labels = [
                label
                for label, rectangle in rectangles.items()
                if _on_boundary(start, rectangle)
            ]
            end_labels = [
                label
                for label, rectangle in rectangles.items()
                if _on_boundary(end, rectangle)
            ]
            if not start_labels and not end_labels:
                continue
            if len(start_labels) != 1 or len(end_labels) != 1:
                endpoint_failures.append(
                    {
                        "path_index": path_index,
                        "start": _point(start),
                        "start_labels": start_labels,
                        "end": _point(end),
                        "end_labels": end_labels,
                    }
                )
                continue
            first, second = start_labels[0], end_labels[0]
            if first == second:
                continue
            earlier, later = sorted(
                (first, second), key=lambda label: rectangles[label].y0, reverse=True
            )
            edges.append(
                {
                    "id": f"p19-path-{path_index}",
                    "earlier": earlier,
                    "later": later,
                    "matrix_page": 1,
                    "pdf_path_index": path_index,
                    "polyline_segments": [
                        [_point(segment[1]), _point(segment[2])]
                        for segment in segments
                    ],
                    "audit_status": "pending_visual_review",
                }
            )

    if endpoint_failures:
        raise ValueError(f"ambiguous connector endpoints: {endpoint_failures}")
    edge_pairs = [(edge["earlier"], edge["later"]) for edge in edges]
    if len(edge_pairs) != len(set(edge_pairs)):
        raise ValueError("duplicate extracted edge")
    if _would_cycle(set(nodes), edge_pairs):
        raise ValueError("extracted candidate graph contains a cycle")
    connected_nodes = {node for edge in edge_pairs for node in edge}
    if connected_nodes != set(nodes):
        raise ValueError(f"unconnected extracted nodes: {set(nodes) - connected_nodes}")
    matrix_labels = set(nodes)

    return {
        "schema": "harrislab.trimmis.profile19.audit-candidate.v1",
        "source": {
            "doi": SOURCE_DOI,
            "matrix_file": matrix_path.name,
            "matrix_md5": MATRIX_MD5,
            "catalog_file": catalog_path.name,
            "catalog_md5": CATALOG_MD5,
            "profile_file": profile_path.name,
            "profile_md5": PROFILE_MD5,
            "license": "CC-BY-3.0",
        },
        "profile": "P19",
        "relation_direction": "older_to_younger",
        "approval_status": "pending_visual_review",
        "node_count": len(nodes),
        "edge_count": len(edges),
        "source_profile_comparison": {
            "shared_labels": sorted(matrix_labels & profile_labels),
            "matrix_only_labels": sorted(matrix_labels - profile_labels),
            "profile_only_labels": sorted(profile_labels - matrix_labels),
        },
        "nodes": sorted(nodes.values(), key=lambda node: node["id"]),
        "edges": sorted(
            edges, key=lambda edge: (edge["earlier"], edge["later"], edge["id"])
        ),
    }


def render_overlay(matrix_path: Path, result: dict[str, Any], output: Path) -> None:
    clip = fitz.Rect(PROFILE_BOUNDARY_X - 8, NODE_TOP_Y, PROFILE_RIGHT_X + 8, NODE_BOTTOM_Y)
    with fitz.open(matrix_path) as document:
        page = document[0]
        for node in result["nodes"]:
            page.draw_rect(
                fitz.Rect(node["matrix_rectangle"]),
                color=(0.0, 0.45, 1.0),
                width=0.6,
                overlay=True,
            )
        for edge in result["edges"]:
            for start, end in edge["polyline_segments"]:
                page.draw_line(
                    fitz.Point(start),
                    fitz.Point(end),
                    color=(1.0, 0.0, 0.7),
                    width=0.8,
                    overlay=True,
                )
            start = edge["polyline_segments"][0][0]
            page.insert_text(
                fitz.Point(start[0] + 1.0, start[1] + 2.5),
                str(edge["pdf_path_index"]),
                fontsize=3.0,
                color=(0.75, 0.0, 0.45),
                overlay=True,
            )
        pixmap = page.get_pixmap(matrix=fitz.Matrix(4, 4), clip=clip, alpha=False)
        output.parent.mkdir(parents=True, exist_ok=True)
        pixmap.save(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_directory", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--overlay",
        type=Path,
        help="Optional PNG with extracted nodes and connectors highlighted",
    )
    arguments = parser.parse_args()
    result = extract(
        arguments.source_directory / "Harris_Matrix.pdf",
        arguments.source_directory / "Katalog_Positionen.xlsx",
        arguments.source_directory / "P19.pdf",
    )
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(result, indent=2, ensure_ascii=True, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if arguments.overlay is not None:
        render_overlay(
            arguments.source_directory / "Harris_Matrix.pdf",
            result,
            arguments.overlay,
        )
    print(
        json.dumps(
            {
                "approval_status": result["approval_status"],
                "edge_count": result["edge_count"],
                "node_count": result["node_count"],
                "output": str(arguments.output),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
