"""Simple heuristic answerer for PALADIN.

Given a natural language query and a list of retrieved documents, this
module attempts to extract a plausible answer using simple pattern
matching.  It does not consult any external knowledge or large
language models.  The goal is to avoid speculation and base the
answer directly on the supplied documents.
"""

from __future__ import annotations

import re
from typing import List, Dict, Optional


def _extract_date(text: str) -> Optional[str]:
    """Search for a date pattern in the text and return the first match.

    This function looks for four‑digit years, month names followed by
    years (e.g. "November 2016") and ISO dates.  It returns the
    matching substring or None if nothing is found.
    """
    # Pattern for month names and years (e.g. January 2020)
    month_pattern = re.compile(r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b")
    match = month_pattern.search(text)
    if match:
        return match.group(0)
    # Pattern for ISO dates (YYYY‑MM‑DD or YYYY‑MM)
    iso_pattern = re.compile(r"\b\d{4}-\d{2}(?:-\d{2})?\b")
    match = iso_pattern.search(text)
    if match:
        return match.group(0)
    # Pattern for standalone years
    year_pattern = re.compile(r"\b\d{4}\b")
    match = year_pattern.search(text)
    if match:
        return match.group(0)
    return None


def answer_question(query: str, documents: List[Dict[str, str]]) -> str:
    """Return a best‑guess answer extracted from the supplied documents.

    The current implementation uses a few simple heuristics.  If the
    query contains ``when`` or ``date``, it searches for a date in
    the highest ranking document.  Otherwise it returns the first
    sentence of the top document truncated to 30 words.
    """
    if not documents:
        return "I don't know."
    top_doc = documents[0]["text"]
    lower_q = query.lower()
    # If question asks for a date
    if any(w in lower_q for w in ["when", "date", "year", "month"]):
        date = _extract_date(top_doc)
        if date:
            return date
    # Otherwise return the first sentence truncated
    # Split on period or newline
    sentence_end = re.search(r"[\.\n]", top_doc)
    first_sentence = top_doc[:sentence_end.start()] if sentence_end else top_doc
    words = first_sentence.split()
    truncated = ' '.join(words[:30])
    return truncated