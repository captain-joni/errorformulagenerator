"""Symbolic-math core for the error formula generator.

This module wraps SymPy for formula parsing, LaTeX rendering, symbolic
differentiation (Gaussian error propagation) and numeric evaluation. It runs
in-process (no shelling out, no subprocess, no eval() of untrusted input) --
see CLAUDE.md for why that matters and what it replaces.
"""
from __future__ import annotations

import math
import re

import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr

# Functions and constants a formula is allowed to use. Anything else that
# looks like a bare name -- INCLUDING single letters SymPy normally treats
# specially, e.g. "I" (imaginary unit), "E" (Euler's number), "Q"/"S"/"O"/"N"/"C"
# (assumption/singleton objects) -- is parsed as a plain free Symbol instead.
# That's the actual fix for the "capital I / Q don't work as variable names"
# bug from the old implementation: it's not a naming limitation, it's that the
# old scripts sympify()'d raw strings against SymPy's full default namespace.
_ALLOWED_CALLABLES = {
    name: getattr(sp, name)
    for name in (
        "sin", "cos", "tan", "asin", "acos", "atan", "atan2",
        "sinh", "cosh", "tanh", "asinh", "acosh", "atanh",
        "exp", "log", "sqrt", "Abs",
    )
}
_ALLOWED_CONSTANTS = {"pi": sp.pi}
# SymPy's parser transformations rewrite bare names into Symbol(...) calls and
# numeric literals into Integer(...)/Float(...)/Rational(...) calls, resolved
# against this namespace -- these four have to be present for *any* formula
# (even one with no functions/constants) to parse with an empty global_dict.
_CORE_CONSTRUCTORS = {
    "Symbol": sp.Symbol,
    "Integer": sp.Integer,
    "Float": sp.Float,
    "Rational": sp.Rational,
}
_SAFE_LOCALS = {**_ALLOWED_CALLABLES, **_ALLOWED_CONSTANTS, **_CORE_CONSTRUCTORS}

# Variable names that are exactly-known constants (mathematical, or SI base
# units fixed by definition since the 2019 redefinition -- these have *zero*
# uncertainty, not just a small one). Used only as a UI convenience: the
# frontend offers to auto-fill the value and skip asking for an error, but
# the user can always override a name here and use it as an ordinary
# variable instead (e.g. "c" for a heat capacity, "g" for a coefficient).
# `pi` is deliberately not in this table -- it's already a real SymPy
# constant handled in `_ALLOWED_CONSTANTS`/`parse_formula`, so it never shows
# up as a free variable in the first place.
KNOWN_CONSTANTS: dict[str, dict[str, object]] = {
    "e": {"value": math.e, "label": "Eulersche Zahl", "unit": ""},
    "c": {"value": 299792458, "label": "Lichtgeschwindigkeit im Vakuum (exakt, SI)", "unit": "m/s"},
    "h": {"value": 6.62607015e-34, "label": "Planck-Konstante (exakt, SI)", "unit": "J·s"},
    "hbar": {"value": 6.62607015e-34 / (2 * math.pi), "label": "reduzierte Planck-Konstante", "unit": "J·s"},
    "kB": {"value": 1.380649e-23, "label": "Boltzmann-Konstante (exakt, SI)", "unit": "J/K"},
    "NA": {"value": 6.02214076e23, "label": "Avogadro-Konstante (exakt, SI)", "unit": "1/mol"},
    "eps0": {"value": 8.8541878128e-12, "label": "elektrische Feldkonstante", "unit": "F/m"},
    "mu0": {"value": 1.25663706212e-6, "label": "magnetische Feldkonstante", "unit": "N/A²"},
    "g": {"value": 9.80665, "label": "Normfallbeschleunigung (Standardwert, ggf. anpassen)", "unit": "m/s²"},
}

_IDENTIFIER_RE = re.compile(r"[A-Za-z_][A-Za-z_0-9]*")


class FormulaError(ValueError):
    """A user-supplied formula/variable list/value couldn't be processed.

    Always caught at the API layer and turned into a 400 with the message
    shown to the user -- never a bare 500.
    """


def parse_formula(formula: str) -> sp.Expr:
    """Parse a Python-expression-style formula string into a SymPy expression.

    Parsed with an *empty* global namespace and only `_SAFE_LOCALS` as
    locals, so every bare name that isn't one of our whitelisted
    functions/constants becomes a plain Symbol -- SymPy's reserved names
    never shadow a user's variable.
    """
    formula = (formula or "").strip()
    if not formula:
        raise FormulaError("Formula is empty.")
    try:
        expr = parse_expr(formula, local_dict=dict(_SAFE_LOCALS), global_dict={}, evaluate=True)
    except FormulaError:
        raise
    except Exception as exc:  # SymPy's parser raises many different exception types
        raise FormulaError(f"Could not parse formula: {exc}") from exc
    if not isinstance(expr, sp.Basic):
        raise FormulaError("Formula did not parse into a valid expression.")
    return expr


_DELTA_PREFIX_RE = re.compile(r"^Delta(?P<rest>[A-Za-z_][A-Za-z0-9_]*)$")


