from rootcheck.evaluation.observations import TargetObservation


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
