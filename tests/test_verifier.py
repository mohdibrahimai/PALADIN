import unittest

from paladin.egl.schema import EvidenceGraph, Node, Edge
from paladin.verifier.hashcheck import check_source_binding
from paladin.verifier.truthlens_adapter import get_support_level
from paladin.verifier.minimality import check_minimality


class TestVerifier(unittest.TestCase):
    def test_hashcheck(self):
        span = "Hello world"
        import hashlib
        h = hashlib.sha256(span.encode("utf-8")).hexdigest()
        graph = EvidenceGraph(nodes=[
            Node(id="c1", type="claim", text="Hello world"),
            Node(id="e1", type="evidence", span=span, hash=h, url="doc1"),
        ], edges=[Edge(source="e1", target="c1", type="supports")])
        ok, problems = check_source_binding(graph)
        self.assertTrue(ok)
        self.assertEqual(problems, [])
        # Tamper with hash
        graph.nodes[1].hash = "deadbeef"
        ok, problems = check_source_binding(graph)
        self.assertFalse(ok)
        self.assertTrue(problems)

    def test_truthlens(self):
        premise = "The capital of France is Paris."
        hypothesis = "France's capital is Paris"
        level = get_support_level(premise, hypothesis)
        self.assertEqual(level, "supported")
        # Contradiction
        premise2 = "The capital of France is not Paris."
        level2 = get_support_level(premise2, hypothesis)
        self.assertEqual(level2, "contradicted")

    def test_minimality(self):
        # Simple minimal graph: one evidence supports one claim
        span = "Water boils at 100°C"
        import hashlib
        h = hashlib.sha256(span.encode("utf-8")).hexdigest()
        graph = EvidenceGraph(nodes=[
            Node(id="c1", type="claim", text="Water boils at 100°C"),
            Node(id="e1", type="evidence", span=span, hash=h, url="doc1"),
        ], edges=[Edge(source="e1", target="c1", type="supports")])
        is_min, removable = check_minimality(graph)
        self.assertTrue(is_min)
        self.assertEqual(removable, [])
        # Add redundant evidence
        span2 = "Boiling point of water is 100 degrees Celsius"
        h2 = hashlib.sha256(span2.encode("utf-8")).hexdigest()
        graph.nodes.append(Node(id="e2", type="evidence", span=span2, hash=h2, url="doc2"))
        graph.edges.append(Edge(source="e2", target="c1", type="supports"))
        is_min2, removable2 = check_minimality(graph)
        self.assertFalse(is_min2)
        self.assertTrue(removable2)


if __name__ == "__main__":
    unittest.main()