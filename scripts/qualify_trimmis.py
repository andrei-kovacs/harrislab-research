"""Reproduce the qualification screen for the Trimmis Harris matrix dataset."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from xml.etree import ElementTree
from zipfile import ZipFile

import fitz

RECORD_ID = "4461075"
RECORD_API = f"https://zenodo.org/api/records/{RECORD_ID}"
EXPECTED_DOI = "10.5281/zenodo.4461075"
EXPECTED_LICENSE = "cc-by-3.0"
REQUIRED_FILES = {
    "Katalog_Positionen.xlsx": "75983db690194fb562ba0378ebd627a3",
    "Harris_Matrix.pdf": "9ece18c188763350f16e164f441a927e",
    "P19.pdf": "53ccf16a523e986ead69a30fc3f8dc24",
}
SPREADSHEET_NS = {
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
}


def _open(url: str):
    request = Request(url, headers={"User-Agent": "HarrisLab/0.1 dataset screen"})
    last_error: HTTPError | URLError | None = None
    for _ in range(3):
        try:
            return urlopen(request, timeout=60)
        except (HTTPError, URLError) as error:
            last_error = error
    assert last_error is not None
    raise last_error


def _read_json(url: str) -> dict[str, Any]:
    with _open(url) as response:
        return json.load(response)


def _download(url: str, destination: Path) -> None:
    with _open(url) as response:
        destination.write_bytes(response.read())


def _md5(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _workbook_summary(path: Path) -> dict[str, Any]:
    with ZipFile(path) as archive:
        workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
        sheet_names = [
            sheet.attrib["name"]
            for sheet in workbook.findall(".//main:sheet", SPREADSHEET_NS)
        ]
        worksheets = [
            name
            for name in archive.namelist()
            if name.startswith("xl/worksheets/sheet") and name.endswith(".xml")
        ]
        row_counts = []
        for worksheet in worksheets:
            root = ElementTree.fromstring(archive.read(worksheet))
            row_counts.append(
                len(root.findall(".//main:sheetData/main:row", SPREADSHEET_NS))
            )
    return {"sheet_names": sheet_names, "row_counts": row_counts}


def _matrix_summary(path: Path) -> dict[str, Any]:
    with fitz.open(path) as document:
        return {
            "page_count": document.page_count,
            "text_blocks": sum(len(page.get_text("blocks")) for page in document),
            "vector_paths": sum(len(page.get_drawings()) for page in document),
            "vector_items": sum(
                len(drawing["items"])
                for page in document
                for drawing in page.get_drawings()
            ),
        }


def qualify(destination: Path) -> dict[str, Any]:
    metadata = _read_json(RECORD_API)
    license_id = metadata["metadata"]["license"]["id"]
    if metadata["doi"] != EXPECTED_DOI:
        raise ValueError(f"unexpected DOI: {metadata['doi']}")
    if license_id != EXPECTED_LICENSE:
        raise ValueError(f"unexpected license: {license_id}")

    destination.mkdir(parents=True, exist_ok=True)
    files_by_name = {item["key"]: item for item in metadata["files"]}
    verified_files: dict[str, dict[str, Any]] = {}
    for name, expected_md5 in REQUIRED_FILES.items():
        item = files_by_name[name]
        path = destination / name
        _download(item["links"]["self"], path)
        actual_md5 = _md5(path)
        if actual_md5 != expected_md5:
            raise ValueError(f"checksum mismatch for {name}: {actual_md5}")
        verified_files[name] = {
            "bytes": path.stat().st_size,
            "md5": actual_md5,
        }

    return {
        "record_id": RECORD_ID,
        "doi": metadata["doi"],
        "license": license_id,
        "resource_type": metadata["metadata"]["resource_type"]["type"],
        "verified_files": verified_files,
        "catalog": _workbook_summary(destination / "Katalog_Positionen.xlsx"),
        "matrix": _matrix_summary(destination / "Harris_Matrix.pdf"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "destination",
        type=Path,
        help="Directory for checksum-verified source artifacts",
    )
    arguments = parser.parse_args()
    print(json.dumps(qualify(arguments.destination), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
