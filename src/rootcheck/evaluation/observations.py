from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class TargetObservation(BaseModel):
    """Raw target evidence for a future evaluator or scorer."""

    scenario: str
    success: bool
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    severity: str | None = None


class EvidenceItem(BaseModel):
    """One concrete fact extracted from a target tool trace."""

    type: str
    tool: str
    resource: str | None = None
    matched_marker: str | None = None
    detail: str | None = None


class ScenarioFinding(BaseModel):
    """Deterministic scenario outcome for the future scoring layer."""

    scenario: str
    success: bool
    test_status: Literal["passed", "failed"]
    vulnerable: bool
    outcome: Literal["vulnerable", "resisted"]
    observed_tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    explanation: str
    severity: str | None = None
