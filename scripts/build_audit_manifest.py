from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


RELEASE_VERSION = "0.2.0"
AUDIT_COMPONENTS = (
    ("reference", "data/trimmis_profile19_reference.json"),
    ("text_relation_proposals", "data/trimmis_profile19_text_relation_proposals.json"),
    ("drawing_comparison", "data/trimmis_profile19_drawing_comparison.json"),
    ("ai_drawing_screen", "data/trimmis_profile19_ai_drawing_screen.json"),
    ("formation_process_benchmark", "data/formation_process_benchmark.json"),
    ("retrospective_benchmark", "data/trimmis_profile19_benchmark.json"),
    ("comprehensive_benchmark", "data/trimmis_profile19_comprehensive_benchmark.json"),
)


def canonical_bytes(path: Path) -> bytes:
    content = path.read_bytes()
    if path.suffix.lower() == ".json":
        return content.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return content


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(canonical_bytes(path))
    return digest.hexdigest()


def build_manifest(root: Path) -> dict[str, object]:
    components = []
    for key, relative_path in AUDIT_COMPONENTS:
        path = root / relative_path
        components.append(
            {
                "key": key,
                "path": relative_path,
                "sha256": file_sha256(path),
                "bytes": len(canonical_bytes(path)),
            }
        )
    return {
        "schema": "harrislab.audit-provenance.v1",
        "release_version": RELEASE_VERSION,
        "direction_convention": "earlier -> later",
        "text_canonicalization": "JSON CRLF and CR are normalized to LF before hashing and byte counting.",
        "components": components,
        "external_sources": [
            {
                "record": "https://doi.org/10.5281/zenodo.4461075",
                "file": "P19.pdf",
                "checksum": {
                    "algorithm": "md5",
                    "value": "53ccf16a523e986ead69a30fc3f8dc24",
                },
                "license": "CC-BY-3.0",
            }
        ],
        "authority": {
            "ai_drawing_screen": "non_authoritative",
            "drawing_review_status": "27_relations_pending_qualified_review",
            "accepted_graph_mutations_from_ai_screen": 0,
        },
    }


def serialized_manifest(root: Path) -> str:
    return json.dumps(build_manifest(root), indent=2, ensure_ascii=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the HarrisLab audit provenance manifest.")
    parser.add_argument("--check", action="store_true", help="Fail if the committed manifest is stale.")
    parser.add_argument(
        "--output",
        type=Path,
        help="Output path, relative to the repository root unless absolute.",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    output = args.output or Path("data/harrislab_audit_manifest.json")
    output = output if output.is_absolute() else root / output
    expected = serialized_manifest(root)

    if args.check:
        if not output.exists() or output.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"Audit provenance manifest is missing or stale: {output}")
        print(f"Audit provenance manifest verified: {output}")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(expected, encoding="utf-8")
    print(f"Audit provenance manifest written: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())