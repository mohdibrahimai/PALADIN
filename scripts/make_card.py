"""Generate a proof carrying answer card report.

This script wraps the evaluation metrics in a structured report that
can be saved as a JSON or Markdown file.  The report includes
metadata such as the date and a brief description of the evaluation
set.  You can extend this script to output other formats such as
PDFs by leveraging libraries like reportlab.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime

from ..retriever.retrieve import SimpleRetriever
from ..evals.metrics import evaluate_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Create model card for PALADIN")
    parser.add_argument("--docs", default="paladin/data/docs.json", help="Path to document JSON file")
    parser.add_argument("--graphs", default="paladin/data/human_graphs/seed.jsonl", help="Path to human graphs JSONL file")
    parser.add_argument("--output", default="paladin/data/cards/report.json", help="Output path for report")
    args = parser.parse_args()
    retriever = SimpleRetriever.from_json(args.docs)
    metrics = evaluate_dataset(retriever, args.graphs)
    report = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "docs": args.docs,
        "graphs": args.graphs,
        "metrics": metrics,
    }
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"Wrote report to {args.output}")


if __name__ == "__main__":
    main()