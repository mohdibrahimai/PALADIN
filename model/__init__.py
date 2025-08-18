"""Model components for PALADIN.

The model package contains the simple answerer and proof planner used
in this reference implementation.  These components are deliberately
lightweight and rule‑based: the answerer extracts candidate answers
using heuristics and the planner builds a minimal evidence graph from
retrieved documents.  In a production system you should replace
these with properly trained language models.
"""

from .answerer import answer_question  # noqa: F401
from .planner import plan_proof  # noqa: F401
from .runner import PaladinRunner  # noqa: F401