def to_latex(expr: sp.Expr) -> str:
    """Render an expression as LaTeX, prettying up `DeltaX` symbols into `\\Delta_{X}`.

    Purely cosmetic (display only -- the `DeltaX` naming convention used
    everywhere else, e.g. `evaluate()`'s variable bindings, is untouched):
    SymPy's printer already turns `Delta_m` into `\\Delta_{m}` via its
    Greek-letter-name recognition, but not the no-separator `Deltam` this
    app actually uses, so re-symbol it with an underscore just for display.
    """
    display_expr = expr.xreplace({
        s: sp.Symbol(f"Delta_{match.group('rest')}")
        for s in expr.free_symbols
        if (match := _DELTA_PREFIX_RE.match(str(s)))
    })
    return sp.latex(display_expr)


def detect_variables(formula: str, expr: sp.Expr) -> list[str]:
    """Return the formula's free variable names, in the order they first appear.

    Reading order (rather than sorted()) is what makes the auto-generated
    variable panel in the UI feel like it matches what the user typed.
    Function names (sin, cos, ...) match the same identifier regex but are
    never in `expr.free_symbols`, so they're naturally excluded.
    """
    free_names = {str(s) for s in expr.free_symbols}
    seen: list[str] = []
    for match in _IDENTIFIER_RE.finditer(formula):
        name = match.group(0)
        if name in free_names and name not in seen:
            seen.append(name)
    return seen


def variable_info(names: list[str]) -> list[dict]:
    """Annotate variable names with known-constant info, for the frontend's
    "treat this as a fixed constant?" UI. See `KNOWN_CONSTANTS`."""
    info = []
    for name in names:
        const = KNOWN_CONSTANTS.get(name)
        if const:
            info.append({
                "name": name,
                "is_known_constant": True,
                "constant_value": const["value"],
                "constant_label": const["label"],
                "constant_unit": const["unit"],
            })
        else:
            info.append({
                "name": name,
                "is_known_constant": False,
                "constant_value": None,
                "constant_label": None,
                "constant_unit": None,
            })
    return info


def differentiate(formula: str, variables: list[str]) -> tuple[sp.Expr, sp.Expr]:
    """Build the Gaussian error-propagation formula for `formula`.

    Returns (original_expr, error_expr). error_expr is the sum of squares
    Sum_i( (df/dx_i * Delta_x_i)^2 ) *without* the outer square root -- kept
    that way on purpose, same as the original tool: easier to read/typeset
    for long formulas. The square root is applied at calculation time in
    `evaluate()` instead. The uncertainty of a variable named `X` is always
    referred to as `DeltaX` (no separator) in the generated formula.
    """
    var_names = [v.strip() for v in variables if v.strip()]
    if not var_names:
        raise FormulaError("No error-carrying variables given.")

    expr = parse_formula(formula)

    terms = []
    for name in var_names:
        symbol = sp.Symbol(name)
        derivative = sp.diff(expr, symbol)
        delta = sp.Symbol(f"Delta{name}")
        terms.append((derivative * delta) ** 2)

    error_expr = sp.Add(*terms)
    return expr, error_expr


def evaluate(
    formula: str,
    error_formula: str,
    values: dict[str, dict[str, str]],
) -> tuple[float, float]:
    """Numerically evaluate `formula` and its propagated error.

    `values` maps variable name -> {"value": ..., "error": ...}; both the
    variable and its `Delta<variable>` counterpart are bound from it.
    Evaluation goes through sympy.lambdify against NumPy -- no eval() of an
    untrusted string, and every SymPy function is supported automatically
    (not just a hardcoded sin/cos/tan/exp substring-replace list).
    """
    expr = parse_formula(formula)
    error_expr = parse_formula(error_formula)

    bindings: dict[str, float] = {}
    for raw_name, entry in values.items():
        name = raw_name.strip()
        if not name:
            continue
        try:
            bindings[name] = float(entry.get("value", ""))
        except (TypeError, ValueError) as exc:
            raise FormulaError(f"Variable '{name}': value must be a number.") from exc
        error_raw = entry.get("error") or "0"
        try:
            bindings[f"Delta{name}"] = float(error_raw)
        except (TypeError, ValueError) as exc:
            raise FormulaError(f"Variable '{name}': error must be a number.") from exc

    def _eval(target: sp.Expr) -> float:
        symbols = sorted(target.free_symbols, key=str)
        missing = [str(s) for s in symbols if str(s) not in bindings]
        if missing:
            raise FormulaError(f"Missing value(s) for: {', '.join(missing)}")
        func = sp.lambdify(symbols, target, modules=["numpy"])
        result = func(*(bindings[str(s)] for s in symbols))
        try:
            return float(np.real(result))
        except (TypeError, ValueError) as exc:
            raise FormulaError(f"Could not evaluate expression numerically: {exc}") from exc

    value = _eval(expr)
    error_value = _eval(error_expr)
    if error_value < 0:
        raise FormulaError("The computed error term is negative -- check the formula.")
    return value, float(np.sqrt(error_value))


def format_measurement(value: float, error: float) -> str:
    """Render "value +/- error", rounded to the error's leading significant digit.

    E.g. value=12.345, error=0.067 -> "12.30 ± 0.07". Falls back to a plain
    number if the error is zero/non-finite (no meaningful precision to round to).
    """
    if not math.isfinite(value):
        return str(value)
    if not math.isfinite(error) or error <= 0:
        return f"{value:.6g}"

    exponent = math.floor(math.log10(abs(error)))
    decimals = -exponent
    rounded_error = round(error, decimals)
    rounded_value = round(value, decimals)
    fmt_decimals = max(decimals, 0)
    return f"{rounded_value:.{fmt_decimals}f} ± {rounded_error:.{fmt_decimals}f}"
