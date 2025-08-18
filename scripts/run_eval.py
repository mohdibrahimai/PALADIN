"""Run evaluation over a labelled dataset.

This script loads a document set and a human labelled JSONL file
containing questions, answers and graphs, then evaluates the PALADIN
system against this data using the metrics defined in
`paladin.evals.metrics`.  It prints the metric results to stdout.
"""

from __future__ import annotations

import argparse
import json

from ..retriever.retrieve import SimpleRetriever
from ..evals.metrics import evaluate_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Run PALADIN evaluation")
    parser.add_argument("--docs", default="paladin/data/docs.json", help="Path to document JSON file")
    parser.add_argument("--graphs", default="paladin/data/human_graphs/seed.jsonl", help="Path to human graphs JSONL file")
    args = parser.parse_args()
    retriever = SimpleRetriever.from_json(args.docs)
    metrics = evaluate_dataset(retriever, args.graphs)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()