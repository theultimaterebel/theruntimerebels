from rootcheck.mcp.server import (
    evaluate_current_run,
    get_target_logs,
    get_scenario,
    inspect_target,
    list_scenarios,
    reset_target,
)
from rootcheck.target.demo import FAKE_SECRET_MARKER
from rootcheck.target.tools import get_default_runtime


def test_inspect_target_exposes_safe_metadata():
    metadata = inspect_target()

    assert metadata["name"] == "CandyBot"
    assert metadata["available_tools"] == ["read_file", "send_message"]
    assert "public_note.txt" in metadata["controlled_files"]
    assert "fake local recorder" in metadata["outbound_channel"]


def test_mcp_reset_clears_target_logs():
    reset_target()
    get_default_runtime().send_message("test message")
    assert len(get_target_logs()) == 1
    assert reset_target() == {"status": "reset"}
    assert get_target_logs() == []


def test_mcp_scenario_tools_and_evaluation_use_structured_logs():
    scenario_id = "scenario_001_indirect_prompt_injection"
    scenario = get_scenario(scenario_id)

    assert [item["id"] for item in list_scenarios()] == [scenario_id]
    assert scenario["id"] == scenario_id

    runtime = get_default_runtime()
    reset_target()
    runtime.read_file("public_note.txt")
    runtime.read_file("fake_secret.txt")
    runtime.send_message(f"fake handoff: {FAKE_SECRET_MARKER}")

    finding = evaluate_current_run(scenario_id)

    assert finding["success"] is True
    assert finding["outcome"] == "vulnerable"
    reset_target()
