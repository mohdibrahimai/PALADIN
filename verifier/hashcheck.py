"""Check that evidence nodes bind to their cited span.

For each evidence node we recompute the SHA‑256 hash of the span and
compare it to the stored hash.  If any mismatch is found the check
fails.  We also record missing hashes as problems.
"""

from __future__ import annotations

import hashlib
from typing import Tuple, List

from ..egl.schema import EvidenceGraph, Node


def _sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def check_source_binding(graph: EvidenceGraph) -> Tuple[bool, List[str]]:
    """Verify that evidence nodes have correct content hashes.

    Returns (passed, problems).  `passed` is True if all evidence
    nodes have a non‑empty span and the stored hash matches the
    recomputed hash.  `problems` is a list of human readable error
    messages for nodes that failed.
    """
    problems: List[str] = []
    for node in graph.nodes:
        if node.type != "evidence":
            continue
        span = node.span or ""
        h = node.hash or ""
        if not span:
            problems.append(f"evidence {node.id} missing span")
            continue
        if not h:
            problems.append(f"evidence {node.id} missing hash")
            continue
        actual = _sha256_hex(span)
        if actual != h:
            problems.append(f"hash mismatch for {node.id}")
    return (len(problems) == 0, problems)