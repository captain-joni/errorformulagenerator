"""Pydantic request/response schemas for the API in app/main.py."""
from __future__ import annotations

from pydantic import BaseModel, Field


class PreviewRequest(BaseModel):
    formula: str


class VariableInfo(BaseModel):
    name: str
    is_known_constant: bool = False
    constant_value: float | None = None
    constant_label: str | None = None
    constant_unit: str | None = None


class PreviewResponse(BaseModel):
    latex: str
    variables: list[VariableInfo] = Field(default_factory=list)


class DifferentiateRequest(BaseModel):
    formula: str
    variables: list[str] = Field(default_factory=list)


class DifferentiateResponse(BaseModel):
    original_latex: str
    latex: str
    python_equation: str


class VariableValue(BaseModel):
    value: str
    error: str = "0"


class CalcRequest(BaseModel):
    formula: str
    error_formula: str
    values: dict[str, VariableValue] = Field(default_factory=dict)


class CalcResponse(BaseModel):
    value: float
    error: float
    formatted: str


class ErrorResponse(BaseModel):
    detail: str
