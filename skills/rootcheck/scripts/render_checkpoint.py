"""Render a small, safe checkpoint artifact from an evaluator outcome."""

from __future__ import annotations

import argparse
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument("--scenario", required=True)
parser.add_argument("--outcome", choices=("vulnerable", "resisted"), required=True)
parser.add_argument("--output", default="rootcheck-checkpoint.md")
args = parser.parse_args()

Path(args.output).write_text(
    f"# RootCheck checkpoint\\n\\nScenario: `{args.scenario}`\\n\\nOutcome: **{args.outcome}**\\n",
    encoding="utf-8",
)
print(args.output)
