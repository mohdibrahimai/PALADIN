import unittest

from paladin.egl.schema import Node, Edge, EvidenceGraph, validate_graph
from paladin.egl.compiler import compile_graph


class TestEGL(unittest.TestCase):
    def test_compile_and_validate(self):
        raw = {
            "nodes": [
                {"id": "c1", "type": "claim", "text": "Earth is round"},
                {"id": "e1", "type": "evidence", "url": "doc1", "span": "Earth is round", "hash": "f728a5b0bc9cdf4c7ef49331f2b3c87d6a3b5b1b473d91dc2c4547606a4d5e63"},
            ],
            "edges": [
                {"source": "e1", "target": "c1", "type": "supports"},
            ],
        }
        graph = compile_graph(raw)
        self.assertIsInstance(graph, EvidenceGraph)
        errors = validate_graph(graph)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()