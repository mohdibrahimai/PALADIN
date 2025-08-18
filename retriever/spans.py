"""Span extraction utilities.

When the retriever returns a full document, the planner often needs
only a small span of text that directly supports the answer.  This
module provides simple heuristics for extracting such spans around the
query terms.
"""

from __future__ import annotations

from typing import List


def _tokenize_words(text: str) -> List[str]:
    return [w for w in text.split() if w]


def extract_span(doc_text: str, query: str, window: int = 30) -> str:
    """Return a substring of ``doc_text`` centred on the first occurrence of the query.

    The returned span will contain at most ``window`` words.  If the
    query does not occur in the document, the first ``window`` words of
    the document are returned instead.
    """
    words = _tokenize_words(doc_text)
    q_words = _tokenize_words(query.lower())
    # Find first index of any query token in the document
    idx = -1
    lower_words = [w.lower() for w in words]
    for qi in q_words:
        if qi in lower_words:
            idx = lower_words.index(qi)
            break
    if idx == -1:
        # No overlap; return start of document
        idx = 0
    start = max(0, idx - window // 2)
    end = min(len(words), start + window)
    return ' '.join(words[start:end])