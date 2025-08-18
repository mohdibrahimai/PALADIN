"""Build a document set for the retriever.

This script assembles a document collection from plain text files in
a directory and writes a JSON file consumable by the SimpleRetriever.
Each file in the input directory is treated as a separate document
with its filename (without extension) as the document id.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import List, Dict


def build_docs(input_dir: str) -> List[Dict[str, str]]:
    docs: List[Dict[str, str]] = []
    for fname in os.listdir(input_dir):
        path = os.path.join(input_dir, fname)
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        doc_id = os.path.splitext(fname)[0]
        docs.append({"id": doc_id, "text": text})
    return docs


def main() -> None:
    parser = argparse.ArgumentParser(description="Build document set for PALADIN")
    parser.add_argument("input_dir", help="Directory containing plain text files")
    parser.add_argument("output_json", help="Path to write output JSON file")
    args = parser.parse_args()
    docs = build_docs(args.input_dir)
    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(docs)} documents to {args.output_json}")


if __name__ == "__main__":
    main()