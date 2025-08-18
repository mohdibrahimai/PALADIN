"""Definitions of the Evidence Graph Language (EGL).

The Evidence Graph Language represents a structured proof as a set of
nodes and edges.  Nodes have a type (claim, evidence, calc or
entailment) and may carry additional fields such as the literal text
for claims, URLs and spans for evidence or code snippets for
calculations.  Edges capture logical relationships between nodes such
as support, refutation or derivation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Iterable


# Define allowed values as constants.  Keeping them in a single place
# makes it easy to audit which relationships are supported.
NODE_TYPES = {"claim", "evidence", "calc", "entailment"}
EDGE_TYPES = {"supports", "refutes", "derives", "uses-tool", "cites"}


@dataclass
class Node:
    """A node in an evidence graph.

    Each node has a unique identifier and a type drawn from
    NODE_TYPES.  Depending on the type, different fields are
    meaningful:

    * claim: the `text` field contains the assertion to prove.
    * evidence: `url` and `span` store the source and quoted
      substring; `hash` is the SHA‑256 hash of the span.
    * calc: `code` stores a simple expression (e.g. ``"2+2"``) and
      `result` stores the computed result as a string.
    * entailment: `premise` and `hypothesis` store sentences; the
      verifier will check that the premise entails the hypothesis.
    """

    id: str
    type: str
    # Optional fields depending on the node type
    text: Optional[str] = None
    url: Optional[str] = None
    span: Optional[str] = None
    hash: Optional[str] = None
    code: Optional[str] = None
    result: Optional[str] = None
    premise: Optional[str] = None
    hypothesis: Optional[str] = None
    lang: Optional[str] = None  # for multilingual experiments

    def __post_init__(self) -> None:
        if self.type not in NODE_TYPES:
            raise ValueError(f"Unknown node type {self.type}")


@dataclass
class Edge:
    """A directed edge connecting two nodes in an evidence graph.

    Each edge has a source (`source`), a target (`target`) and a type
    drawn from EDGE_TYPES.  Edges encode logical relationships between
    nodes.  For example, an evidence node may support a claim, or a
    calculation node may derive a new claim.
    """

    source: str
    target: str
    type: str

    def __post_init__(self) -> None:
        if self.type not in EDGE_TYPES:
            raise ValueError(f"Unknown edge type {self.type}")


@dataclass
class EvidenceGraph:
    """A set of nodes and edges representing a proof.

    This class stores lists of nodes and edges and provides helper
    methods for validating connectivity and retrieving nodes by id.
    """

    nodes: List[Node] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)

    def node_map(self) -> Dict[str, Node]:
        """Return a mapping from node id to node for quick lookup."""
        return {n.id: n for n in self.nodes}

    def get_node(self, node_id: str) -> Optional[Node]:
        """Return the node with the given id or None if not present."""
        return self.node_map().get(node_id)

    def outgoing(self, node_id: str) -> Iterable[Edge]:
        """Iterate over edges starting at the given node."""
        return [e for e in self.edges if e.source == node_id]

    def incoming(self, node_id: str) -> Iterable[Edge]:
        """Iterate over edges pointing to the given node."""
        return [e for e in self.edges if e.target == node_id]

    def claims(self) -> Iterable[Node]:
        """Return all claim nodes."""
        return [n for n in self.nodes if n.type == "claim"]

    def evidence_nodes(self) -> Iterable[Node]:
        """Return all evidence nodes."""
        return [n for n in self.nodes if n.type == "evidence"]

    def is_final_claim(self, node: Node) -> bool:
        """Heuristic to decide if a claim is final.

        A claim is considered final if no other claim derives it via an
        outgoing edge.  This method is simplistic; in more complex
        systems one might annotate claims explicitly as final.
        """
        return all(e.type != "derives" for e in self.incoming(node.id))

    def final_claims(self) -> List[Node]:
        """Return all claims that are not derived by other claims."""
        return [c for c in self.claims() if self.is_final_claim(c)]

    def reachable_from_evidence(self) -> Dict[str, bool]:
        """Return a dictionary indicating which nodes are reachable from evidence or calc nodes.

        The verifier uses this to check that every final claim can be
        traced back to some evidence or tool node.  We perform a simple
        graph traversal from all nodes of type ``evidence`` or ``calc``.
        """
        reachable: Dict[str, bool] = {n.id: False for n in self.nodes}
        # Start from evidence and calc nodes
        stack = [n.id for n in self.nodes if n.type in {"evidence", "calc", "entailment"}]
        for nid in stack:
            reachable[nid] = True
        # Depth‑first search over supports, derives and cites edges
        while stack:
            current = stack.pop()
            for edge in self.outgoing(current):
                if edge.type in {"supports", "derives", "cites", "uses-tool"}:
                    if not reachable[edge.target]:
                        reachable[edge.target] = True
                        stack.append(edge.target)
        return reachable

    def validate_connectivity(self) -> bool:
        """Check that every final claim is reachable from evidence or tools.

        Returns True if all final claims are reachable, False otherwise.
        """
        reachable = self.reachable_from_evidence()
        for claim in self.final_claims():
            if not reachable.get(claim.id, False):
                return False
        return True

    def to_dict(self) -> Dict[str, object]:
        """Convert the graph into a serialisable dictionary.

        This makes it easy to dump graphs to JSON for logging or
        inspection.  The JSON format matches the schema used in human
        labelling.
        """
        return {
            "nodes": [n.__dict__ for n in self.nodes],
            "edges": [e.__dict__ for e in self.edges],
        }


def validate_graph(graph: EvidenceGraph) -> List[str]:
    """Validate structural properties of an evidence graph.

    Returns a list of error messages; if empty, the graph is
    structurally valid.  The verifier should still perform semantic
    checks (e.g. hash binding, entailment, minimality) separately.
    """
    errors: List[str] = []
    node_ids = {n.id for n in graph.nodes}
    # All nodes have unique identifiers
    if len(node_ids) != len(graph.nodes):
        errors.append("Duplicate node identifiers found")
    # All edges refer to existing nodes
    for edge in graph.edges:
        if edge.source not in node_ids:
            errors.append(f"Edge source {edge.source} does not exist")
        if edge.target not in node_ids:
            errors.append(f"Edge target {edge.target} does not exist")
    # Final claims must be reachable
    if not graph.validate_connectivity():
        errors.append("Final claims are not reachable from evidence or calc nodes")
    return errors