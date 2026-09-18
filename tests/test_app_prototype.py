import unittest
from pathlib import Path


class AppPrototypeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).parents[1]
        cls.document = (root / "docs" / "app-prototype.html").read_text(
            encoding="utf-8"
        )

    def test_harp_dataset_contract_is_explicit(self) -> None:
        for required in (
            'option value="harp"',
            "harp_inn_group1_reference.json?v=0.3.1",
            "harp_inn_group1_benchmark.json?v=0.3.1",
            "function renderHarpQuestions",
            "CONTEMPORARY remains typed evidence outside the DAG",
        ):
            self.assertIn(required, self.document)

    def test_trimmis_only_panels_are_marked(self) -> None:
        self.assertEqual(self.document.count("data-trimmis-only"), 9)
        self.assertIn(
            'document.querySelectorAll("[data-trimmis-only]")', self.document
        )


if __name__ == "__main__":
    unittest.main()