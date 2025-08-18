"""Basic lexical entailment checker.

This module provides a naive implementation of natural language
inference (NLI).  It checks whether the hypothesis is lexically
entailed by the premise by computing the ratio of hypothesis tokens
that appear in the premise.  It is not a replacement for trained
entailment models but allows the verifier to flag obvious
contradictions or unsupported claims.
"""

from __future__ import annotations

from typing import List


def _tokenize(text: str) -> List[str]:
    return [t.lower() for t in text.split() if t]


def check_entailment(premise: str, hypothesis: str, threshold: float = 0.5) -> bool:
    """Return True if the premise lexically entails the hypothesis.

    The entailment score is the fraction of hypothesis tokens that
    appear in the premise.  A threshold of 0.5 means at least half
    of the hypothesis tokens must be present in the premise.  The
    threshold can be adjusted by callers.
    """
    premise_tokens = set(_tokenize(premise))
    hypo_tokens = _tokenize(hypothesis)
    if not hypo_tokens:
        return False
    matches = sum(1 for t in hypo_tokens if t in premise_tokens)
    return (matches / len(hypo_tokens)) >= threshold