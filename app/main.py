"""FastAPI app: serves the frontend and the error-formula-generator API.

Replaces the old Node/Express server + three standalone Python CLI scripts
with a single in-process Python service. See CLAUDE.md for the full
before/after picture.
"""
from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from . import mathcore
from .models import (
    CalcRequest,
    CalcResponse,
    DifferentiateRequest,
    DifferentiateResponse,
    ErrorResponse,
    PreviewRequest,
    PreviewResponse,
)

logger = logging.getLogger("errorformulagenerator")

BASE_DIR = Path(__file__).resolve().parent.parent
PUBLIC_DIR = BASE_DIR / "public"

app = FastAPI(title="Error Formula Generator")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/preview", response_model=PreviewResponse, responses={400: {"model": ErrorResponse}})
def preview(req: PreviewRequest) -> PreviewResponse:
    """Render a formula as LaTeX so the user can check it parsed as intended."""
    try:
        expr = mathcore.parse_formula(req.formula)
        return PreviewResponse(latex=mathcore.to_latex(expr))
    except mathcore.FormulaError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post(
    "/api/differentiate",
    response_model=DifferentiateResponse,
    responses={400: {"model": ErrorResponse}},
)
def differentiate(req: DifferentiateRequest) -> DifferentiateResponse:
    """Symbolically build the Gaussian error propagation formula."""
    try:
        expr, error_expr = mathcore.differentiate(req.formula, req.variables)
        return DifferentiateResponse(
            original_latex=mathcore.to_latex(expr),
            latex=mathcore.to_latex(error_expr),
            python_equation=str(error_expr),
        )
    except mathcore.FormulaError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/calc", response_model=CalcResponse, responses={400: {"model": ErrorResponse}})
def calc(req: CalcRequest) -> CalcResponse:
    """Numerically evaluate the formula and its propagated error."""
    try:
        values = {name: {"value": v.value, "error": v.error} for name, v in req.values.items()}
        value, error = mathcore.evaluate(req.formula, req.error_formula, values)
        return CalcResponse(value=value, error=error, formatted=mathcore.format_measurement(value, error))
    except mathcore.FormulaError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# Mounted last / at "/" so it only catches what the API routes above don't --
# serves public/index.html, app.js, styles.css.
app.mount("/", StaticFiles(directory=PUBLIC_DIR, html=True), name="public")
