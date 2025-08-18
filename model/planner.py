"""Proof planner for PALADIN.

The planner constructs a minimal evidence graph given a question,
answer and a set of retrieved documents.  In this reference
implementation the planner is deliberately simple: it picks the top
document returned by the retriever, extracts a span of text around
query terms and links it to the answer via a single ``supports``
edge.  More sophisticated planners could compose multiple pieces of
evidence and include entailment or calculation nodes.
"""

from __future__ import annotations

import hashlib
from typing import List, Dict

from ..egl.schema import EvidenceGraph, Node, Edge
from ..retriever.spans import extract_span


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def plan_proof(query: str, answer: str, documents: List[Dict[str, str]]) -> EvidenceGraph:
    """Construct a minimal evidence graph for the given question and answer.

    The current strategy is to link the answer claim to a single
    evidence span extracted from the top document.  If no documents
    are supplied the graph will contain only the claim node and fail
    verification.
    """
    nodes: List[Node] = []
    edges: List[Edge] = []
    # Create claim node
    claim_id = "c1"
    claim_node = Node(id=claim_id, type="claim", text=answer)
    nodes.append(claim_node)
    if documents:
        # Use top document as evidence source
        doc = documents[0]
        span_text = extract_span(doc.get("text", ""), query, window=40)
        hash_val = _hash_text(span_text)
        evidence_id = "e1"
        evidence_node = Node(id=evidence_id, type="evidence",
                             url=doc.get("id", "unknown"),
                             span=span_text, hash=hash_val)
        nodes.append(evidence_node)
        # Add support edge
        edges.append(Edge(source=evidence_id, target=claim_id, type="supports"))
    # Build evidence graph
    graph = EvidenceGraph(nodes=nodes, edges=edges)
    return graph