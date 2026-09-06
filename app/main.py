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
from prometheus_client import Counter
from prometheus_fastapi_instrumentator import Instrumentator

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

# --- Metrics -----------------------------------------------------------
#
# This app only *exposes* metrics (via /metrics, Prometheus text format) --
# it does not run or ship a Prometheus/Grafana stack itself. Scraping,
# storage and dashboards are an external concern (point an existing
# Prometheus at this container's /metrics and add it as a Grafana
# datasource); see CLAUDE.md for the full picture.
#
# Instrumentator() with defaults gives generic HTTP metrics for free --
# http_requests_total{handler,method,status} (this is "how often was the
# site/API hit"), request latency histograms, etc. -- labeled by route, so
# "/", "/api/preview", "/api/differentiate", "/api/calc" are each broken
# out individually.
Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

# On top of the generic HTTP counters above, these track the actual
# business events the user cares about ("how many error formulas did it
# generate"), independent of HTTP status/route bookkeeping.
PREVIEWS_RENDERED = Counter(
    "efg_previews_rendered_total",
    "Successful formula previews (POST /api/preview)",
)
FORMULAS_GENERATED = Counter(
    "efg_formulas_generated_total",
    "Successful error-propagation formulas generated (POST /api/differentiate)",
)
CALCULATIONS_PERFORMED = Counter(
    "efg_calculations_performed_total",
    "Successful numeric evaluations (POST /api/calc)",
)
FORMULA_ERRORS = Counter(
    "efg_formula_errors_total",
    "Requests rejected with a FormulaError (bad user input), by endpoint",
    ["endpoint"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/preview", response_model=PreviewResponse, responses={400: {"model": ErrorResponse}})
def preview(req: PreviewRequest) -> PreviewResponse:
    """Render a formula as LaTeX so the user can check it parsed as intended."""
    try:
        expr = mathcore.parse_formula(req.formula)
        names = mathcore.detect_variables(req.formula, expr)
        response = PreviewResponse(latex=mathcore.to_latex(expr), variables=mathcore.variable_info(names))
    except mathcore.FormulaError as exc:
        FORMULA_ERRORS.labels(endpoint="preview").inc()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    PREVIEWS_RENDERED.inc()
    return response


@app.post(
    "/api/differentiate",
    response_model=DifferentiateResponse,
    responses={400: {"model": ErrorResponse}},
)
def differentiate(req: DifferentiateRequest) -> DifferentiateResponse:
    """Symbolically build the Gaussian error propagation formula."""
    try:
        expr, error_expr, delta_symbols = mathcore.differentiate(req.formula, req.variables)
        response = DifferentiateResponse(
            original_latex=mathcore.to_latex(expr),
            latex=mathcore.to_latex(error_expr, delta_symbols),
            python_equation=str(error_expr),
        )
    except mathcore.FormulaError as exc:
        FORMULA_ERRORS.labels(endpoint="differentiate").inc()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    FORMULAS_GENERATED.inc()
    return response


@app.post("/api/calc", response_model=CalcResponse, responses={400: {"model": ErrorResponse}})
def calc(req: CalcRequest) -> CalcResponse:
    """Numerically evaluate the formula and its propagated error."""
    try:
        values = {name: {"value": v.value, "error": v.error} for name, v in req.values.items()}
        value, error = mathcore.evaluate(req.formula, req.error_formula, values)
        response = CalcResponse(value=value, error=error, formatted=mathcore.format_measurement(value, error))
    except mathcore.FormulaError as exc:
        FORMULA_ERRORS.labels(endpoint="calc").inc()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    CALCULATIONS_PERFORMED.inc()
    return response


# Mounted last / at "/" so it only catches what the API routes above don't --
# serves public/index.html, app.js, styles.css.
app.mount("/", StaticFiles(directory=PUBLIC_DIR, html=True), name="public")
