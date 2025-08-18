import unittest

from paladin.egl.schema import EvidenceGraph, Node, Edge
from paladin.verifier.minimality import check_minimality


class TestMinimality(unittest.TestCase):
    def test_single_edge_minimal(self):
        span = "A fact"
        import hashlib
        h = hashlib.sha256(span.encode("utf-8")).hexdigest()
        graph = EvidenceGraph(nodes=[
            Node(id="c1", type="claim", text="A fact"),
            Node(id="e1", type="evidence", span=span, hash=h, url="doc")
        ], edges=[Edge(source="e1", target="c1", type="supports")])
        is_min, removable = check_minimality(graph)
        self.assertTrue(is_min)
        self.assertEqual(removable, [])

    def test_two_edges_not_minimal(self):
        span1 = "Fact one"
        span2 = "Fact two"
        import hashlib
        h1 = hashlib.sha256(span1.encode()).hexdigest()
        h2 = hashlib.sha256(span2.encode()).hexdigest()
        graph = EvidenceGraph(nodes=[
            Node(id="c1", type="claim", text="Composite fact"),
            Node(id="e1", type="evidence", span=span1, hash=h1, url="doc1"),
            Node(id="e2", type="evidence", span=span2, hash=h2, url="doc2")
        ], edges=[
            Edge(source="e1", target="c1", type="supports"),
            Edge(source="e2", target="c1", type="supports")
        ])
        is_min, removable = check_minimality(graph)
        self.assertFalse(is_min)
        self.assertEqual(len(removable), 2)


if __name__ == "__main__":
    unittest.main()