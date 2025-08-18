"""Top level orchestrator for PALADIN.

The runner ties together retrieval, answer generation, proof
construction and verification.  It exposes a single method
`answer_and_proof` which takes a natural language question and
returns the answer, the evidence graph in dict form and a boolean
indicating whether the proof passed verification.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Dict, Any, Tuple

from ..retriever.retrieve import SimpleRetriever
from ..model.answerer import answer_question
from ..model.planner import plan_proof
from ..egl.schema import EvidenceGraph
from ..verifier import hashcheck, nli_check, numeric_time_check, truthlens_adapter, minimality


class PaladinRunner:
    """Coordinate retrieval, answer extraction, planning and verification."""

    def __init__(self, retriever: SimpleRetriever):
        self.retriever = retriever

    def _verify(self, graph: EvidenceGraph) -> Tuple[bool, Dict[str, Any]]:
        """Run all verifiers on the evidence graph.

        Returns a tuple `(valid, details)` where `valid` is True if
        all checks pass and `details` contains information on each
        check.  This method is internal to the runner.
        """
        details = {}
        # Hash check
        ok_hash, problems = hashcheck.check_source_binding(graph)
        details["hash"] = {"passed": ok_hash, "problems": problems}
        # Local entailment checks: for each support edge, check that the
        # evidence span supports the claim text using a simple lexical
        # overlap heuristic.  Contradiction/unverifiable is handled by
        # truthlens_adapter.get_support_level.
        support_ok = True
        entail_results = []
        for edge in graph.edges:
            if edge.type == "supports":
                src = graph.get_node(edge.source)
                tgt = graph.get_node(edge.target)
                if src and tgt and src.type == "evidence" and tgt.type == "claim":
                    level = truthlens_adapter.get_support_level(src.span or "", tgt.text or "")
                    entail_results.append(level)
                    if level != "supported":
                        support_ok = False
        details["entailment"] = {"passed": support_ok, "levels": entail_results}
        # Minimality check
        is_min, removable = minimality.check_minimality(graph)
        details["minimality"] = {"passed": is_min, "removable": removable}
        # Numeric/time checks: iterate over calc nodes (not used in this simple planner)
        # For completeness we run the check on all calc nodes
        numeric_ok = True
        numeric_problems = []
        for node in graph.nodes:
            if node.type == "calc" and node.code is not None and node.result is not None:
                try:
                    ok = numeric_time_check.check_numeric_calc(node.code, node.result)
                    if not ok:
                        numeric_ok = False
                        numeric_problems.append(node.id)
                except Exception:
                    numeric_ok = False
                    numeric_problems.append(node.id)
        details["numeric"] = {"passed": numeric_ok, "problems": numeric_problems}
        # Final decision: all checks must pass
        valid = ok_hash and support_ok and is_min and numeric_ok
        return valid, details

    def answer_and_proof(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """Return answer and proof for the query.

        The returned dictionary has keys ``answer``, ``graph`` (the
        evidence graph as a dict), ``valid`` (bool) and ``details``
        containing per‑checker results.
        """
        # Retrieve documents
        docs = self.retriever.retrieve(query, top_k=top_k)
        # Generate answer
        answer = answer_question(query, docs)
        # Plan proof
        graph = plan_proof(query, answer, docs)
        # Verify
        valid, details = self._verify(graph)
        return {
            "answer": answer,
            "graph": graph.to_dict(),
            "valid": valid,
            "details": details,
        }