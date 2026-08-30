from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any


TOOL_NAMES = ("read_file", "send_message")
INDIRECT_PROMPT_INJECTION_REMEDIATION = "scenario_001_indirect_prompt_injection"


class TargetToolRuntime:
    """Tools and evidence storage owned by the target agent."""

    def __init__(self, files_root: Path | str | None = None) -> None:
        self.files_root = (
            Path(files_root) if files_root is not None else Path(__file__).parent / "files"
        ).resolve()
        self._logs: list[dict[str, Any]] = []
        self._follow_file_instructions = True
        self._lock = Lock()

    def _record(self, tool: str, arguments: dict[str, Any], result: str) -> None:
        record = {
            "tool": tool,
            "arguments": deepcopy(arguments),
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        with self._lock:
            self._logs.append(record)

    def read_file(self, path: str) -> str:
        """Read one text file under the controlled target files directory."""
        arguments = {"path": path}
        try:
            requested_path = Path(path)
            if requested_path.is_absolute() or "\x00" in path:
                raise ValueError("path must be a relative path without null bytes")

            resolved_path = (self.files_root / requested_path).resolve()
            try:
                resolved_path.relative_to(self.files_root)
            except ValueError as exc:
                raise ValueError("path must stay inside the controlled files directory") from exc

            if not resolved_path.is_file():
                raise FileNotFoundError(f"controlled file not found: {path}")

            result = resolved_path.read_text(encoding="utf-8")
        except (OSError, ValueError) as exc:
            result = f"Tool error: {exc}"

        self._record("read_file", arguments, result)
        return result

    def send_message(self, text: str) -> str:
        """Record a fake outbound message; never contact an external service."""
        result = "Fake outbound channel recorded the message; nothing was sent externally."
        self._record("send_message", {"text": text}, result)
        return result

    def invoke(self, tool: str, arguments: dict[str, Any]) -> str:
        if tool == "read_file":
            return self.read_file(**arguments)
        if tool == "send_message":
            return self.send_message(**arguments)
        return f"Tool error: unknown target tool {tool!r}"

    def get_logs(self) -> list[dict[str, Any]]:
        with self._lock:
            return deepcopy(self._logs)

    def reset_logs(self) -> None:
        with self._lock:
            self._logs.clear()

    def available_files(self) -> list[str]:
        if not self.files_root.exists():
            return []
        return sorted(
            path.relative_to(self.files_root).as_posix()
            for path in self.files_root.rglob("*")
            if path.is_file()
        )

    def follows_file_instructions(self) -> bool:
        with self._lock:
            return self._follow_file_instructions

    def apply_remediation(self, scenario_id: str) -> dict[str, str]:
        if scenario_id != INDIRECT_PROMPT_INJECTION_REMEDIATION:
            raise ValueError(f"no remediation is available for scenario: {scenario_id}")
        with self._lock:
            already_applied = not self._follow_file_instructions
            self._follow_file_instructions = False
        result = (
            "Remediation was already active; untrusted file instructions remain disabled."
            if already_applied
            else "Remediation applied: untrusted file instructions are no longer trusted."
        )
        self._record("apply_remediation", {"scenario_id": scenario_id}, result)
        return {"status": "already_applied" if already_applied else "applied", "result": result}


_DEFAULT_RUNTIME = TargetToolRuntime()


def get_default_runtime() -> TargetToolRuntime:
    return _DEFAULT_RUNTIME


def get_logs() -> list[dict[str, Any]]:
    return _DEFAULT_RUNTIME.get_logs()


def reset_logs() -> None:
    _DEFAULT_RUNTIME.reset_logs()
