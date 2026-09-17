"""Create or validate a privacy-safe P19 drawing review checklist."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harrislab.drawing_review import (
    create_drawing_review_template,
    drawing_review_csv,
    drawing_review_from_csv,
    validate_drawing_review_document,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--comparison",
        type=Path,
        default=Path("data/trimmis_profile19_drawing_comparison.json"),
    )
    parser.add_argument("--validate", type=Path, metavar="REVIEW_CSV")
    parser.add_argument(
        "--template-json",
        type=Path,
        default=Path("data/trimmis_profile19_drawing_review_template.json"),
    )
    parser.add_argument(
        "--template-csv",
        type=Path,
        default=Path("docs/trimmis_profile19_drawing_review_checklist.csv"),
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("drawing_review_summary.json"),
    )
    arguments = parser.parse_args()

    if arguments.validate:
        review = drawing_review_from_csv(arguments.validate)
        summary = validate_drawing_review_document(arguments.comparison, review)
        arguments.summary.write_text(
            json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(summary["decision_counts"], sort_keys=True))
        return

    template = create_drawing_review_template(arguments.comparison)
    arguments.template_json.write_text(
        json.dumps(template, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    arguments.template_csv.write_text(drawing_review_csv(template), encoding="utf-8")
    print(f"Created {len(template['relation_reviews'])} drawing review rows")


if __name__ == "__main__":
    main()