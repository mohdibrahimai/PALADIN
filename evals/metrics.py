"""Evaluation metrics for PALADIN.

This module defines functions to compute the core metrics described in
the PALADIN design.  These metrics operate over labelled examples and
call the runner to generate answers and proofs.  The metrics are
simple heuristics and should be treated as illustrative.  For
publishable results you should align the metric definitions with your
task requirements.
"""

from __future__ import annotations

import json
import time
from typing import Dict, List

from ..retriever.retrieve import SimpleRetriever
from ..model.runner import PaladinRunner


def _load_jsonl(path: str) -> List[dict]:
    examples = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                examples.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return examples


def evaluate_dataset(retriever: SimpleRetriever, data_path: str) -> Dict[str, float]:
    """Compute metrics over a labelled dataset.

    Returns a dictionary with keys ``PVR``, ``minimality``, ``truth_consistency``
    and ``citation_precision``.  A simple latency measure is also
    provided as ``latency`` (milliseconds).
    """
    examples = _load_jsonl(data_path)
    if not examples:
        return {
            "PVR": 0.0,
            "minimality": 0.0,
            "truth_consistency": 0.0,
            "citation_precision": 0.0,
            "latency": 0.0,
        }
    runner = PaladinRunner(retriever)
    valid_count = 0
    minimality_scores: List[float] = []
    truth_scores: List[float] = []
    citation_scores: List[float] = []
    latencies: List[float] = []
    for ex in examples:
        q = ex.get("question", "")
        start = time.time()
        result = runner.answer_and_proof(q)
        latencies.append((time.time() - start) * 1000)
        if result["valid"]:
            valid_count += 1
        # Minimality score: 1 - (# removable / total edges)
        details = result.get("details", {})
        min_det = details.get("minimality", {})
        removable = min_det.get("removable", [])
        total_edges = len(result["graph"].get("edges", [])) or 1
        minimality_scores.append(1.0 - (len(removable) / total_edges))
        # Truth consistency: count of supported edges vs total supports
        entail_det = details.get("entailment", {})
        levels = entail_det.get("levels", [])
        if levels:
            supported = sum(1 for l in levels if l == "supported")
            truth_scores.append(supported / len(levels))
        else:
            truth_scores.append(0.0)
        # Citation precision: proportion of evidence spans that contain the answer text
        answer_text = ex.get("answer", "").lower()
        evidences = [node for node in result["graph"]["nodes"] if node.get("type") == "evidence"]
        if evidences:
            matches = sum(1 for e in evidences if answer_text and answer_text in (e.get("span", "").lower()))
            citation_scores.append(matches / len(evidences))
        else:
            citation_scores.append(0.0)
    n = len(examples)
    return {
        "PVR": valid_count / n,
        "minimality": sum(minimality_scores) / n,
        "truth_consistency": sum(truth_scores) / n,
        "citation_precision": sum(citation_scores) / n,
        "latency": sum(latencies) / n,
    }