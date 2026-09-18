from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path


def canonical_bytes(path: Path) -> bytes:
    content = path.read_bytes()
    if path.suffix.lower() == ".json":
        return content.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return content


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(canonical_bytes(path))
    return digest.hexdigest()


def run(root: Path, *arguments: str) -> None:
    command = [sys.executable, *arguments]
    result = subprocess.run(
        command,
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    detail = result.stdout.strip().splitlines()
    print(f"PASS {' '.join(arguments)}")
    if detail:
        print(f"     {detail[-1]}")


def require_identical(generated: Path, committed: Path) -> None:
    generated_hash = sha256(generated)
    committed_hash = sha256(committed)
    if generated_hash != committed_hash:
        raise RuntimeError(
            f"reproduction mismatch for {committed}: "
            f"generated={generated_hash}, committed={committed_hash}"
        )
    print(f"PASS reproduced {committed.relative_to(committed.parents[1])}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate and verify all HarrisLab v0.2.0 release artifacts."
    )
    parser.add_argument(
        "--source-directory",
        type=Path,
        default=Path(".local-data/trimmis-source"),
        help="Directory containing checksum-verified Trimmis source files.",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    source_directory = args.source_directory
    if not source_directory.is_absolute():
        source_directory = root / source_directory
    required_sources = ("Harris_Matrix.pdf", "Katalog_Positionen.xlsx", "P19.pdf")
    missing = [name for name in required_sources if not (source_directory / name).is_file()]
    if missing:
        raise SystemExit(f"missing source files in {source_directory}: {', '.join(missing)}")

    with tempfile.TemporaryDirectory(prefix="harrislab-release-") as temporary:
        workspace = Path(temporary)
        data = workspace / "data"
        docs = workspace / "docs"
        data.mkdir()
        docs.mkdir()

        candidate = data / "trimmis_profile19_audit_candidate.json"
        published = data / "trimmis_profile19_published_reference.json"
        reference = data / "trimmis_profile19_reference.json"
        drawing = data / "trimmis_profile19_drawing_comparison.json"
        profile_image = docs / "trimmis_profile19_source_profile.png"
        text_proposals = data / "trimmis_profile19_text_relation_proposals.json"
        retrospective = data / "trimmis_profile19_benchmark.json"
        comprehensive = data / "trimmis_profile19_comprehensive_benchmark.json"
        formation = data / "formation_process_benchmark.json"

        run(root, "scripts/extract_trimmis_profile19.py", str(source_directory), str(candidate))
        require_identical(candidate, root / "data/trimmis_profile19_audit_candidate.json")

        run(
            root,
            "scripts/review_trimmis_profile19.py",
            "approve",
            str(candidate),
            "data/trimmis_profile19_review.json",
            str(published),
        )
        require_identical(published, root / "data/trimmis_profile19_published_reference.json")

        run(
            root,
            "scripts/review_trimmis_profile19.py",
            "correct",
            str(published),
            "data/trimmis_profile19_corrections.json",
            str(reference),
        )
        require_identical(reference, root / "data/trimmis_profile19_reference.json")

        run(
            root,
            "scripts/compare_trimmis_profile19_drawing.py",
            str(source_directory),
            "--reference",
            str(reference),
            "--published-reference",
            str(published),
            "--corrections",
            "data/trimmis_profile19_corrections.json",
            "--output",
            str(drawing),
            "--image",
            str(profile_image),
        )
        require_identical(drawing, root / "data/trimmis_profile19_drawing_comparison.json")
        require_identical(profile_image, root / "docs/trimmis_profile19_source_profile.png")

        run(
            root,
            "scripts/extract_trimmis_profile19_text_relations.py",
            str(source_directory),
            "--reference",
            str(reference),
            "--output",
            str(text_proposals),
        )
        require_identical(text_proposals, root / "data/trimmis_profile19_text_relation_proposals.json")

        run(root, "scripts/benchmark_trimmis_profile19.py", "--reference", str(reference), "--output", str(retrospective))
        require_identical(retrospective, root / "data/trimmis_profile19_benchmark.json")

        run(
            root,
            "scripts/benchmark_trimmis_profile19_comprehensive.py",
            "--reference",
            str(reference),
            "--preregistration",
            "data/trimmis_profile19_benchmark_preregistration.json",
            "--output",
            str(comprehensive),
        )
        require_identical(comprehensive, root / "data/trimmis_profile19_comprehensive_benchmark.json")

        run(
            root,
            "scripts/benchmark_formation_process.py",
            "--preregistration",
            "data/formation_process_benchmark_preregistration.json",
            "--output",
            str(formation),
        )
        require_identical(formation, root / "data/formation_process_benchmark.json")

    run(root, "scripts/build_audit_manifest.py", "--check")
    run(root, "-m", "unittest", "discover", "-s", "tests", "-v")
    print("HarrisLab v0.2.0 release validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())