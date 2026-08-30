from rootcheck.mcp.server import (
    get_target_logs,
    inspect_target,
    reset_target,
)


def test_inspect_target_exposes_safe_metadata():
    metadata = inspect_target()

    assert metadata["name"] == "CandyBot"
    assert metadata["available_tools"] == ["read_file", "send_message"]
    assert "public_note.txt" in metadata["controlled_files"]
    assert "fake local recorder" in metadata["outbound_channel"]


def test_mcp_reset_clears_target_logs():
    reset_target()
    assert get_target_logs() == []
