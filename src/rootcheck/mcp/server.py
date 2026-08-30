from __future__ import annotations

import os
from typing import Any

from mcp.server.mcpserver import MCPServer

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


def main() -> None:
    server.run(
        "streamable-http",
        host=os.getenv("MCP_HOST") or "127.0.0.1",
        port=int(os.getenv("MCP_PORT") or "8000"),
        streamable_http_path=os.getenv("MCP_PATH") or "/mcp",
    )


if __name__ == "__main__":
    main()
