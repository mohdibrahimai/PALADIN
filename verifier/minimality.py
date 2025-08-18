"""Minimality checker for evidence graphs.

Minimal proofs are those for which removing any single evidence edge
breaks the proof.  This module provides a function to identify
removable edges and report whether a graph is minimal.
"""

from __future__ import annotations

from typing import List, Tuple

from ..egl.schema import EvidenceGraph, Edge
from .truthlens_adapter import get_support_level


def _graph_without_edge(graph: EvidenceGraph, edge_to_remove: Edge) -> EvidenceGraph:
    """Return a shallow copy of graph with the specified edge removed."""
    new_edges = [e for e in graph.edges if e is not edge_to_remove]
    # nodes can be reused; edges are new list
    return EvidenceGraph(nodes=list(graph.nodes), edges=new_edges)


def _supports_valid(graph: EvidenceGraph) -> bool:
    """Check that all supports edges still support their claim lexically."""
    for edge in graph.edges:
        if edge.type != "supports":
            continue
        src = graph.get_node(edge.source)
        tgt = graph.get_node(edge.target)
        if not src or not tgt:
            return False
        if src.type != "evidence" or tgt.type != "claim":
            continue
        level = get_support_level(src.span or "", tgt.text or "")
        if level != "supported":
            return False
    return True


def check_minimality(graph: EvidenceGraph) -> Tuple[bool, List[str]]:
    """Return (is_minimal, removable_edge_ids).

    An evidence graph is minimal if removing any single edge breaks the
    proof: either the claim becomes unreachable from evidence or
    support fails.  The function returns a boolean and a list of
    removable edge identifiers (strings of the form ``source->target``).
    """
    removable: List[str] = []
    if not graph.edges:
        return False, []
    # Identify final claims
    final_claims = graph.final_claims()
    for edge in graph.edges:
        # Only consider evidence supports edges for minimality
        temp_graph = _graph_without_edge(graph, edge)
        # Check connectivity: final claims must be reachable
        if not temp_graph.validate_connectivity():
            continue
        # Check lexical support of remaining edges
        if not _supports_valid(temp_graph):
            continue
        # All checks passed: edge removable
        removable.append(f"{edge.source}->{edge.target}")
    is_minimal = len(removable) == 0
    return is_minimal, removable