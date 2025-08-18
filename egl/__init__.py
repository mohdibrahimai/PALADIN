"""Evidence Graph Language (EGL) package.

This package defines a small domain specific language for encoding
machine‑checkable proofs of answers.  The core types (Node, Edge
EvidenceGraph) live in the `schema` module.  Helper functions for
validating and compiling graphs live in `compiler`.
"""

from .schema import Node, Edge, EvidenceGraph  # noqa: F401