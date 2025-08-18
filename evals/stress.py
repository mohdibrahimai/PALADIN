"""Stress tests for PALADIN (placeholder).

This module contains basic functions to test the robustness of PALADIN
under simple transformations such as paraphrasing or negation.  In
this environment we do not implement any paraphrasing models, so the
functions simply return the original input.  You can extend these
functions by integrating paraphrasing models or adding noise to the
query.
"""

from __future__ import annotations

from typing import List


def paraphrase_query(query: str) -> List[str]:
    """Return a list of paraphrased queries (identity function).

    Replace this implementation with calls to a paraphrasing model if
    you have access to one.  The default behaviour returns a list
    containing only the original query.
    """
    return [query]