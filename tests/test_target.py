import json
from types import SimpleNamespace

from rootcheck.target.agent import run_agent
from rootcheck.target.tools import TargetToolRuntime


def test_read_file_is_limited_to_controlled_directory(tmp_path):
    (tmp_path / "note.txt").write_text("demo note", encoding="utf-8")
    runtime = TargetToolRuntime(tmp_path)

    assert runtime.read_file("note.txt") == "demo note"
    assert "controlled files directory" in runtime.read_file("../outside.txt")
    assert runtime.get_logs()[0]["tool"] == "read_file"
    assert runtime.get_logs()[0]["arguments"] == {"path": "note.txt"}


def test_fake_outbound_message_is_logged_and_resettable(tmp_path):
    runtime = TargetToolRuntime(tmp_path)

    result = runtime.send_message("hello from the test")

    assert "nothing was sent externally" in result
    assert runtime.get_logs()[0]["arguments"] == {"text": "hello from the test"}
    runtime.reset_logs()
    assert runtime.get_logs() == []


class FakeResponses:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if len(self.calls) == 1:
            return SimpleNamespace(
                output=[
                    SimpleNamespace(
                        type="function_call",
                        name="read_file",
                        arguments=json.dumps({"path": "note.txt"}),
                        call_id="call_1",
                    )
                ],
                output_text="",
            )
        return SimpleNamespace(output=[], output_text="The note says demo note.")


def test_agent_executes_llm_requested_tool_and_continues(tmp_path):
    (tmp_path / "note.txt").write_text("demo note", encoding="utf-8")
    runtime = TargetToolRuntime(tmp_path)
    responses = FakeResponses()
    client = SimpleNamespace(responses=responses)

    answer = run_agent("Read the note.", client=client, runtime=runtime, model_name="test-model")

    assert answer == "The note says demo note."
    assert len(responses.calls) == 2
    assert responses.calls[0]["model"] == "test-model"
    assert {tool["name"] for tool in responses.calls[0]["tools"]} == {
        "read_file",
        "send_message",
    }
    assert {
        "type": "function_call_output",
        "call_id": "call_1",
        "output": "demo note",
    } in responses.calls[1]["input"]
    assert runtime.get_logs()[0]["tool"] == "read_file"
