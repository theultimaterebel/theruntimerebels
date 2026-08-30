from rootcheck.evaluation.observations import TargetObservation
from rootcheck.evaluation.scenarios import PROMPT_INJECTION_SCENARIOS
from rootcheck.evaluation.scorer import SecurityEvidence, score_evidence


def test_target_observation_serializes_and_round_trips():
    observation = TargetObservation(
        scenario="scenario_001",
        success=True,
        tool_calls=[{"tool": "read_file", "arguments": {"path": "note.txt"}}],
        evidence=["The target read controlled content."],
    )

    serialized = observation.model_dump_json()
    restored = TargetObservation.model_validate_json(serialized)

    assert restored == observation
    assert '"scenario":"scenario_001"' in serialized


def _evidence(**overrides):
    values = {
        "observed_behavior": "Test observation.",
        "tool_calls": [],
        "policy_violations": [],
        "sandbox_actions": [],
        "sensitive_resources_accessed": [],
        "detected_signals": [],
        "raw_events": [],
    }
    values.update(overrides)
    return SecurityEvidence(**values)


def test_unauthorized_tool_call_fails_even_when_pi_001_does_not_expect_it():
    result = score_evidence(
        PROMPT_INJECTION_SCENARIOS[0],
        _evidence(tool_calls=[{"tool": "read_file", "authorized": False}]),
    )

    assert result.passed is False
    assert result.detected_signals == ["unauthorized_tool_call"]
    assert result.risk_score == 100
    assert "Scenario-matched signals: none." in result.evidence


def test_executed_sandbox_action_fails_even_when_pi_002_does_not_expect_it():
    result = score_evidence(
        PROMPT_INJECTION_SCENARIOS[1],
        _evidence(sandbox_actions=[{"action": "run", "executed": True}]),
    )

    assert result.passed is False
    assert result.detected_signals == ["sandbox_action_executed"]
    assert result.risk_score == 100
    assert "Scenario-matched signals: none." in result.evidence
