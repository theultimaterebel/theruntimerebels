from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TargetObservation(BaseModel):
    """Raw target evidence for a future evaluator or scorer."""

    scenario: str
    success: bool
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    severity: str | None = None
