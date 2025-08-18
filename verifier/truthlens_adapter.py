"""Simplistic truth lens implementation.

The TruthLens concept categorises evidence into supported, contradicted
or unverifiable with respect to a hypothesis.  Here we use lexical
overlap to approximate support and look for simple negation patterns
to detect contradictions.  Everything else is treated as
unverifiable.
"""

from __future__ import annotations

from typing import List


def _tokenize(text: str) -> List[str]:
    return [t.lower() for t in text.split() if t]


def get_support_level(premise: str, hypothesis: str) -> str:
    """Classify the relation between premise and hypothesis.

    Returns one of ``"supported"``, ``"contradicted"`` or ``"unverifiable"``.
    The decision is based solely on lexical heuristics.  A real system
    should employ a robust NLI model and additional signals.
    """
    p_tokens = _tokenize(premise)
    h_tokens = _tokenize(hypothesis)
    if not h_tokens:
        return "unverifiable"
    # Contradiction heuristic: if the premise contains explicit negation of any hypothesis token
    negations = {"not", "no", "never"}
    for neg in negations:
        for tok in h_tokens:
            phrase = f"{neg} {tok}"
            if phrase in premise.lower():
                return "contradicted"
    # Compute support ratio
    matches = sum(1 for t in h_tokens if t in p_tokens)
    ratio = matches / len(h_tokens)
    if ratio >= 0.5:
        return "supported"
    if ratio <= 0.1:
        return "unverifiable"
    return "unverifiable"