"""Supervised fine‑tuning script for PALADIN proof planner.

This script demonstrates how to load human‑labelled evidence graphs
from a JSONL file and prepare them for fine‑tuning a language model
to produce structured output.  Due to the restricted environment
provided for this exercise, the script does not perform any real
training; instead it parses the dataset and prints summary
statistics.  You can extend this script to call your favourite
deep learning framework when you run it on a machine with GPU and
internet connectivity.

Each line of the input file should be a JSON object with at least
the keys ``question``, ``answer`` and ``evidence_graph``.  The
``evidence_graph`` must conform to the schema defined in
`paladin/egl/schema.py`.
"""

from __future__ import annotations

import argparse
import json
from typing import List


def load_examples(path: str) -> List[dict]:
    examples = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                examples.append(obj)
            except json.JSONDecodeError:
                continue
    return examples


def main() -> None:
    parser = argparse.ArgumentParser(description="Supervised fine tuning placeholder for PALADIN")
    parser.add_argument("--data", default="paladin/data/human_graphs/seed.jsonl", help="Path to JSONL file of human graphs")
    args = parser.parse_args()
    examples = load_examples(args.data)
    print(f"Loaded {len(examples)} examples from {args.data}")
    if examples:
        # Print a few examples to illustrate
        print(json.dumps(examples[0], indent=2)[:1000])
    print("This script does not train a model in this environment.  Please adapt it for your own use.")


if __name__ == "__main__":
    main()