"""Verifier package.

The verifier performs deterministic checks over evidence graphs.  Each
submodule implements one aspect of verification: source binding
(`hashcheck`), lexical entailment (`nli_check`), numeric and date
recomputation (`numeric_time_check`), truth lens (`truthlens_adapter`)
and minimality (`minimality`).
"""

from .hashcheck import check_source_binding  # noqa: F401
from .nli_check import check_entailment  # noqa: F401
from .numeric_time_check import check_numeric_calc, check_date_after  # noqa: F401
from .truthlens_adapter import get_support_level  # noqa: F401
from .minimality import check_minimality  # noqa: F401