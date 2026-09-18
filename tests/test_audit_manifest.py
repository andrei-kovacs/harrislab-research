import json
import unittest
from pathlib import Path

from scripts.build_audit_manifest import (
    AUDIT_COMPONENTS,
    build_manifest,
    canonical_bytes,
    file_sha256,
    serialized_manifest,
)


class AuditManifestTests(unittest.TestCase):
    def test_committed_manifest_matches_export_components(self) -> None:
        root = Path(__file__).resolve().parents[1]
        manifest_path = root / "data" / "harrislab_audit_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        self.assertEqual(manifest_path.read_text(encoding="utf-8"), serialized_manifest(root))
        self.assertEqual(manifest, build_manifest(root))
        self.assertEqual(
            [(item["key"], item["path"]) for item in manifest["components"]],
            list(AUDIT_COMPONENTS),
        )
        self.assertEqual(manifest["authority"]["ai_drawing_screen"], "non_authoritative")
        self.assertEqual(
            manifest["authority"]["drawing_review_status"],
            "27_relations_pending_qualified_review",
        )
        self.assertEqual(
            manifest["authority"]["accepted_graph_mutations_from_ai_screen"], 0
        )
        self.assertEqual(manifest["release_version"], "0.3.0")
        self.assertEqual(
            manifest["authority"]["harp_inn_contemporary_status"],
            "typed_non_precedence",
        )
        self.assertEqual(
            manifest["authority"]["accepted_harp_inn_graph_mutations_from_ai"], 0
        )

    def test_json_hash_is_stable_across_line_endings(self) -> None:
        root = Path(__file__).resolve().parents[1]
        source = root / "data" / "trimmis_profile19_reference.json"
        lf_content = canonical_bytes(source)
        temporary = root / ".local-data" / "line-ending-probe.json"
        temporary.parent.mkdir(exist_ok=True)
        try:
            temporary.write_bytes(lf_content.replace(b"\n", b"\r\n"))
            self.assertEqual(file_sha256(source), file_sha256(temporary))
            self.assertEqual(len(canonical_bytes(source)), len(canonical_bytes(temporary)))
        finally:
            temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()