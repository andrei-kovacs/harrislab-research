"""Create or apply an independent review for the Trimmis P19 candidate."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from harrislab.approval import (
    apply_confirmed_corrections,
    approve_candidate,
    create_review_template,
    file_sha256,
)


def _write(path: Path, document: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(document, indent=2, ensure_ascii=True, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    template = subparsers.add_parser("template")
    template.add_argument("candidate", type=Path)
    template.add_argument("review", type=Path)
    approve = subparsers.add_parser("approve")
    approve.add_argument("candidate", type=Path)
    approve.add_argument("review", type=Path)
    approve.add_argument("output", type=Path)
    correct = subparsers.add_parser("correct")
    correct.add_argument("reference", type=Path)
    correct.add_argument("corrections", type=Path)
    correct.add_argument("output", type=Path)
    arguments = parser.parse_args()

    if arguments.command == "template":
        _write(arguments.review, create_review_template(arguments.candidate))
        print(json.dumps({"status": "pending_review", "review": str(arguments.review)}))
        return

    if arguments.command == "approve":
        result = approve_candidate(arguments.candidate, arguments.review)
    else:
        result = apply_confirmed_corrections(
            arguments.reference, arguments.corrections
        )
    _write(arguments.output, result)
    print(
        json.dumps(
            {
                "status": arguments.command,
                "output": str(arguments.output),
                "sha256": file_sha256(arguments.output),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()