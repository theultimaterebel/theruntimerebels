from src.agent import run_agent


def test_run_agent_returns_expected_status():
    assert run_agent() == "Agent Harness is running"
