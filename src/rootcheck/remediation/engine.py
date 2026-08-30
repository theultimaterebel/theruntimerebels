"""Narrow, reviewable remediations for controlled RootCheck scenarios."""

from __future__ import annotations

from pydantic import BaseModel

from rootcheck.evaluation.scenarios import INDIRECT_PROMPT_INJECTION_SCENARIO
from rootcheck.target.tools import TargetToolRuntime


class RemediationProposal(BaseModel):
    scenario_id: str
    title: str
    explanation: str
    change: str
    requires_human_approval: bool = True


def propose_remediation(scenario_id: str) -> RemediationProposal:
    if scenario_id != INDIRECT_PROMPT_INJECTION_SCENARIO.id:
        raise ValueError(f"no remediation proposal is available for scenario: {scenario_id}")
    return RemediationProposal(
        scenario_id=scenario_id,
        title="Stop trusting instructions embedded in files",
        explanation="Treat file content as untrusted data, not follow-on tool instructions.",
        change="Disable the target's controlled untrusted-file instruction policy.",
    )


def apply_remediation(scenario_id: str, runtime: TargetToolRuntime) -> dict[str, str]:
    propose_remediation(scenario_id)
    return runtime.apply_remediation(scenario_id)
