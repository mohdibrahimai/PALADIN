"""Simple document retrieval and span extraction module.

Retrievers index a collection of documents and can return the most
relevant documents for a query.  This package provides a very simple
TF‑IDF based retriever implemented in pure Python.  Span extraction
helpers live in the `spans` module.
"""

from .retrieve import SimpleRetriever  # noqa: F401