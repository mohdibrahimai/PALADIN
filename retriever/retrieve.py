"""A lightweight TF‑IDF based document retriever.

This module implements a simple retriever that indexes a list of
documents and returns the most relevant documents for a given query.
It is intentionally minimal and avoids external dependencies such as
scikit‑learn.  The retrieval quality is adequate for demonstration
purposes but not intended for production use.
"""

from __future__ import annotations

import json
import math
import os
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Iterable


def _tokenize(text: str) -> List[str]:
    """Whitespace tokenizer with basic stemming.

    The text is lowercased, punctuation is replaced with spaces and
    tokens are stemmed using PorterStemmer.  Stemming helps align
    morphological variants such as "boils" and "boiling".
    """
    from nltk.stem.porter import PorterStemmer  # imported inside to avoid global dependency
    stemmer = PorterStemmer()
    # Replace punctuation with spaces
    punct = ''.join([c for c in text if not c.isalnum() and not c.isspace()])
    trans = str.maketrans({c: ' ' for c in punct})
    cleaned = text.translate(trans).lower()
    tokens = [t for t in cleaned.split() if t]
    # Stem tokens
    return [stemmer.stem(t) for t in tokens]


class SimpleRetriever:
    """A pure Python TF‑IDF retriever.

    Given a list of documents, builds an inverted index, computes
    document frequencies and returns the top documents for a query
    using cosine similarity between TF‑IDF vectors.  All internal
    structures are computed eagerly at initialisation time.
    """

    def __init__(self, docs: List[Dict[str, str]]):
        """Create a retriever from a list of documents.

        Each document must be a dict with at least an ``id`` and
        ``text`` key.  Additional keys are ignored.
        """
        self.docs = docs
        self._vocab: Dict[str, int] = {}
        self._idf: Dict[str, float] = {}
        self._doc_vectors: List[Dict[str, float]] = []
        self._build_index()

    @classmethod
    def from_json(cls, path: str) -> "SimpleRetriever":
        """Load documents from a JSON file.

        The JSON file must contain a list of objects with ``id`` and
        ``text`` fields.  If the file does not exist, an empty
        retriever is returned.
        """
        if not os.path.exists(path):
            return cls([])
        with open(path, encoding="utf-8") as f:
            docs = json.load(f)
        return cls(docs)

    def _build_index(self) -> None:
        """Compute document frequencies, IDF and TF‑IDF vectors."""
        df: Counter[str] = Counter()
        doc_tokens: List[List[str]] = []
        # Tokenise documents and accumulate document frequencies
        for doc in self.docs:
            tokens = list(dict.fromkeys(_tokenize(doc.get("text", ""))))
            doc_tokens.append(tokens)
            df.update(tokens)
        # Build IDF
        num_docs = max(len(self.docs), 1)
        self._idf = {term: math.log((num_docs + 1) / (df_val + 1)) + 1.0 for term, df_val in df.items()}
        # Build TF‑IDF vectors
        self._doc_vectors = []
        for doc, tokens in zip(self.docs, doc_tokens):
            tf = Counter(_tokenize(doc.get("text", "")))
            vec: Dict[str, float] = {}
            for term, count in tf.items():
                idf = self._idf.get(term, 0.0)
                vec[term] = (count / len(tf)) * idf
            self._doc_vectors.append(vec)

    def _vectorise_query(self, query: str) -> Dict[str, float]:
        """Compute a TF‑IDF vector for the query."""
        tokens = _tokenize(query)
        tf = Counter(tokens)
        vec: Dict[str, float] = {}
        for term, count in tf.items():
            idf = self._idf.get(term, 0.0)
            vec[term] = (count / len(tf)) * idf
        return vec

    @staticmethod
    def _cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
        """Compute cosine similarity between two sparse vectors."""
        # dot product
        dot = sum(a.get(k, 0.0) * b.get(k, 0.0) for k in a)
        # norms
        norm_a = math.sqrt(sum(v * v for v in a.values()))
        norm_b = math.sqrt(sum(v * v for v in b.values()))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, str]]:
        """Return the top documents for the query.

        This implementation combines TF‑IDF cosine similarity with a
        simple keyword overlap score.  Documents with more query token
        overlap are weighted higher.  The top ``top_k`` documents are
        returned in descending score order.
        """
        if not self.docs:
            return []
        q_vec = self._vectorise_query(query)
        # Tokenise query for overlap measure
        q_tokens = set(_tokenize(query))
        scores: List[Tuple[float, int]] = []
        for i, doc_vec in enumerate(self._doc_vectors):
            cos = self._cosine(q_vec, doc_vec)
            # Overlap measure: sum IDF values of query tokens present in the document
            doc_tokens = set(_tokenize(self.docs[i].get("text", "")))
            overlap_weight = 0.0
            for tok in q_tokens:
                if tok in doc_tokens:
                    overlap_weight += self._idf.get(tok, 0.0)
            # Weight the cosine score by (1 + overlap_weight)
            weighted = cos * (1.0 + overlap_weight)
            scores.append((weighted, i))
        scores.sort(key=lambda x: x[0], reverse=True)
        top_indices = [idx for _, idx in scores[:top_k]]
        return [self.docs[i] for i in top_indices]