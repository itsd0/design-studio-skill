#!/usr/bin/env python3
"""
Design Studio — MCP server.

Exposes the skill's tools to any MCP-capable agent (Claude Code, Codex,
Cursor, Gemini CLI, OpenCode, …):

    design_studio_lint      source gates — slop, tokens, structure
    design_studio_verify    render gates — overflow, contrast, tap targets
    design_studio_contract  DESIGN.md ↔ artifact drift
    design_studio_extract   URL / file / screenshot → DESIGN.md + tokens.css
    design_studio_score     craft scorecard + distance from the default
    design_studio_directions  candidate directions from a brief

Transport: newline-delimited JSON-RPC 2.0 over stdio.

Usage:
    python3 scripts/mcp_server.py
    claude mcp add design-studio -- python3 scripts/mcp_server.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

PROTOCOL_VERSION = "2024-11-05"

TOOLS = [
    {
        "name": "design_studio_lint",
        "description": (
            "Lint a single-file HTML design artifact against the Design Studio quality "
            "gates: purple/indigo defaults, trust gradients, emoji icons, left-accent "
            "cards, invented metrics, filler copy, raw hex outside :root, missing alt "
            "text, unlabelled controls, zoom blockers, broken deck themes. "
            "Returns findings with severity, message and a fix."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the HTML artifact."},
            },
            "required": ["path"],
        },
    },
    {
        "name": "design_studio_verify",
        "description": (
            "Render a single-file HTML artifact in headless Chrome at 390/768/1440 and "
            "report what source analysis cannot see: horizontal overflow (with the "
            "element that causes it), text clipped by an overflow:hidden box, computed "
            "text contrast, tap targets under 24x24, runtime JS errors, missing image "
            "dimensions, missing focus indicators, a missing viewport meta."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the HTML artifact."},
            },
            "required": ["path"],
        },
    },
    {
        "name": "design_studio_contract",
        "description": (
            "Check an artifact against its DESIGN.md brand contract: token drift, missing "
            "tokens, font drift, missing contract sections, section order, and unrecorded "
            "experience dials. Finds DESIGN.md next to the artifact by default."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the HTML artifact."},
                "design": {"type": "string", "description": "Optional path to DESIGN.md."},
            },
            "required": ["path"],
        },
    },
    {
        "name": "design_studio_extract",
        "description": (
            "Extract a design system from a live URL, a local HTML file, or a reference "
            "screenshot and write a DESIGN.md brand contract plus a tokens.css twin. "
            "This is how a brand becomes a contract instead of a vibe."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "URL, HTML file or image path."},
                "out": {"type": "string", "description": "Output directory (default: cwd)."},
                "name": {"type": "string", "description": "Brand name for the contract."},
            },
            "required": ["target"],
        },
    },
    {
        "name": "design_studio_score",
        "description": (
            "Score a rendered artifact against a design review: hierarchy, type "
            "discipline, accent budget, section rhythm, content completeness, motion, "
            "self-containment — and how far the page sits from the default AI look."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the HTML artifact."},
            },
            "required": ["path"],
        },
    },
    {
        "name": "design_studio_directions",
        "description": (
            "Derive candidate visual directions from a brief — palette, type, density, "
            "and the reason each one fits — or render them side by side into a single "
            "comparison sheet so the user can choose."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "brief": {"type": "string", "description": "The brief or product description."},
                "count": {"type": "integer", "description": "How many candidates (default 3)."},
                "sheet": {"type": "string", "description": "Optional PNG path for the comparison sheet."},
            },
            "required": ["brief"],
        },
    },
    {
        "name": "design_studio_handoff",
        "description": (
            "Turn an approved artifact into an implementation spec another engineer or "
            "agent can build from: tokens, type, page inventory, components, states, "
            "breakpoints, the accessibility contract and the acceptance checks. Writes "
            "HANDOFF.md next to the artifact."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the HTML artifact."},
                "design": {"type": "string", "description": "Optional path to DESIGN.md."},
                "out": {"type": "string", "description": "Optional output path."},
            },
            "required": ["path"],
        },
    },
    {
        "name": "design_studio_review",
        "description": (
            "Run all four gates over an artifact and write a publishable review document: "
            "a verdict, findings per gate, the craft scorecard, screenshots and the "
            "judgement checklist that still needs a human. Exits non-zero on a P0."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the HTML artifact."},
                "out": {"type": "string", "description": "Optional output path for the report."},
            },
            "required": ["path"],
        },
    },
]


def run_tool(name: str, args: dict) -> str:
    """Run a tool and return its output as text."""
    path = args.get("path")
    if name == "design_studio_lint":
        cmd = [sys.executable, str(HERE / "lint.py"), "--json", path]
    elif name == "design_studio_verify":
        cmd = [sys.executable, str(HERE / "verify.py"), "--json", path]
    elif name == "design_studio_contract":
        cmd = [sys.executable, str(HERE / "contract.py"), "--json"]
        if args.get("design"):
            cmd += ["--design", args["design"]]
        cmd += [path]
    elif name == "design_studio_extract":
        cmd = [sys.executable, str(HERE / "extract.py"), args["target"], "--json"]
        if args.get("out"):
            cmd += ["--out", args["out"]]
        if args.get("name"):
            cmd += ["--name", args["name"]]
    elif name == "design_studio_score":
        cmd = [sys.executable, str(HERE / "score.py"), "--json", path]
    elif name == "design_studio_directions":
        cmd = [sys.executable, str(HERE / "directions.py"), "--brief", args.get("brief", "")]
        if args.get("count"):
            cmd += ["--count", str(args["count"])]
        if args.get("sheet"):
            cmd += ["--sheet", args["sheet"]]
        cmd += ["--json"]
    elif name == "design_studio_handoff":
        cmd = [sys.executable, str(HERE / "handoff.py"), path, "--json"]
        if args.get("design"):
            cmd += ["--design", args["design"]]
        if args.get("out"):
            cmd += ["--out", args["out"]]
    elif name == "design_studio_review":
        cmd = [sys.executable, str(HERE / "review.py"), path, "--json"]
        if args.get("out"):
            cmd += ["--out", args["out"]]
    else:
        return f"unknown tool: {name}"

    proc = subprocess.run(cmd, capture_output=True, text=True)
    out = proc.stdout.strip()
    if not out:
        out = (proc.stderr or "no output").strip()
    return out


def send(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload) + "\n")
    sys.stdout.flush()


def handle(message: dict) -> None:
    method = message.get("method")
    mid = message.get("id")
    params = message.get("params", {})

    if method is None:
        return  # a response to something we sent — ignore

    if method == "initialize":
        send({
            "jsonrpc": "2.0", "id": mid,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "design-studio", "version": "1.8.0"},
            },
        })
    elif method == "tools/list":
        send({"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}})
    elif method == "tools/call":
        name = params.get("name", "")
        args = params.get("arguments", {})
        try:
            text = run_tool(name, args)
        except Exception as exc:  # a tool must never kill the server
            text = f"tool error: {exc}"
        send({
            "jsonrpc": "2.0", "id": mid,
            "result": {
                "content": [{"type": "text", "text": text}],
                "isError": False,
            },
        })
    elif method == "ping":
        send({"jsonrpc": "2.0", "id": mid, "result": {}})
    elif method.startswith("notifications/"):
        return
    elif mid is not None:
        send({
            "jsonrpc": "2.0", "id": mid,
            "error": {"code": -32601, "message": f"method not found: {method}"},
        })


def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except ValueError:
            continue
        try:
            handle(message)
        except Exception as exc:
            mid = message.get("id")
            if mid is not None:
                send({
                    "jsonrpc": "2.0", "id": mid,
                    "error": {"code": -32603, "message": str(exc)},
                })
    return 0


if __name__ == "__main__":
    sys.exit(main())
