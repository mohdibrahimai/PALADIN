"""Compiler for the Evidence Graph Language (EGL).

The compiler transforms raw dictionary representations of evidence
graphs into typed `EvidenceGraph` instances and performs structural
validation.  It also computes simple normalisations such as sorting
nodes by identifier to make graphs deterministic.
"""

from __future__ import annotations

from typing import Dict, Any, List

from .schema import Node, Edge, EvidenceGraph, validate_graph


def compile_graph(raw: Dict[str, Any]) -> EvidenceGraph:
    """Compile a raw dictionary into an `EvidenceGraph`.

    The input dictionary should have the keys ``nodes`` and ``edges``
    where nodes are dictionaries with fields described in
    `egl.schema.Node` and edges are dictionaries with `source`,
    `target` and `type` fields.  Unknown keys on nodes are ignored.

    Raises a ValueError if the resulting graph fails structural
    validation.
    """
    nodes_data: List[Dict[str, Any]] = raw.get("nodes", [])
    edges_data: List[Dict[str, Any]] = raw.get("edges", [])
    nodes: List[Node] = []
    for nd in nodes_data:
        # Filter out unknown keys to avoid passing them to Node init
        node_kwargs = {k: v for k, v in nd.items() if k in {
            "id", "type", "text", "url", "span", "hash", "code",
            "result", "premise", "hypothesis", "lang"
        }}
        nodes.append(Node(**node_kwargs))
    edges: List[Edge] = []
    for ed in edges_data:
        edge_kwargs = {k: v for k, v in ed.items() if k in {"source", "target", "type"}}
        edges.append(Edge(**edge_kwargs))
    # Sort nodes and edges by id for determinism
    nodes.sort(key=lambda n: n.id)
    edges.sort(key=lambda e: (e.source, e.target, e.type))
    graph = EvidenceGraph(nodes=nodes, edges=edges)
    errors = validate_graph(graph)
    if errors:
        raise ValueError("Invalid evidence graph: " + "; ".join(errors))
    return graph