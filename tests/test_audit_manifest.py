import json
import unittest
from pathlib import Path

from scripts.build_audit_manifest import AUDIT_COMPONENTS, build_manifest, serialized_manifest


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


if __name__ == "__main__":
    unittest.main()