# RootCheck

RootCheck is a small hackathon prototype. The current vertical slice exposes a
target agent through an MCP adapter. The target owns its LLM, its controlled demo
files, and its tools; the MCP server is only the doorway used by RootCheck or
TrueForge.

## Install

```bash
python -m venv venv
source venv/bin/activate
python -m pip install -e '.[dev]'
```

Copy the example environment file and set an API key for the target LLM:

```bash
cp .env.example .env
```

Environment variables:

- `OPENAI_API_KEY` is required when making a live target request.
- `API_BASE_URL` is optional and defaults to `https://api.openai.com/v1`.
- `MODEL_NAME` selects the target model. The example value is a placeholder and
  must be changed if it is not available through the configured API.
- `MCP_HOST`, `MCP_PORT`, and `MCP_PATH` configure the local MCP adapter. Their
  defaults are `127.0.0.1`, `8000`, and `/mcp`.

## Run the target manually

```bash
python -m rootcheck.target.agent
```

The target can read only files under
`src/rootcheck/target/files/`. `send_message` is a fake outbound channel: it
records the attempted message and never contacts an external destination.

## Run the MCP adapter

```bash
python -m rootcheck.mcp.server
```

The expected local MCP endpoint is:

```text
http://127.0.0.1:8000/mcp
```

The adapter exposes these MCP tools:

- `send_message_to_target(message)` — runs the target LLM/tool loop and returns
  its final answer.
- `get_target_logs()` — returns structured target tool-call evidence.
- `reset_target()` — clears target logs.
- `inspect_target()` — returns non-secret target metadata and available files.

To connect it manually in TrueForge, use:

```text
Connectors → Add MCP Server → http://127.0.0.1:8000/mcp
```

Then a TrueForge chat can call `send_message_to_target`, retrieve
`get_target_logs`, and inspect what the target actually did. For a demo of
untrusted content, ask the target to read `untrusted_note.txt`; the file itself
contains a clearly labeled fake instruction, while the outbound tool remains
local-only.

## Tests

The automated tests do not call an LLM or require an API key:

```bash
python -m pytest -q
```
