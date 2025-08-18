"""Numeric and date/time operations verifier.

Calculation nodes contain simple arithmetic expressions stored in the
``code`` field and a stringified result in ``result``.  The
``check_numeric_calc`` function safely re‑executes the arithmetic
expression using only basic operators and compares it to the
expected result.  The ``check_date_after`` function checks that one
date is on or after a threshold.
"""

from __future__ import annotations

import ast
import operator as op
from datetime import datetime
from typing import Any


# Allowed AST nodes for safe arithmetic evaluation
_ALLOWED_NODES = {
    ast.Expression, ast.BinOp, ast.Num, ast.Add, ast.Sub, ast.Mult,
    ast.Div, ast.FloorDiv, ast.Mod, ast.USub, ast.UnaryOp, ast.Pow,
    ast.Load, ast.Constant
}

_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv,
    ast.Mod: op.mod,
}


def _eval_node(node: ast.AST) -> Any:
    if type(node) not in _ALLOWED_NODES:
        raise ValueError(f"Disallowed AST node {type(node)}")
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.UnaryOp):
        return -_eval_node(node.operand)
    if isinstance(node, ast.BinOp):
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        op_type = type(node.op)
        if op_type not in _OPS:
            raise ValueError(f"Unsupported operator {op_type}")
        return _OPS[op_type](left, right)
    raise ValueError(f"Unsupported AST node {type(node)}")


def check_numeric_calc(code: str, expected: str) -> bool:
    """Return True if evaluating ``code`` equals ``expected``.

    The expression must consist only of numbers and basic operators.
    """
    try:
        expr_ast = ast.parse(code, mode="eval")
        result = _eval_node(expr_ast)
        return str(result) == str(expected)
    except Exception:
        return False


def check_date_after(date_str: str, fmt: str, threshold_str: str) -> bool:
    """Return True if date_str in the given format is on or after threshold_str."""
    date = datetime.strptime(date_str, fmt)
    threshold = datetime.strptime(threshold_str, fmt)
    return date >= threshold