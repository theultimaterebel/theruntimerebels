from __future__ import annotations

import os
from typing import Any

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

from rootcheck.evaluation.evaluator import evaluate_scenario
from rootcheck.evaluation.scenarios import get_scenario as get_scenario_definition
from rootcheck.evaluation.scenarios import list_scenarios as list_scenario_definitions
from rootcheck.remediation.engine import apply_remediation as apply_target_remediation
from rootcheck.remediation.engine import propose_remediation as build_remediation_proposal
from rootcheck.target.agent import inspect_target as inspect_target_agent
from rootcheck.target.agent import run_agent
from rootcheck.target.tools import get_default_runtime


server = MCPServer(
    name="rootcheck-target",
    title="RootCheck Target Adapter",
    description="MCP doorway to the isolated CandyBot target agent.",
    version="0.1.0",
)


@server.tool()
def send_message_to_target(message: str) -> str:
    """Send a message to the separate target agent and return its final response."""
    return run_agent(message, runtime=get_default_runtime())


@server.tool()
def get_target_logs() -> list[dict[str, Any]]:
    """Return structured evidence for tool calls made by the target agent."""
    return get_default_runtime().get_logs()


@server.tool()
def reset_target() -> dict[str, str]:
    """Clear target tool logs before another test run."""
    get_default_runtime().reset_logs()
    return {"status": "reset"}


@server.tool()
def inspect_target() -> dict[str, Any]:
    """Return non-secret metadata about the target agent and its tools."""
    return inspect_target_agent(runtime=get_default_runtime())


@server.tool()
def list_scenarios() -> list[dict[str, Any]]:
    """List the controlled RootCheck scenarios that can be run against the target."""
    return [scenario.model_dump(mode="json") for scenario in list_scenario_definitions()]


@server.tool()
def get_scenario(scenario_id: str) -> dict[str, Any]:
    """Return the message and expected evidence for one controlled scenario."""
    return get_scenario_definition(scenario_id).model_dump(mode="json")


@server.tool()
def evaluate_current_run(scenario_id: str) -> dict[str, Any]:
    """Deterministically evaluate the current target logs for one scenario."""
    logs = get_default_runtime().get_logs()
    return evaluate_scenario(scenario_id, logs).model_dump(mode="json")


@server.tool()
def propose_remediation(scenario_id: str) -> dict[str, Any]:
    """Describe the limited local remediation for a vulnerable scenario."""
    return build_remediation_proposal(scenario_id).model_dump(mode="json")


@server.tool(
    annotations=ToolAnnotations(
        destructiveHint=True,
        idempotentHint=True,
        openWorldHint=False,
    )
)
def apply_remediation(scenario_id: str) -> dict[str, str]:
    """Apply a local target change after human approval in TrueForge."""
    return apply_target_remediation(scenario_id, get_default_runtime())


def main() -> None:
    server.run(
        "streamable-http",
        host=os.getenv("MCP_HOST") or "127.0.0.1",
        port=int(os.getenv("MCP_PORT") or "8000"),
        streamable_http_path=os.getenv("MCP_PATH") or "/mcp",
    )


if __name__ == "__main__":
    main()
